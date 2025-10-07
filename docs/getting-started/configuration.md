# Configuration Guide

This guide covers all configuration options for BookGen.

## 📋 Configuration Overview

BookGen uses environment variables for configuration, stored in a `.env` file. This approach:

- ✅ Keeps secrets out of version control
- ✅ Makes deployment easy across environments
- ✅ Follows [12-factor app](https://12factor.net/) principles
- ✅ Simplifies Docker deployment

## 🔧 Environment File Setup

### Creating Your Configuration

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

### Configuration File Location

- **Development**: `/home/runner/work/bookgen/bookgen/.env`
- **Docker**: Mounted at `/app/.env` in containers
- **Production**: `/opt/bookgen/.env` (recommended)

---

## 🔑 Required Configuration

### OpenRouter API (Required)

```bash
# Your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Base URL for OpenRouter API
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# AI model to use (free tier available)
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free

# Site information (for OpenRouter rankings)
SITE_URL=https://bookgen.ai
SITE_TITLE=BookGen AI System
```

**Getting an API Key:**
1. Visit [https://openrouter.ai](https://openrouter.ai)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new key
5. Copy and paste into `.env`

**Available Models:**
- `qwen/qwen2.5-vl-72b-instruct:free` - Free, good quality
- `anthropic/claude-3.5-sonnet` - Premium, best quality
- `openai/gpt-4-turbo-preview` - Premium, great quality
- `google/gemini-pro` - Good quality

---

## ⚙️ System Configuration

### Biography Generation Settings

```bash
# Number of chapters per biography
CHAPTERS_NUMBER=20

# Total words in the biography
TOTAL_WORDS=51000

# Words per chapter (calculated: TOTAL_WORDS / CHAPTERS_NUMBER)
WORDS_PER_CHAPTER=2550

# Tolerance for word count validation (±5%)
VALIDATION_TOLERANCE=0.05
```

**Recommendations:**
- **Short biography**: 10 chapters, 25,000 words
- **Standard biography**: 20 chapters, 50,000 words
- **Comprehensive biography**: 30 chapters, 75,000 words

### Quality Control Settings

```bash
# Source validation
MIN_SOURCES=40              # Minimum valid sources required
MAX_SOURCES=60              # Maximum sources to process
URL_VALIDATION_TIMEOUT=30   # Seconds to wait for URL response

# Content quality
COHERENCE_THRESHOLD=0.8     # Minimum coherence score (0-1)
RELEVANCE_THRESHOLD=0.7     # Minimum relevance score (0-1)
CONTENT_MATCH_THRESHOLD=0.6 # Content-source match threshold
```

### Performance Settings

```bash
# Concurrency limits
MAX_CONCURRENT_JOBS=3       # Maximum simultaneous biography jobs
MAX_CONCURRENT_REQUESTS=5   # Maximum concurrent API requests

# Timeouts
CHECKPOINT_INTERVAL=300     # Save checkpoint every N seconds
RETRY_ATTEMPTS=3            # Retry failed operations
TIMEOUT_PER_PHASE=3600      # Maximum seconds per generation phase

# Batch processing
BATCH_SIZE_CHAPTERS=5              # Chapters to generate in parallel
BATCH_SIZE_SPECIAL_SECTIONS=3      # Special sections in parallel
```

---

## 🗄️ Database Configuration

### PostgreSQL Settings

```bash
# Full database URL (recommended)
DATABASE_URL=postgresql://user:password@host:port/database

# Or individual components
DB_HOST=localhost
DB_PORT=5432
DB_USER=bookgen
DB_PASSWORD=secure_password_here
DB_NAME=bookgen

# Connection pooling
DB_POOL_SIZE=5              # Connection pool size
DB_MAX_OVERFLOW=10          # Maximum overflow connections
DB_POOL_TIMEOUT=30          # Pool timeout in seconds
```

**Production Recommendations:**
- Use strong passwords (20+ characters)
- Enable SSL: `DATABASE_URL=postgresql://...?sslmode=require`
- Tune pool size based on worker count
- Regular backups (automated via deployment scripts)

---

## 🔴 Redis Configuration

### Redis Settings

```bash
# Redis connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Redis password (if enabled)
REDIS_PASSWORD=your_redis_password

# Connection pool
REDIS_MAX_CONNECTIONS=50

# Task queue settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

**Production Recommendations:**
- Enable password authentication
- Use dedicated Redis instance
- Enable persistence (RDB + AOF)
- Monitor memory usage

---

## 📧 Notification Configuration

### Email Notifications (Optional)

```bash
# Enable/disable email notifications
ENABLE_EMAIL_NOTIFICATIONS=true

# SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@bookgen.ai
SMTP_USE_TLS=true

# Email recipients
ADMIN_EMAILS=admin@example.com,support@example.com
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Use app password in `SMTP_PASSWORD`

### Webhook Notifications (Optional)

```bash
# Enable/disable webhooks
ENABLE_WEBHOOKS=true

# Default webhook URL
WEBHOOK_URL=https://your-app.com/webhook

# Webhook authentication
WEBHOOK_SECRET=your-webhook-secret-key
WEBHOOK_TIMEOUT=30

# Retry settings
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=5
```

**Webhook Payload Example:**
```json
{
  "event": "biography.completed",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "character": "Albert Einstein",
  "status": "completed",
  "timestamp": "2025-01-07T12:00:00Z"
}
```

### WebSocket Settings

```bash
# WebSocket configuration
WS_MAX_CONNECTIONS=100        # Maximum concurrent connections
WS_HEARTBEAT_INTERVAL=30      # Heartbeat interval in seconds
WS_MESSAGE_QUEUE_SIZE=1000    # Maximum queued messages
```

---

## 🔒 Security Configuration

### API Security

```bash
# Secret key for JWT tokens (generate with: openssl rand -hex 32)
SECRET_KEY=your-very-secret-key-here

# CORS settings
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Rate limiting
RATE_LIMIT_PER_MINUTE=60      # Requests per minute per IP
RATE_LIMIT_BURST=10           # Burst allowance

# API keys (optional)
API_KEY_REQUIRED=false         # Require API key for requests
VALID_API_KEYS=key1,key2,key3  # Comma-separated valid keys
```

### SSL/TLS Settings (Production)

```bash
# SSL certificate paths
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem

# Force HTTPS
FORCE_HTTPS=true
```

---

## 📁 File Storage Configuration

### Output Settings

```bash
# Output directory for generated files
OUTPUT_DIRECTORY=docx

# Word template for export
WORD_TEMPLATE=wordTemplate/reference.docx

# File naming convention
OUTPUT_FILENAME_PATTERN=La biografia de {character}.docx

# Temporary files
TEMP_DIRECTORY=/tmp/bookgen
CLEANUP_TEMP_FILES=true
```

### Storage Limits

```bash
# Maximum file sizes
MAX_UPLOAD_SIZE=10485760      # 10 MB in bytes
MAX_BIOGRAPHY_SIZE=52428800   # 50 MB in bytes

# Storage cleanup
AUTO_CLEANUP_DAYS=30          # Delete old files after N days
```

---

## 🔍 Advanced Source Validation

### Content Analysis Settings

```bash
# Enable advanced validation features
ENABLE_CONTENT_ANALYSIS=true
ENABLE_ACADEMIC_VALIDATION=true
ENABLE_PLAGIARISM_CHECK=true

# Validation thresholds
ACADEMIC_FORMAT_THRESHOLD=0.75
MAX_REDIRECTS=3

# Content extraction
MIN_CONTENT_LENGTH=500        # Minimum words per source
MAX_CONTENT_LENGTH=50000      # Maximum words per source
```

---

## 🌍 Environment-Specific Configuration

### Development Environment

```bash
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Development helpers
HOT_RELOAD=true
SKIP_MIGRATIONS=false
MOCK_EXTERNAL_APIS=false
```

### Staging Environment

```bash
ENV=staging
DEBUG=false
LOG_LEVEL=INFO

# Staging settings
USE_TEST_API_KEYS=true
LIMIT_GENERATION_JOBS=true
```

### Production Environment

```bash
ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Production settings
ENABLE_MONITORING=true
ENABLE_METRICS=true
REQUIRE_HTTPS=true
```

---

## 📊 Logging Configuration

### Log Settings

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log format
LOG_FORMAT=json               # json or text

# Log destinations
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/bookgen/app.log
LOG_TO_CONSOLE=true
LOG_TO_SYSLOG=false

# Log rotation
LOG_MAX_BYTES=10485760        # 10 MB
LOG_BACKUP_COUNT=5
```

---

## 🧪 Testing Configuration

### Test Settings

```bash
# Test database
TEST_DATABASE_URL=postgresql://bookgen:bookgen@localhost/bookgen_test

# Test Redis
TEST_REDIS_URL=redis://localhost:6379/15

# Test behavior
RUN_INTEGRATION_TESTS=true
RUN_SLOW_TESTS=false
MOCK_OPENROUTER_API=true
```

---

## 📝 Configuration Templates

### Minimal Development Setup

```bash
# .env.development
OPENROUTER_API_KEY=your-key-here
ENV=development
DEBUG=true
```

### Production Setup

```bash
# .env.production
OPENROUTER_API_KEY=your-key-here
ENV=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost/bookgen
REDIS_HOST=localhost
SECRET_KEY=generate-random-key
CORS_ORIGINS=https://yourdomain.com
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=app-password
```

---

## ✅ Configuration Validation

### Validate Your Configuration

```bash
# Run configuration validator
./validate-config.sh

# Or manually with Python
python -c "from src.config import settings; print('✅ Config valid')"
```

### Required Variables Checklist

- [ ] `OPENROUTER_API_KEY` is set and valid
- [ ] `DATABASE_URL` is correct and accessible
- [ ] `REDIS_HOST` and `REDIS_PORT` are reachable
- [ ] `SECRET_KEY` is set (production only)
- [ ] File paths exist and are writable
- [ ] SMTP settings are correct (if email enabled)

---

## 🔄 Updating Configuration

### Reloading Configuration

**Docker:**
```bash
# Restart services to apply changes
docker-compose restart api worker
```

**Manual:**
```bash
# Restart API server (Ctrl+C and restart uvicorn)
# Restart Celery worker (Ctrl+C and restart celery)
```

### Configuration Hot Reload

Some settings support hot reload without restart:
- Log level
- Rate limits
- Feature flags

Most settings require service restart:
- Database connection
- Redis connection
- API keys
- Model selection

---

## 🆘 Troubleshooting

### Common Configuration Issues

**Issue**: API key invalid
```bash
# Verify key format
echo $OPENROUTER_API_KEY | grep "^sk-or-v1-"

# Test API key
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models
```

**Issue**: Database connection failed
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Check database is running
sudo systemctl status postgresql
```

**Issue**: Redis connection error
```bash
# Test Redis connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# Check Redis is running
sudo systemctl status redis-server
```

---

## 📚 Next Steps

- **[Quick Start Guide](quick-start.md)** - Create your first biography
- **[API Documentation](../api/overview.md)** - Learn the API
- **[Deployment Guide](../operations/deployment.md)** - Deploy to production

---

[← Installation Guide](installation.md) | [Quick Start Guide →](quick-start.md)
