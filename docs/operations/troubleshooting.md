# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with BookGen.

## 🔍 Quick Diagnostics

### System Health Check

Run this command first for any issue:

```bash
# If using Docker
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status

# Check all services
docker-compose logs --tail=50
```

**Expected Healthy Output:**
```
NAME                STATUS    PORTS
bookgen-api         Up        0.0.0.0:8000->8000/tcp
bookgen-worker      Up
bookgen-db          Up        5432/tcp
bookgen-redis       Up        6379/tcp
```

---

## 🐛 Common Issues

### Issue: API Not Responding

**Symptoms:**
- `curl: (7) Failed to connect to localhost port 8000`
- Web browser shows "Connection refused"
- API docs page won't load

**Diagnosis:**
```bash
# Check if API container is running
docker ps | grep bookgen-api

# Check API logs
docker logs bookgen-api --tail=100

# Check port binding
netstat -tlnp | grep 8000
```

**Solutions:**

**Solution 1: API container stopped**
```bash
# Restart API service
docker-compose restart api

# Or rebuild if needed
docker-compose up -d --build api
```

**Solution 2: Port already in use**
```bash
# Find process using port 8000
sudo lsof -i :8000
sudo kill -9 <PID>

# Or change port in infrastructure/docker-compose.yml
# Then restart
docker-compose down
docker-compose up -d
```

**Solution 3: Configuration error**
```bash
# Check environment variables
docker exec bookgen-api env | grep OPENROUTER

# Verify .env file exists and is valid
cat .env | grep OPENROUTER_API_KEY

# Restart with fresh config
docker-compose down
docker-compose up -d
```

---

### Issue: Worker Not Processing Jobs

**Symptoms:**
- Jobs stay in "pending" status
- No progress updates
- Worker logs show no activity

**Diagnosis:**
```bash
# Check worker status
docker ps | grep worker

# Check worker logs
docker logs bookgen-worker --tail=50

# Check Redis connection
docker exec bookgen-redis redis-cli ping
# Expected: PONG

# Check Celery queue
docker exec bookgen-worker celery -A src.worker inspect active
```

**Solutions:**

**Solution 1: Worker not running**
```bash
# Restart worker
docker-compose restart worker

# Check it started successfully
docker logs bookgen-worker --tail=20
```

**Solution 2: Redis connection issue**
```bash
# Check Redis is running
docker ps | grep redis

# Restart Redis
docker-compose restart redis

# Restart worker to reconnect
docker-compose restart worker
```

**Solution 3: Worker crashed with error**
```bash
# Check logs for error
docker logs bookgen-worker | grep ERROR

# Common fixes:
# - Missing OPENROUTER_API_KEY
# - Database connection issue
# - Python dependency issue

# Rebuild worker container
docker-compose build worker
docker-compose up -d worker
```

---

### Issue: Database Connection Failed

**Symptoms:**
- Error: "could not connect to server"
- Error: "FATAL: database 'bookgen' does not exist"
- API fails to start

**Diagnosis:**
```bash
# Check database container
docker ps | grep bookgen-db

# Check database logs
docker logs bookgen-db --tail=50

# Try to connect manually
docker exec -it bookgen-db psql -U bookgen -d bookgen
```

**Solutions:**

**Solution 1: Database not running**
```bash
# Start database
docker-compose up -d db

# Wait for database to be ready
sleep 10

# Restart API and worker
docker-compose restart api worker
```

**Solution 2: Database not initialized**
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Verify tables exist
docker exec -it bookgen-db psql -U bookgen -d bookgen -c "\dt"
```

**Solution 3: Wrong credentials**
```bash
# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Should match infrastructure/docker-compose.yml database settings
# Example: postgresql://bookgen:bookgen@db:5432/bookgen

# Fix and restart
docker-compose down
docker-compose up -d
```

---

### Issue: Source Validation Failing

**Symptoms:**
- Error: "Insufficient valid sources"
- Most sources marked as invalid
- Generation fails at source validation phase

**Diagnosis:**
```bash
# Test source URLs manually
curl -I https://your-source-url.com

# Check validation settings
cat .env | grep -E "(MIN_SOURCES|MAX_SOURCES|URL_VALIDATION_TIMEOUT)"

# Check worker logs for validation errors
docker logs bookgen-worker | grep "source validation"
```

**Solutions:**

**Solution 1: Inaccessible URLs**
```bash
# Verify URLs are publicly accessible
# Remove paywalled or login-required sources
# Use stable, permanent URLs (avoid URL shorteners)

# Test each source:
for url in $(cat sources.txt); do
  echo "Testing: $url"
  curl -I -L --max-time 10 "$url" && echo "✅" || echo "❌"
done
```

**Solution 2: Timeout too low**
```bash
# Increase timeout in .env
URL_VALIDATION_TIMEOUT=60

# Restart services
docker-compose restart
```

**Solution 3: Not enough sources**
```bash
# Check minimum required
echo $MIN_SOURCES  # Default: 40

# Provide more sources (50-60 recommended)
# Or temporarily lower threshold for testing:
MIN_SOURCES=30  # In .env

# Restart
docker-compose restart
```

---

### Issue: Generation Takes Too Long

**Symptoms:**
- Job running for 6+ hours
- Stuck on one chapter
- No progress updates

**Diagnosis:**
```bash
# Check job status
curl http://localhost:8000/api/v1/biographies/<job_id>

# Check current progress
docker logs bookgen-worker --tail=50 | grep "Progress"

# Check system resources
docker stats
```

**Solutions:**

**Solution 1: API rate limiting**
```bash
# Check OpenRouter rate limits
# Free tier has stricter limits

# Option A: Wait for rate limit reset
# Option B: Upgrade to paid tier
# Option C: Use different model

# Update .env:
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free
# Or premium model if paid account
```

**Solution 2: System resource constraints**
```bash
# Check CPU and memory
docker stats

# If near limits, reduce concurrency:
# Update .env:
MAX_CONCURRENT_REQUESTS=2
BATCH_SIZE_CHAPTERS=2

# Restart
docker-compose restart
```

**Solution 3: Stuck in infinite loop**
```bash
# Check logs for repeating errors
docker logs bookgen-worker | tail -100

# If truly stuck, restart worker
docker-compose restart worker

# Job will resume from last checkpoint
```

---

### Issue: Word Export Fails

**Symptoms:**
- Error: "Failed to export to Word"
- .docx file not created
- Markdown file exists but Word doesn't

**Diagnosis:**
```bash
# Check if Pandoc is installed
docker exec bookgen-api which pandoc

# Check Word template exists
docker exec bookgen-api ls -la wordTemplate/reference.docx

# Check output directory permissions
docker exec bookgen-api ls -ld docx/
```

**Solutions:**

**Solution 1: Pandoc not installed**
```bash
# Rebuild container with Pandoc
docker-compose build api
docker-compose up -d api
```

**Solution 2: Template missing**
```bash
# Verify template exists locally
ls -la wordTemplate/reference.docx

# If missing, create from Word:
# 1. Open Word
# 2. Create document with desired styles
# 3. Save as reference.docx in wordTemplate/

# Restart to mount volume
docker-compose restart api
```

**Solution 3: Permission issue**
```bash
# Fix permissions
sudo chown -R $USER:$USER docx/

# Verify writable
docker exec bookgen-api touch docx/test.txt
docker exec bookgen-api rm docx/test.txt
```

---

### Issue: WebSocket Connection Fails

**Symptoms:**
- WebSocket connection refused
- Error: "WebSocket is closed before the connection is established"
- No real-time updates

**Diagnosis:**
```bash
# Check WebSocket endpoint
curl http://localhost:8000/ws/notifications

# Check API logs for WebSocket errors
docker logs bookgen-api | grep -i websocket

# Test with wscat if installed
npm install -g wscat
wscat -c ws://localhost:8000/ws/notifications?job_id=<job_id>
```

**Solutions:**

**Solution 1: Wrong URL scheme**
```bash
# Use ws:// not http://
# Correct: ws://localhost:8000/ws/notifications
# Wrong: http://localhost:8000/ws/notifications

# In production with SSL, use wss://
# Correct: wss://yourdomain.com/ws/notifications
```

**Solution 2: CORS issue**
```bash
# Check CORS settings in .env
cat .env | grep CORS_ORIGINS

# Add your frontend origin
CORS_ORIGINS=http://localhost:3000,ws://localhost:8000

# Restart API
docker-compose restart api
```

**Solution 3: Nginx proxy issue (production)**
```bash
# Add WebSocket support to nginx config
# In /etc/nginx/sites-available/bookgen:

location /ws/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

# Reload nginx
sudo nginx -t && sudo nginx -s reload
```

---

### Issue: High Memory Usage

**Symptoms:**
- Docker containers using excessive RAM
- System becomes slow
- OOM (Out of Memory) errors

**Diagnosis:**
```bash
# Check memory usage
docker stats

# Check system memory
free -h

# Check logs for OOM
dmesg | grep -i oom
```

**Solutions:**

**Solution 1: Reduce batch sizes**
```bash
# Update .env
BATCH_SIZE_CHAPTERS=2
BATCH_SIZE_SPECIAL_SECTIONS=2
MAX_CONCURRENT_JOBS=1

# Restart
docker-compose restart
```

**Solution 2: Limit Docker memory**
```bash
# In infrastructure/docker-compose.yml, add:
services:
  api:
    mem_limit: 2g
  worker:
    mem_limit: 3g

# Restart
docker-compose down
docker-compose up -d
```

**Solution 3: Clean up old data**
```bash
# Remove old biographies
find bios/ -mtime +30 -type d -exec rm -rf {} +
find docx/ -mtime +30 -type f -delete

# Clean Docker
docker system prune -a --volumes
```

---

## 🔧 Advanced Troubleshooting

### Enable Debug Logging

```bash
# Update .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart

# Watch debug logs
docker-compose logs -f
```

### Inspect Database

```bash
# Connect to database
docker exec -it bookgen-db psql -U bookgen -d bookgen

# List all jobs
SELECT job_id, character, status, created_at FROM biography_jobs ORDER BY created_at DESC LIMIT 10;

# Check specific job
SELECT * FROM biography_jobs WHERE job_id = 'your-job-id';

# Exit
\q
```

### Inspect Redis Queue

```bash
# Connect to Redis
docker exec -it bookgen-redis redis-cli

# List all keys
KEYS *

# Check queue length
LLEN celery

# View queue contents
LRANGE celery 0 -1

# Exit
exit
```

### Reset Everything

```bash
# ⚠️ WARNING: This deletes all data!

# Stop all services
docker-compose down -v

# Remove all data
rm -rf bios/* docx/*

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

---

## 📊 Diagnostic Commands Summary

### Quick Health Check
```bash
./verify-vps-deployment.sh  # Automated check
```

### Service Status
```bash
docker-compose ps           # Container status
docker-compose logs         # Recent logs
docker stats                # Resource usage
```

### API Status
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
curl http://localhost:8000/api/v1/metrics
```

### Database
```bash
docker exec bookgen-db pg_isready
docker exec -it bookgen-db psql -U bookgen -d bookgen
```

### Redis
```bash
docker exec bookgen-redis redis-cli ping
docker exec bookgen-redis redis-cli INFO
```

### Worker
```bash
docker exec bookgen-worker celery -A src.worker inspect active
docker exec bookgen-worker celery -A src.worker inspect stats
```

---

## 🆘 Getting Help

If you can't resolve the issue:

1. **Gather Information:**
   ```bash
   # Save logs
   docker-compose logs > debug-logs.txt
   
   # Save configuration (remove sensitive data!)
   cat .env | grep -v "API_KEY\|PASSWORD" > debug-config.txt
   
   # Save system info
   docker version > debug-system.txt
   docker-compose version >> debug-system.txt
   ```

2. **Search Documentation:**
   - Check [User Guide](../user-guide/)
   - Review [API Documentation](../api/)
   - See [Emergency Procedures](../emergency/)

3. **Report Issue:**
   - Create GitHub issue: https://github.com/JPMarichal/bookgen/issues
   - Include logs and configuration
   - Describe steps to reproduce

4. **Emergency Support:**
   - See [Incident Response](../emergency/incident-response.md)
   - Contact system administrator
   - Check service status page

---

[← Operations Overview](monitoring.md) | [Runbooks →](runbooks.md)
