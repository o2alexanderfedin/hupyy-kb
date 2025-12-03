"""
Verification orchestrator - Kafka consumer for verify_chunks topic.

Responsibilities:
- Consume verification requests from Kafka
- Invoke Hupyy client for verification
- Publish results to verification_complete/verification_failed topics
- Handle retries with exponential backoff
- Respect feature flags
- Graceful shutdown
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config.feature_flags import FeatureFlagService
from app.infrastructure.metrics import get_metrics
from app.verification.hupyy_client import HupyyClient
from app.verification.models import (
    VerificationRequest,
    VerificationResult,
    VerificationVerdict,
)


class VerificationOrchestrator:
    """
    Orchestrates verification workflow via Kafka.

    Consumes from: verify_chunks
    Produces to: verification_complete, verification_failed
    """

    def __init__(
        self,
        kafka_brokers: str,
        consumer_group: str,
        hupyy_client: HupyyClient,
        feature_flag_service: FeatureFlagService,
        batch_size: int = 10,
        max_concurrency: int = 5,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize verification orchestrator.

        Args:
            kafka_brokers: Kafka broker list (e.g., "localhost:9092")
            consumer_group: Kafka consumer group ID
            hupyy_client: Hupyy client instance
            feature_flag_service: Feature flag service
            batch_size: Batch size for consuming messages
            max_concurrency: Max concurrent verifications
            logger: Optional logger instance
        """
        self.kafka_brokers = kafka_brokers
        self.consumer_group = consumer_group
        self.hupyy_client = hupyy_client
        self.feature_flag_service = feature_flag_service
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = get_metrics()

        # Kafka clients (initialized in start())
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None

        # Shutdown flag
        self.shutdown_requested = False

    async def start(self) -> None:
        """Initialize Kafka consumer and producer."""
        # Create consumer
        self.consumer = AIOKafkaConsumer(
            "verify_chunks",
            bootstrap_servers=self.kafka_brokers,
            group_id=self.consumer_group,
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=self.batch_size,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Create producer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        await self.consumer.start()
        await self.producer.start()

        self.logger.info(
            f"✅ Verification orchestrator started (group: {self.consumer_group}, "
            f"batch: {self.batch_size}, concurrency: {self.max_concurrency})"
        )

    async def stop(self) -> None:
        """Stop Kafka consumer and producer."""
        self.shutdown_requested = True

        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        if self.hupyy_client:
            await self.hupyy_client.close()

        self.logger.info("✅ Verification orchestrator stopped")

    async def run(self) -> None:
        """Main orchestrator loop."""
        await self.start()

        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda: asyncio.create_task(self.stop())
            )

        try:
            while not self.shutdown_requested:
                # Check if verification is enabled
                flags = await self.feature_flag_service.get_verification_flags()
                if not flags.verification_enabled:
                    self.logger.debug(
                        "⏸️  Verification disabled by feature flag, sleeping..."
                    )
                    await asyncio.sleep(5)
                    continue

                # Consume batch
                messages = await self.consumer.getmany(
                    timeout_ms=1000, max_records=self.batch_size
                )

                if not messages:
                    continue

                # Flatten messages from all partitions
                all_messages = []
                for partition_messages in messages.values():
                    all_messages.extend(partition_messages)

                self.logger.info(
                    f"📬 Received {len(all_messages)} verification requests"
                )

                # Process batch
                await self.process_batch(all_messages)

                # Commit offsets
                await self.consumer.commit()

        except Exception as e:
            self.logger.error(f"❌ Orchestrator error: {str(e)}")
            raise
        finally:
            await self.stop()

    async def process_batch(self, messages: List[Any]) -> None:
        """
        Process batch of verification requests.

        Args:
            messages: List of Kafka messages
        """
        # Parse messages into verification requests
        verification_requests = []
        message_metadata = []  # Store original message metadata

        for msg in messages:
            try:
                # Extract message data
                data = msg.value
                request = VerificationRequest(
                    request_id=data["request_id"],
                    content=data["content"],
                    chunk_index=data.get("chunk_index", 0),
                    total_chunks=data.get("total_chunks", 1),
                    nl_query=data["nl_query"],
                    source_document_id=data.get("source_document_id"),
                    timestamp=(
                        datetime.fromisoformat(data["timestamp"])
                        if "timestamp" in data
                        else datetime.utcnow()
                    ),
                )
                verification_requests.append(request)
                message_metadata.append(
                    {
                        "org_id": data.get("org_id"),
                        "user_id": data.get("user_id"),
                        "query_id": data.get("query_id"),
                        "document_id": data.get("document_id"),
                    }
                )

            except Exception as e:
                self.logger.error(f"Failed to parse message: {str(e)}")
                # Send to DLQ (dead letter queue)
                await self.send_to_dlq(msg.value, f"Parse error: {str(e)}")

        # Verify in parallel
        try:
            results = await self.hupyy_client.verify_parallel(
                verification_requests, max_concurrency=self.max_concurrency
            )

            # Publish results
            for result, metadata in zip(results, message_metadata):
                await self.publish_result(result, metadata)

        except Exception as e:
            self.logger.error(f"Batch verification failed: {str(e)}")
            # Retry individual requests
            for req, metadata in zip(verification_requests, message_metadata):
                try:
                    result = await self.hupyy_client.verify(req)
                    await self.publish_result(result, metadata)
                except Exception as retry_error:
                    self.logger.error(
                        f"Individual verification failed: {str(retry_error)}"
                    )
                    await self.send_to_failed_topic(req, metadata, str(retry_error))

    async def publish_result(
        self, result: VerificationResult, metadata: Dict[str, Any]
    ) -> None:
        """
        Publish verification result to appropriate topic.

        Args:
            result: Verification result
            metadata: Original request metadata
        """
        try:
            # Prepare message
            message = {
                "request_id": result.request_id,
                "chunk_index": result.chunk_index,
                "verdict": result.verdict.value,
                "confidence": result.confidence,
                "formalization_similarity": result.formalization_similarity,
                "explanation": result.explanation,
                "failure_mode": (
                    result.failure_mode.value if result.failure_mode else None
                ),
                "metadata": result.metadata,
                "duration_seconds": result.duration_seconds,
                "cached": result.cached,
                "timestamp": result.timestamp.isoformat(),
                # Include original metadata
                "org_id": metadata.get("org_id"),
                "user_id": metadata.get("user_id"),
                "query_id": metadata.get("query_id"),
                "document_id": metadata.get("document_id"),
            }

            # Publish to appropriate topic
            if result.verdict in [VerificationVerdict.SAT, VerificationVerdict.UNSAT]:
                await self.producer.send("verification_complete", value=message)
                self.logger.info(
                    f"✅ Published result for {result.request_id} (verdict: {result.verdict.value})"
                )
            else:
                await self.producer.send("verification_failed", value=message)
                self.logger.warning(
                    f"⚠️  Published failed result for {result.request_id} "
                    f"(verdict: {result.verdict.value})"
                )

            # Update metrics
            self.metrics.record_verification_request(
                (
                    "success"
                    if result.verdict
                    in [VerificationVerdict.SAT, VerificationVerdict.UNSAT]
                    else "failure"
                ),
                result.duration_seconds,
            )

        except KafkaError as e:
            self.logger.error(f"Failed to publish result: {str(e)}")
            raise

    async def send_to_failed_topic(
        self, request: VerificationRequest, metadata: Dict[str, Any], error_message: str
    ) -> None:
        """
        Send failed verification to verification_failed topic.

        Args:
            request: Original verification request
            metadata: Request metadata
            error_message: Error description
        """
        try:
            message = {
                "request_id": request.request_id,
                "chunk_index": request.chunk_index,
                "content": request.content,
                "nl_query": request.nl_query,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat(),
                "org_id": metadata.get("org_id"),
                "user_id": metadata.get("user_id"),
                "query_id": metadata.get("query_id"),
                "document_id": metadata.get("document_id"),
            }

            await self.producer.send("verification_failed", value=message)
            self.logger.warning(
                f"⚠️  Sent failed request {request.request_id} to failed topic"
            )

        except Exception as e:
            self.logger.error(f"Failed to send to failed topic: {str(e)}")

    async def send_to_dlq(
        self, message_data: Dict[str, Any], error_reason: str
    ) -> None:
        """
        Send message to dead letter queue.

        Args:
            message_data: Original message data
            error_reason: Reason for DLQ
        """
        try:
            dlq_message = {
                "original_message": message_data,
                "error_reason": error_reason,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.producer.send("verify_chunks_dlq", value=dlq_message)
            self.logger.error(f"☠️  Sent message to DLQ: {error_reason}")

        except Exception as e:
            self.logger.error(f"Failed to send to DLQ: {str(e)}")


async def main():
    """Main entry point for orchestrator service."""
    import os

    from app.infrastructure.cache import VerificationCache
    from app.verification.hupyy_client import HupyyClient

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Load configuration from environment
    kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "hupyy")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    hupyy_api_url = os.getenv(
        "HUPYY_API_URL", "https://verticalslice-smt-service-gvav8.ondigitalocean.app"
    )

    # Initialize services
    logger.info("🚀 Starting verification orchestrator...")

    feature_flag_service = await FeatureFlagService.create(mongo_uri, mongo_db, logger)
    cache = await VerificationCache.create(redis_url, logger=logger)
    hupyy_client = HupyyClient(api_url=hupyy_api_url, cache=cache, logger=logger)

    # Create orchestrator
    orchestrator = VerificationOrchestrator(
        kafka_brokers=kafka_brokers,
        consumer_group="verification-orchestrator-group",
        hupyy_client=hupyy_client,
        feature_flag_service=feature_flag_service,
        batch_size=10,
        max_concurrency=5,
        logger=logger,
    )

    # Run
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
