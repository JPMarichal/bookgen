# Operational Runbooks

Standard operating procedures for common BookGen operations.

## 📚 Table of Contents

- [Service Management](#service-management)
- [Deployment Procedures](#deployment-procedures)
- [Backup and Restore](#backup-and-restore)
- [Performance Tuning](#performance-tuning)
- [Security Operations](#security-operations)
- [Monitoring and Alerts](#monitoring-and-alerts)

---

## 🔧 Service Management

### Starting Services

**Docker Deployment:**
```bash
# Start all services
cd /opt/bookgen  # or your installation directory
docker-compose up -d

# Verify all containers started
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50

# Expected: All services showing "Up" status
```

**Systemd Service (Production):**
```bash
# Start service
sudo systemctl start bookgen

# Verify status
sudo systemctl status bookgen

# Enable auto-start on boot
sudo systemctl enable bookgen
```

### Stopping Services

**Docker:**
```bash
# Graceful shutdown
docker-compose stop

# Verify all stopped
docker-compose ps

# Force stop if needed
docker-compose kill
```

**Systemd:**
```bash
# Stop service
sudo systemctl stop bookgen

# Verify stopped
sudo systemctl status bookgen
```

### Restarting Services

**Docker - Individual Services:**
```bash
# Restart API only
docker-compose restart api

# Restart worker only
docker-compose restart worker

# Restart database
docker-compose restart db

# Restart Redis
docker-compose restart redis
```

**Docker - All Services:**
```bash
# Graceful restart
docker-compose restart

# Hard restart (down then up)
docker-compose down
docker-compose up -d
```

**Systemd:**
```bash
# Restart service
sudo systemctl restart bookgen

# Reload configuration without restart
sudo systemctl reload bookgen
```

### Checking Service Status

**Docker:**
```bash
# Container status
docker-compose ps

# Detailed container info
docker inspect bookgen-api

# Resource usage
docker stats --no-stream
```

**Systemd:**
```bash
# Service status
sudo systemctl status bookgen

# Recent logs
sudo journalctl -u bookgen -n 50

# Follow logs
sudo journalctl -u bookgen -f
```

---

## 🚀 Deployment Procedures

### Standard Deployment

**Pre-deployment Checklist:**
- [ ] Backup current database
- [ ] Review changes in changelog
- [ ] Test in staging environment
- [ ] Notify users of maintenance window
- [ ] Verify rollback plan ready

**Deployment Steps:**

1. **Pull Latest Code:**
   ```bash
   cd /opt/bookgen
   git fetch origin
   git checkout main
   git pull origin main
   ```

2. **Backup Database:**
   ```bash
   # Run backup script
   ./scripts/backup_database.sh
   
   # Verify backup created
   ls -lh /opt/bookgen/backups/ | head -1
   ```

3. **Update Dependencies:**
   ```bash
   # Rebuild Docker images with latest dependencies
   docker-compose build --no-cache
   ```

4. **Run Database Migrations:**
   ```bash
   # Apply migrations
   docker-compose run --rm api alembic upgrade head
   
   # Verify migration success
   docker-compose run --rm api alembic current
   ```

5. **Deploy New Version:**
   ```bash
   # Stop services
   docker-compose down
   
   # Start with new images
   docker-compose up -d
   
   # Wait for services to be ready
   sleep 30
   ```

6. **Verify Deployment:**
   ```bash
   # Run verification script
   ./verify-vps-deployment.sh
   
   # Manual checks
   curl http://localhost:8000/health
   curl http://localhost:8000/api/v1/status
   ```

7. **Monitor Logs:**
   ```bash
   # Watch for errors
   docker-compose logs -f --tail=100
   ```

**Post-deployment:**
- [ ] Verify health checks passing
- [ ] Test critical workflows
- [ ] Monitor error rates
- [ ] Update documentation if needed
- [ ] Notify users deployment complete

### Rollback Procedure

**If deployment fails:**

1. **Stop Failed Deployment:**
   ```bash
   docker-compose down
   ```

2. **Revert to Previous Version:**
   ```bash
   # Get previous commit hash
   git log --oneline -5
   
   # Checkout previous version
   git checkout <previous-commit-hash>
   ```

3. **Restore Database (if migrations applied):**
   ```bash
   # Restore from backup
   ./scripts/restore_database.sh /opt/bookgen/backups/latest.sql
   ```

4. **Start Previous Version:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

5. **Verify Rollback:**
   ```bash
   curl http://localhost:8000/health
   ./verify-vps-deployment.sh
   ```

6. **Document Incident:**
   - Record what failed
   - Document root cause
   - Plan fix for next deployment

---

## 💾 Backup and Restore

### Database Backup

**Manual Backup:**
```bash
# Create backup
docker exec bookgen-db pg_dump -U bookgen bookgen > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_*.sql | tail -1

# Move to backup directory
mkdir -p /opt/bookgen/backups
mv backup_*.sql /opt/bookgen/backups/
```

**Automated Backup (Cron):**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /opt/bookgen && ./scripts/backup_database.sh >> /var/log/bookgen/backup.log 2>&1
```

**Backup Script (/opt/bookgen/scripts/backup_database.sh):**
```bash
#!/bin/bash
BACKUP_DIR="/opt/bookgen/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bookgen_backup_$TIMESTAMP.sql"

# Create backup
docker exec bookgen-db pg_dump -U bookgen bookgen > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# Log result
echo "$(date): Backup completed: $BACKUP_FILE.gz"
```

### Database Restore

**Restore from Backup:**
```bash
# Stop services
docker-compose stop api worker

# Restore database
gunzip < /opt/bookgen/backups/bookgen_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i bookgen-db psql -U bookgen -d bookgen

# Restart services
docker-compose start api worker

# Verify restore
curl http://localhost:8000/api/v1/status
```

### File Backup

**Backup Generated Biographies:**
```bash
# Create archive of generated files
tar -czf biographies_backup_$(date +%Y%m%d).tar.gz bios/ docx/

# Move to backup location
mv biographies_backup_*.tar.gz /opt/bookgen/backups/

# Clean old backups (keep 30 days)
find /opt/bookgen/backups -name "biographies_backup_*.tar.gz" -mtime +30 -delete
```

### Configuration Backup

**Backup Configuration:**
```bash
# Backup .env file (remove sensitive data first)
cp .env .env.backup.$(date +%Y%m%d)

# Backup docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d)

# Store securely (encrypted)
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env.backup.* docker-compose.yml.backup.*
gpg -c config_backup_*.tar.gz
rm config_backup_*.tar.gz .env.backup.* docker-compose.yml.backup.*
```

---

## ⚡ Performance Tuning

### Database Optimization

**Analyze Query Performance:**
```bash
# Connect to database
docker exec -it bookgen-db psql -U bookgen -d bookgen

# Enable query timing
\timing

# Run slow query log analysis
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

**Index Optimization:**
```bash
# Check missing indexes
docker exec -it bookgen-db psql -U bookgen -d bookgen << EOF
SELECT schemaname, tablename, attname, n_distinct
FROM pg_stats
WHERE schemaname = 'public'
AND n_distinct > 100
ORDER BY n_distinct DESC;
EOF
```

**Vacuum and Analyze:**
```bash
# Run maintenance
docker exec bookgen-db psql -U bookgen -d bookgen -c "VACUUM ANALYZE;"

# Schedule regular maintenance
# Add to crontab:
0 3 * * 0 docker exec bookgen-db psql -U bookgen -d bookgen -c "VACUUM ANALYZE;"
```

### Redis Optimization

**Check Redis Stats:**
```bash
# Connect to Redis
docker exec -it bookgen-redis redis-cli

# Get info
INFO stats
INFO memory

# Check slow log
SLOWLOG GET 10
```

**Optimize Memory:**
```bash
# Set max memory limit
docker exec bookgen-redis redis-cli CONFIG SET maxmemory 256mb

# Set eviction policy
docker exec bookgen-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Worker Performance

**Adjust Worker Concurrency:**
```bash
# Update worker concurrency in docker-compose.yml
services:
  worker:
    command: celery -A src.worker worker --loglevel=info --concurrency=4

# Restart worker
docker-compose restart worker
```

**Monitor Worker Performance:**
```bash
# Check active tasks
docker exec bookgen-worker celery -A src.worker inspect active

# Check worker stats
docker exec bookgen-worker celery -A src.worker inspect stats

# Check queue length
docker exec bookgen-redis redis-cli LLEN celery
```

---

## 🔒 Security Operations

### SSL Certificate Renewal

**Let's Encrypt (Certbot):**
```bash
# Test renewal
sudo certbot renew --dry-run

# Renew certificates
sudo certbot renew

# Reload Nginx
sudo nginx -s reload

# Verify certificate
curl -vI https://yourdomain.com 2>&1 | grep "expire"
```

**Automate Renewal:**
```bash
# Add to crontab
0 3 * * 1 certbot renew --quiet && nginx -s reload
```

### Security Updates

**Update Docker Images:**
```bash
# Pull latest base images
docker-compose pull

# Rebuild with security patches
docker-compose build --pull

# Deploy updated images
docker-compose up -d
```

**Update System Packages:**
```bash
# Update OS packages
sudo apt update
sudo apt upgrade -y

# Check for security updates
sudo apt list --upgradable | grep -i security
```

### Access Control Review

**Review Active Sessions:**
```bash
# Check active database connections
docker exec bookgen-db psql -U bookgen -d bookgen -c \
  "SELECT pid, usename, application_name, client_addr, state 
   FROM pg_stat_activity;"
```

**Review API Access:**
```bash
# Check recent API access
docker logs bookgen-api | grep "POST\|GET" | tail -100

# Monitor for suspicious activity
docker logs bookgen-api | grep -E "40[134]|50[03]"
```

---

## 📊 Monitoring and Alerts

### Health Check Monitoring

**Automated Health Checks:**
```bash
# Add to crontab for monitoring every 5 minutes
*/5 * * * * curl -f http://localhost:8000/health || echo "Health check failed at $(date)" | mail -s "BookGen Alert" admin@example.com
```

**Comprehensive Check Script:**
```bash
#!/bin/bash
# /opt/bookgen/scripts/health_check.sh

# Check API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
  echo "API health check failed" | mail -s "BookGen Alert" admin@example.com
fi

# Check database
if ! docker exec bookgen-db pg_isready -U bookgen > /dev/null 2>&1; then
  echo "Database health check failed" | mail -s "BookGen Alert" admin@example.com
fi

# Check Redis
if ! docker exec bookgen-redis redis-cli ping > /dev/null 2>&1; then
  echo "Redis health check failed" | mail -s "BookGen Alert" admin@example.com
fi

# Check worker
ACTIVE_WORKERS=$(docker exec bookgen-worker celery -A src.worker inspect active 2>&1)
if [ $? -ne 0 ]; then
  echo "Worker health check failed" | mail -s "BookGen Alert" admin@example.com
fi
```

### Log Monitoring

**Monitor Error Logs:**
```bash
# Watch for errors
docker-compose logs -f | grep -i error

# Count errors in last hour
docker-compose logs --since 1h | grep -c ERROR

# Send alerts on errors
docker-compose logs --since 5m | grep ERROR && \
  echo "Errors detected" | mail -s "BookGen Errors" admin@example.com
```

### Disk Space Monitoring

**Check Disk Usage:**
```bash
# Overall disk usage
df -h

# Check Docker disk usage
docker system df

# Check specific directories
du -sh /opt/bookgen/bios/*
du -sh /opt/bookgen/docx/*
```

**Automated Cleanup:**
```bash
# Clean old generated files (30+ days)
find /opt/bookgen/bios -mtime +30 -type d -exec rm -rf {} +
find /opt/bookgen/docx -mtime +30 -type f -delete

# Clean Docker
docker system prune -af --volumes --filter "until=720h"
```

---

## 📋 Operational Checklists

### Daily Operations
- [ ] Check system health (`curl /health`)
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups completed
- [ ] Check active jobs

### Weekly Operations
- [ ] Review performance metrics
- [ ] Analyze slow queries
- [ ] Update system packages
- [ ] Test backup restoration
- [ ] Review access logs

### Monthly Operations
- [ ] Security audit
- [ ] Capacity planning review
- [ ] Clean old data
- [ ] Update documentation
- [ ] Review and update runbooks

---

[← Deployment](deployment.md) | [Emergency Procedures →](../emergency/incident-response.md)
