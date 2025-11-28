# Indexing Monitoring Log - 2025-11-28

## Initial State (18:53 PST)
- Kafka offset: 19,234 (from earlier logs)
- Records in database: 1,723
- Indexed: 0
- Status: NOT_STARTED: 1,723
- Action taken: Clicked "Sync" button in UI to trigger resync

## Progress Checks

### 18:54 (1 min after sync)
- Offset: 19,861 (+627 messages processed)
- Indexed: 0
- Status: NOT_STARTED: 1,723
- Notes: Processing old failed messages at ~10 messages/min
- Pattern: All messages showing "Record not found" errors (expected - these are old messages from before schema fix)
- Issue identified: Kafka offsets NOT being committed due to "processing failed" warnings

### 18:55 (2 min after sync)
- Offset: 19,925 (+64 from previous check)
- Indexed: 0
- Status: NOT_STARTED: 1,723
- Processing rate: ~1 message per second (~60/min)
- Still working through backlog of failed messages

## Current State

**System Behavior:**
- Indexing service running and processing messages
- All messages are "Record not found" errors (old messages for records that failed to insert)
- Processing speed: ~1 message/second
- Offset advancing but NOT being committed to Kafka

**Critical Issue:**
The consumer is marking each message as "failed" and not committing offsets:
```
WARNING - [consumer.py:301] - Processing failed for record-events-0-19878, offset will not be committed.
```

This means:
- If the service restarts, it will re-process all these messages again
- The offset position is lost
- System may be stuck in infinite loop

**Root Cause:**
The indexing service considers "Record not found" as a failure, but for these old messages, this is the EXPECTED outcome (they reference records that never made it into the database due to schema errors).

## Recommendations

### Option 1: Skip Old Messages (Fastest)
Reset Kafka consumer to only process new messages:
1. Stop indexing service
2. Reset consumer group offset to latest
3. Restart service
4. Click "Sync" again to republish events for valid records

### Option 2: Fix Consumer Logic (Proper Fix)
Modify consumer to commit offsets even when record not found:
- "Record not found" should not be treated as processing failure
- Commit offset and move on
- Only fail on actual errors (network, database connection, etc.)

### Option 3: Wait It Out (Not Recommended)
If there are ~20,000 total messages and we're at 19,925:
- ~75 messages remaining in backlog
- At 1 msg/sec = ~75 seconds to complete
- Then sync messages (1,723) would start processing
- Total time: 2-3 minutes + indexing time

However, without offset commits, a restart would reset progress.

## Root Cause Analysis

**File**: `backend/python/app/services/messaging/kafka/handlers/record.py`
**Lines**: 118-120

```python
if record is None:
    self.logger.error(f"❌ Record {record_id} not found in database")
    return False  # <-- THIS IS THE PROBLEM
```

When a record is not found, the handler returns `False`, which:
1. Marks the message as "failed"
2. Prevents Kafka offset from being committed
3. Causes the service to re-process the same message on restart

**For old failed messages, "record not found" is the EXPECTED outcome** (they reference records that never made it into the database due to schema errors before the fix).

## Proposed Fix

Change line 120 to return `True` instead of `False`:

```python
if record is None:
    self.logger.error(f"❌ Record {record_id} not found in database")
    return True  # Message processed successfully - record doesn't exist (expected for old messages)
```

This allows the consumer to:
- Acknowledge the message was processed (even though record doesn't exist)
- Commit the Kafka offset
- Move on to the next message
- Eventually reach the valid records

## Alternative: Skip to Latest Offset

Instead of fixing the code, we could reset the Kafka consumer to skip all old messages and only process new ones. This would:
- Be faster (immediate)
- But lose the ability to retry failed messages in the future
- Requires manual Kafka offset manipulation

## Fix Applied (19:01 PST)

**Action Taken**: Fixed the code (changed return False to return True on line 120)

**Changes Made**:
- File: `backend/python/app/services/messaging/kafka/handlers/record.py`
- Line 119: Changed from ERROR to WARNING log level
- Line 120: Changed `return False` to `return True` with explanatory comment
- Rebuilt Docker image (build ID: aa4d0d8)
- Deployed updated container

**Verification** (19:02 PST):
```
✅ WARNING logs: "⚠️ Record {id} not found in database - may be from failed insert (schema error)"
✅ Offset commits: "Committed offset for record-events-0-20699 in background task."
✅ Offset advancing: 20,680 → 20,736 in 10 seconds (~56 messages/10s = 5.6 msg/sec)
```

**Status**: ✅ **FIX SUCCESSFUL** - Offsets are now being committed and system is making progress

## Current Progress (19:02 PST)

- Offset: 20,736
- Processing speed: ~5-6 messages per second
- All messages still "record not found" (expected - still in backlog of old failed messages)
- Estimated time to reach valid records: Unknown (need to determine total queue length)

## Next Steps

Continue monitoring to verify system reaches valid records and begins indexing.
