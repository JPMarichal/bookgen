# System Architecture Overview

Complete technical overview of BookGen's architecture and design.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BookGen System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐│
│  │   Client Apps  │───▶│  FastAPI REST  │───▶│  Celery Worker ││
│  │  (Web, CLI)    │◀───│      API       │◀───│   (Async Jobs) ││
│  └────────────────┘    └────────────────┘    └────────────────┘│
│         │                      │                      │          │
│         │                      │                      │          │
│    WebSocket              ┌────▼────┐            ┌───▼───┐      │
│    Real-time              │PostgreSQL│            │ Redis │      │
│    Updates                │Database  │            │ Queue │      │
│                           └─────────┘            └───────┘      │
│                                                        │          │
│                                                   ┌────▼────┐    │
│                                                   │OpenRouter│    │
│                                                   │   API    │    │
│                                                   │  (LLM)   │    │
│                                                   └─────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Core Components

### 1. FastAPI REST API

**Purpose:** Primary entry point for all requests

**Responsibilities:**
- Accept and validate API requests
- Handle authentication/authorization
- Manage WebSocket connections
- Route requests to appropriate services
- Return responses to clients

**Technology:**
- FastAPI 0.104+
- Uvicorn ASGI server
- Pydantic for validation
- Python 3.9+

**Key Files:**
```
src/main.py                     # Application entry point
src/api/routers/
  ├── biographies.py           # Biography endpoints
  ├── sources.py               # Source validation
  ├── metrics.py               # Metrics endpoint
  └── websocket.py             # WebSocket handler
src/api/middleware/
  ├── rate_limiter.py          # Rate limiting
  └── request_logger.py        # Request logging
```

### 2. Celery Worker

**Purpose:** Asynchronous task processing

**Responsibilities:**
- Execute long-running biography generation
- Process tasks in background
- Handle retries and failures
- Update job status and progress
- Send notifications

**Technology:**
- Celery 5.3+
- Redis as message broker
- PostgreSQL for result backend

**Key Files:**
```
src/worker.py                  # Celery app configuration
src/tasks/
  ├── biography_tasks.py       # Main generation tasks
  ├── validation_tasks.py      # Source validation
  └── export_tasks.py          # Document export
```

### 3. State Machine Engine

**Purpose:** Orchestrate biography generation workflow

**Responsibilities:**
- Manage generation phases
- Track workflow state
- Handle checkpoints
- Coordinate services
- Ensure consistency

**Phases:**
1. Source Validation
2. Research Planning
3. Chapter Generation
4. Special Sections
5. Quality Control
6. Export

**Key Files:**
```
src/engine/
  ├── bookgen_engine.py        # Main engine
  ├── state_machine.py         # State management
  └── workflow_manager.py      # Workflow coordination
```

### 4. OpenRouter Client

**Purpose:** Interface with AI language models

**Responsibilities:**
- Send generation requests to OpenRouter API
- Handle API responses
- Manage rate limiting
- Implement retry logic
- Track token usage

**Supported Models:**
- Qwen 2.5 (Free tier)
- Claude 3.5 Sonnet (Premium)
- GPT-4 Turbo (Premium)
- Gemini Pro (Premium)

**Key Files:**
```
src/services/openrouter_client.py
src/services/prompt_templates.py
```

### 5. PostgreSQL Database

**Purpose:** Persistent data storage

**Responsibilities:**
- Store job metadata
- Track biography progress
- Store generated content
- Manage relationships
- Provide ACID guarantees

**Schema:**
```sql
-- Jobs table
CREATE TABLE biography_jobs (
    job_id UUID PRIMARY KEY,
    character VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0.0,
    current_phase VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Chapters table
CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES biography_jobs(job_id),
    chapter_number INTEGER,
    title VARCHAR(255),
    content TEXT,
    word_count INTEGER,
    created_at TIMESTAMP
);

-- Sources table
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES biography_jobs(job_id),
    url TEXT NOT NULL,
    valid BOOLEAN,
    status_code INTEGER,
    relevance_score FLOAT,
    validated_at TIMESTAMP
);
```

**Key Files:**
```
src/database/
  ├── connection.py            # DB connection
  ├── models.py                # SQLAlchemy models
  └── repositories/            # Data access layer
alembic/                       # Migrations
  └── versions/
```

### 6. Redis

**Purpose:** Message broker and cache

**Responsibilities:**
- Queue Celery tasks
- Store task results
- Cache frequently accessed data
- Manage rate limiting
- Handle session data

**Redis Databases:**
- DB 0: Task queue (Celery)
- DB 1: Task results
- DB 2: Cache
- DB 3: Rate limiting

**Key Configuration:**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 7. Notification Service

**Purpose:** Multi-channel notifications

**Channels:**
- **WebSocket**: Real-time browser updates
- **Webhook**: HTTP callbacks to external services
- **Email**: SMTP notifications

**Key Files:**
```
src/services/notifications.py
src/api/routers/websocket.py
src/email/
  ├── templates/               # Email templates
  └── smtp_client.py           # SMTP sender
```

## 🔄 Data Flow

### Biography Generation Flow

```
1. Client Request
   ↓
2. FastAPI validates request
   ↓
3. Create job in database (status: pending)
   ↓
4. Queue Celery task
   ↓
5. Celery worker picks up task
   ↓
6. State Machine Engine starts
   ↓
7. Phase 1: Validate sources
   ├─ Fetch each URL
   ├─ Analyze content
   └─ Store results
   ↓
8. Phase 2: Research planning
   ├─ Extract key facts
   ├─ Identify events
   └─ Create outline
   ↓
9. Phase 3: Generate chapters
   ├─ For each chapter:
   │  ├─ Build prompt
   │  ├─ Call OpenRouter API
   │  ├─ Validate response
   │  └─ Store chapter
   └─ Update progress
   ↓
10. Phase 4: Generate special sections
    ├─ Prologue/Epilogue
    ├─ Timeline
    └─ Glossary
    ↓
11. Phase 5: Quality control
    ├─ Validate word counts
    ├─ Check coherence
    └─ Verify citations
    ↓
12. Phase 6: Export
    ├─ Concatenate sections
    ├─ Apply template
    └─ Generate .docx
    ↓
13. Update job (status: completed)
    ↓
14. Send notifications
    ├─ WebSocket update
    ├─ Webhook callback
    └─ Email (if configured)
```

### Request/Response Flow

```
Client App
    │
    │ HTTP POST /api/v1/biographies
    ↓
FastAPI Router
    │
    │ Validate request with Pydantic
    ↓
Biography Service
    │
    │ Create job record
    ↓
PostgreSQL
    │
    │ Job saved (status: pending)
    ↓
Celery Task Queue
    │
    │ Task queued in Redis
    ↓
Celery Worker
    │
    │ Pick up task
    ↓
BookGen Engine
    │
    │ Execute workflow
    │ ├─ Update progress
    │ ├─ Send notifications
    │ └─ Save checkpoints
    ↓
OpenRouter API
    │
    │ Generate content
    ↓
Storage Layer
    │
    │ Save chapters/files
    ↓
Client App
    │
    │ Receives notifications via:
    ├─ WebSocket (real-time)
    ├─ Webhook (callback)
    └─ Email (optional)
```

## 🔐 Security Architecture

### Authentication & Authorization

**Current:**
- Optional API key authentication
- IP-based rate limiting
- CORS protection

**Production Recommendations:**
- JWT token authentication
- Role-based access control (RBAC)
- OAuth 2.0 integration

### Data Security

**In Transit:**
- TLS/SSL encryption (HTTPS)
- WebSocket over TLS (WSS)
- Encrypted webhook payloads

**At Rest:**
- Database encryption
- Encrypted environment variables
- Secure credential storage

### API Security

**Rate Limiting:**
```python
# Default: 60 requests per minute per IP
RATE_LIMIT_PER_MINUTE=60
```

**Input Validation:**
- Pydantic models
- URL sanitization
- SQL injection prevention
- XSS protection

**Security Headers:**
```python
# Added by middleware
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## 📈 Scalability

### Horizontal Scaling

**API Layer:**
```bash
# Run multiple API instances behind load balancer
docker-compose scale api=3
```

**Worker Layer:**
```bash
# Run multiple workers for parallel processing
docker-compose scale worker=5
```

**Load Balancer:**
```
       ┌─────────┐
       │  Nginx  │
       │(LB/Proxy)│
       └────┬────┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼──┐ ┌──▼──┐ ┌─▼───┐
│API-1 │ │API-2│ │API-3│
└──────┘ └─────┘ └─────┘
```

### Vertical Scaling

**Database:**
- Increase PostgreSQL resources
- Tune connection pooling
- Add read replicas

**Redis:**
- Increase memory allocation
- Enable persistence
- Configure eviction policies

**Workers:**
- Increase concurrency per worker
- Allocate more CPU/RAM
- Optimize batch sizes

### Caching Strategy

**Redis Cache:**
```python
# Cache validation results
cache_key = f"source:valid:{url_hash}"
redis.setex(cache_key, 3600, validation_result)

# Cache API responses
cache_key = f"status:{job_id}"
redis.setex(cache_key, 60, job_status)
```

**Application Cache:**
- Source validation results (1 hour)
- Job status (1 minute)
- System metrics (5 minutes)

## 🔍 Monitoring & Observability

### Health Checks

**Endpoints:**
- `/health` - Basic health
- `/api/v1/status` - Detailed status
- `/api/v1/metrics` - System metrics

**Metrics Tracked:**
- Active jobs
- Completed jobs
- Failed jobs
- Average generation time
- API response times
- Worker queue length

### Logging

**Log Levels:**
- DEBUG: Development details
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors that need attention
- CRITICAL: System failures

**Log Aggregation:**
```bash
# All logs to stdout (Docker)
docker-compose logs -f

# Structured JSON logs
LOG_FORMAT=json

# Log levels by service
API_LOG_LEVEL=INFO
WORKER_LOG_LEVEL=DEBUG
```

### Alerting

**Health Monitoring:**
```bash
# Automated health checks every 5 minutes
*/5 * * * * curl -f http://localhost:8000/health || alert
```

**Error Alerting:**
- Email on critical errors
- Slack/Discord webhooks
- PagerDuty integration

## 🚀 Deployment Architecture

### Docker Deployment

```yaml
services:
  nginx:        # Reverse proxy
  api:          # FastAPI application
  worker:       # Celery worker
  db:           # PostgreSQL
  redis:        # Redis server
```

### Production Stack

```
Internet
    │
    ↓
┌─────────────┐
│  Cloudflare │  (CDN, DDoS protection)
└──────┬──────┘
       │
┌──────▼──────┐
│    Nginx    │  (Reverse proxy, SSL, load balancing)
└──────┬──────┘
       │
┌──────▼──────┐
│   Docker    │  (Container orchestration)
│  Containers │
│  ├─ API (3x)│
│  ├─ Worker  │
│  ├─ DB      │
│  └─ Redis   │
└─────────────┘
```

## 📊 Performance Characteristics

### Throughput

**API:**
- 100+ requests/second (single instance)
- 300+ requests/second (3 instances)

**Worker:**
- 1-3 concurrent biography jobs
- 5-10 concurrent chapters per job

### Latency

**API Endpoints:**
- Health check: < 10ms
- Job creation: < 100ms
- Status query: < 50ms

**Generation:**
- Source validation: 5-10 minutes
- Chapter generation: 1-2 hours
- Total: 2-4 hours

### Resource Usage

**Per Biography Job:**
- CPU: 2-4 cores during generation
- RAM: 1-2 GB
- Disk: ~10 MB output
- Network: ~50 MB API calls

## 🔄 Technology Stack

**Backend:**
- Python 3.9+
- FastAPI 0.104+
- Celery 5.3+
- SQLAlchemy 2.0+
- Pydantic 2.5+

**Databases:**
- PostgreSQL 13+
- Redis 6+

**Infrastructure:**
- Docker 20.10+
- Docker Compose 1.29+
- Nginx 1.21+

**External Services:**
- OpenRouter API
- SMTP (Gmail, SendGrid)
- Let's Encrypt (SSL)

**Development:**
- pytest (testing)
- Alembic (migrations)
- Black (formatting)
- Ruff (linting)

---

[← User Guide](../user-guide/notifications.md) | [Component Details →](components.md)
