# Hupyy Verification Operations Runbook

## Overview

This runbook provides operational guidance for the Hupyy-PipesHub SMT verification integration. Use this guide for monitoring, troubleshooting, and managing the verification system.

## Architecture Overview

```
User Query → Search API → Qdrant/ArangoDB
                ↓
           verify_chunks (Kafka topic)
                ↓
       Verification Orchestrator
                ↓
           Hupyy API (1-2 min latency)
                ↓
   verification_complete/verification_failed
                ↓
       ┌────────┴────────┐
       ↓                 ↓
  Qdrant Updater    ArangoDB Updater
  (EMA scores)      (document metrics)
       ↓                 ↓
  Enhanced Ranking  PageRank Calculator
```

## Service Components

### 1. Verification Orchestrator
- **Location**: `backend/python/app/verification/orchestrator.py`
- **Purpose**: Consumes verification requests, calls Hupyy API, publishes results
- **Consumer Group**: `verification-orchestrator-group`
- **Topics**: Consumes `verify_chunks`, produces to `verification_complete` and `verification_failed`

### 2. Qdrant Updater
- **Location**: `backend/python/app/feedback/qdrant_updater.py`
- **Purpose**: Updates vector DB payloads with verification metadata
- **Consumer Group**: `qdrant-updater-group`
- **Topics**: Consumes `verification_complete`
- **SLA**: <100ms update latency

### 3. ArangoDB Updater
- **Location**: `backend/python/app/feedback/arangodb_updater.py`
- **Purpose**: Updates document-level verification metrics
- **Consumer Group**: `arango-updater-group`
- **Topics**: Consumes `verification_complete`, produces to `pagerank_recalc`

### 4. PageRank Calculator
- **Location**: `backend/python/app/graph/pagerank_calculator.py`
- **Purpose**: Recalculates PageRank with quality multipliers
- **Consumer Group**: `pagerank-calculator-group`
- **Schedule**: Daily or triggered

## Feature Flags

All feature flags are stored in MongoDB collection `feature_flags`.

### Enable/Disable Verification

```python
from app.config.feature_flags import FeatureFlagService

# Initialize service
flag_service = await FeatureFlagService.create(
    mongo_uri="mongodb://localhost:27017",
    database_name="pipeshub"
)

# Enable verification
await flag_service.set_flag("verification_enabled", True)

# Disable verification
await flag_service.set_flag("verification_enabled", False)
```

### Adjust Ranking Weight

```python
# Set verification weight (0.0 to 0.15)
await flag_service.set_flag("verification_ranking_weight", 0.15)

# Gradual rollout (increase slowly)
await flag_service.set_flag("verification_ranking_weight", 0.05)  # Week 1
await flag_service.set_flag("verification_ranking_weight", 0.10)  # Week 2
await flag_service.set_flag("verification_ranking_weight", 0.15)  # Week 3
```

### Adjust Top-K Sampling

```python
# Verify 5 results (lighter load)
await flag_service.set_flag("verification_top_k", 5)

# Verify 10 results (heavier load)
await flag_service.set_flag("verification_top_k", 10)
```

### Adjust Cache TTL

```python
# Set cache TTL to 12 hours (43200 seconds)
await flag_service.set_flag("verification_cache_ttl", 43200)

# Set cache TTL to 48 hours (172800 seconds)
await flag_service.set_flag("verification_cache_ttl", 172800)
```

## Monitoring

### Grafana Dashboard

Access Grafana dashboard at: `http://localhost:3000` (or production URL)

Dashboard name: **Hupyy Verification Metrics**

Key panels:
1. **Success Rate**: Verification success percentage
2. **Circuit Breaker State**: Open/Half-Open/Closed indicator
3. **Cache Hit Rate**: Cache effectiveness
4. **Queue Depth**: Kafka consumer lag
5. **Latency Percentiles**: p50, p95, p99 verification times
6. **Chunks by Verdict**: SAT/UNSAT/UNKNOWN distribution

### Circuit Breaker States

- **CLOSED (Green)**: Normal operation, all requests proceed
- **HALF_OPEN (Yellow)**: Testing recovery, limited requests allowed
- **OPEN (Red)**: Service degraded, all requests fail fast

### Alert Thresholds

**CRITICAL (PagerDuty)**:
- Circuit breaker stays OPEN for >5 minutes
- Verification success rate <50% for >10 minutes
- Kafka consumer lag >10,000 messages

**WARNING (Slack)**:
- Cache hit rate <40%
- Queue depth >1000 messages
- Average latency >120 seconds

## Troubleshooting

### Circuit Breaker is OPEN

**Symptoms**: Verification requests fail immediately, circuit breaker OPEN in Grafana

**Diagnosis**:
```bash
# Check Hupyy API health
curl https://verticalslice-smt-service-gvav8.ondigitalocean.app/health

# Check circuit breaker logs
docker logs verification-orchestrator | grep "Circuit breaker"
```

**Resolution**:
1. Verify Hupyy API is accessible
2. If Hupyy is down, wait for recovery (circuit auto-recovers after 60s)
3. If persistent, check network connectivity
4. Manually reset circuit breaker (restart orchestrator)

### Kafka Consumer Lag Growing

**Symptoms**: `queue_depth` metric increasing, verification delayed

**Diagnosis**:
```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group verification-orchestrator-group --describe
```

**Resolution**:
1. Scale orchestrator (increase replicas)
2. Increase `max_concurrency` (default: 5)
3. Reduce `verification_top_k` (verify fewer results)
4. Check if Hupyy API is slow (1-2 min expected)

### Cache Hit Rate Low (<40%)

**Symptoms**: Most verifications hit Hupyy API, high latency

**Diagnosis**:
```bash
# Check cache stats
redis-cli INFO stats
redis-cli DBSIZE
```

**Resolution**:
1. Increase cache TTL (`verification_cache_ttl`)
2. Verify Redis is not evicting entries (check memory)
3. Check if content is changing frequently (invalidation issue)

### Qdrant Update Latency >100ms

**Symptoms**: Slow feedback loop, ranking updates delayed

**Diagnosis**:
```bash
# Check Qdrant performance
curl http://localhost:6333/metrics
```

**Resolution**:
1. Increase Qdrant resources (CPU, memory)
2. Reduce batch size in Qdrant updater
3. Create indexes on verification fields
4. Check network latency to Qdrant

### Verification Stuck in UNKNOWN

**Symptoms**: Most verdicts are UNKNOWN, low SAT/UNSAT rate

**Diagnosis**:
```bash
# Check failure mode distribution
docker logs verification-orchestrator | grep "failure_mode"
```

**Resolution**:
1. If `timeout`: Increase `verification_timeout_seconds`
2. If `theory_incomplete`: Expected for undecidable logics
3. If `parse_error`: Check SMT formula formatting
4. Review Hupyy API error responses

## Cache Management

### Invalidate Cache for Document

```python
from app.infrastructure.cache import VerificationCache

cache = await VerificationCache.create("redis://localhost:6379")

# Invalidate specific content
await cache.invalidate("(assert (> x 0))")

# Invalidate all entries
await cache.invalidate_pattern("*")

await cache.close()
```

### View Cache Stats

```python
cache = await VerificationCache.create("redis://localhost:6379")

stats = await cache.get_cache_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Memory used: {stats['memory_bytes']} bytes")

await cache.close()
```

## Scaling

### Scale Verification Orchestrator

**Docker Compose**:
```yaml
# docker-compose.prod.yml
verification-orchestrator:
  replicas: 3  # Scale to 3 instances
```

**Kubernetes**:
```bash
kubectl scale deployment verification-orchestrator --replicas=3
```

### Increase Concurrency

```bash
# Set environment variable
export MAX_CONCURRENT_VERIFICATIONS=10

# Or in docker-compose.yml
environment:
  - MAX_CONCURRENT_VERIFICATIONS=10
```

### Partition Kafka Topics

```bash
# Increase partitions for parallel consumption
kafka-topics --alter --topic verify_chunks \
  --partitions 6 --bootstrap-server localhost:9092
```

## Backup and Recovery

### Backup Verification Data

```bash
# Backup MongoDB feature flags
mongodump --db pipeshub --collection feature_flags \
  --out /backup/mongodb

# Backup Qdrant collection
curl -X POST http://localhost:6333/collections/pipeshub_chunks/snapshots

# Backup ArangoDB
arangodump --server.endpoint http://localhost:8529 \
  --output-directory /backup/arango
```

### Restore from Backup

```bash
# Restore MongoDB
mongorestore --db pipeshub /backup/mongodb/pipeshub

# Restore Qdrant (manual process)
# See Qdrant documentation

# Restore ArangoDB
arangorestore --server.endpoint http://localhost:8529 \
  --input-directory /backup/arango
```

## Deployment Checklist

### Pre-Deployment

- [ ] Review feature flags (start with `verification_enabled=false`)
- [ ] Verify Hupyy API connectivity
- [ ] Check Kafka topic creation
- [ ] Verify Redis availability
- [ ] Confirm database schemas updated

### Deployment

- [ ] Deploy orchestrator
- [ ] Deploy Qdrant updater
- [ ] Deploy ArangoDB updater
- [ ] Deploy PageRank calculator
- [ ] Verify all services healthy

### Post-Deployment

- [ ] Enable verification for 10% of users
- [ ] Monitor Grafana dashboard
- [ ] Check circuit breaker state
- [ ] Verify cache hit rate
- [ ] Gradually increase to 100%

## Emergency Procedures

### Disable Verification Immediately

```python
# Use feature flag
await flag_service.set_flag("verification_enabled", False)
```

### Stop All Verification Services

```bash
# Docker Compose
docker-compose stop verification-orchestrator \
  qdrant-updater arango-updater pagerank-calculator

# Kubernetes
kubectl delete deployment verification-orchestrator
kubectl delete deployment qdrant-updater
kubectl delete deployment arango-updater
kubectl delete deployment pagerank-calculator
```

### Drain Kafka Topics

```bash
# Delete all messages from topic
kafka-topics --delete --topic verify_chunks \
  --bootstrap-server localhost:9092

# Recreate topic
kafka-topics --create --topic verify_chunks \
  --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:9092
```

## Contact Information

- **On-Call Engineer**: [Your PagerDuty rotation]
- **Slack Channel**: #verification-ops
- **Documentation**: /docs/hupyy-integration/
- **Runbook Updates**: Submit PR to this file

## References

- [Hupyy API Documentation](https://verticalslice-smt-service-gvav8.ondigitalocean.app/docs)
- [Architecture Document](../hupyy-integration/architecture.md)
- [Research Report](../.prompts/001-hupyy-integration-research/hupyy-integration-research.md)
- [Implementation Plan](../.prompts/002-hupyy-integration-plan/SUMMARY-UPDATED.md)
