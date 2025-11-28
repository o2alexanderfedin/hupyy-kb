# PipesHub Setup Guide: Local Infrastructure with Anthropic Claude

This guide walks you through setting up PipesHub with:
- **All infrastructure services running locally via Docker**
- **Anthropic Claude as the LLM provider** (for high-quality responses)
- **Local Sentence Transformers for embeddings** (cost-effective, private)

This configuration provides maximum data privacy with all processing happening locally, while leveraging Anthropic's Claude for intelligent responses.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start](#2-quick-start)
3. [Configuration Details](#3-configuration-details)
4. [Verification Checklist](#4-verification-checklist)
5. [Troubleshooting](#5-troubleshooting)
6. [Security Notes](#6-security-notes)

---

## 1. Prerequisites

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 2 cores | 4+ cores |
| Disk Space | 30 GB | 50 GB |
| OS | macOS, Linux, Windows (WSL2) | macOS, Linux |

### Required Software

| Software | Minimum Version | Installation |
|----------|-----------------|--------------|
| Docker | 24.0+ | [Install Docker](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.20+ | Included with Docker Desktop |
| Git | 2.0+ | [Install Git](https://git-scm.com/downloads) |

### Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy and securely store the API key (you'll need it during setup)

> **Note**: Anthropic offers different Claude models with version-independent short names:
> - `sonnet` - Balanced performance and cost
> - `haiku` - Faster, more economical
> - `opus` - Most capable

---

## 2. Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/pipeshub/pipeshub-ai.git
cd pipeshub-ai
```

### Step 2: Configure Environment Variables

Create a `.env` file in the `deployment/docker-compose/` directory:

```bash
cd deployment/docker-compose/
cat > .env << 'EOF'
# ===========================================
# PipesHub Local Deployment Configuration
# ===========================================

# Core Settings
NODE_ENV=production
LOG_LEVEL=info
ALLOWED_ORIGINS=http://localhost:3000

# Security Keys - CHANGE ALL OF THESE IN PRODUCTION
# Generate with: openssl rand -hex 32
SECRET_KEY=your_random_encryption_secret_key_change_me_32chars

# Public URLs
FRONTEND_PUBLIC_URL=http://localhost:3000
CONNECTOR_PUBLIC_BACKEND=http://localhost:8088

# ArangoDB Configuration
ARANGO_PASSWORD=your_secure_arango_password

# MongoDB Configuration
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_mongo_password

# Redis Configuration (leave empty for no password in development)
REDIS_PASSWORD=your_secure_redis_password

# Qdrant Vector Database
QDRANT_API_KEY=your_secure_qdrant_api_key

# Docker Image Tag
IMAGE_TAG=latest
EOF
```

### Step 3: Start Docker Services

```bash
# From the deployment/docker-compose/ directory
docker compose -f docker-compose.prod.yml up -d
```

Wait for all services to become healthy (2-5 minutes on first run):

```bash
docker compose -f docker-compose.prod.yml ps
```

### Step 4: Access the Web Interface

Open your browser and navigate to:

```
http://localhost:3000
```

### Step 5: Configure AI Models in the UI

1. **Initial Setup**: Complete the initial setup wizard if prompted

2. **Navigate to AI Models Settings**:
   - Go to **Account Settings** > **AI Models**

3. **Configure Anthropic as LLM Provider**:
   - Click **Add Model** or **Configure** under LLM section
   - Select **Anthropic** from the provider list
   - Fill in the configuration:
     - **API Key**: Your Anthropic API key
     - **Model**: `sonnet` (or `haiku` or `opus`)
     - **Is Multimodal**: Enable if using vision features
   - Click **Save** and **Set as Default**

4. **Configure Sentence Transformers for Embeddings**:
   - Click **Add Model** under Embedding section
   - Select **Sentence Transformers** from the provider list
   - Fill in the configuration:
     - **Model**: `sentence-transformers/all-MiniLM-L6-v2`
   - Click **Save** and **Set as Default**

---

## 2a. Automated Configuration with Playwright

For automated setup of AI models via the web UI, use the provided Playwright script.

### Prerequisites

```bash
# Install Playwright and Chromium
npm install playwright
npx playwright install chromium
```

### Run Automated Configuration

```bash
# From the repository root
node scripts/configure-pipeshub.js
```

The script will:
1. Navigate to PipesHub UI
2. Complete initial admin setup if needed
3. Configure Anthropic as the LLM provider
4. Configure Sentence Transformers for embeddings
5. Set both as default models

**Note**: You'll need to set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY=your-anthropic-api-key-here
node scripts/configure-pipeshub.js
```

---

## 3. Configuration Details

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Environment mode | `production` | No |
| `LOG_LEVEL` | Logging verbosity | `info` | No |
| `SECRET_KEY` | Encryption key for secrets | - | **Yes** |
| `ARANGO_PASSWORD` | ArangoDB root password | `your_password` | **Yes** |
| `MONGO_USERNAME` | MongoDB admin username | `admin` | No |
| `MONGO_PASSWORD` | MongoDB admin password | `password` | **Yes** |
| `REDIS_PASSWORD` | Redis password | - | No |
| `QDRANT_API_KEY` | Qdrant vector DB API key | - | **Yes** |
| `FRONTEND_PUBLIC_URL` | Public URL for frontend | - | No |
| `CONNECTOR_PUBLIC_BACKEND` | Public URL for connector API | - | No |

### Docker Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| `pipeshub-ai` | 3000, 8000, 8081, 8088, 8091 | Main application (frontend, query, connector, indexing) |
| `mongodb` | 27017 | Document storage for application data |
| `redis` | 6379 | Caching and session management |
| `arango` | 8529 | Graph database for knowledge graphs |
| `etcd` | 2379 | Distributed configuration store |
| `kafka-1` | 9092 | Message queue for async processing |
| `zookeeper` | 2181 | Kafka coordination |
| `qdrant` | 6333, 6334 | Vector database for embeddings |

### Anthropic Model Configuration

When configuring Anthropic in the UI, use these fields:

| Field | Description | Example |
|-------|-------------|---------|
| API Key | Your Anthropic API key | `sk-ant-api03-...` |
| Model | Model identifier(s) | `sonnet` |
| Is Multimodal | Enable vision capabilities | `true` |
| Is Reasoning | For advanced reasoning tasks | `false` |

**Available Claude Models** (use short names):
- `sonnet` - Best balance of intelligence and speed
- `haiku` - Fastest, most economical
- `opus` - Most capable for complex tasks

These short names are version-independent and will automatically use the latest version of each model.

### Sentence Transformers Embedding Configuration

| Field | Description | Example |
|-------|-------------|---------|
| Model | Embedding model name | `sentence-transformers/all-MiniLM-L6-v2` |

The `sentence-transformers/all-MiniLM-L6-v2` model runs locally within the PipesHub container, providing fast and efficient embeddings without any external service dependencies.

---

## 4. Verification Checklist

### Service Health Checks

Run these commands to verify all services are healthy:

```bash
# Check all container status
docker compose -f docker-compose.prod.yml ps

# Check specific services
docker compose -f docker-compose.prod.yml logs pipeshub-ai --tail 50
docker compose -f docker-compose.prod.yml logs qdrant --tail 20
```

All services should show status `healthy` or `running`.

### Verify Anthropic API

Test your API key directly:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

> **Note**: The API test uses the full model name, but in PipesHub configuration you should use the short name `sonnet`.

### UI Verification Steps

1. **Login/Setup**: Access `http://localhost:3000` and complete initial setup
2. **Check AI Models**: Navigate to Account Settings > AI Models
   - Verify Anthropic LLM is configured and marked as default
   - Verify Sentence Transformers embeddings are configured and marked as default
3. **Test Chat**: Use the Q&A or Ask Me Anything feature to send a test query
4. **Check Indexing**: If you have documents, verify they are being indexed (check Qdrant dashboard at `http://localhost:6333/dashboard`)

---

## 5. Troubleshooting

### Common Issues and Solutions

#### Docker Container Won't Start

**Symptom**: Container exits immediately or fails health check

```bash
# Check container logs
docker compose -f docker-compose.prod.yml logs <service-name>

# Check resource usage
docker stats
```

**Solutions**:
- Ensure Docker has enough memory allocated (8GB minimum, 16GB+ recommended)
- Check if ports are already in use: `lsof -i :3000`
- Verify environment variables are set correctly

#### Anthropic API Errors

**Symptom**: 401 Unauthorized or API errors

**Solutions**:

1. Verify API key is valid and not expired
2. Check API key has correct permissions in Anthropic Console
3. Ensure you're not exceeding rate limits
4. Verify you're using the correct short model name (haiku, sonnet, or opus)

**Common error codes**:
- `401`: Invalid API key
- `429`: Rate limit exceeded
- `500`: Anthropic service error

#### Port Conflicts

**Symptom**: "Port already in use" error

**Solutions**:

```bash
# Find what's using the port
lsof -i :3000
lsof -i :8529

# Kill the process or change the port in docker-compose
```

To use different ports, modify the `ports` mapping in docker-compose.yml:
```yaml
ports:
  - "3001:3000"  # Map to port 3001 instead
```

#### Qdrant Connection Issues

**Symptom**: Vector search fails or returns errors

**Solutions**:

1. Verify Qdrant is healthy:
   ```bash
   curl http://localhost:6333/collections
   ```

2. Check API key matches:
   - Environment variable: `QDRANT_API_KEY`
   - Must match `QDRANT__SERVICE__API_KEY` in container

#### Embedding Model Issues

**Symptom**: Embeddings fail to generate or indexing errors

**Solutions**:

1. Verify the embedding model is configured correctly in the UI
2. Check PipesHub container logs for Sentence Transformers errors:
   ```bash
   docker compose -f docker-compose.prod.yml logs pipeshub-ai | grep -i embed
   ```
3. Ensure the container has sufficient memory for the model

#### MongoDB/ArangoDB Authentication Failures

**Symptom**: Database connection errors on startup

**Solutions**:

1. Ensure passwords don't contain special characters that need escaping
2. For fresh installation, remove volumes and restart:
   ```bash
   docker compose -f docker-compose.prod.yml down -v
   docker compose -f docker-compose.prod.yml up -d
   ```

### Viewing Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f pipeshub-ai

# Last N lines
docker compose -f docker-compose.prod.yml logs --tail 100 pipeshub-ai
```

---

## 6. Security Notes

### API Key Handling

- **Never commit API keys** to version control
- Use environment variables or secrets management
- Rotate Anthropic API keys periodically
- Set usage limits in Anthropic Console to prevent unexpected charges

### Network Security

- **Default ports are exposed** to localhost only
- For production deployment:
  - Use a reverse proxy (nginx, traefik) with TLS
  - Restrict port exposure in docker-compose
  - Implement proper authentication

### Data Privacy Benefits

This configuration provides enhanced privacy:

| Component | Privacy Benefit |
|-----------|-----------------|
| Local Sentence Transformers Embeddings | All document vectorization stays on your infrastructure |
| Local Vector Database | Embeddings never leave your servers |
| Local Document Storage | Files processed and stored locally |
| Local Databases | All metadata and configurations stored locally |

**Only LLM queries go to Anthropic** - your documents and embeddings remain local.

### Production Recommendations

1. **Change all default passwords** in the `.env` file
2. **Use strong, unique secrets** for:
   - `SECRET_KEY` (32+ random characters)
   - All database passwords
   - `QDRANT_API_KEY`
3. **Enable TLS/HTTPS** for all public endpoints
4. **Implement backup strategy** for Docker volumes
5. **Monitor resource usage** to prevent service disruption
6. **Set up log aggregation** for security monitoring

### Firewall Rules

For a secure setup, only expose these ports externally:

```bash
# Frontend (through reverse proxy)
3000 -> 443 (via nginx/traefik)

# All other ports should be internal only
```

---

## Additional Resources

- [PipesHub Documentation](https://docs.pipeshub.ai)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

## Appendix: Complete .env Example

```bash
# ===========================================
# PipesHub Local Deployment Configuration
# ===========================================

# Core Settings
NODE_ENV=production
LOG_LEVEL=info
ALLOWED_ORIGINS=http://localhost:3000

# Security Keys - CHANGE ALL OF THESE
# Generate SECRET_KEY with: openssl rand -hex 32
SECRET_KEY=your_random_encryption_secret_key_change_me_32chars

# Public URLs
FRONTEND_PUBLIC_URL=http://localhost:3000
CONNECTOR_PUBLIC_BACKEND=http://localhost:8088

# ArangoDB
ARANGO_PASSWORD=your_secure_arango_password

# MongoDB
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_mongo_password

# Redis (leave empty for no password in development)
REDIS_PASSWORD=your_secure_redis_password

# Qdrant Vector Database
QDRANT_API_KEY=your_secure_qdrant_api_key

# Docker Image Tag (for production)
IMAGE_TAG=latest
```

Save this as `deployment/docker-compose/.env` and customize the values before starting.

---

## Appendix: Playwright Automation Script

The `scripts/configure-pipeshub.js` script automates the web UI configuration. Here's what it does:

```javascript
// Key configuration steps performed by the script:
// 1. Waits for PipesHub UI to be available
// 2. Navigates to Account Settings > AI Models
// 3. Adds Anthropic as LLM provider with your API key
// 4. Sets Anthropic model (sonnet) as default
// 5. Adds Sentence Transformers as embedding provider
// 6. Sets embedding model (sentence-transformers/all-MiniLM-L6-v2) as default
```

To customize the script behavior, edit `scripts/configure-pipeshub.js` and modify:
- `PIPESHUB_URL` - Change if using different port
- `MODEL_NAME` - Change to 'haiku' or 'opus' if preferred
- Admin credentials for initial setup
