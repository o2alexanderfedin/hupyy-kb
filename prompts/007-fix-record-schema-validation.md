# Fix ArangoDB Record Schema Validation - Local Filesystem Connector

<objective>
Fix the critical bug preventing Local Filesystem connector from persisting records to ArangoDB. Every record insert is failing with schema validation error ERR 1620, resulting in 0 indexed files despite the connector discovering and processing files.

This is a BLOCKER for the entire indexing pipeline - no records = no search = no functionality.
</objective>

<context>
## Current State

**Problem**: Local Filesystem connector discovers files and attempts to create records, but ALL inserts fail:
```
❌ Batch upsert failed: [HTTP 400][ERR 1620] AQL: Document does not match the record schema.
```

**Evidence from logs**:
- Connector discovers files: ✅ Working
- Connector creates RecordGroups (directories): ✅ Working
- Connector attempts to insert records: ❌ FAILING (schema validation)
- Result: 0 records in ArangoDB despite processing hundreds of files

**Root Cause**: The record objects being created by the connector don't match ArangoDB's strict schema. The schema has `"additionalProperties": false` which means any extra fields or missing required fields cause rejection.

## ArangoDB Schema Requirements

The `records` collection has a strict JSON schema with:

**Required fields**:
- `recordName` (string, minLength: 1)
- `externalRecordId` (string, minLength: 1)
- `recordType` (enum: FILE, DRIVE, WEBPAGE, MESSAGE, MAIL, TICKET, etc.)
- `origin` (enum: CONNECTOR, UPLOAD)
- `createdAtTimestamp` (number)

**Optional but schema-validated fields**:
- `orgId` (string)
- `externalGroupId` (string | null)
- `externalParentId` (string | null)
- `externalRevisionId` (string | null, default: null)
- `externalRootGroupId` (string | null)
- `version` (number, default: 0)
- `connectorName` (enum including LOCAL_FILESYSTEM)
- `mimeType` (string | null, default: null)
- `webUrl` (string | null)
- `updatedAtTimestamp` (number)
- `lastSyncTimestamp` (number | null)
- `sourceCreatedAtTimestamp` (number | null)
- `sourceLastModifiedTimestamp` (number | null)
- `isDeleted` (boolean, default: false)
- `isArchived` (boolean, default: false)
- `deletedByUserId` (string | null)
- `indexingStatus` (enum: NOT_STARTED, IN_PROGRESS, PAUSED, FAILED, COMPLETED, etc.)
- `extractionStatus` (enum: NOT_STARTED, IN_PROGRESS, etc.)
- `isLatestVersion` (boolean, default: true)
- `isDirty` (boolean, default: false)
- `reason` (string | null)
- `lastIndexTimestamp` (number | null)
- `lastExtractionTimestamp` (number | null)
- `summaryDocumentId` (string | null)
- `virtualRecordId` (string | null, default: null)
- `previewRenderable` (boolean | null, default: true)
- `isShared` (boolean | null, default: false)

**CRITICAL**: `"additionalProperties": false` - NO extra fields allowed!

## Key Files

**Connector code**:
- `backend/python/app/connectors/sources/local_filesystem/connector.py` - Main connector logic
- `backend/python/app/connectors/services/base_arango_service.py` - Database operations (line 4029: batch upsert)

**Locations to investigate**:
- Where record objects are created before upsert
- Field name mapping (Python snake_case vs schema camelCase)
- Type conversions (especially timestamps)
</context>

<requirements>

## Phase 1: Diagnose Schema Mismatch

1. **Find record creation code** in Local Filesystem connector:
   - Search for where record objects are built
   - Identify all fields being set on record objects
   - Check field names (camelCase vs snake_case)

2. **Compare with schema**:
   - List all fields the connector is sending
   - Identify fields NOT in schema (extra fields = rejection)
   - Identify required fields that might be missing
   - Check type mismatches (string vs number, etc.)

3. **Check type conversions**:
   - Timestamps must be numbers (not strings, not datetime objects)
   - Enums must match exact case and values
   - Booleans must be true/false (not 1/0)

## Phase 2: Fix Record Object Construction

1. **Remove or rename invalid fields**:
   - Any field not in schema must be removed
   - Common issues: `record_name` → `recordName`, `external_record_id` → `externalRecordId`

2. **Ensure all required fields are present**:
   - `recordName`: File name
   - `externalRecordId`: Full file path
   - `recordType`: "FILE"
   - `origin`: "CONNECTOR"
   - `createdAtTimestamp`: Unix timestamp (seconds or milliseconds - check existing data)

3. **Fix field types**:
   - All timestamps must be numbers
   - `connectorName` must be exactly "LOCAL_FILESYSTEM" (from enum)
   - `indexingStatus` must be from enum (default: "NOT_STARTED")
   - `extractionStatus` must be from enum (default: "NOT_STARTED")

4. **Set sensible defaults**:
   ```python
   {
       "recordName": file_name,
       "externalRecordId": full_path,
       "recordType": "FILE",
       "origin": "CONNECTOR",
       "connectorName": "LOCAL_FILESYSTEM",
       "createdAtTimestamp": int(time.time() * 1000),  # milliseconds
       "updatedAtTimestamp": int(time.time() * 1000),
       "indexingStatus": "NOT_STARTED",
       "extractionStatus": "NOT_STARTED",
       "isDeleted": False,
       "isArchived": False,
       "isLatestVersion": True,
       "isDirty": False,
       "version": 0,
       "mimeType": mime_type or None,
       "orgId": org_id,
       "externalGroupId": parent_directory_id or None,
       # Only include fields that are in the schema
   }
   ```

## Phase 3: Test and Verify

1. **Test record creation**:
   ```bash
   # Check logs for successful inserts
   docker compose -f docker-compose.dev.yml logs pipeshub-ai --tail=50 | grep "Batch upserting"

   # Should see success, not errors
   ```

2. **Verify records in database**:
   ```python
   # Query ArangoDB
   from arango import ArangoClient
   client = ArangoClient(hosts='http://arango:8529')
   db = client.db('es', username='root', password='czXG+1VB1mMGFcRoLJ2lzGA+E9fxGJqm')

   result = list(db.aql.execute('''
   RETURN LENGTH(
     FOR doc IN records
     FILTER doc.connector_name == "LOCAL_FILESYSTEM"
     RETURN 1
   )
   '''))
   print(f'Local Filesystem records: {result[0]}')
   # Should be > 0
   ```

3. **Check UI**:
   - Open http://localhost:3000
   - Navigate to Connectors section
   - Verify Local Filesystem connector shows > 0 records

</requirements>

<implementation>

## Investigation Strategy

1. **Start with the upsert call** (base_arango_service.py:4029):
   - Read the batch_upsert method
   - Trace backwards to find what data is passed in
   - Identify the record object structure

2. **Find record creation in connector**:
   - Search for "record" creation in local_filesystem/connector.py
   - Look for dictionary/object construction
   - Check data_source_entities_processor.py if needed

3. **Common issues to check**:
   - Snake_case field names instead of camelCase
   - Extra fields not in schema
   - Missing required fields
   - Wrong enum values (case-sensitive)
   - Timestamps as strings or datetime objects instead of numbers

## Fix Approach

**DO**:
- Use exact field names from schema (camelCase)
- Convert all timestamps to integers (milliseconds since epoch)
- Use exact enum values from schema
- Set defaults for all boolean fields
- Include only fields that exist in schema

**DON'T**:
- Add custom fields not in schema
- Use snake_case field names
- Pass None for required fields
- Use string timestamps
- Include undefined fields even if null

## Type Safety

Ensure strict type checking:
```python
from typing import TypedDict, Literal, Optional

class RecordDocument(TypedDict, total=False):
    recordName: str
    externalRecordId: str
    recordType: Literal["FILE", "DRIVE", "WEBPAGE", ...]
    origin: Literal["CONNECTOR", "UPLOAD"]
    connectorName: Literal["LOCAL_FILESYSTEM", ...]
    createdAtTimestamp: int
    updatedAtTimestamp: int
    indexingStatus: Literal["NOT_STARTED", "IN_PROGRESS", ...]
    extractionStatus: Literal["NOT_STARTED", "IN_PROGRESS", ...]
    # ... all other fields
```

This prevents accidental field name typos and type errors.
</implementation>

<constraints>

1. **Schema Compliance**: MUST match ArangoDB schema exactly - no exceptions
2. **No Schema Changes**: DO NOT modify the ArangoDB schema - fix the code
3. **Preserve Functionality**: RecordGroups (directories) are working - don't break them
4. **No Data Loss**: All existing RecordGroups must remain intact
5. **Type Safety**: Use proper Python type hints to prevent future errors
6. **Backwards Compatibility**: Changes should not affect other connectors (DRIVE, GMAIL, etc.)

</constraints>

<output>

## Modified Files

Update these files with schema-compliant record creation:

1. **Primary fix location** (most likely):
   - `backend/python/app/connectors/sources/local_filesystem/connector.py`
   - OR `backend/python/app/connectors/services/base_arango_service.py`
   - OR `backend/python/app/connectors/sources/local_filesystem/data_source_entities_processor.py`

2. **Add type definitions** (if beneficial):
   - `backend/python/app/connectors/types/record_types.py` (create if needed)

## Evidence Required

Provide before/after comparison showing:

1. **Before**: Log showing schema validation errors
2. **After**: Log showing successful batch upsert
3. **Database query** showing record count > 0
4. **UI screenshot** (optional) showing indexed files

## Summary Document

Create `./prompts/007-fix-record-schema-validation/SUMMARY.md` with:

- Root cause identified
- Fields that were causing rejection
- Changes made to fix schema compliance
- Test results (logs + database query)
- Verification that UI shows records

</output>

<verification>

## Pre-Deployment Checks

Before declaring complete, verify ALL of these:

- [ ] No schema validation errors in logs
- [ ] Batch upsert operations succeed (check logs)
- [ ] ArangoDB query returns count > 0 for LOCAL_FILESYSTEM records
- [ ] Sample record query shows correct field names (camelCase)
- [ ] Sample record query shows correct field types (timestamps are numbers)
- [ ] No "Record not found in database" errors in indexing service
- [ ] Kafka offset commits succeed (no "Processing failed" warnings)

## Runtime Verification

After deploying fix:

1. **Restart connector service**:
   ```bash
   docker compose -f docker-compose.dev.yml restart pipeshub-ai
   ```

2. **Watch logs for success**:
   ```bash
   docker compose -f docker-compose.dev.yml logs pipeshub-ai -f | grep "Batch upsert"
   ```
   Should see: ✅ messages, NOT ❌ errors

3. **Query database**:
   ```bash
   docker compose -f docker-compose.dev.yml exec pipeshub-ai python3 -c "
   from arango import ArangoClient
   client = ArangoClient(hosts='http://arango:8529')
   db = client.db('es', username='root', password='czXG+1VB1mMGFcRoLJ2lzGA+E9fxGJqm')

   # Count records
   result = list(db.aql.execute('RETURN LENGTH(FOR doc IN records FILTER doc.connectorName == \"LOCAL_FILESYSTEM\" RETURN 1)'))
   print(f'Total records: {result[0]}')

   # Sample one record to verify structure
   sample = list(db.aql.execute('FOR doc IN records FILTER doc.connectorName == \"LOCAL_FILESYSTEM\" LIMIT 1 RETURN doc'))
   if sample:
       import json
       print(json.dumps(sample[0], indent=2))
   "
   ```

4. **Check UI** (manual):
   - Navigate to http://localhost:3000/connectors
   - Local Filesystem connector should show record count > 0
   - Click to view indexed files

</verification>

<success_criteria>

This task is DONE-DONE-DONE when ALL criteria are met:

✅ **Schema Compliance**
- All record objects match ArangoDB schema exactly
- No extra fields present
- All required fields included
- Correct field names (camelCase)
- Correct field types (timestamps as numbers)

✅ **Database Operations**
- Batch upsert succeeds (logs show ✅ not ❌)
- Records persist to ArangoDB
- Database query returns count > 0
- Indexing service finds records (no "not found" errors)

✅ **End-to-End Verification**
- Connector discovers files
- Records created and saved to database
- Indexing service processes records
- UI displays indexed files
- Search functionality works with indexed content

✅ **Code Quality**
- Type hints added for record structure
- Clear comments explaining schema requirements
- No breaking changes to other connectors
- Linting passes (ruff, mypy)

✅ **Documentation**
- SUMMARY.md explains the fix
- Code comments reference schema fields
- Future developers can understand schema requirements

**The bug is FIXED when the UI shows > 0 records and files are searchable.**

</success_criteria>

<execution_notes>

## Debugging Tips

If records still fail after initial fix:

1. **Print the record object** before upsert:
   ```python
   import json
   print("DEBUG: Record object:", json.dumps(record_dict, indent=2))
   ```

2. **Compare with working connector**:
   - Check how DRIVE or GMAIL connector creates records
   - Copy the exact pattern

3. **Test with minimal record**:
   ```python
   minimal_record = {
       "recordName": "test.txt",
       "externalRecordId": "/data/local-files/test.txt",
       "recordType": "FILE",
       "origin": "CONNECTOR",
       "createdAtTimestamp": int(time.time() * 1000)
   }
   # Try to insert this - if it works, add fields one by one
   ```

4. **Check ArangoDB error details**:
   - Schema validation errors may include which field failed
   - Look for specific field names in error messages

## Performance Note

Once working, monitor performance:
- Batch inserts should be fast (< 100ms per batch)
- No memory leaks from retry loops
- Kafka consumers commit offsets properly

## Rollback Plan

If fix causes issues:
1. Revert code changes
2. Restart service
3. RecordGroups remain intact (they're working)
4. Only file records affected

</execution_notes>
