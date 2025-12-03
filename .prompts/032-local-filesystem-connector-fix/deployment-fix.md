# Deployment Fix Guide: Local Filesystem Connector

## Quick Fix for Existing Deployments

If you're experiencing the "0 records" issue with the Local Filesystem connector, follow this guide to fix it.

## Prerequisites

- Docker and Docker Compose installed
- Access to the deployment directory
- Basic command line knowledge

## Symptoms

Your deployment shows:
- ✗ Local Filesystem connector status: "Active and syncing data"
- ✗ Records created: 0
- ✗ Indexing progress: 0% (0/0 records)
- ✗ Search returns no results

## Root Cause

The volume mount in `docker-compose.dev.yml` points to an empty directory instead of your actual files.

## Fix Steps

### Step 1: Stop Running Services

```bash
cd /path/to/hupyy-kb/deployment/docker-compose
docker compose -f docker-compose.dev.yml down
```

**Expected output:**
```
Container docker-compose-hupyy-kb-1  Stopped
Container docker-compose-hupyy-kb-1  Removed
...
```

### Step 2: Update docker-compose.dev.yml

Edit `deployment/docker-compose/docker-compose.dev.yml` and locate the volumes section (around line 100-103):

**BEFORE:**
```yaml
volumes:
  - hupyy_data:/data/hupyy
  - hupyy_root_local:/root/.local
  - /Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig:/data/local-files:ro
```

**AFTER (Development - mount project directory):**
```yaml
volumes:
  - hupyy_data:/data/hupyy
  - hupyy_root_local:/root/.local
  - /Users/alexanderfedin/Projects/hapyy/hupyy-kb:/data/local-files:ro
```

**OR (Custom directory):**
```yaml
volumes:
  - hupyy_data:/data/hupyy
  - hupyy_root_local:/root/.local
  - /path/to/your/documents:/data/local-files:ro
```

**Important:**
- Use absolute paths (not relative)
- Ensure the directory contains files you want to index
- Keep `:ro` at the end (read-only mount for security)

### Step 3: Verify Source Directory Has Files

```bash
# Check the directory you're mounting has files
ls -la /path/to/your/source/directory | head -20

# Count files
find /path/to/your/source/directory -type f | wc -l
```

**Expected:** Should show multiple files. If output is empty, choose a different directory!

### Step 4: Update Production Configuration (Optional)

If deploying to production, update `deployment/docker-compose/docker-compose.prod.yml`:

**BEFORE:**
```yaml
- ${LOCAL_FILES_PATH:-/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig}:/data/local-files:ro
```

**AFTER:**
```yaml
- ${LOCAL_FILES_PATH:-./data/local-files}:/data/local-files:ro
```

This allows configuring the path via environment variable:
```bash
export LOCAL_FILES_PATH=/var/lib/hupyy/documents
```

### Step 5: Update Documentation (Optional)

Update `CLAUDE.md` to reflect your configuration:

```markdown
### Docker Volume Mounts
- **Host Path**: `/your/actual/path` (development)
- **Host Path**: `${LOCAL_FILES_PATH:-./data/local-files}` (production)
- **Container Path**: `/data/local-files`
- **Mode**: Read-only (`:ro`)
```

### Step 6: Restart Services

```bash
cd /path/to/hupyy-kb/deployment/docker-compose
docker compose -f docker-compose.dev.yml up -d
```

**Expected output:**
```
Network docker-compose_default  Created
Container docker-compose-qdrant-1  Created
...
Container docker-compose-hupyy-kb-1  Started
```

### Step 7: Verify Volume Mount

Wait 10 seconds for services to start, then verify:

```bash
# Check files are accessible in container
docker exec docker-compose-hupyy-kb-1 ls -la /data/local-files | head -20

# Count accessible files
docker exec docker-compose-hupyy-kb-1 find /data/local-files -type f | wc -l
```

**Expected:** Should show your files and non-zero count.

### Step 8: Trigger Connector Sync

**Option A: Via UI**
1. Open http://localhost:3000
2. Go to Settings → Connectors
3. Click on "Local Filesystem"
4. Click "Sync" button

**Option B: Via Logs**
The connector should auto-sync on startup. Check logs:

```bash
docker logs docker-compose-hupyy-kb-1 2>&1 | grep "Found.*files to sync"
```

**Expected output:**
```
2025-12-03 22:14:45,298 - INFO - Found 1871 files to sync
```

If it shows "Found 0 files", the volume mount is still wrong!

### Step 9: Monitor Sync Progress

```bash
# Watch sync progress
docker logs -f docker-compose-hupyy-kb-1 2>&1 | grep -E "Processed batch|sync completed"
```

**Expected output:**
```
INFO - Processed batch of 100 records
INFO - Processed batch of 100 records
...
INFO - Local Filesystem full sync completed
```

### Step 10: Verify Records Created

```bash
# Count Kafka messages (should be thousands)
docker logs docker-compose-hupyy-kb-1 2>&1 | grep "Message successfully produced to record-events" | wc -l
```

**Expected:** Number should be 3-4x your file count (files + directories + permissions).

### Step 11: Check UI (Allow 5-10 Minutes)

1. Open http://localhost:3000
2. Go to Settings → Connectors → Local Filesystem
3. Click "Refresh Status"

**Note:** UI stats may take 5-10 minutes to update. This is normal.

## Troubleshooting

### Issue: "Found 0 files to sync"

**Causes:**
1. Volume mount still pointing to empty directory
2. Directory path doesn't exist
3. Permission denied

**Solutions:**
```bash
# Verify docker-compose.yml was saved
grep "local-files" deployment/docker-compose/docker-compose.dev.yml

# Check directory exists on host
ls -la /your/mounted/path

# Check container can see files
docker exec docker-compose-hupyy-kb-1 ls /data/local-files

# Restart services
docker compose -f docker-compose.dev.yml restart
```

### Issue: "Permission denied" in logs

**Cause:** Container user cannot read mounted directory

**Solutions:**
```bash
# Make directory readable (macOS/Linux)
chmod -R 755 /your/source/directory

# Or change mount to read-write temporarily
# In docker-compose.yml, change :ro to :rw
- /your/path:/data/local-files:rw
```

### Issue: UI still shows "0 records" after 10 minutes

**Cause:** Stats service not updating or organization mismatch

**Solutions:**
1. Check logs for actual record creation:
   ```bash
   docker logs docker-compose-hupyy-kb-1 2>&1 | grep "Upserting new record" | head -10
   ```

2. Trigger another sync from UI

3. Test search functionality directly:
   - Go to Knowledge Search
   - Search for a known file name
   - If search works, connector is functional (stats UI is just delayed)

### Issue: Services won't start after change

**Cause:** Invalid docker-compose.yml syntax

**Solutions:**
```bash
# Validate syntax
docker compose -f docker-compose.dev.yml config

# Check for common errors:
# - Missing quotes around paths with spaces
# - Incorrect indentation (use spaces, not tabs)
# - Missing :ro or :rw mode

# Restore from backup if needed
git checkout deployment/docker-compose/docker-compose.dev.yml
```

## Rollback Procedure

If fix causes issues:

```bash
# Stop services
docker compose -f docker-compose.dev.yml down

# Restore original configuration
git checkout deployment/docker-compose/docker-compose.dev.yml

# Start services
docker compose -f docker-compose.dev.yml up -d
```

## Production Deployment

For production deployments:

### Using Environment Variable (Recommended)

Create `.env` file:
```bash
LOCAL_FILES_PATH=/var/lib/hupyy/documents
```

### Using Docker Compose Override

Create `docker-compose.override.yml`:
```yaml
version: '3.8'
services:
  hupyy-kb:
    volumes:
      - /custom/path:/data/local-files:ro
```

### Verification Checklist

Before deploying to production:
- [ ] Source directory exists and contains files
- [ ] Source directory is readable by container user
- [ ] Volume mount uses absolute path
- [ ] Mount mode is :ro (read-only) for security
- [ ] Tested on staging/dev environment first
- [ ] Documented custom path for team
- [ ] Set up monitoring for connector status
- [ ] Verified backup/restore procedures

## Post-Fix Validation

After applying fix, verify:

1. **File Discovery**
   ```bash
   docker logs docker-compose-hupyy-kb-1 2>&1 | grep "Found.*files" | tail -1
   ```
   ✓ Should show non-zero file count

2. **Record Creation**
   ```bash
   docker logs docker-compose-hupyy-kb-1 2>&1 | grep "Upserting new record" | wc -l
   ```
   ✓ Should show hundreds of records

3. **Kafka Events**
   ```bash
   docker logs docker-compose-hupyy-kb-1 2>&1 | grep "successfully produced" | wc -l
   ```
   ✓ Should show thousands of events

4. **Sync Completion**
   ```bash
   docker logs docker-compose-hupyy-kb-1 2>&1 | grep "sync completed" | tail -1
   ```
   ✓ Should show recent completion timestamp

5. **Search Functionality**
   - Go to Knowledge Search
   - Search for known file or content
   ✓ Should return results (may take 10-15 minutes initially)

## Support

If issues persist after following this guide:

1. **Collect diagnostic info:**
   ```bash
   # Save logs
   docker logs docker-compose-hupyy-kb-1 > /tmp/hupyy-logs.txt 2>&1

   # Save configuration
   docker inspect docker-compose-hupyy-kb-1 > /tmp/hupyy-inspect.json
   ```

2. **Check documentation:**
   - https://docs.hupyy.com/connectors/local-filesystem
   - https://github.com/hupyy/hupyy-kb/issues

3. **Report issue:**
   Include in bug report:
   - Steps you followed
   - Error messages from logs
   - Docker version: `docker --version`
   - Operating system
   - Volume mount configuration

## Summary

**Time to fix:** 5-10 minutes
**Difficulty:** Easy
**Risk:** Low (non-destructive change)
**Downtime:** 2-3 minutes (service restart)

The fix is straightforward: update the volume mount path to point to a directory with actual files, restart services, and trigger a sync. The connector will then discover and index your files automatically.
