# Emergency Incident Response

Critical procedures for handling BookGen emergencies.

## 🚨 Emergency Contact Information

**Primary Contacts:**
- **System Administrator**: [Contact details]
- **Database Administrator**: [Contact details]
- **On-Call Engineer**: [Contact details]

**Escalation Path:**
1. On-Call Engineer (immediate)
2. System Administrator (15 minutes)
3. Engineering Lead (30 minutes)
4. CTO (1 hour)

---

## ⚡ Critical Incidents

### CRITICAL: Complete System Down

**Definition**: All services unavailable, users cannot access system.

**Immediate Response (5 minutes):**

1. **Verify Outage:**
   ```bash
   curl http://localhost:8000/health
   curl http://yourdomain.com/health
   ```

2. **Check All Services:**
   ```bash
   docker-compose ps
   sudo systemctl status bookgen
   ```

3. **Notify Stakeholders:**
   ```bash
   # Send alert
   echo "CRITICAL: BookGen system down at $(date)" | \
     mail -s "CRITICAL ALERT" admin@example.com,oncall@example.com
   ```

**Investigation (5-10 minutes):**

1. **Check System Resources:**
   ```bash
   # CPU and memory
   top -bn1 | head -20
   
   # Disk space
   df -h
   
   # Docker stats
   docker stats --no-stream
   ```

2. **Check Recent Changes:**
   ```bash
   # Recent git commits
   git log --oneline -5
   
   # Recent deployments
   cat /var/log/bookgen/deploy.log | tail -50
   ```

3. **Review Error Logs:**
   ```bash
   # All service logs
   docker-compose logs --tail=200
   
   # System logs
   sudo journalctl -xe | tail -100
   ```

**Recovery Actions:**

**Option 1: Quick Restart (try first)**
```bash
# Restart all services
docker-compose restart

# Wait 30 seconds
sleep 30

# Verify health
curl http://localhost:8000/health
```

**Option 2: Full Restart**
```bash
# Stop all services
docker-compose down

# Start fresh
docker-compose up -d

# Wait for initialization
sleep 60

# Verify health
./verify-vps-deployment.sh
```

**Option 3: Rollback (if recent deployment)**
```bash
# Stop services
docker-compose down

# Rollback to previous version
git log --oneline -5
git checkout <previous-commit>

# Restore database if needed
./scripts/restore_database.sh /opt/bookgen/backups/latest.sql

# Start previous version
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

**Post-Recovery:**
- [ ] Document root cause
- [ ] Update runbooks
- [ ] Implement prevention measures
- [ ] Notify stakeholders of resolution

---

### CRITICAL: Database Corruption

**Definition**: Database inaccessible, data integrity issues, corruption errors.

**Immediate Response:**

1. **Stop All Writes:**
   ```bash
   # Stop API and worker immediately
   docker-compose stop api worker
   ```

2. **Assess Damage:**
   ```bash
   # Connect to database
   docker exec -it bookgen-db psql -U bookgen -d bookgen
   
   # Check for corruption
   SELECT * FROM pg_stat_database WHERE datname = 'bookgen';
   
   # Exit
   \q
   ```

3. **Notify DBA:**
   ```bash
   echo "CRITICAL: Database corruption detected at $(date)" | \
     mail -s "DATABASE EMERGENCY" dba@example.com
   ```

**Recovery Steps:**

1. **Create Emergency Backup:**
   ```bash
   # Backup current state (even if corrupted)
   docker exec bookgen-db pg_dump -U bookgen bookgen > \
     /opt/bookgen/backups/emergency_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Attempt Repair:**
   ```bash
   # Run database repair
   docker exec bookgen-db psql -U bookgen -d bookgen -c "REINDEX DATABASE bookgen;"
   
   # Vacuum full
   docker exec bookgen-db psql -U bookgen -d bookgen -c "VACUUM FULL;"
   ```

3. **If Repair Fails - Restore from Backup:**
   ```bash
   # Find latest good backup
   ls -lt /opt/bookgen/backups/*.sql.gz | head -1
   
   # Drop and recreate database
   docker exec bookgen-db psql -U postgres << EOF
   DROP DATABASE bookgen;
   CREATE DATABASE bookgen;
   GRANT ALL PRIVILEGES ON DATABASE bookgen TO bookgen;
   EOF
   
   # Restore backup
   gunzip < /opt/bookgen/backups/latest_good_backup.sql.gz | \
     docker exec -i bookgen-db psql -U bookgen -d bookgen
   ```

4. **Verify and Restart:**
   ```bash
   # Run migrations
   docker-compose run --rm api alembic upgrade head
   
   # Start services
   docker-compose start api worker
   
   # Verify
   curl http://localhost:8000/api/v1/status
   ```

---

### CRITICAL: Security Breach

**Definition**: Unauthorized access, data breach, malicious activity detected.

**IMMEDIATE ACTIONS (DO NOT DELAY):**

1. **Isolate System:**
   ```bash
   # Block all external access
   sudo ufw deny in on eth0
   
   # Stop services
   docker-compose down
   ```

2. **Document Everything:**
   ```bash
   # Capture current state
   docker-compose logs > /tmp/breach_logs_$(date +%Y%m%d_%H%M%S).txt
   
   # Capture network connections
   netstat -tunapl > /tmp/breach_network_$(date +%Y%m%d_%H%M%S).txt
   
   # Capture process list
   ps auxf > /tmp/breach_processes_$(date +%Y%m%d_%H%M%S).txt
   ```

3. **Notify Security Team:**
   ```bash
   echo "SECURITY BREACH DETECTED at $(date)" | \
     mail -s "SECURITY EMERGENCY - IMMEDIATE ACTION REQUIRED" \
     security@example.com,cto@example.com
   ```

4. **Preserve Evidence:**
   ```bash
   # DO NOT delete anything
   # Copy all logs to secure location
   tar -czf /tmp/breach_evidence_$(date +%Y%m%d_%H%M%S).tar.gz \
     /var/log/bookgen/ /opt/bookgen/.env /tmp/breach_*
   ```

**Investigation (Security Team):**

1. Check access logs for unauthorized access
2. Review database for data exfiltration
3. Check for malware/backdoors
4. Identify attack vector
5. Assess data compromise

**Recovery (After Security Clearance):**

1. **Change All Credentials:**
   ```bash
   # Generate new secrets
   openssl rand -hex 32 > new_secret_key.txt
   
   # Update .env with new credentials
   # - DATABASE_PASSWORD
   # - REDIS_PASSWORD
   # - SECRET_KEY
   # - OPENROUTER_API_KEY (if compromised)
   ```

2. **Rebuild System:**
   ```bash
   # Pull clean images
   docker-compose pull
   docker-compose build --no-cache
   
   # Start with new configuration
   docker-compose up -d
   ```

3. **Restore from Pre-Breach Backup:**
   ```bash
   # Restore database from before breach
   ./scripts/restore_database.sh /opt/bookgen/backups/pre_breach.sql
   ```

4. **Implement Additional Security:**
   ```bash
   # Enable fail2ban
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   
   # Update firewall rules
   sudo ufw default deny incoming
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw enable
   
   # Enable audit logging
   sudo apt install auditd
   sudo systemctl enable auditd
   ```

---

### HIGH: Worker Process Crashed

**Definition**: Celery worker crashed, jobs not processing.

**Immediate Response:**

1. **Check Worker Status:**
   ```bash
   docker ps | grep worker
   docker logs bookgen-worker --tail=100
   ```

2. **Restart Worker:**
   ```bash
   docker-compose restart worker
   
   # Wait for worker to initialize
   sleep 10
   
   # Verify worker is processing
   docker exec bookgen-worker celery -A src.worker inspect active
   ```

3. **Check for Stuck Jobs:**
   ```bash
   # Connect to database
   docker exec -it bookgen-db psql -U bookgen -d bookgen
   
   # Find jobs in "processing" state for > 1 hour
   SELECT job_id, character, status, created_at 
   FROM biography_jobs 
   WHERE status = 'processing' 
   AND created_at < NOW() - INTERVAL '1 hour';
   ```

4. **Reset Stuck Jobs (if needed):**
   ```bash
   # Update stuck jobs to failed
   docker exec -it bookgen-db psql -U bookgen -d bookgen -c \
     "UPDATE biography_jobs 
      SET status = 'failed', 
          error_message = 'Worker crashed - job reset' 
      WHERE status = 'processing' 
      AND created_at < NOW() - INTERVAL '1 hour';"
   ```

---

### HIGH: Disk Space Critical

**Definition**: Less than 10% disk space remaining.

**Immediate Response:**

1. **Check Disk Usage:**
   ```bash
   df -h
   du -sh /opt/bookgen/* | sort -h
   ```

2. **Emergency Cleanup:**
   ```bash
   # Clean Docker
   docker system prune -af --volumes
   
   # Clean old generated files
   find /opt/bookgen/bios -mtime +7 -type d -exec rm -rf {} +
   find /opt/bookgen/docx -mtime +7 -type f -delete
   
   # Clean old logs
   find /var/log/bookgen -name "*.log.*" -mtime +7 -delete
   
   # Clean old backups (keep 3 days)
   find /opt/bookgen/backups -name "*.sql.gz" -mtime +3 -delete
   ```

3. **Verify Space Freed:**
   ```bash
   df -h
   ```

4. **If Still Critical - Archive to External Storage:**
   ```bash
   # Archive old biographies
   tar -czf /mnt/external/biographies_$(date +%Y%m%d).tar.gz \
     /opt/bookgen/bios/ /opt/bookgen/docx/
   
   # Verify archive
   tar -tzf /mnt/external/biographies_$(date +%Y%m%d).tar.gz | head
   
   # Delete local copies
   rm -rf /opt/bookgen/bios/* /opt/bookgen/docx/*
   ```

---

### HIGH: Memory Exhausted

**Definition**: System OOM errors, services killed by kernel.

**Immediate Response:**

1. **Check Memory Usage:**
   ```bash
   free -h
   docker stats --no-stream
   ```

2. **Identify Memory Hog:**
   ```bash
   # Find process using most memory
   ps aux --sort=-%mem | head -10
   ```

3. **Emergency Memory Recovery:**
   ```bash
   # Stop non-critical services
   docker-compose stop worker
   
   # Clear caches
   sync; echo 3 | sudo tee /proc/sys/vm/drop_caches
   
   # Restart critical services only
   docker-compose start api
   ```

4. **Long-term Fix:**
   ```bash
   # Reduce batch sizes in .env
   BATCH_SIZE_CHAPTERS=2
   BATCH_SIZE_SPECIAL_SECTIONS=1
   MAX_CONCURRENT_JOBS=1
   
   # Limit Docker memory in docker-compose.yml
   services:
     api:
       mem_limit: 2g
     worker:
       mem_limit: 2g
   
   # Restart with new limits
   docker-compose down
   docker-compose up -d
   ```

---

## 📋 Emergency Checklists

### System Down Checklist
- [ ] Verify outage confirmed
- [ ] Check service status
- [ ] Notify stakeholders
- [ ] Review recent changes
- [ ] Check system resources
- [ ] Review error logs
- [ ] Attempt quick restart
- [ ] Full restart if needed
- [ ] Rollback if recent deployment
- [ ] Verify recovery
- [ ] Document incident

### Data Loss Prevention
- [ ] Stop all writes immediately
- [ ] Create emergency backup
- [ ] Assess data integrity
- [ ] Document corruption extent
- [ ] Notify DBA
- [ ] Attempt repair
- [ ] Restore from backup if needed
- [ ] Verify data consistency
- [ ] Resume operations
- [ ] Post-incident review

### Security Breach Response
- [ ] Isolate system
- [ ] Preserve evidence
- [ ] Notify security team
- [ ] Document everything
- [ ] Begin investigation
- [ ] Change all credentials
- [ ] Rebuild from clean images
- [ ] Restore from backup
- [ ] Implement additional security
- [ ] Monitor for reinfection
- [ ] Notify affected users
- [ ] File incident report

---

## 🆘 Contact Information

### Internal Contacts
- **On-Call Engineer**: [Phone] | [Email]
- **System Administrator**: [Phone] | [Email]
- **Database Administrator**: [Phone] | [Email]
- **Security Team**: [Email] | [Slack Channel]

### External Contacts
- **Hosting Provider Support**: [Phone] | [Portal URL]
- **OpenRouter Support**: support@openrouter.ai
- **Emergency Services**: [As applicable]

### Communication Channels
- **Slack**: #bookgen-alerts, #bookgen-incidents
- **Email**: incidents@example.com
- **Phone Tree**: [Escalation path]
- **Status Page**: https://status.bookgen.example.com

---

## 📝 Post-Incident Procedures

### Immediate (Within 1 hour)
1. Verify system fully operational
2. Document timeline of events
3. Notify stakeholders of resolution
4. Begin preliminary root cause analysis

### Short-term (Within 24 hours)
1. Complete incident report
2. Identify root cause
3. Document lessons learned
4. Plan preventive measures

### Long-term (Within 1 week)
1. Implement preventive measures
2. Update runbooks and documentation
3. Conduct team post-mortem
4. Update monitoring and alerts
5. Test incident response procedures

---

[← Runbooks](../operations/runbooks.md) | [Recovery Procedures →](recovery.md)
