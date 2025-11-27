# TO-DOS

## COMPLETED - File Streaming Issue Fixed - 2025-11-21 05:20

- ~~**Add debug logging to stream_record**~~ - **RESOLVED**: The "File not found" errors were caused by old records with incorrect paths from a previous volume mount. **Fix applied:**
  1. Added debug logging to `connector.py:280-307`
  2. Identified old records had paths like `/data/local-files/pipeshub/pipeshub-ai/...` instead of `/data/local-files/...`
  3. Cleared old records from ArangoDB
  4. Cleared orphaned embeddings from Qdrant
  5. Reset Kafka consumer offset to skip old messages
  6. Triggered fresh sync with correct paths

  The Local Filesystem connector is now fully functional with proper file streaming.

