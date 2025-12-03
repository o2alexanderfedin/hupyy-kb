# PipesHub to Hupyy KB Migration Guide

## For Self-Hosted Users

### Docker Compose Migration

If you're running PipesHub with Docker Compose, follow these steps:

1. **Stop Current Containers**
   ```bash
   docker compose -f docker-compose.prod.yml -p pipeshub-ai down
   ```

2. **Pull New Image**
   ```bash
   docker pull hupyy/hupyy-kb:latest
   ```

3. **Migrate Volume Data** (IMPORTANT - preserves your data)
   ```bash
   # Create new volumes
   docker volume create hupyy_data
   docker volume create hupyy_root_local

   # Copy data from old volumes to new
   docker run --rm -v pipeshub_data:/from -v hupyy_data:/to alpine sh -c "cd /from && cp -av . /to"
   docker run --rm -v pipeshub_root_local:/from -v hupyy_root_local:/to alpine sh -c "cd /from && cp -av . /to"
   ```

4. **Update docker-compose.yml**
   - Change image: `hupyy/hupyy-kb:latest`
   - Update service name: `hupyy-kb`
   - Update volume names: `hupyy_data`, `hupyy_root_local`

5. **Start with New Configuration**
   ```bash
   docker compose -f docker-compose.prod.yml -p hupyy-kb up -d
   ```

### Configuration Changes

Update environment variables if you've customized:
- Service name references
- Volume mount paths
- Container names in scripts

### What Doesn't Change

- Database schemas (unchanged)
- API endpoints (unchanged)
- Connector configurations (unchanged)
- User data and credentials (preserved)

## For Developers

### Local Development Setup

1. **Pull Latest Code**
   ```bash
   git pull origin develop
   ```

2. **Update Environment**
   ```bash
   cd deployment/docker-compose
   docker compose -f docker-compose.dev.yml -p hupyy-kb up --build -d
   ```

3. **Verify Services**
   ```bash
   docker ps | grep hupyy-kb
   ```

### Package Names

If you've integrated PipesHub as a dependency:
- NPM packages: Update to `@hupyy/*`
- Docker images: Update to `hupyy/hupyy-kb`

## Rollback Procedure

If you encounter issues:

1. **Stop new containers**
   ```bash
   docker compose -f docker-compose.prod.yml -p hupyy-kb down
   ```

2. **Revert to old image**
   ```bash
   docker compose -f docker-compose.prod.yml -p pipeshub-ai up -d
   ```

Your original volumes (`pipeshub_data`, `pipeshub_root_local`) remain intact.

## Support

- GitHub Issues: https://github.com/hupyy/hupyy-kb/issues
- Email: support@hupyy.com
- Discord: https://discord.gg/hupyy
