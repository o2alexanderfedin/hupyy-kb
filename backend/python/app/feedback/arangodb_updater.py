"""
ArangoDB updater - Updates knowledge graph with verification results.

Responsibilities:
- Aggregate document-level verification metrics
- Calculate quality multipliers for PageRank
- Update document properties
- Trigger PageRank recalculation on significant changes
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from arango.database import StandardDatabase

from app.infrastructure.metrics import get_metrics


class ArangoDBUpdater:
    """Updates ArangoDB documents with verification metrics."""

    def __init__(
        self,
        kafka_brokers: str,
        consumer_group: str,
        arango_db: StandardDatabase,
        documents_collection: str = "documents",
        batch_size: int = 10,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize ArangoDB updater.

        Args:
            kafka_brokers: Kafka broker list
            consumer_group: Consumer group ID
            arango_db: ArangoDB database instance
            documents_collection: Documents collection name
            batch_size: Batch size for updates
            logger: Optional logger
        """
        self.kafka_brokers = kafka_brokers
        self.consumer_group = consumer_group
        self.arango_db = arango_db
        self.documents_collection = documents_collection
        self.batch_size = batch_size
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = get_metrics()
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.shutdown_requested = False

    async def start(self) -> None:
        """Start Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            "verification_complete",
            bootstrap_servers=self.kafka_brokers,
            group_id=self.consumer_group,
            enable_auto_commit=False,
            max_poll_records=self.batch_size,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        await self.consumer.start()
        await self.producer.start()
        self.logger.info("✅ ArangoDB updater started")

    async def stop(self) -> None:
        """Stop consumer and producer."""
        self.shutdown_requested = True
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        self.logger.info("✅ ArangoDB updater stopped")

    async def run(self) -> None:
        """Main update loop."""
        await self.start()

        try:
            while not self.shutdown_requested:
                messages = await self.consumer.getmany(
                    timeout_ms=1000, max_records=self.batch_size
                )

                if not messages:
                    continue

                all_messages = []
                for partition_messages in messages.values():
                    all_messages.extend(partition_messages)

                self.logger.info(
                    f"📬 Received {len(all_messages)} verification results"
                )

                await self.process_batch([msg.value for msg in all_messages])
                await self.consumer.commit()

        except Exception as e:
            self.logger.error(f"ArangoDB updater error: {str(e)}")
            raise
        finally:
            await self.stop()

    async def process_batch(self, messages: List[Dict[str, Any]]) -> None:
        """Process batch of verification results."""
        for msg in messages:
            try:
                await self.update_document(msg)
            except Exception as e:
                self.logger.error(f"Failed to update document: {str(e)}")

    async def update_document(self, message: Dict[str, Any]) -> None:
        """
        Update document with verification metrics.

        Args:
            message: Verification result message
        """
        document_id = message.get("document_id") or message.get("source_document_id")
        if not document_id:
            self.logger.warning("No document_id in message, skipping")
            return

        verdict = message["verdict"]
        confidence = message["confidence"]

        # Get current document
        collection = self.arango_db.collection(self.documents_collection)
        try:
            document = collection.get(document_id)
        except Exception:
            self.logger.warning(f"Document {document_id} not found")
            return

        # Get current metrics
        metrics = document.get("verification_metrics", {})
        verified_chunks = metrics.get("verified_chunks", 0)
        total_chunks = metrics.get("total_chunks", 1)
        avg_confidence = metrics.get("avg_confidence", 0.0)
        sat_count = metrics.get("sat_count", 0)
        unsat_count = metrics.get("unsat_count", 0)
        unknown_count = metrics.get("unknown_count", 0)

        # Update metrics
        verified_chunks += 1
        avg_confidence = (
            avg_confidence * (verified_chunks - 1) + confidence
        ) / verified_chunks

        if verdict == "SAT":
            sat_count += 1
        elif verdict == "UNSAT":
            unsat_count += 1
        else:
            unknown_count += 1

        verification_rate = verified_chunks / total_chunks if total_chunks > 0 else 0.0

        # Calculate quality multiplier
        old_quality_multiplier = document.get("quality_signals", {}).get(
            "quality_multiplier", 1.0
        )
        new_quality_multiplier = self._calculate_quality_multiplier(avg_confidence)

        # Update document
        update_data = {
            "verification_metrics": {
                "total_chunks": total_chunks,
                "verified_chunks": verified_chunks,
                "verification_rate": verification_rate,
                "avg_confidence": avg_confidence,
                "sat_count": sat_count,
                "unsat_count": unsat_count,
                "unknown_count": unknown_count,
                "last_verification_scan": message.get("timestamp"),
            },
            "quality_signals": {
                "quality_multiplier": new_quality_multiplier,
                "reliability_class": self._get_reliability_class(avg_confidence),
            },
        }

        collection.update({"_key": document_id, **update_data})

        self.logger.debug(
            f"✅ Updated document {document_id} "
            f"(verified: {verified_chunks}, avg_conf: {avg_confidence:.3f})"
        )

        # Trigger PageRank recalc if significant change
        delta_quality = abs(new_quality_multiplier - old_quality_multiplier)
        if delta_quality > 0.2:
            await self._trigger_pagerank_recalc(document_id)

    def _calculate_quality_multiplier(self, avg_confidence: float) -> float:
        """
        Calculate PageRank quality multiplier.

        Formula (from architecture):
        - avg_conf < 0.5 → Q = 0.5 (penalize low quality)
        - no verification → Q = 1.0 (neutral)
        - avg_conf ≥ 0.5 → Q = 1.0 + avg_conf (boost, max 2.0)

        Args:
            avg_confidence: Average confidence score

        Returns:
            Quality multiplier (0.5 to 2.0)
        """
        if avg_confidence < 0.5:
            return 0.5
        else:
            return min(1.0 + avg_confidence, 2.0)

    def _get_reliability_class(self, avg_confidence: float) -> str:
        """
        Classify document reliability.

        Args:
            avg_confidence: Average confidence score

        Returns:
            Reliability class (high/medium/low)
        """
        if avg_confidence >= 0.75:
            return "high"
        elif avg_confidence >= 0.50:
            return "medium"
        else:
            return "low"

    async def _trigger_pagerank_recalc(self, document_id: str) -> None:
        """
        Trigger PageRank recalculation.

        Args:
            document_id: Document that changed
        """
        try:
            message = {
                "document_id": document_id,
                "trigger": "quality_change",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await self.producer.send("pagerank_recalc", value=message)
            self.logger.info(f"🔄 Triggered PageRank recalc for {document_id}")
        except Exception as e:
            self.logger.error(f"Failed to trigger PageRank recalc: {str(e)}")


async def main():
    """Main entry point."""
    import os

    from arango import ArangoClient

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")
    arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
    arango_username = os.getenv("ARANGO_USERNAME", "root")
    arango_password = os.getenv("ARANGO_PASSWORD", "")
    arango_db_name = os.getenv("ARANGO_DB", "pipeshub")

    client = ArangoClient(hosts=arango_url)
    db = client.db(arango_db_name, username=arango_username, password=arango_password)

    updater = ArangoDBUpdater(
        kafka_brokers=kafka_brokers,
        consumer_group="arango-updater-group",
        arango_db=db,
        logger=logger,
    )

    try:
        await updater.run()
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
    finally:
        await updater.stop()


if __name__ == "__main__":
    asyncio.run(main())
