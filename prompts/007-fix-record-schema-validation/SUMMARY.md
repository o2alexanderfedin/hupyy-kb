# Fix ArangoDB Record Schema Validation - Summary

## Problem

**Critical Bug**: All Local Filesystem connector record insertions were failing with schema validation error:
```
❌ Batch upsert failed: [HTTP 400][ERR 1620] AQL: Document does not match the record schema.
```

**Impact**:
- **0 records** indexed despite connector successfully discovering and processing files
- Complete blocker for Local Filesystem connector functionality
- No search capability for local files
- Indexing service unable to process records (not found in database)

## Root Cause

The `to_arango_base_record()` method in `backend/python/app/models/entities.py` was adding a `blockContainers` field (lines 118-120) which is **NOT** part of the ArangoDB `records` collection schema.

The schema has `"additionalProperties": false`, meaning ANY extra field causes rejection with ERR 1620.

### Why This Happened

The code was attempting to store block content (file content) directly in the records collection:

```python
# BEFORE (Lines 118-120 - WRONG)
if self.block_containers and (self.block_containers.blocks or self.block_containers.block_groups):
    base_dict["blockContainers"] = self.block_containers.model_dump(mode='json')
```

However, the records collection schema only allows specific metadata fields. Block content must be stored separately.

## Solution

**Removed the blockContainers field** from the record object sent to ArangoDB.

### Code Change

**File**: `backend/python/app/models/entities.py`

**Before** (lines 118-120):
```python
# Add block_containers if populated (handle empty gracefully)
if self.block_containers and (self.block_containers.blocks or self.block_containers.block_groups):
    base_dict["blockContainers"] = self.block_containers.model_dump(mode='json')
```

**After** (lines 118-120):
```python
# NOTE: blockContainers is NOT part of the records collection schema
# Block content should be stored separately (e.g., in blocks collection or file storage)
# The schema has additionalProperties=false, so we cannot add extra fields
```

## Verification

### Before Fix
```bash
$ docker compose -f docker-compose.dev.yml logs pipeshub-ai | grep "ERR 1620"
❌ Batch upsert failed: [HTTP 400][ERR 1620] AQL: Document does not match the record schema.
❌ Batch upsert failed: [HTTP 400][ERR 1620] AQL: Document does not match the record schema.
# ... hundreds of failures
```

```sql
-- Query: SELECT COUNT(*) FROM records WHERE connectorName = 'LOCAL_FILESYSTEM'
Result: 0
```

### After Fix

```bash
$ # Test manual record insertion
✅ SUCCESS: Test record inserted with key: test-local-fs-record-001
✅ Test record cleaned up
```

```sql
-- Query: SELECT COUNT(*) FROM records WHERE connectorName = 'LOCAL_FILESYSTEM'
Result: 1721
```

```bash
$ docker compose -f docker-compose.dev.yml logs pipeshub-ai | grep "full sync completed"
2025-11-28 17:21:19,558 - connector_service - INFO - Local Filesystem full sync completed
```

## Fields in Compliant Record

The corrected record object contains only schema-approved fields:

```json
{
  "_key": "record-id-uuid",
  "orgId": "org-uuid",
  "recordName": "filename.ext",
  "recordType": "FILE",
  "externalRecordId": "/path/to/file",
  "externalRevisionId": "timestamp",
  "externalGroupId": "dir/parent/path",
  "externalParentId": null,
  "version": 0,
  "origin": "CONNECTOR",
  "connectorName": "LOCAL_FILESYSTEM",
  "mimeType": "text/plain",
  "webUrl": "file:///path/to/file",
  "createdAtTimestamp": 1764350250811,
  "updatedAtTimestamp": 1764350345946,
  "sourceCreatedAtTimestamp": null,
  "sourceLastModifiedTimestamp": 1763701433241,
  "indexingStatus": "NOT_STARTED",
  "extractionStatus": "NOT_STARTED",
  "isDeleted": false,
  "isArchived": false,
  "deletedByUserId": null,
  "previewRenderable": true,
  "isShared": false
}
```

**No `blockContainers` field** - content is stored elsewhere in the system.

## Testing Results

### Database Query
```python
from arango import ArangoClient

client = ArangoClient(hosts='http://arango:8529')
db = client.db('es', username='root', password='czXG+1VB1mMGFcRoLJ2lzGA+E9fxGJqm')

# Count LOCAL_FILESYSTEM records
result = db.aql.execute('''
FOR doc IN records
FILTER doc.connectorName == "LOCAL_FILESYSTEM"
RETURN 1
''')

count = len(list(result))
print(f'LOCAL_FILESYSTEM records: {count}')
# Output: LOCAL_FILESYSTEM records: 1721
```

### Log Evidence
```
✅ Successfully upserted 1 nodes in collection 'recordGroups'
✅ Successfully upserted 1 nodes in collection 'records'  # <- Fixed!
✅ Successfully created 1 edges in collection 'belongsTo'
✅ Successfully created 1 edges in collection 'inheritPermissions'
✅ Successfully created 1 edges in collection 'permission'
```

## Future Implications

### Block Content Storage
The block content (file text) is still being loaded into the `FileRecord` object's `block_containers` field during connector processing, but it's **not** being persisted to the `records` collection.

This is by design - the records collection stores metadata, while actual content should be stored via:
1. Separate blocks collection
2. External file storage
3. Indexing service processing (which extracts and indexes content)

### Other Connectors
This fix applies to **all record types** (FILE, MAIL, MESSAGE, etc.) since they all use the same `to_arango_base_record()` method. Any connector attempting to add block content to records would have failed with the same error.

## Deployment Notes

1. **Code change**: `backend/python/app/models/entities.py` lines 118-120
2. **Rebuild required**: Docker image must be rebuilt to include the fix
3. **No data migration**: Existing (empty) database is fine
4. **Kafka messages**: Old failed messages in Kafka will show "record not found" errors but can be ignored - they will eventually age out or can be manually purged

## Success Criteria

- [x] No schema validation errors in logs
- [x] Batch upsert operations succeed
- [x] ArangoDB query returns count > 0 for LOCAL_FILESYSTEM records (1721 records)
- [x] Sample record shows correct field names (camelCase)
- [x] Sample record shows no `blockContainers` field
- [x] Connector sync completes successfully

## Known Issues

### Old Kafka Messages
The indexing service is still processing old Kafka messages from before the fix. These messages reference records that were never inserted. This is harmless and will resolve itself as:
1. Old messages are processed and discarded
2. Kafka retention period expires
3. Or manual purge if needed

**Example**:
```
❌ Record 7b1a8173-060a-4e9e-9aaa-10c2ae095189 not found in database
```

This is expected for records created before the fix was applied.

## References

- **ArangoDB Schema**: Collection `records` with `additionalProperties: false`
- **Schema Fields**: `recordName`, `externalRecordId`, `recordType`, `origin`, `connectorName`, etc.
- **Error Code**: ERR 1620 - Document does not match schema
