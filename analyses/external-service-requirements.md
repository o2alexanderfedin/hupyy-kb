# PipesHub External Service Requirements Analysis

## Executive Summary

PipesHub is a document indexing and retrieval platform with a robust local infrastructure (MongoDB, Redis, ArangoDB, Qdrant, Kafka, etcd) that handles core functionality. The platform's external dependencies fall into two categories: **mandatory external services** (enterprise SaaS connectors) and **optional external services** (AI/ML providers, cloud storage).

The minimum viable deployment requires at least one AI model provider (either cloud-based like OpenAI/Anthropic or local Ollama) for embeddings and LLM capabilities. Enterprise connectors (Google Workspace, Microsoft 365, etc.) inherently require external connectivity as they integrate with third-party SaaS platforms. Cloud storage (S3/Azure Blob) is optional and can be replaced with local storage for many use cases.

For cost-conscious deployments, running Ollama locally with open-source models provides a zero-cost AI solution at the expense of reduced quality for complex tasks. The ideal production setup combines local Ollama for embeddings (cost savings on high-volume operations) with cloud LLMs for chat/reasoning (quality-critical operations). Security-sensitive deployments should prioritize Ollama for all AI operations to prevent document content from leaving the local environment.

---

## Service-by-Service Analysis

### 1. AI/ML Model Providers

| Provider | Type | Essential | Cost | Quality | Security | Recommendation |
|----------|------|-----------|------|---------|----------|----------------|
| **OpenAI** | Cloud | High | $$$$ | Excellent | Data sent externally | Production chat/reasoning |
| **Anthropic** | Cloud | Medium | $$$$ | Excellent | Data sent externally | Alternative to OpenAI |
| **Azure OpenAI** | Cloud | Medium | $$$$ | Excellent | Enterprise compliance | Enterprise deployments |
| **Gemini** | Cloud | Medium | $$$ | Very Good | Data sent externally | Cost-effective alternative |
| **Groq** | Cloud | Low | $$ | Good | Data sent externally | Fast inference needs |
| **Cohere** | Cloud | Low | $$$ | Very Good | Data sent externally | Embedding specialist |
| **Mistral** | Cloud | Low | $$ | Good | Data sent externally | European alternative |
| **Together/Fireworks** | Cloud | Low | $$ | Good | Data sent externally | Open model hosting |
| **AWS Bedrock** | Cloud | Medium | $$$$ | Excellent | AWS compliance | AWS-native deployments |
| **Ollama** | Local | High | Free | Variable | Data stays local | Development & cost savings |

**Key Findings:**
- **Embeddings**: Ollama with models like `mxbai-embed-large` provides excellent quality at zero cost
- **LLM Chat**: Cloud providers still lead in quality; Ollama with `llama3.1`, `qwen2.5`, or `phi4` is adequate for many tasks
- **Multimodal**: Cloud providers (OpenAI, Anthropic, Gemini) remain superior for image understanding

### 2. Enterprise Connectors

| Connector | Connection Type | Authentication | Rate Limits | Data Residency Notes |
|-----------|----------------|----------------|-------------|---------------------|
| **Google Workspace** | External (Required) | OAuth 2.0 | Yes (varies by API) | Data in Google's infrastructure |
| **Microsoft 365** | External (Required) | OAuth 2.0 / Azure AD | Yes (Graph API limits) | Data in Microsoft's infrastructure |
| **Slack** | External (Required) | OAuth 2.0 | Strict (Tier-based) | Data in Slack's infrastructure |
| **Atlassian (Jira/Confluence)** | External (Required) | OAuth 2.0 | Yes | Data in Atlassian Cloud |
| **Dropbox** | External (Required) | OAuth 2.0 | Yes | Data in Dropbox infrastructure |
| **ServiceNow** | External (Required) | OAuth 2.0 / Basic | Yes | Customer instance |
| **Notion** | External (Required) | OAuth 2.0 | Yes | Data in Notion infrastructure |
| **BookStack** | External/Internal | API Token | Minimal | Self-hosted option available |
| **Local KB** | Local | N/A | None | Full local control |

**Key Findings:**
- All SaaS connectors **must** connect externally by nature
- Rate limiting handled by PipesHub's `rate_limiter` infrastructure
- OAuth tokens stored securely in etcd
- Consider data residency requirements for compliance (GDPR, HIPAA, etc.)

### 3. Cloud Storage

| Service | Use Case | Alternative | Cost Impact | Recommendation |
|---------|----------|-------------|-------------|----------------|
| **Local Storage** | Primary | N/A | Free | Default choice |
| **AWS S3** | Backup, CDN, Scale | Local + rsync | $$-$$$$ | Large-scale production |
| **Azure Blob** | Backup, CDN, Scale | Local + rsync | $$-$$$$ | Azure-native deployments |

**Configuration in PipesHub:**
- Local storage: `mountName` and optional `baseUrl`
- S3: `s3AccessKeyId`, `s3SecretAccessKey`, `s3Region`, `s3BucketName`
- Azure Blob: `accountName`, `accountKey`, `containerName`, `endpointProtocol`, `endpointSuffix`

### 4. Document Processing

| Service | Type | Cost | Quality | Recommendation |
|---------|------|------|---------|----------------|
| **Azure Document Intelligence** | Cloud | $$$$ | Excellent | Complex document extraction |
| **Local OCR (Tesseract)** | Local | Free | Good | Standard documents |
| **PDF parsing (built-in)** | Local | Free | Good | Standard PDFs |

**Note:** PipesHub includes built-in document processing capabilities. Azure Document Intelligence is optional for advanced OCR and form extraction.

### 5. Ollama Configuration Analysis

**Current Setup:**
- Configured to connect via `host.docker.internal:11434`
- Expected to run on host machine outside Docker
- Default model: `phi4` (per start-ollama.sh script)

**Should Ollama be in docker-compose?**

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **External (current)** | GPU access easy, shared across projects | Manual setup, version management | Best for development |
| **In docker-compose (CPU)** | Self-contained, reproducible | Slow inference, no GPU | Only for demos |
| **In docker-compose (GPU)** | Self-contained with performance | Complex GPU passthrough, NVIDIA only | Advanced production |

**GPU Requirements:**
- Minimum: 8GB VRAM for small models (phi4, llama3.2-3b)
- Recommended: 16GB+ VRAM for larger models (llama3.1-8b, qwen2.5-14b)
- Alternative: CPU inference (significantly slower, 10-50x)

---

## Deployment Scenario Recommendations

### Development Environment

| Service Category | Recommendation | Rationale |
|-----------------|----------------|-----------|
| **AI/ML** | Ollama (local) | Fast iteration, no API costs |
| **Enterprise Connectors** | Test accounts | Use sandbox/dev instances |
| **Storage** | Local only | Simplicity |
| **Document Processing** | Built-in | Adequate for testing |

**Configuration:**
```yaml
# docker-compose.dev.yml is ready to use
# Run Ollama separately: ollama serve
# Models: ollama pull phi4 (chat) + ollama pull mxbai-embed-large (embeddings)
```

### Small Production (Single Server)

| Service Category | Recommendation | Rationale |
|-----------------|----------------|-----------|
| **AI/ML (Embeddings)** | Ollama | Cost savings on high-volume operation |
| **AI/ML (Chat)** | Cloud (OpenAI/Anthropic) + Ollama fallback | Quality for user-facing interactions |
| **Enterprise Connectors** | All needed | Business requirement |
| **Storage** | Local + S3 backup | Disaster recovery |
| **Document Processing** | Built-in + Azure DI (optional) | Scale as needed |

**Estimated Monthly Costs:**
- Ollama: $0 (uses existing server resources)
- Cloud AI: $50-500 depending on usage
- S3 backup: $5-50 depending on data volume

### Large Production (Distributed)

| Service Category | Recommendation | Rationale |
|-----------------|----------------|-----------|
| **AI/ML (Embeddings)** | Cloud (OpenAI/Cohere) or dedicated Ollama cluster | Scale and reliability |
| **AI/ML (Chat)** | Cloud with load balancing | SLA requirements |
| **Enterprise Connectors** | All needed + premium tiers | Higher rate limits |
| **Storage** | S3/Azure Blob primary | Global distribution, CDN |
| **Document Processing** | Azure Document Intelligence | Advanced features, scale |

**Estimated Monthly Costs:**
- Cloud AI: $500-5,000+
- Cloud Storage: $100-1,000+
- Document Processing: $100-500+

---

## Trade-off Matrix

| Criterion | Local Services | Cloud Services |
|-----------|---------------|----------------|
| **Cost** | Hardware CapEx, electricity | Usage-based OpEx, can escalate |
| **Performance** | Consistent, no network latency | Variable, network dependent |
| **Security** | Data stays local | Data leaves environment |
| **Scalability** | Limited by hardware | Elastic, pay-per-use |
| **Reliability** | Self-managed | Provider SLAs |
| **Maintenance** | Self-managed updates | Provider-managed |
| **Quality (AI)** | Good for embeddings, variable for LLM | State-of-the-art models |

### Decision Framework by Priority

**Cost Priority:**
1. Ollama for all AI (free)
2. Local storage only (free)
3. Built-in document processing (free)
4. Only essential enterprise connectors

**Quality Priority:**
1. OpenAI/Anthropic for chat
2. OpenAI/Cohere for embeddings
3. Azure Document Intelligence
4. S3/Azure Blob for global access

**Security Priority:**
1. Ollama for all AI (data stays local)
2. Local storage only
3. Built-in document processing
4. Self-hosted alternatives where possible (BookStack vs Notion)

**Scalability Priority:**
1. Cloud AI providers with auto-scaling
2. S3/Azure Blob storage
3. Azure Document Intelligence
4. Consider managed Kafka (Confluent Cloud)

---

## Discussion Point Answers

### 1. Minimum Viable External Dependencies

**Absolute Minimum:**
- One AI provider (Ollama = zero external, or one cloud provider)
- Zero enterprise connectors (use Local KB only)
- Local storage

**Practical Minimum for Business Use:**
- AI: Ollama (embeddings) + one cloud LLM (chat)
- Connectors: At least one (e.g., Google Drive or OneDrive)
- Storage: Local with backup strategy

### 2. Cost Optimization Opportunities

| Replace This | With This | Quality Impact | Monthly Savings |
|--------------|-----------|----------------|-----------------|
| OpenAI embeddings | Ollama mxbai-embed-large | Minimal | $100-1,000+ |
| GPT-4o for simple tasks | Ollama phi4/llama3.1 | Moderate | $50-500 |
| S3 for internal docs | Local storage | None | $10-100 |
| Azure Document Intelligence | Built-in OCR | Moderate for complex docs | $50-200 |

### 3. Security Posture Recommendations

**Keep Local (Sensitive Data):**
- All AI processing via Ollama (documents/queries contain business data)
- Document storage (use local, not S3)
- Vector database (Qdrant already local)

**Safe for Cloud:**
- Enterprise connectors (accessing data already in cloud)
- Metadata-only operations
- Non-sensitive document processing

### 4. Scaling Bottlenecks

| Component | Bottleneck Risk | Solution |
|-----------|-----------------|----------|
| **Ollama (local)** | High - GPU/CPU bound | Upgrade hardware or move to cloud AI |
| **Qdrant (local)** | Medium - Memory bound | Horizontal scaling, cloud migration |
| **MongoDB/ArangoDB** | Medium - Storage/IO | Sharding, replication |
| **Kafka** | Low - Well-scaled | Confluent Cloud for extreme scale |
| **Document Processing** | Medium - CPU bound | Azure Document Intelligence |

### 5. Ollama Deployment Recommendation

**Development:** Keep external (current setup)
- Easy GPU access
- Flexible model experimentation
- Simple to update

**Production (Recommended):** Dedicated GPU server or cloud GPU instance
- Not in docker-compose due to GPU complexity
- Use separate deployment with high availability
- Consider multiple instances behind load balancer

**docker-compose Addition (If Needed):**
```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_models:/root/.ollama
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### 6. Hybrid Recommendations by Scenario

#### Development Environment
```
Local: MongoDB, Redis, ArangoDB, Qdrant, Kafka, etcd, Ollama (100%)
Cloud: None
```

#### Small Production (Single Server, Security-Focused)
```
Local: All infrastructure + Ollama for AI (95%)
Cloud: Enterprise connectors only (5%)
```

#### Small Production (Single Server, Quality-Focused)
```
Local: All infrastructure (80%)
Cloud: OpenAI/Anthropic for LLM, enterprise connectors (20%)
```

#### Large Production (Distributed)
```
Local: Frontend, backend services (30%)
Cloud:
- AI providers for scale
- S3/Azure Blob storage
- Managed Kafka (optional)
- Azure Document Intelligence
- Enterprise connectors (70%)
```

---

## Decision Checklist

### Before Deployment

- [ ] **AI Provider Selection**
  - [ ] Will document content contain sensitive/regulated data?
  - [ ] What is the monthly budget for AI API calls?
  - [ ] Is GPU hardware available for Ollama?
  - [ ] What quality level is required for chat responses?

- [ ] **Enterprise Connector Needs**
  - [ ] Which platforms do users need to connect?
  - [ ] Are OAuth credentials available for each platform?
  - [ ] Have API rate limits been reviewed?
  - [ ] Are there data residency requirements?

- [ ] **Storage Strategy**
  - [ ] What is the expected document volume?
  - [ ] Is disaster recovery required?
  - [ ] Is CDN/global access needed?
  - [ ] What is the backup strategy?

- [ ] **Document Processing**
  - [ ] What document types will be processed?
  - [ ] Are there complex forms or handwritten content?
  - [ ] What is the expected processing volume?

### Configuration Steps

1. **Deploy base infrastructure** (docker-compose.dev.yml or docker-compose.prod.yml)
2. **Set up Ollama** (if using local AI)
   - Install on host or GPU server
   - Pull required models: `ollama pull phi4 && ollama pull mxbai-embed-large`
3. **Configure AI providers** (via frontend settings or etcd)
4. **Set up enterprise connectors** (OAuth credentials in platform settings)
5. **Configure storage** (local paths or cloud credentials)
6. **Test document processing** pipeline

---

## Cost Estimation Templates

### Small Deployment (Monthly)

| Item | Local Cost | Cloud Cost | Hybrid Cost |
|------|------------|------------|-------------|
| AI (10K queries) | $0 (Ollama) | $100-300 | $50-150 |
| Storage (100GB) | $0 | $10-30 | $5-15 |
| Infrastructure | Server costs | N/A | Server costs |
| **Total** | **Server only** | **$110-330** | **$55-165** |

### Medium Deployment (Monthly)

| Item | Local Cost | Cloud Cost | Hybrid Cost |
|------|------------|------------|-------------|
| AI (100K queries) | $0 (Ollama) | $500-1,500 | $200-500 |
| Storage (1TB) | $0 | $50-150 | $25-75 |
| Infrastructure | Server costs | N/A | Server costs |
| **Total** | **Server only** | **$550-1,650** | **$225-575** |

---

## Appendix: Supported Models Reference

### LLM Providers (Chat/Reasoning)
- OpenAI: gpt-4o, gpt-4o-mini, o1, o1-mini
- Anthropic: claude-3.5-sonnet, claude-3.5-haiku
- Gemini: gemini-2.0-flash, gemini-1.5-pro
- Azure OpenAI: Same as OpenAI (deployed)
- AWS Bedrock: Claude, Llama, Titan
- Ollama: llama3.1, qwen2.5, phi4, mistral, etc.
- Groq: llama3.1-8b, mixtral
- Mistral: mistral-large, mistral-medium
- Together/Fireworks: Open models (Llama, Qwen, etc.)

### Embedding Providers
- OpenAI: text-embedding-3-small, text-embedding-3-large
- Cohere: embed-english-v3.0, embed-multilingual-v3.0
- Gemini: embedding-001
- Azure OpenAI: text-embedding-3-small (deployed)
- AWS Bedrock: titan-embed-text, cohere-embed
- Ollama: mxbai-embed-large, nomic-embed-text
- Sentence Transformers: all-MiniLM-L6-v2, all-mpnet-base-v2
- Jina AI: jina-embeddings-v2
- Voyage: voyage-2, voyage-large-2

---

*Analysis generated on November 20, 2025*
*Based on PipesHub codebase configuration files and provider documentation*
