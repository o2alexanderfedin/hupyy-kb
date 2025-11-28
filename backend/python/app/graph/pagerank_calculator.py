"""
PageRank calculator with quality multipliers.

Modified PageRank formula (from architecture):
PR_v(A) = (1-d)/N + d × Σ(Q(Ti) × PR_v(Ti) / C(Ti))

Where:
- d = 0.85 (damping factor)
- Q(Ti) = quality multiplier (0.5 to 2.0)
- C(Ti) = outlink count

Algorithm: Power iteration (max 100 iterations, ε=1e-6)
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple

from aiokafka import AIOKafkaConsumer
from arango.database import StandardDatabase


class PageRankCalculator:
    """Calculates PageRank on ArangoDB citation network."""

    DAMPING_FACTOR = 0.85
    MAX_ITERATIONS = 100
    CONVERGENCE_EPSILON = 1e-6

    def __init__(
        self,
        kafka_brokers: str,
        consumer_group: str,
        arango_db: StandardDatabase,
        documents_collection: str = "documents",
        citations_collection: str = "citations",
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize PageRank calculator.

        Args:
            kafka_brokers: Kafka broker list
            consumer_group: Consumer group ID
            arango_db: ArangoDB database instance
            documents_collection: Documents collection name
            citations_collection: Citations edge collection name
            logger: Optional logger
        """
        self.kafka_brokers = kafka_brokers
        self.consumer_group = consumer_group
        self.arango_db = arango_db
        self.documents_collection = documents_collection
        self.citations_collection = citations_collection
        self.logger = logger or logging.getLogger(__name__)
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.shutdown_requested = False

    async def start(self) -> None:
        """Start Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            "pagerank_recalc",
            bootstrap_servers=self.kafka_brokers,
            group_id=self.consumer_group,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        self.logger.info("✅ PageRank calculator started")

    async def stop(self) -> None:
        """Stop consumer."""
        self.shutdown_requested = True
        if self.consumer:
            await self.consumer.stop()
        self.logger.info("✅ PageRank calculator stopped")

    async def run(self) -> None:
        """Main calculation loop."""
        await self.start()

        try:
            while not self.shutdown_requested:
                messages = await self.consumer.getmany(timeout_ms=1000)

                if not messages:
                    # Periodic recalculation (daily)
                    await asyncio.sleep(86400)  # 24 hours
                    await self.calculate_full_pagerank()
                    continue

                # Triggered recalculation
                self.logger.info("🔄 Triggered PageRank recalculation")
                await self.calculate_full_pagerank()
                await self.consumer.commit()

        except Exception as e:
            self.logger.error(f"PageRank calculator error: {str(e)}")
            raise
        finally:
            await self.stop()

    async def calculate_full_pagerank(self) -> Dict[str, float]:
        """
        Calculate PageRank for all documents.

        Returns:
            Dictionary mapping document_id to PageRank score
        """
        import time

        start_time = time.time()

        # Get citation graph
        documents, citation_graph, quality_multipliers = (
            await self._build_citation_graph()
        )

        if not documents:
            self.logger.warning("No documents found, skipping PageRank")
            return {}

        N = len(documents)
        self.logger.info(f"📊 Calculating PageRank for {N} documents")

        # Initialize PageRank scores (uniform distribution)
        pagerank = {doc_id: 1.0 / N for doc_id in documents}

        # Power iteration
        for iteration in range(self.MAX_ITERATIONS):
            new_pagerank = {}
            max_delta = 0.0

            for doc_id in documents:
                # Calculate sum of incoming contributions
                incoming_sum = 0.0

                for source_id, targets in citation_graph.items():
                    if doc_id in targets:
                        quality = quality_multipliers.get(source_id, 1.0)
                        outlink_count = len(targets)
                        incoming_sum += quality * pagerank[source_id] / outlink_count

                # Modified PageRank formula
                new_score = (
                    1 - self.DAMPING_FACTOR
                ) / N + self.DAMPING_FACTOR * incoming_sum
                new_pagerank[doc_id] = new_score

                # Track convergence
                delta = abs(new_score - pagerank[doc_id])
                max_delta = max(max_delta, delta)

            pagerank = new_pagerank

            # Check convergence
            if max_delta < self.CONVERGENCE_EPSILON:
                self.logger.info(
                    f"✅ PageRank converged after {iteration + 1} iterations"
                )
                break

        # Update ArangoDB
        await self._update_pagerank_scores(pagerank)

        duration = time.time() - start_time
        self.logger.info(f"✅ PageRank calculation completed in {duration:.2f}s")

        return pagerank

    async def _build_citation_graph(
        self,
    ) -> Tuple[List[str], Dict[str, List[str]], Dict[str, float]]:
        """
        Build citation graph from ArangoDB.

        Returns:
            Tuple of (document_ids, citation_graph, quality_multipliers)
        """
        documents_col = self.arango_db.collection(self.documents_collection)
        citations_col = self.arango_db.collection(self.citations_collection)

        # Get all documents
        documents = []
        quality_multipliers = {}

        for doc in documents_col.all():
            doc_id = doc["_key"]
            documents.append(doc_id)

            # Get quality multiplier
            quality = doc.get("quality_signals", {}).get("quality_multiplier", 1.0)
            quality_multipliers[doc_id] = quality

        # Build citation graph (adjacency list)
        citation_graph: Dict[str, List[str]] = {doc_id: [] for doc_id in documents}

        for citation in citations_col.all():
            source = citation["_from"].split("/")[1]  # Extract ID from _from
            target = citation["_to"].split("/")[1]  # Extract ID from _to

            if source in citation_graph:
                citation_graph[source].append(target)

        return documents, citation_graph, quality_multipliers

    async def _update_pagerank_scores(self, pagerank: Dict[str, float]) -> None:
        """
        Update PageRank scores in ArangoDB.

        Args:
            pagerank: Dictionary mapping document_id to PageRank score
        """
        documents_col = self.arango_db.collection(self.documents_collection)

        for doc_id, score in pagerank.items():
            try:
                documents_col.update(
                    {
                        "_key": doc_id,
                        "pagerank_data": {
                            "verification_weighted_pagerank": score,
                            "last_calculated": asyncio.get_event_loop().time(),
                        },
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to update PageRank for {doc_id}: {str(e)}")


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

    calculator = PageRankCalculator(
        kafka_brokers=kafka_brokers,
        consumer_group="pagerank-calculator-group",
        arango_db=db,
        logger=logger,
    )

    try:
        await calculator.run()
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
    finally:
        await calculator.stop()


if __name__ == "__main__":
    asyncio.run(main())
