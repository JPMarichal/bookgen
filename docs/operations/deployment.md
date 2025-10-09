# Production Deployment Guide

Complete guide for deploying BookGen to production environments.

## 📋 Deployment Overview

This guide covers deploying BookGen to:
- VPS (Ubuntu/Debian)
- Cloud platforms (AWS, Google Cloud, Azure)
- Container orchestration (Docker, Kubernetes)

---

## 🚀 Quick Deployment (VPS)

### Prerequisites

- Ubuntu 20.04+ or Debian 11+ server
- Root or sudo access
- Domain name (optional, for SSL)
- Minimum 4 GB RAM, 2 CPU cores

### One-Command Deployment

```bash
# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/JPMarichal/bookgen/main/deploy-vps.sh -o deploy-vps.sh
chmod +x deploy-vps.sh
sudo ./deploy-vps.sh
```

**What this does:**
- ✅ Installs Docker and Docker Compose
- ✅ Creates system user and directories
- ✅ Configures firewall (UFW)
- ✅ Sets up Fail2ban for security
- ✅ Creates systemd service
- ✅ Configures log rotation
- ✅ Sets up automated backups
- ✅ Configures health monitoring

### Post-Deployment Configuration

```bash
# Edit environment variables
cd /opt/bookgen
sudo nano .env.production

# Critical variables to set:
OPENROUTER_API_KEY=your-api-key-here
SECRET_KEY=generate-random-32-char-key
SITE_URL=https://yourdomain.com

# Start services
sudo systemctl start bookgen

# Verify deployment
./verify-vps-deployment.sh
```

---

## 🔧 Manual Deployment

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  git curl wget \
  docker.io docker-compose \
  nginx certbot python3-certbot-nginx \
  ufw fail2ban
```

### Step 2: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/bookgen
sudo chown $USER:$USER /opt/bookgen

# Clone repository
cd /opt/bookgen
git clone https://github.com/JPMarichal/bookgen.git .
```

### Step 3: Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit configuration
nano .env.production
```

**Required Configuration:**
```bash
# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Environment
ENV=production
DEBUG=false

# Security
SECRET_KEY=your-generated-secret-key
CORS_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql://bookgen:secure_password@db:5432/bookgen

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Step 4: Configure Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/bookgen << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/bookgen /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Configure SSL (Let's Encrypt)

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Configure auto-renewal (already in cron)
sudo systemctl status certbot.timer
```

### Step 6: Configure Firewall

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Verify
sudo ufw status
```

### Step 7: Configure Fail2ban

```bash
# Create BookGen jail
sudo tee /etc/fail2ban/jail.d/bookgen.conf << 'EOF'
[bookgen-api]
enabled = true
port = 80,443
filter = bookgen-api
logpath = /var/log/nginx/access.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

# Create filter
sudo tee /etc/fail2ban/filter.d/bookgen-api.conf << 'EOF'
[Definition]
failregex = ^<HOST> - .* "(GET|POST|HEAD).*" (429|403|401) .*$
ignoreregex =
EOF

# Restart Fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status bookgen-api
```

### Step 8: Start Services

```bash
# Start Docker containers
cd /opt/bookgen
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# Verify all running
docker-compose -f infrastructure/docker-compose.prod.yml ps

# Check logs
docker-compose -f infrastructure/docker-compose.prod.yml logs -f --tail=50
```

### Step 9: Create Systemd Service

```bash
# Create service file
sudo tee /etc/systemd/system/bookgen.service << 'EOF'
[Unit]
Description=BookGen Biography Generation Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/bookgen
ExecStart=/usr/bin/docker-compose -f infrastructure/docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f infrastructure/docker-compose.prod.yml down
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable bookgen
sudo systemctl start bookgen
sudo systemctl status bookgen
```

### Step 10: Configure Backups

```bash
# Create backup script
sudo tee /opt/bookgen/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/bookgen/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec bookgen-db pg_dump -U bookgen bookgen | \
  gzip > $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz

# Backup files
tar -czf $BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz \
  /opt/bookgen/bios \
  /opt/bookgen/docx \
  /opt/bookgen/.env.production

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

# Make executable
sudo chmod +x /opt/bookgen/scripts/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/bookgen/scripts/backup.sh >> /var/log/bookgen/backup.log 2>&1") | crontab -
```

### Step 11: Verify Deployment

```bash
# Run verification script
cd /opt/bookgen
./verify-vps-deployment.sh

# Manual checks
curl http://localhost:8000/health
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/status

# Check all services
docker-compose -f infrastructure/docker-compose.prod.yml ps
sudo systemctl status bookgen
sudo systemctl status nginx
sudo ufw status
sudo fail2ban-client status
```

---

## ☁️ Cloud Platform Deployment

### AWS Deployment

**Using EC2:**
```bash
# 1. Launch EC2 instance (Ubuntu 20.04, t3.medium or larger)
# 2. Configure security group (ports 22, 80, 443)
# 3. Connect via SSH
# 4. Follow VPS deployment steps above

# Additional: Use RDS for PostgreSQL
DATABASE_URL=postgresql://user:pass@your-rds-instance.region.rds.amazonaws.com/bookgen

# Additional: Use ElastiCache for Redis
REDIS_HOST=your-elasticache-instance.region.cache.amazonaws.com
```

**Using ECS (Elastic Container Service):**
```yaml
# task-definition.json
{
  "family": "bookgen",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "bookgen/api:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENV", "value": "production"},
        {"name": "DATABASE_URL", "value": "..."}
      ]
    }
  ]
}
```

### Google Cloud Platform

**Using Compute Engine:**
```bash
# Create VM instance
gcloud compute instances create bookgen-instance \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh bookgen-instance

# Follow VPS deployment steps
```

**Using Cloud Run:**
```bash
# Build container
docker build -t gcr.io/YOUR_PROJECT/bookgen-api .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT/bookgen-api

# Deploy to Cloud Run
gcloud run deploy bookgen-api \
  --image gcr.io/YOUR_PROJECT/bookgen-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

**Using Azure Container Instances:**
```bash
# Create resource group
az group create --name bookgen-rg --location eastus

# Deploy container
az container create \
  --resource-group bookgen-rg \
  --name bookgen-api \
  --image bookgen/api:latest \
  --dns-name-label bookgen-api \
  --ports 8000 \
  --environment-variables \
    ENV=production \
    DATABASE_URL=postgresql://...
```

---

## 🐳 Docker Deployment

### Production Docker Compose

```yaml
# infrastructure/docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: infrastructure/Dockerfile
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - ./bios:/app/bios
      - ./docx:/app/docx
    restart: unless-stopped
    mem_limit: 2g
    cpus: 2

  worker:
    build:
      context: .
      dockerfile: infrastructure/Dockerfile
    command: celery -A src.worker worker --loglevel=info --concurrency=4
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - ./bios:/app/bios
      - ./docx:/app/docx
    restart: unless-stopped
    mem_limit: 3g
    cpus: 4

  db:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: bookgen
      POSTGRES_USER: bookgen
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    mem_limit: 1g

  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    mem_limit: 512m

volumes:
  postgres_data:
  redis_data:
```

### Building Production Images

```bash
# Build optimized production image
docker build \
  --target production \
  --tag bookgen/api:latest \
  --tag bookgen/api:v1.0.0 \
  .

# Push to registry
docker push bookgen/api:latest
docker push bookgen/api:v1.0.0
```

---

## 📊 Post-Deployment

### Monitoring Setup

```bash
# Set up health monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * curl -f https://yourdomain.com/health || echo 'Health check failed' | mail -s 'BookGen Alert' admin@example.com") | crontab -
```

### Log Management

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/bookgen << 'EOF'
/var/log/bookgen/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 bookgen bookgen
    sharedscripts
    postrotate
        systemctl reload bookgen > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Performance Tuning

```bash
# Tune database
docker exec bookgen-db psql -U bookgen -d bookgen << 'EOF'
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
EOF
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Server meets minimum requirements
- [ ] Domain DNS configured (if using)
- [ ] OpenRouter API key obtained
- [ ] Backup plan in place
- [ ] Rollback plan documented

### Deployment
- [ ] Repository cloned
- [ ] Environment configured
- [ ] Docker installed
- [ ] Nginx configured
- [ ] SSL certificate obtained
- [ ] Firewall configured
- [ ] Fail2ban configured
- [ ] Services started

### Post-Deployment
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Backups scheduled
- [ ] Monitoring active
- [ ] Logs rotating
- [ ] Documentation updated

### Security
- [ ] Firewall enabled
- [ ] Fail2ban active
- [ ] SSL/TLS enabled
- [ ] Strong passwords set
- [ ] API keys secured
- [ ] Security headers configured

---

## 🔄 Updating Production

```bash
# 1. Backup current state
./scripts/backup.sh

# 2. Pull latest changes
cd /opt/bookgen
git fetch origin
git checkout v1.1.0  # or main for latest

# 3. Rebuild containers
docker-compose -f infrastructure/docker-compose.prod.yml build

# 4. Run migrations
docker-compose -f infrastructure/docker-compose.prod.yml run --rm api alembic upgrade head

# 5. Restart services
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# 6. Verify
./verify-vps-deployment.sh
```

---

[← Runbooks](runbooks.md) | [Monitoring →](monitoring.md)
