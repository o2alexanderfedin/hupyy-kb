---
name: deploy-local-docker
description: Deploy OilField application to local Docker containers with docker-compose. Includes building images, running migrations, and verifying services.
---

# Deploy to Local Docker

Deploy the OilField application to local Docker containers using docker-compose.

## Prerequisites

- Docker and Docker Compose installed
- Mapbox token configured in environment

## Deployment Steps

### 1. Check Docker Status

```bash
docker --version
docker-compose --version
docker ps
```

### 2. Environment Configuration

Ensure `.env` file exists in project root with:
```
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

### 3. Build and Start Services

```bash
# Build all containers
docker-compose build

# Start all services in detached mode
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 4. Run Database Migrations and Seeds

```bash
# Run migrations
docker-compose exec backend npm run migrate:latest

# Run seeds (if needed)
docker-compose exec backend npm run seed
```

### 5. Verify Deployment

Check each service:

```bash
# Backend health check
curl http://localhost:3001/health

# Test wells API
curl http://localhost:3001/api/wells?limit=5

# Database connection
docker-compose exec postgres psql -U oilfield -d oilfield -c "SELECT COUNT(*) FROM wells;"
```

### 6. Access Application

- **Frontend**: http://localhost:8090
- **Backend API**: http://localhost:3001
- **Database**: localhost:5434 (user: oilfield, password: oilfield_dev)

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes database data)
docker-compose down -v

# Fresh start
docker-compose up -d --build
```

### Common Issues

1. **Port conflicts**: Check if ports 3001, 5434, or 8090 are already in use
2. **Database connection**: Wait for postgres healthcheck to complete before running migrations
3. **Missing Mapbox token**: Ensure VITE_MAPBOX_TOKEN is set in .env

## Services

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| postgres | oilfield-postgres | 5434 | PostgreSQL with pgvector |
| backend | oilfield-backend | 3001 | Express API |
| frontend | oilfield-frontend | 8090 | React app (nginx) |
