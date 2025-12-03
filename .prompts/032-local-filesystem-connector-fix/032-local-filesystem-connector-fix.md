# Investigation & Fix: Local Filesystem Connector Zero Records on Fresh Deployment

## Metadata
```xml
<prompt_metadata>
  <id>032</id>
  <topic>local-filesystem-connector-fix</topic>
  <purpose>do</purpose>
  <complexity>high</complexity>
  <references>
    <research>007-connector-missing-content-research/connector-missing-content-research.md</research>
  </references>
  <created>2025-12-03</created>
  <scope>comprehensive_solution</scope>
  <depth>deep_analysis</depth>
</prompt_metadata>
```

## Objective

Investigate and permanently fix the critical issue where the Local Filesystem connector shows **0 records indexed** on fresh Docker deployments, despite being configured and showing "Active and syncing data" status.

**Success Criteria:**
1. Local Filesystem connector creates and indexes records on fresh deployment
2. Root cause identified and documented
3. Robust fix implemented with safeguards
4. Solution works "out of the box" with no manual intervention
5. Verification tests pass showing files are indexed and searchable

## Context

### Current Problem
User screenshot shows:
- **Connector Status**: "Active and syncing data"
- **Records Created**: 0 records
- **Indexing Progress**: 0% (0/0 records indexed)
- **All metrics at zero**: 0 Indexed, 0 Failed, 0 In Progress, 0 Not Started

### Environment
- **Deployment**: Fresh Docker deployment using docker-compose.dev.yml
- **Volume Mount**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig:/data/local-files:ro`
- **Services**: All 8 Docker services running and healthy
- **Databases**: MongoDB, ArangoDB, Qdrant, Redis (freshly cleared)

### Previous Research Context
From `.prompts/007-connector-missing-content-research/`:
- Research focused on records with **missing content** (700+ records created but no content)
- This issue is different: **zero records created at all**
- Previous findings: Connector doesn't store content in records, only metadata
- Indexing Service handles content extraction and embedding generation

### Critical Question
Why is the connector not discovering/creating ANY records on fresh deployment?

## Investigation Strategy

### Phase 1: Initial Diagnostic (Quick Wins)
**Goal**: Identify obvious blockers preventing record creation

<investigation_tasks>
1. **Check Docker logs for connector service**
   - Command: `docker logs docker-compose-hupyy-kb-1 2>&1 | grep -i "local.*filesystem\|connector" | tail -100`
   - Look for: Errors, warnings, initialization failures, file permission issues

2. **Verify volume mount accessibility**
   - Check from inside container: `docker exec docker-compose-hupyy-kb-1 ls -la /data/local-files | head -20`
   - Verify files exist and are readable
   - Check file count: `docker exec docker-compose-hupyy-kb-1 find /data/local-files -type f | wc -l`

3. **Check connector configuration in database**
   - MongoDB: `db.getSiblingDB('es').connectorsConfig.find({type: "local_filesystem"}).pretty()`
   - Verify: path configured, enabled=true, no errors in config

4. **Verify Kafka topics and messages**
   - Check if connector is publishing to Kafka: `docker exec docker-compose-kafka-1-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic record-events --from-beginning --max-messages 10`
   - Look for: Any "newRecord" events from LOCAL_FILESYSTEM source

5. **Check ArangoDB for any records**
   - Query: `db._query("FOR doc IN records FILTER doc.source == 'LOCAL_FILESYSTEM' RETURN doc")`
   - Expected: 0 records if nothing created

6. **Service initialization order**
   - Check if connector service starts before databases are ready
   - Review docker-compose depends_on and health checks
</investigation_tasks>

### Phase 2: Code Path Tracing (Deep Dive)
**Goal**: Understand exact failure point in record creation pipeline

<code_analysis>
1. **Entry Point Analysis**
   - File: `backend/python/app/connectors/sources/local_filesystem/connector.py`
   - Method: `LocalFilesystemConnector.run_sync()` (line ~488)
   - Verify:
     - Is `run_sync()` being called?
     - Does `_scan_directory()` find files?
     - Does `_create_file_record()` get called?

2. **Directory Scanning Logic**
   - Method: `_scan_directory()` (line ~424-438)
   - Add debug logging to confirm:
     - Directory path being scanned
     - Number of files found
     - File extensions being filtered
     - Actual file paths discovered

3. **Record Creation Flow**
   - Method: `_create_file_record()` (line ~378-422)
   - Verify for each file:
     - File ID generation
     - Metadata extraction (size, mime type, extension)
     - Record object construction
     - Permissions creation

4. **Batch Processing**
   - Method: `run_sync()` batch loop
   - Check:
     - Are records being batched?
     - Is `on_new_records()` being called with non-empty list?
     - Are transactions committing successfully?

5. **Database Persistence**
   - File: `backend/python/app/connectors/core/base/data_processor/data_source_entities_processor.py`
   - Method: `on_new_records()` (line ~316)
   - Verify:
     - Transaction creation
     - Record insertion to ArangoDB
     - Kafka message publication

6. **Error Handling**
   - Check all try/except blocks in the pipeline
   - Look for silent failures (errors caught but not logged)
   - Review exception handling in:
     - File I/O operations
     - Database transactions
     - Kafka publishing
</code_analysis>

### Phase 3: System State Analysis
**Goal**: Verify all dependencies and prerequisites

<system_checks>
1. **Database Connectivity**
   - ArangoDB: Can connector service connect and write?
   - MongoDB: Can connector config be read?
   - Redis: Is cache accessible?

2. **Kafka Health**
   - Are topics created? (`record-events`, `sync-events`)
   - Can producer publish messages?
   - Are partitions assigned?

3. **File System Permissions**
   - Container user/group permissions
   - Volume mount read permissions
   - Symlink resolution

4. **Connector Lifecycle**
   - Is connector registered in system?
   - Is it in "active" state in database?
   - When was last sync attempted?
   - Are there any stale locks or sync flags?

5. **Service Dependencies**
   - Indexing service status
   - Kafka consumer group status
   - Database initialization status
</system_checks>

### Phase 4: Root Cause Hypothesis Testing
**Goal**: Test specific failure scenarios

<hypothesis_tests>
**Hypothesis 1: Connector never starts sync**
- Test: Check if `run_sync()` is ever called
- Evidence: Add logging at entry point, check logs
- Fix if true: Investigate connector scheduler/trigger mechanism

**Hypothesis 2: Directory scan finds zero files**
- Test: Manually run directory scan with same filters
- Evidence: Compare file count in container vs host
- Fix if true: Adjust file filters, check extensions whitelist

**Hypothesis 3: Permission denied reading files**
- Test: Try reading a file from inside container as connector user
- Evidence: Check file ownership, mount permissions
- Fix if true: Adjust volume mount permissions or run as different user

**Hypothesis 4: Database transaction fails silently**
- Test: Enable transaction logging, check for rollbacks
- Evidence: Look for transaction errors in ArangoDB logs
- Fix if true: Add explicit error handling, retry logic

**Hypothesis 5: Connector config missing or invalid**
- Test: Validate connector config schema
- Evidence: Check MongoDB connectorsConfig collection
- Fix if true: Create default config on first run

**Hypothesis 6: Kafka producer initialization fails**
- Test: Check Kafka connection status, topic availability
- Evidence: Kafka logs showing connection attempts
- Fix if true: Add connection retry, ensure topics exist before sync

**Hypothesis 7: Service initialization race condition**
- Test: Check if connector starts before databases are ready
- Evidence: Review startup logs, depends_on in docker-compose
- Fix if true: Add proper health checks and startup delays
</hypothesis_tests>

## Implementation Requirements

### Fix Criteria
1. **Immediate Fix**: Get connector working on current deployment
2. **Robust Solution**: Handle edge cases (missing dirs, permissions, etc.)
3. **Initialization Safety**: Ensure services start in correct order
4. **Error Visibility**: Log all failures clearly
5. **Self-Healing**: Auto-retry on transient failures
6. **Verification**: Add health check endpoint showing sync status

### Code Changes Expected
Based on investigation findings, implement:

1. **Enhanced Logging**
   - Add DEBUG level logging to all critical methods
   - Log file counts, paths, success/failure counts
   - Structured logging with context

2. **Startup Health Checks**
   - Verify volume mount before sync
   - Check database connectivity before writing
   - Ensure Kafka topics exist before publishing

3. **Error Handling Improvements**
   - Never silently catch exceptions
   - Log full stack traces
   - Return meaningful error messages to UI

4. **Configuration Validation**
   - Validate path exists and is readable
   - Check file extension filters are sensible
   - Warn if no files match filters

5. **Sync Status Reporting**
   - Expose metrics: files_scanned, records_created, errors_encountered
   - Update UI to show detailed sync progress
   - Add last_sync_time, last_error fields

6. **Database Migration** (if needed)
   - Add missing indexes
   - Create default connector config on first run
   - Handle schema changes gracefully

### Testing Plan
1. **Fresh Deployment Test**
   - Clear all databases
   - Restart Docker services
   - Verify connector creates records within 2 minutes

2. **File Discovery Test**
   - Known directory with N files
   - Verify N records created in database
   - Check all file types are processed

3. **Error Recovery Test**
   - Temporarily make volume unreadable
   - Verify error is logged and visible
   - Fix permissions, verify auto-recovery

4. **Kafka Integration Test**
   - Monitor Kafka messages during sync
   - Verify message format and content
   - Check indexing service receives messages

## Deliverables

<required_outputs>
1. **Root Cause Report** (root-cause.md)
   ```xml
   <root_cause_analysis>
     <problem_statement>Exact failure point</problem_statement>
     <evidence>Logs, queries, test results</evidence>
     <fix_description>What was changed and why</fix_description>
   </root_cause_analysis>
   ```

2. **Code Changes**
   - Modified files with inline comments
   - Commit message following project standards
   - Added tests where applicable

3. **Verification Evidence** (verification.md)
   - Screenshots showing records created
   - Log excerpts showing successful sync
   - Database queries confirming records exist
   - Kafka messages captured

4. **Deployment Guide** (deployment-fix.md)
   - Steps to apply fix on existing deployments
   - Migration commands if database changes needed
   - Rollback procedure if issues occur

5. **Prevention Measures** (prevention.md)
   - Monitoring recommendations
   - Health check improvements
   - Documentation updates needed
</required_outputs>

## Execution Instructions

### Step 1: Diagnostics (30 minutes)
Run all Phase 1 investigation tasks in parallel using Task tool.
Report findings in structured format.

### Step 2: Code Analysis (45 minutes)
Trace code paths identified as suspicious from Phase 1.
Add temporary debug logging if needed.

### Step 3: Root Cause Identification (15 minutes)
Based on evidence, determine exact failure point.
Document with evidence references.

### Step 4: Fix Implementation (60 minutes)
Write code changes following TDD:
1. Write failing test demonstrating bug
2. Implement fix
3. Verify test passes
4. Run full test suite

### Step 5: Verification (30 minutes)
1. Apply fix to running system
2. Trigger fresh sync
3. Verify records appear in UI
4. Check Kafka messages flow
5. Confirm search works on indexed content

### Step 6: Documentation (30 minutes)
Create all required deliverables.
Update TO-DOS.md with resolution details.

## Success Metrics

- [ ] Connector shows non-zero record count
- [ ] Files from `/data/local-files` are discoverable
- [ ] Records exist in ArangoDB
- [ ] Kafka messages published to record-events topic
- [ ] Indexing service processes records
- [ ] Search returns results from indexed files
- [ ] Fix works on completely fresh deployment
- [ ] No manual intervention required

## Notes

- **Priority**: Critical blocker for production use
- **Timeline**: Must be fixed before system is usable
- **Scope**: This fix must work for ALL fresh deployments
- **Testing**: Verify on clean database state, not existing data
- **Documentation**: Update deployment docs with any new requirements

## Previous Context Reference

See `.prompts/007-connector-missing-content-research/connector-missing-content-research.md` for:
- Understanding of connector architecture
- Database schema details
- Kafka message format
- Indexing service integration

That research dealt with missing **content** in existing records.
This investigation deals with missing **records** entirely.
