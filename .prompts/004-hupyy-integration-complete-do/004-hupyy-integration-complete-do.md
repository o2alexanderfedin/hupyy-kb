# Meta-Prompt: Complete Hupyy-PipesHub Integration (Phases 2-4)

## Context

This is a "Do" prompt to complete the Hupyy-PipesHub SMT verification integration. Phases 0-1 are already complete (50% of project).

### Completed Work
- **Phase 0**: Infrastructure (Kafka topics, Redis cache, feature flags, Prometheus metrics, Grafana dashboards)
- **Phase 1**: Backend verification service (models, circuit breaker, Hupyy client) + Frontend UI (checkbox, progress bar, metadata viewer)
- **Commits**: edf2cd17 (Phase 0-1 backend), 0fbf6cad (Phase 1 frontend)

### Reference Documents
- Research: `.prompts/001-hupyy-integration-research/hupyy-integration-research.md`
- Plan: `.prompts/002-hupyy-integration-plan/SUMMARY-UPDATED.md`
- Phase 0-1: `.prompts/003-hupyy-integration-implement/SUMMARY.md`

### Critical Constraints (User-Specified)
1. **Hupyy is SLOW**: 1-2 minutes per call (not 20-30s)
2. **Async/Parallel**: Mandatory for performance
3. **Top-K Sampling**: 5-10 results only (not 50)
4. **UI Requirements**: Checkbox, progress indicators, metadata display
5. **enrich=false**: Always in Hupyy requests
6. **Simple Caching**: SHA256 content hash, 24h TTL
7. **Not Production**: Skip shadow mode delays, no canary rollout

## Task: Complete Phases 2-4 Implementation

Implement the remaining 50% of the Hupyy-PipesHub integration following TDD, SOLID principles, and strong typing.

### Phase 2: Orchestrator + Feedback (Weeks 5-7, 50% effort)

**Files to Create:**

1. **`backend/python/app/verification/orchestrator.py`**
   - Kafka consumer for `verify_chunks` topic
   - Invokes HupyyClient for verification
   - Publishes to `verification_complete` or `verification_failed`
   - Handles retries with exponential backoff
   - Respects feature flags (verification_enabled, verification_top_k)
   - Type: Async service with graceful shutdown

2. **`backend/python/app/feedback/qdrant_updater.py`**
   - Kafka consumer for `verification_complete` topic
   - Updates Qdrant payloads with verification metadata
   - Schema: `{verified: bool, verdict: str, confidence: float, formalization_similarity: float}`
   - Batch updates (10 at a time, <100ms latency)
   - Error handling with dead letter queue

3. **`backend/python/app/feedback/arangodb_updater.py`**
   - Kafka consumer for `verification_complete` topic
   - Updates ArangoDB document metrics
   - Increments `verification_count`, updates `avg_confidence`
   - Updates edge weights for citation network
   - Transaction-safe updates

4. **`backend/python/app/verification/cache_manager.py`**
   - Cache invalidation on source document changes
   - LRU eviction when cache exceeds size limit
   - Cache warming for frequently accessed documents
   - Metrics: hit rate, eviction count, size

5. **`backend/nodejs/apps/src/services/verification.service.ts`**
   - Triggers verification from search pipeline
   - Top-K sampling (5-10 results based on feature flag)
   - Publishes to Kafka `verify_chunks` topic
   - WebSocket notifications for progress updates
   - Aggregates chunk-level results

**Tests to Create:**
- `backend/python/app/tests/verification/test_orchestrator.py`
- `backend/python/app/tests/feedback/test_qdrant_updater.py`
- `backend/python/app/tests/feedback/test_arangodb_updater.py`
- `backend/python/app/tests/verification/test_cache_manager.py`
- `backend/nodejs/apps/src/tests/services/verification.service.test.ts`

**Integration Points:**
- Wire `verification.service.ts` into existing search API endpoint
- Connect React `useVerification` hook to WebSocket for real-time updates
- Add VerificationMetadata component to search result items

### Phase 3: Enhanced Ranking + PageRank (Weeks 8-10, 30% effort)

**Files to Create:**

1. **`backend/python/app/ranking/enhanced_ranker.py`**
   - Implements ranking formula: `0.45*semantic + 0.30*pagerank + 0.15*verification + 0.10*historical`
   - Verification score calculation:
     ```python
     if verdict == SAT:
         score = confidence * formalization_similarity * failure_mode_multiplier
     elif verdict == UNSAT:
         score = 0.5 * confidence  # Penalty for contradiction
     else:  # UNKNOWN/ERROR
         score = 0.0  # Neutral (fallback to other signals)
     ```
   - Cold start strategy: Gradual weight transition (0% → 15% over 1 week)
   - Feature flag integration for weight tuning

2. **`backend/python/app/graph/pagerank_calculator.py`**
   - Calculates PageRank on ArangoDB citation network
   - Algorithm: Power iteration (max 100 iterations, ε=1e-6)
   - Damping factor: 0.85
   - Runs daily via cron job
   - Stores results in `pagerank` edge attribute

3. **`backend/python/app/graph/failure_mode_classifier.py`**
   - Maps failure modes to confidence multipliers:
     ```python
     FAILURE_MODE_MULTIPLIERS = {
         FailureMode.TIMEOUT: 0.7,           # Partial confidence
         FailureMode.RESOURCE_LIMIT: 0.6,    # Lower confidence
         FailureMode.PARSE_ERROR: 0.0,       # No confidence
         FailureMode.SOLVER_ERROR: 0.0,      # No confidence
         FailureMode.NETWORK_ERROR: 1.0,     # Retry, not solver issue
         FailureMode.UNKNOWN: 0.5,           # Conservative
     }
     ```

**Tests to Create:**
- `backend/python/app/tests/ranking/test_enhanced_ranker.py`
- `backend/python/app/tests/graph/test_pagerank_calculator.py`
- `backend/python/app/tests/graph/test_failure_mode_classifier.py`

**Integration Points:**
- Replace existing ranker in search pipeline
- Schedule PageRank calculation job
- Update search API to return verification scores

### Phase 4: Polish + Documentation (Week 11, 20% effort)

**Tasks:**

1. **Code Review**
   - Review all Phase 2-3 files with separate subtask
   - Check SOLID compliance
   - Verify error handling completeness
   - Ensure type safety (no `any`, full Pydantic validation)

2. **Linting**
   ```bash
   # Python
   python3 -m black backend/python/app/verification backend/python/app/feedback backend/python/app/ranking backend/python/app/graph
   python3 -m flake8 backend/python/app/verification backend/python/app/feedback backend/python/app/ranking backend/python/app/graph
   python3 -m mypy backend/python/app/verification backend/python/app/feedback backend/python/app/ranking backend/python/app/graph

   # TypeScript
   cd backend/nodejs
   npm run lint
   npm run type-check

   cd ../../frontend
   npm run lint
   npm run type-check
   ```

3. **API Documentation**
   - Create OpenAPI/Swagger spec for verification endpoints
   - Document WebSocket protocol for progress updates
   - Add JSDoc/docstrings to all public functions

4. **Architecture Diagrams**
   - Create Mermaid sequence diagram for full verification flow
   - Create component diagram showing all services
   - Update existing architecture doc with Phase 2-3 details

5. **Runbooks**
   - Create `docs/runbooks/hupyy-verification-ops.md`:
     - How to enable/disable verification
     - How to tune ranking weights
     - How to monitor circuit breaker
     - How to invalidate cache
     - How to troubleshoot failures
     - How to scale Kafka consumers

6. **Test Coverage**
   ```bash
   # Python
   cd backend/python
   pytest --cov=app.verification --cov=app.feedback --cov=app.ranking --cov=app.graph --cov-report=html

   # TypeScript
   cd backend/nodejs
   npm run test:coverage

   cd ../../frontend
   npm run test:coverage
   ```
   - Target: 80%+ coverage for all new code

7. **README Updates**
   - Update `backend/python/README.md` with verification service setup
   - Update `backend/nodejs/README.md` with verification service integration
   - Update `frontend/README.md` with UI component usage
   - Update root `README.md` with Hupyy integration overview

**Files to Create:**
- `docs/api/verification-openapi.yaml`
- `docs/architecture/verification-sequence-diagram.md`
- `docs/runbooks/hupyy-verification-ops.md`
- Updated README files

## Execution Instructions

### Pre-Implementation
1. Read all reference documents (research, plan, Phase 0-1 summary)
2. Read completed Phase 0-1 code to understand patterns
3. Create comprehensive task list with TodoWrite

### Implementation Strategy
1. **TDD**: Write failing tests first, then minimal code to pass
2. **Parallel Execution**: Use multiple Task tools in same message for independent work
3. **Strong Typing**: Pydantic models, TypeScript interfaces, no `any`
4. **Error Handling**: Circuit breaker, retries, dead letter queues
5. **Observability**: Prometheus metrics, structured logging, Grafana dashboards

### Phase Execution Order
1. Phase 2: Backend orchestrator → updaters → cache → Node.js service → integration
2. Phase 3: Ranker → PageRank → failure modes → integration
3. Phase 4: Review → lint → docs → coverage

### Git Workflow
After each phase:
```bash
git add <phase-files>
git commit -m "feat: implement Phase X - <description>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push fork main
```

### Verification Checklist
- [ ] All tests pass (`pytest`, `npm test`)
- [ ] All linters pass (black, flake8, mypy, eslint, prettier)
- [ ] Type coverage 100% (no `any`, full Pydantic validation)
- [ ] Test coverage ≥80%
- [ ] Circuit breaker tested with failure injection
- [ ] Kafka consumers handle all edge cases (rebalance, errors, shutdown)
- [ ] UI components render correctly with all verification states
- [ ] WebSocket progress updates work end-to-end
- [ ] Feature flags control behavior correctly
- [ ] Cache invalidation works on document changes
- [ ] Ranking formula produces expected scores
- [ ] PageRank converges within 100 iterations
- [ ] Documentation complete (API, runbooks, READMEs)

## Success Criteria

1. **Functional**:
   - User can enable verification via checkbox in UI
   - Progress bar shows real-time verification status
   - Metadata viewer displays SAT/UNSAT/UNKNOWN verdicts
   - Search results re-rank based on verification scores
   - Cache reduces redundant Hupyy calls

2. **Performance**:
   - Verification handles 1-2 minute Hupyy latency via async
   - Top-K sampling limits load (5-10 results)
   - Kafka throughput: 100+ chunks/sec
   - Qdrant updates: <100ms latency
   - Cache hit rate: >60% after warm-up

3. **Quality**:
   - Test coverage: ≥80%
   - Type coverage: 100%
   - All linters pass
   - No `any` types
   - Full error handling

4. **Observability**:
   - Grafana dashboard shows all metrics
   - Circuit breaker state visible
   - Cache hit rate tracked
   - Verification success rate monitored

## Deliverables

### Code
- 15+ production files (orchestrator, updaters, ranker, PageRank, etc.)
- 15+ test files
- Updated configuration files

### Documentation
- OpenAPI spec for verification API
- Sequence diagram for verification flow
- Operations runbook
- Updated READMEs

### Git
- 3 commits (Phase 2, Phase 3, Phase 4)
- All pushed to fork

### Metrics
- Test coverage report (≥80%)
- Linting report (all pass)
- Type coverage report (100%)

## Notes

- **Existing Files**: Do not modify Phase 0-1 files unless bug found
- **Database Schema**: Qdrant/ArangoDB schemas already defined in research doc
- **Feature Flags**: MongoDB collection already created in Phase 0
- **Kafka Topics**: Already created in Phase 0 (verify_chunks, verification_complete, verification_failed)
- **Frontend Integration**: Wire existing components into search UI
- **Monitoring**: Grafana dashboard already created in Phase 0

## Timeline Estimate

- Phase 2: 3 weeks (orchestrator + feedback + integration)
- Phase 3: 2.5 weeks (ranking + PageRank)
- Phase 4: 1 week (polish + docs)
- **Total**: 6.5 weeks (remaining 50% of 11-week project)
