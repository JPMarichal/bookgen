# 🐳 Docker Setup Guide - BookGen AI System

This guide covers the complete Docker setup for BookGen, including development and production configurations.

## 📋 Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2.0+ (or docker-compose v1.29+)
- At least 2GB free disk space
- (Production) VPS Ubuntu Server with minimum 4GB RAM

## 🚀 Quick Start - Development

### 1. Clone and Configure

```bash
git clone https://github.com/JPMarichal/bookgen.git
cd bookgen
cp .env.production.example .env  # Or use existing .env
```

### 2. Build and Run

```bash
# Build the Docker image
docker build -t bookgen:latest .

# Or use Docker Compose (recommended)
docker compose up -d
```

### 3. Verify Setup

```bash
# Run automated tests
./test-docker-setup.sh

# Or manually test
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T01:00:09.038453",
  "environment": "development",
  "debug": true
}
```

### 4. Stop Services

```bash
docker compose down
```

## 🏭 Production Deployment (VPS Ubuntu)

### 1. Prepare VPS

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Create directories
sudo mkdir -p /opt/bookgen/{data,output,sources,collections,templates}
sudo mkdir -p /var/log/bookgen

# Clone repository
cd /opt
sudo git clone https://github.com/JPMarichal/bookgen.git
cd bookgen
```

### 2. Configure Environment

```bash
# Copy and edit production environment file
sudo cp .env.production.example .env.production
sudo nano .env.production

# Update these variables:
# - OPENROUTER_API_KEY=your_actual_api_key
# - SITE_URL=https://your-domain.com
# - SECRET_KEY=generate_a_secure_random_key
```

### 3. Deploy with Docker Compose

```bash
# Pull or build image
sudo docker pull ghcr.io/jpmarichal/bookgen:latest
# OR build locally:
sudo docker build -t ghcr.io/jpmarichal/bookgen:latest .

# Start production services
sudo docker compose -f infrastructure/docker-compose.prod.yml up -d

# Check status
sudo docker compose -f infrastructure/docker-compose.prod.yml ps
```

### 4. Setup Auto-Start (systemd)

See `deploy-vps.sh` for automated systemd service configuration, or manually:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

## 📁 File Structure

```
bookgen/
├── infrastructure/Dockerfile                  # Multi-stage production build
├── infrastructure/docker-compose.yml          # Development configuration
├── infrastructure/docker-compose.prod.yml     # Production configuration
├── .dockerignore              # Build context exclusions
├── test-docker-setup.sh       # Automated verification tests
├── DOCKER_OPTIMIZATION.md     # Size optimization notes
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   └── worker.py              # Background worker
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## 🔧 Configuration

### Environment Variables

Key variables in `.env` or `.env.production`:

```bash
# Environment
ENV=development|production
DEBUG=true|false

# OpenRouter API
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free

# Application
CHAPTERS_NUMBER=20
TOTAL_WORDS=51000
WORDS_PER_CHAPTER=2550

# Performance
MAX_CONCURRENT_JOBS=3
WORKER_POOL_SIZE=2
```

### Docker Compose Services

#### Development (`infrastructure/docker-compose.yml`)
- **bookgen-api**: Main FastAPI application (port 8000)
- **bookgen-worker**: Background content generator
- **bookgen-storage**: Persistent data container

#### Production (`infrastructure/docker-compose.prod.yml`)
- **bookgen-api**: Main API with resource limits (4G RAM, 2 CPUs)
- **bookgen-worker-1**: Content generator worker
- **bookgen-worker-2**: Source validator worker

### Volume Mappings

#### Development
```yaml
- ./data:/app/data              # Database and state
- ./docx:/app/docx              # Generated documents
- ./esquemas:/app/esquemas      # Source schemas
- ./colecciones:/app/colecciones # Collections
- ./wordTemplate:/app/wordTemplate # Templates
```

#### Production
```yaml
- /opt/bookgen/data:/app/data
- /opt/bookgen/output:/app/docx
- /opt/bookgen/sources:/app/esquemas
- /opt/bookgen/collections:/app/colecciones
- /opt/bookgen/templates:/app/wordTemplate
- /var/log/bookgen:/app/data/logs
```

## 🏗️ Architecture

### Multi-Stage Build

The infrastructure/Dockerfile uses a 2-stage build process:

1. **Builder Stage**: Compiles dependencies with build tools
   - Base: `python:3.11-slim`
   - Installs: gcc, g++, build-essential
   - Builds: All Python wheels
   - Size optimization: Removes source files, docs, examples

2. **Runtime Stage**: Minimal production image
   - Base: `python:3.11-slim` (125MB)
   - Runtime deps: pandoc, curl, ca-certificates
   - Non-root user: `bookgen`
   - Final size: ~649MB (with all AI/ML dependencies)

### Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # Development: 30s, Production: 60s
  timeout: 10s
  retries: 3
  start_period: 40s  # Development: 40s, Production: 120s
```

### Resource Limits (Production)

```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

## 🧪 Testing

### Run All Tests

```bash
./test-docker-setup.sh
```

### Manual Testing

```bash
# Build test
docker build -t bookgen:test .

# Import test
docker run --rm bookgen:test python -c "import src.main; print('OK')"

# Compose test
docker compose up -d
curl -f http://localhost:8000/health
docker compose down

# Check logs
docker compose logs -f bookgen-api
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs bookgen-api

# Check health status
docker compose ps

# Restart services
docker compose restart
```

### Health Check Failing

```bash
# Test health endpoint manually
docker exec bookgen-api curl localhost:8000/health

# Check if uvicorn is running
docker exec bookgen-api ps aux | grep uvicorn
```

### Port Already in Use

```bash
# Change port in infrastructure/docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

### Out of Memory

```bash
# Check container stats
docker stats

# Reduce worker count in infrastructure/docker-compose.yml
# or increase VPS RAM
```

## 📊 Image Size

Current image size: **649MB**

Size breakdown:
- Python 3.11-slim base: 125MB
- Scientific libraries (numpy, scipy, pandas, sklearn): ~250MB
- Other dependencies: ~150MB
- System packages (pandoc, curl): ~50MB
- Application code: ~5MB
- Optimization overhead: ~69MB

See `DOCKER_OPTIMIZATION.md` for detailed analysis.

## 🔐 Security

- ✅ Non-root user (`bookgen`)
- ✅ Minimal attack surface (slim base)
- ✅ No build tools in runtime image
- ✅ Health checks for reliability
- ✅ Resource limits prevent DoS
- ⚠️ Store secrets in environment files (not in image)

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [BookGen Documentation](./REQUERIMIENTOS_SISTEMA_AUTOMATIZADO.md)

## 🆘 Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Run tests: `./test-docker-setup.sh`
3. Review configuration: `.env` and `infrastructure/docker-compose.yml`
4. Open an issue on GitHub

## 📝 License

See main repository LICENSE file.
