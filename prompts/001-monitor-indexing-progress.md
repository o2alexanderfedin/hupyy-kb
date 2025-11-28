# Monitor Local Filesystem Connector Indexing Progress

<objective>
Monitor the PipesHub AI indexing service to verify it successfully processes the Local Filesystem connector's 1,723 records through the Kafka queue backlog. The system needs to work through old failed messages (from before the schema fix) before reaching new valid messages.

This verification ensures the deployment is fully operational and the schema validation fix is working end-to-end.
</objective>

<context>
## Current State

**Deployment Complete**: Release 0.1.10-alpha deployed with schema validation fix
- Git flow release: merged, tagged, pushed
- Docker container: rebuilt and restarted
- ArangoDB: 1,723 LOCAL_FILESYSTEM records exist with correct schema (no blockContainers field)
- Schema fix applied: Removed blockContainers from record creation code

**Indexing Challenge**:
- Kafka queue contains ~19,000+ old messages from before the schema fix
- Old messages reference records that failed to insert (schema validation errors)
- Indexing service must process through all old messages before reaching new valid messages
- Current offset: ~19,234 (processing old failed records)

**Expected Behavior**:
- Indexing service processes old messages → "Record not found" errors (expected)
- Eventually reaches messages for the 1,723 valid records
- Begins indexing those records successfully
- Indexing progress should increase from 0% toward 100%

## System Details

- Working directory: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/deployment/docker-compose`
- Docker compose file: `docker-compose.dev.yml`
- Database: ArangoDB at arango:8529
- Kafka: Processing record-events topic, partition 0
- Frontend: http://localhost:3000 (logged in as test@example.com)
</context>

<requirements>

## Monitoring Strategy

1. **Check Kafka Offset Progress** (every 2-3 minutes):
   ```bash
   docker compose -f docker-compose.dev.yml logs pipeshub-ai --tail=20 --since=30s | grep "offset="
   ```
   - Look for increasing offset numbers
   - Note: ~500-1000 messages per minute is normal processing speed

2. **Monitor Indexing Service Logs** (every 2-3 minutes):
   ```bash
   docker compose -f docker-compose.dev.yml logs pipeshub-ai --tail=50 --since=30s | grep -E "indexing_service|Processing record|successfully indexed"
   ```
   - Expected initially: Many "Record not found" errors (old failed messages)
   - Watch for: Successful indexing messages when it reaches valid records

3. **Check Database Record Status** (every 5 minutes):
   ```bash
   docker compose -f docker-compose.dev.yml exec -T pipeshub-ai python3 -c "
   from arango import ArangoClient
   client = ArangoClient(hosts='http://arango:8529')
   db = client.db('es', username='root', password='czXG+1VB1mMGFcRoLJ2lzGA+E9fxGJqm')

   result = list(db.aql.execute('''
     FOR doc IN records
     FILTER doc.connectorName == \"LOCAL_FILESYSTEM\"
     COLLECT status = doc.indexingStatus WITH COUNT INTO count
     RETURN { status, count }
   '''))

   print('Indexing Status Breakdown:')
   for item in result:
       print(f'  {item[\"status\"]}: {item[\"count\"]}')
   "
   ```
   - Watch for: `COMPLETED` or `IN_PROGRESS` counts increasing
   - Watch for: `NOT_STARTED` count decreasing from 1,723

4. **Refresh UI Stats** (optional, every 5-10 minutes):
   - Navigate to: http://localhost:3000/account/individual/settings/connector/Local%20Filesystem
   - Click "Refresh Status" button
   - Check: Indexed count, In Progress count

## Success Indicators

Monitor for these positive signs:
- ✅ Kafka offset advancing (even if slowly)
- ✅ "Record not found" errors decreasing over time
- ✅ Successful indexing log messages appearing
- ✅ Database query showing status changes (NOT_STARTED → IN_PROGRESS or COMPLETED)
- ✅ UI showing increasing indexed count

## Failure Indicators

Stop monitoring if you see:
- ❌ Kafka offset stuck at same number for 10+ minutes
- ❌ Service crashed/restarting continuously
- ❌ New schema validation errors appearing
- ❌ Indexing service consuming 100% CPU continuously
</requirements>

<execution>

## Monitoring Timeline

**Phase 1: Initial Assessment (0-5 minutes)**
1. Check current Kafka offset
2. Verify indexing service is running and processing
3. Confirm 1,723 records exist in database
4. Note starting offset number

**Phase 2: Active Monitoring (5-30 minutes)**
1. Every 3 minutes: Check Kafka offset progress
2. Every 5 minutes: Run database status query
3. Every 5 minutes: Check logs for pattern changes
4. Document any significant changes or transitions

**Phase 3: Verification (when progress observed)**
1. Confirm indexing counts are increasing
2. Verify no new errors appearing
3. Check at least 10-20 records have been indexed
4. Validate progress is continuing

## Monitoring Commands Reference

```bash
# Quick status check (run frequently)
docker compose -f docker-compose.dev.yml logs pipeshub-ai --tail=10 --since=1m | grep "offset="

# Detailed indexing logs
docker compose -f docker-compose.dev.yml logs pipeshub-ai --tail=50 --since=2m | grep indexing_service

# Database status (comprehensive)
docker compose -f docker-compose.dev.yml exec -T pipeshub-ai python3 -c "
from arango import ArangoClient
client = ArangoClient(hosts='http://arango:8529')
db = client.db('es', username='root', password='czXG+1VB1mMGFcRoLJ2lzGA+E9fxGJqm')

# Count by status
statuses = list(db.aql.execute('''
  FOR doc IN records
  FILTER doc.connectorName == \"LOCAL_FILESYSTEM\"
  COLLECT status = doc.indexingStatus WITH COUNT INTO count
  RETURN { status, count }
'''))

# Sample indexed record
indexed = list(db.aql.execute('''
  FOR doc IN records
  FILTER doc.connectorName == \"LOCAL_FILESYSTEM\"
  FILTER doc.indexingStatus == \"COMPLETED\"
  LIMIT 1
  RETURN { recordName: doc.recordName, status: doc.indexingStatus }
'''))

print('Status breakdown:', statuses)
print('Sample indexed:', indexed if indexed else 'None yet')
"

# Container health check
docker compose -f docker-compose.dev.yml ps pipeshub-ai
```

## Decision Points

**After 10 minutes of monitoring:**
- If offset advancing and no critical errors → Continue monitoring
- If offset stuck → Investigate Kafka consumer group lag
- If service errors → Check container logs for root cause

**After 20-30 minutes of monitoring:**
- If ANY records showing progress (COMPLETED or IN_PROGRESS) → Success! Continue to completion
- If still 0% after 30 minutes → May need Kafka offset reset (advanced troubleshooting)

**Early Exit Conditions:**
- 10+ records successfully indexed → Indexing is working, can stop active monitoring
- Service crashed → Need to troubleshoot deployment
- No progress after 30 minutes → May need intervention
</execution>

<output>

Create monitoring log file: `./deployment/INDEXING-MONITORING.md`

Include:
- Start time and initial state
- Kafka offset progression over time
- Database status snapshots
- Key observations and transitions
- Any errors or issues encountered
- Final outcome and recommendations

## Example Log Format

```markdown
# Indexing Monitoring Log - 2025-11-28

## Initial State (18:50)
- Kafka offset: 19,234
- Records in database: 1,723
- Indexed: 0
- Status: NOT_STARTED: 1,723

## Progress Checks

### 18:53 (3 min)
- Offset: 19,456 (+222)
- Indexed: 0
- Notes: Processing old failed messages

### 18:58 (8 min)
- Offset: 19,789 (+333)
- Indexed: 0
- Notes: Still working through backlog

[Continue snapshots every 5 minutes]

## Outcome
[Success/Failure]
[Recommendations for next steps]
```
</output>

<constraints>

1. **Patience Required**: This may take 30-60 minutes to complete
2. **Resource Monitoring**: Watch for excessive CPU/memory usage
3. **No Intervention**: Let the system process naturally unless critical issues arise
4. **Background Build Jobs**: Multiple background build processes (43696f, 27c67b, etc.) can be ignored
5. **Expected Errors**: "Record not found" errors are normal during backlog processing

## Do NOT Do These Things

- ❌ Don't restart services unless they crash
- ❌ Don't manually delete Kafka messages
- ❌ Don't modify database records during indexing
- ❌ Don't run multiple sync operations simultaneously
- ❌ Don't stop monitoring before seeing progress indicators
</constraints>

<success_criteria>

This monitoring task is complete when ONE of the following occurs:

✅ **Success Path** (ideal outcome):
- At least 10-20 records show indexingStatus: COMPLETED or IN_PROGRESS
- Kafka offset continues advancing steadily
- No critical errors in logs
- UI reflects increasing indexed count

⚠️ **Acceptable Path** (progress observed):
- Even 1-5 records successfully indexed proves the system works
- May take longer but indexing is progressing
- Continue monitoring or document state for async completion

❌ **Failure Path** (intervention needed):
- Service crashed or stuck after 30+ minutes
- No records indexed and offset not advancing
- New schema validation errors appearing
- System resource exhaustion (OOM, 100% CPU sustained)

## Final Verification

Before completing, confirm:
- [ ] Monitoring log created with detailed observations
- [ ] Clear outcome documented (success/in-progress/failed)
- [ ] Recommendations provided for next steps
- [ ] If successful: Estimated time to full completion noted
- [ ] If failed: Root cause identified and troubleshooting steps suggested
</success_criteria>

<meta>
This is a monitoring and verification task, not a coding task. The goal is to observe and document the system's behavior, not to modify it. Be patient, thorough, and detail-oriented in your observations.
</meta>
