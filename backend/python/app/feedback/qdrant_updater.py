"""
Qdrant updater - Updates vector DB payloads with verification results.

Fast feedback tier (Tier 1):
- <100ms update latency
- EMA smoothing (α=0.1)
- Temporal decay
- Batch updates
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer
from qdrant_client import AsyncQdrantClient

from app.infrastructure.metrics import get_metrics


class QdrantUpdater:
    """Updates Qdrant payloads with verification results."""

    ALPHA = 0.1  # EMA smoothing factor
    LAMBDA_DECAY = 0.01  # Temporal decay factor (per day)

    def __init__(
        self,
        kafka_brokers: str,
        consumer_group: str,
        qdrant_client: AsyncQdrantClient,
        collection_name: str,
        batch_size: int = 10,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize Qdrant updater.

        Args:
            kafka_brokers: Kafka broker list
            consumer_group: Consumer group ID
            qdrant_client: Qdrant async client
            collection_name: Qdrant collection name
            batch_size: Batch size for updates
            logger: Optional logger
        """
        self.kafka_brokers = kafka_brokers
        self.consumer_group = consumer_group
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.batch_size = batch_size
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = get_metrics()
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.shutdown_requested = False

    async def start(self) -> None:
        """Start Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            "verification_complete",
            bootstrap_servers=self.kafka_brokers,
            group_id=self.consumer_group,
            enable_auto_commit=False,
            max_poll_records=self.batch_size,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        self.logger.info(
            f"✅ Qdrant updater started (collection: {self.collection_name})"
        )

    async def stop(self) -> None:
        """Stop consumer."""
        self.shutdown_requested = True
        if self.consumer:
            await self.consumer.stop()
        self.logger.info("✅ Qdrant updater stopped")

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

                # Flatten messages
                all_messages = []
                for partition_messages in messages.values():
                    all_messages.extend(partition_messages)

                self.logger.info(
                    f"📬 Received {len(all_messages)} verification results"
                )

                # Process batch
                await self.process_batch([msg.value for msg in all_messages])

                # Commit
                await self.consumer.commit()

        except Exception as e:
            self.logger.error(f"Updater error: {str(e)}")
            raise
        finally:
            await self.stop()

    async def process_batch(self, messages: List[Dict[str, Any]]) -> None:
        """
        Process batch of verification results.

        Args:
            messages: List of verification result messages
        """
        import time

        start_time = time.time()

        for msg in messages:
            try:
                await self.update_payload(msg)
            except Exception as e:
                self.logger.error(f"Failed to update payload: {str(e)}")

        duration_ms = (time.time() - start_time) * 1000
        self.logger.info(f"✅ Updated {len(messages)} payloads in {duration_ms:.2f}ms")

        # Verify latency requirement (<100ms)
        avg_latency = duration_ms / len(messages) if messages else 0
        if avg_latency > 100:
            self.logger.warning(
                f"⚠️  Average update latency {avg_latency:.2f}ms exceeds 100ms target"
            )

    async def update_payload(self, message: Dict[str, Any]) -> None:
        """
        Update single payload with verification result.

        Args:
            message: Verification result message
        """
        chunk_id = message.get("chunk_id") or message.get("request_id")
        verdict = message["verdict"]
        confidence = message["confidence"]
        formalization_similarity = message.get("formalization_similarity")
        timestamp = message.get("timestamp", datetime.utcnow().isoformat())

        # Calculate EMA score
        historical_score = await self._get_historical_score(chunk_id)
        new_score = self.ALPHA * confidence + (1 - self.ALPHA) * historical_score

        # Calculate temporal weight
        temporal_weight = self._calculate_temporal_weight(timestamp)

        # Prepare payload update
        payload_update = {
            "verification": {
                "verdict": verdict,
                "confidence": confidence,
                "formalization_similarity": formalization_similarity,
                "timestamp": timestamp,
                "failure_mode": message.get("failure_mode"),
            },
            "verification_metrics": {
                "verification_quality_score": new_score,
                "last_verified": timestamp,
                "temporal_weight": temporal_weight,
            },
        }

        # Update Qdrant
        await self.qdrant_client.set_payload(
            collection_name=self.collection_name,
            payload=payload_update,
            points=[chunk_id],
        )

        self.logger.debug(
            f"✅ Updated payload for chunk {chunk_id} (score: {new_score:.3f})"
        )

    async def _get_historical_score(self, chunk_id: str) -> float:
        """
        Get historical verification score for chunk.

        Args:
            chunk_id: Chunk ID

        Returns:
            Historical score (default: 0.0)
        """
        try:
            points = await self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_payload=True,
            )

            if points:
                return (
                    points[0]
                    .payload.get("verification_metrics", {})
                    .get("verification_quality_score", 0.0)
                )

        except Exception as e:
            self.logger.warning(f"Failed to get historical score: {str(e)}")

        return 0.0

    def _calculate_temporal_weight(self, timestamp_str: str) -> float:
        """
        Calculate temporal weight with exponential decay.

        Formula: exp(-λ × Δt) where Δt is days since verification

        Args:
            timestamp_str: ISO format timestamp

        Returns:
            Temporal weight (0.0 to 1.0)
        """
        import math

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            delta_days = (datetime.utcnow() - timestamp).total_seconds() / 86400
            return math.exp(-self.LAMBDA_DECAY * delta_days)
        except Exception:
            return 1.0  # Default to full weight


async def main():
    """Main entry point."""
    import os

    from qdrant_client import AsyncQdrantClient

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    collection_name = os.getenv("QDRANT_COLLECTION", "pipeshub_chunks")

    qdrant_client = AsyncQdrantClient(host=qdrant_host, port=qdrant_port)

    updater = QdrantUpdater(
        kafka_brokers=kafka_brokers,
        consumer_group="qdrant-updater-group",
        qdrant_client=qdrant_client,
        collection_name=collection_name,
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
