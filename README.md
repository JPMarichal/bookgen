# 📚 BookGen AI - Automated Biography Generation System

> **AI-powered biography generation system that creates comprehensive, well-researched biographies in minutes, not months.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/JPMarichal/bookgen)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start (< 5 minutes)

Get BookGen running in under 5 minutes:

```bash
# Clone the repository
git clone https://github.com/JPMarichal/bookgen.git
cd bookgen

# Start with Docker (Recommended)
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
```

**🎉 That's it!** Your BookGen instance is now running at `http://localhost:8000`

👉 **Next Steps:**
- View [Interactive API Docs](http://localhost:8000/docs)
- Read the [Full Setup Guide](docs/getting-started/installation.md)
- Check out [Usage Examples](docs/examples/)

---

## 📖 What is BookGen?

BookGen is a production-ready system that automates the entire biography writing process:

- **🤖 AI-Powered Generation**: Uses state-of-the-art LLMs via OpenRouter
- **🎯 Three Generation Modes**: Automatic, Hybrid, or Manual source discovery
- **📊 Quality Assured**: Advanced validation for sources, length, and content quality
- **⚡ Fast & Scalable**: Generates 20-chapter biographies (50,000+ words) in hours
- **🔄 Fully Automated**: From character selection to Word document export
- **📧 Smart Notifications**: Real-time updates via WebSocket, Webhook, and Email
- **🔒 Production Ready**: Containerized, monitored, and deployment-ready

### Three Ways to Generate Biographies

BookGen offers flexibility in how you provide sources:

| Mode | Description | Best For |
|------|-------------|----------|
| **🤖 Automatic** | AI generates all sources automatically | Quick generation, unfamiliar subjects |
| **🔗 Hybrid** | Mix of your sources + AI completion | Key sources + auto-completion to 40-60 |
| **📝 Manual** | You provide all sources | Complete control, specialized sources |

**Quick Example - Automatic Mode:**
```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Marie Curie",
    "mode": "automatic"
  }'
```

→ See [Quick Start Guide](docs/getting-started/quick-start.md) and [Auto-Generation Guide](docs/guides/AUTO_GENERATION_GUIDE.md) for details

### Key Features

| Feature | Description |
|---------|-------------|
| **Automated Source Discovery** | AI-powered search across Wikipedia, academic databases, and archives |
| **Smart Validation** | Relevance scoring, credibility assessment, and accessibility checks |
| **Structured Content** | 20 chapters + prologue, epilogue, glossary, timeline |
| **Quality Control** | Length validation, coherence checking, plagiarism detection |
| **Multiple Formats** | Markdown and Word (.docx) export with professional formatting |
| **Task Queue** | Celery-based job queue with Redis backend |
| **Real-time Updates** | WebSocket support for live progress tracking |
| **REST API** | Full FastAPI implementation with OpenAPI docs |

---

## 📚 Documentation

### 🎯 Getting Started
- **[Installation Guide](docs/getting-started/installation.md)** - Complete setup instructions
- **[Configuration](docs/getting-started/configuration.md)** - Environment variables and settings
- **[Quick Start Tutorial](docs/getting-started/quick-start.md)** - Generate your first biography
- **[Automatic Generation Guide](docs/guides/AUTO_GENERATION_GUIDE.md)** - Using AI-powered source discovery

### 🔌 API Documentation
- **[API Overview](docs/api/overview.md)** - REST API introduction
- **[Endpoints Reference](docs/api/endpoints.md)** - Complete endpoint documentation
- **[WebSocket Guide](docs/api/websocket.md)** - Real-time communication
- **[API Examples](docs/examples/automatic_generation_examples.py)** - Practical code examples

### 👥 User Guide
- **[Creating Biographies](docs/user-guide/creating-biographies.md)** - Step-by-step guide
- **[Managing Sources](docs/user-guide/managing-sources.md)** - Source validation workflow
- **[Understanding Notifications](docs/user-guide/notifications.md)** - How to interpret updates
- **[Export Options](docs/user-guide/export-formats.md)** - Document generation

### 🏗️ Architecture
- **[System Architecture](docs/architecture/system-overview.md)** - High-level design
- **[Component Guide](docs/architecture/components.md)** - Detailed component breakdown
- **[Data Flow](docs/architecture/data-flow.md)** - How data moves through the system
- **[Technology Stack](docs/architecture/tech-stack.md)** - Technologies used

### 🔧 Operations
- **[Deployment Guide](docs/operations/deployment.md)** - Production deployment
- **[Monitoring](docs/operations/monitoring.md)** - Health checks and metrics
- **[Troubleshooting](docs/operations/troubleshooting.md)** - Common issues and solutions
- **[Runbooks](docs/operations/runbooks.md)** - Operational procedures

### 🚨 Emergency Procedures
- **[Incident Response](docs/emergency/incident-response.md)** - Emergency procedures
- **[Recovery Procedures](docs/emergency/recovery.md)** - Disaster recovery
- **[Rollback Guide](docs/emergency/rollback.md)** - How to rollback deployments

---

## 🎯 Use Cases

### Academic Research
Generate comprehensive biographical research documents with cited sources.

### Content Creation
Create biography drafts for books, articles, or educational materials.

### Historical Documentation
Systematically document historical figures with structured narratives.

### Publishing Workflow
Automate the first draft phase of biography writing projects.

---

## 🏃 Running BookGen

### Using Docker (Recommended)

```bash
# Production mode
docker-compose -f docker-compose.prod.yml up -d

# Development mode
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn src.main:app --reload

# Start the Celery worker (in another terminal)
celery -A src.worker worker --loglevel=info
```

---

## 🔧 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        BookGen System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   FastAPI    │───▶│    Celery    │───▶│   OpenRouter │  │
│  │   REST API   │    │  Task Queue  │    │   LLM API    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                               │
│         │                    │                               │
│  ┌──────▼──────┐    ┌───────▼────────┐    ┌──────────────┐│
│  │  WebSocket  │    │  State Machine │    │  PostgreSQL  ││
│  │ Notifications│    │    Engine      │    │   Database   ││
│  └─────────────┘    └────────────────┘    └──────────────┘│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **FastAPI REST API**: Entry point for all requests
2. **Celery Task Queue**: Asynchronous job processing
3. **State Machine Engine**: Orchestrates biography generation workflow
4. **OpenRouter Client**: LLM integration for content generation
5. **PostgreSQL Database**: Persistent storage for jobs and biographies
6. **WebSocket Server**: Real-time progress updates
7. **Notification Service**: Multi-channel alerts (Email, Webhook, WebSocket)

---

## 🌐 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check for monitoring |
| `GET` | `/api/v1/status` | Detailed system status |
| `POST` | `/api/v1/biographies` | Create new biography job |
| `GET` | `/api/v1/biographies/{id}` | Get biography details |
| `POST` | `/api/v1/sources/validate` | Validate source URLs |
| `GET` | `/api/v1/metrics` | System metrics |
| `WS` | `/ws/notifications` | WebSocket for real-time updates |

👉 **Full API documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📊 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ / macOS / Windows with WSL2
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 10 GB free space
- **Docker**: 20.10+ (if using Docker)
- **Python**: 3.9+ (if running manually)

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB SSD
- **PostgreSQL**: 13+
- **Redis**: 6+

---

## 🔑 Configuration

### Essential Environment Variables

```bash
# OpenRouter API (Required)
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free

# System Configuration
CHAPTERS_NUMBER=20
TOTAL_WORDS=51000
WORDS_PER_CHAPTER=2550

# Database (if not using Docker defaults)
DATABASE_URL=postgresql://user:pass@localhost/bookgen

# Redis (if not using Docker defaults)
REDIS_HOST=localhost
REDIS_PORT=6379
```

📖 See [Configuration Guide](docs/getting-started/configuration.md) for all options.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only

# Run fast tests only
pytest -m fast
```

**Test Coverage**: 228 tests passing with 85%+ coverage

---

## 📝 Example Usage

### Generate a Biography

```python
import requests

# Create a biography job
response = requests.post(
    "http://localhost:8000/api/v1/biographies",
    json={
        "character": "Albert Einstein",
        "sources": [
            "https://en.wikipedia.org/wiki/Albert_Einstein",
            "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
            # ... 38 more sources
        ]
    }
)

job = response.json()
print(f"Job created: {job['job_id']}")

# Monitor progress via WebSocket
import websocket

ws = websocket.WebSocket()
ws.connect(f"ws://localhost:8000/ws/notifications?job_id={job['job_id']}")

while True:
    message = ws.recv()
    print(f"Progress: {message}")
```

📚 More examples in [docs/examples/](docs/examples/)

---

## 🚀 Production Deployment

### Quick Deploy to VPS

```bash
# Download deployment script
curl -fsSL https://raw.githubusercontent.com/JPMarichal/bookgen/main/deploy-vps.sh -o deploy-vps.sh

# Make executable and run
chmod +x deploy-vps.sh
sudo ./deploy-vps.sh

# Verify deployment
./verify-vps-deployment.sh
```

📖 See [Deployment Guide](docs/operations/deployment.md) for complete instructions.

### What's Included

- ✅ Docker containerization
- ✅ Nginx reverse proxy
- ✅ SSL/TLS certificates (Let's Encrypt)
- ✅ Systemd service management
- ✅ Automated backups
- ✅ Log rotation
- ✅ Monitoring and health checks
- ✅ Firewall configuration (UFW)
- ✅ Fail2ban protection

---

## 📈 Monitoring & Health

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status

# System metrics
curl http://localhost:8000/api/v1/metrics
```

### Expected Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-07T12:00:00Z",
  "environment": "production",
  "debug": false
}
```

📖 See [Monitoring Guide](docs/operations/monitoring.md) for advanced monitoring.

---

## 🔧 Troubleshooting

### Common Issues

#### API Not Responding
```bash
# Check if container is running
docker ps

# Check logs
docker logs bookgen-api

# Restart service
docker-compose restart api
```

#### Worker Not Processing Jobs
```bash
# Check Celery worker status
docker logs bookgen-worker

# Check Redis connection
docker exec bookgen-redis redis-cli ping
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker logs bookgen-db

# Test connection
docker exec bookgen-db psql -U bookgen -c "SELECT 1"
```

📖 Complete troubleshooting guide: [docs/operations/troubleshooting.md](docs/operations/troubleshooting.md)

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/bookgen.git
cd bookgen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Start development server
uvicorn src.main:app --reload
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenRouter** - LLM API provider
- **FastAPI** - Modern web framework
- **Celery** - Distributed task queue
- **PostgreSQL** - Robust database
- **Docker** - Containerization platform

---

## 📞 Support

### Documentation
- 📚 [Full Documentation](docs/)
- 🔌 [API Reference](http://localhost:8000/docs)
- 📖 [User Guide](docs/user-guide/)

### Issues & Questions
- 🐛 [Report a Bug](https://github.com/JPMarichal/bookgen/issues/new?template=bug_report.md)
- 💡 [Request a Feature](https://github.com/JPMarichal/bookgen/issues/new?template=feature_request.md)
- ❓ [Ask a Question](https://github.com/JPMarichal/bookgen/discussions)

### Emergency Support
- 🚨 [Emergency Procedures](docs/emergency/incident-response.md)
- 🔥 [Critical Issues Runbook](docs/operations/runbooks.md#critical-issues)

---

## 🗺️ Roadmap

### Current Version (v1.0.0)
- ✅ Core biography generation
- ✅ Source validation
- ✅ REST API
- ✅ WebSocket notifications
- ✅ Docker deployment

### Planned Features
- [ ] Multi-language support
- [ ] Advanced AI models (GPT-4, Claude 3)
- [ ] PDF export
- [ ] Collaborative editing
- [ ] API rate limiting tiers
- [ ] Prometheus metrics export
- [ ] Grafana dashboards

---

## 📊 Stats

- **Code**: 15,000+ lines of Python
- **Tests**: 228 automated tests
- **Coverage**: 85%+
- **Docker Images**: Optimized multi-stage builds
- **API Endpoints**: 10+ documented endpoints
- **Documentation**: 50+ pages

---

**Made with ❤️ by the BookGen Team**

⭐ **Star us on GitHub** if you find BookGen useful!
