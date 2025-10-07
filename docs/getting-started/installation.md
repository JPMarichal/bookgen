# Installation Guide

This guide will help you install and set up BookGen on your system.

## 📋 Prerequisites

### System Requirements

- **Operating System**: 
  - Linux (Ubuntu 20.04+ recommended)
  - macOS 10.15+
  - Windows 10+ with WSL2
  
- **Hardware**:
  - **Minimum**: 2 CPU cores, 4 GB RAM, 10 GB disk space
  - **Recommended**: 4+ CPU cores, 8+ GB RAM, 50+ GB SSD

- **Software**:
  - Docker 20.10+ and Docker Compose 1.29+ (recommended)
  - OR Python 3.9+, PostgreSQL 13+, Redis 6+

### API Keys Required

- **OpenRouter API Key** (Required)
  - Sign up at [https://openrouter.ai](https://openrouter.ai)
  - Free tier available
  - Used for AI content generation

## 🚀 Installation Methods

### Method 1: Docker (Recommended)

The fastest and most reliable way to get started.

#### Step 1: Install Docker

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications
```

**Windows:**
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Ensure WSL2 is enabled

#### Step 2: Clone Repository

```bash
git clone https://github.com/JPMarichal/bookgen.git
cd bookgen
```

#### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (add your OpenRouter API key)
nano .env
```

**Required variables in `.env`:**
```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free
```

#### Step 4: Start Services

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### Step 5: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","timestamp":"...","environment":"development","debug":false}

# Access interactive API docs
open http://localhost:8000/docs
```

**🎉 Installation Complete!** Jump to [Quick Start](quick-start.md) to create your first biography.

---

### Method 2: Manual Installation

For development or when Docker is not available.

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Pandoc (for Word export)
sudo apt install -y pandoc
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.9 postgresql redis pandoc
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/JPMarichal/bookgen.git
cd bookgen
```

#### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Configure Database

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE bookgen;
CREATE USER bookgen WITH PASSWORD 'bookgen_password';
GRANT ALL PRIVILEGES ON DATABASE bookgen TO bookgen;
\q
EOF
```

#### Step 5: Configure Redis

```bash
# Start Redis
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping
# Expected output: PONG
```

#### Step 6: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Update these variables in `.env`:**
```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your-api-key-here

# Database Configuration
DATABASE_URL=postgresql://bookgen:bookgen_password@localhost/bookgen

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

#### Step 7: Initialize Database

```bash
# Run database migrations
alembic upgrade head
```

#### Step 8: Start Services

You'll need 2 terminal windows:

**Terminal 1 - API Server:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start Celery worker
celery -A src.worker worker --loglevel=info
```

#### Step 9: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Access interactive API docs
open http://localhost:8000/docs
```

**🎉 Installation Complete!** Jump to [Quick Start](quick-start.md) to create your first biography.

---

## 🔧 Post-Installation Configuration

### Optional: NLTK Data

BookGen uses NLTK for text analysis. Download required data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Optional: Email Notifications

To enable email notifications, add to `.env`:

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

### Optional: Webhook Notifications

To enable webhook notifications, add to `.env`:

```bash
# Webhook Configuration
WEBHOOK_URL=https://your-app.com/webhook
WEBHOOK_SECRET=your-webhook-secret
```

---

## 🧪 Verify Installation

### Run Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status

# System metrics
curl http://localhost:8000/api/v1/metrics
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Container fails to start
```bash
# Check logs
docker-compose logs api

# Common solution: Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

**Problem**: Port 8000 already in use
```bash
# Find process using port
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

### Database Issues

**Problem**: Connection refused
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Verify connection
psql -U bookgen -d bookgen -h localhost
```

**Problem**: Migration fails
```bash
# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head
```

### Redis Issues

**Problem**: Redis connection error
```bash
# Check Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis-server

# Check Redis logs
sudo journalctl -u redis-server
```

### Python Issues

**Problem**: Module not found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: NLTK data missing
```bash
# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 📚 Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Generate your first biography
2. **[Configuration Guide](configuration.md)** - Advanced configuration options
3. **[API Documentation](../api/overview.md)** - Learn the API
4. **[User Guide](../user-guide/creating-biographies.md)** - Complete workflow guide

---

## 🆘 Getting Help

- 📚 [Troubleshooting Guide](../operations/troubleshooting.md)
- 🐛 [Report an Issue](https://github.com/JPMarichal/bookgen/issues)
- 💬 [Community Discussions](https://github.com/JPMarichal/bookgen/discussions)
- 📧 [Contact Support](mailto:support@bookgen.ai)

---

[← Back to README](../../README.md) | [Configuration Guide →](configuration.md)
