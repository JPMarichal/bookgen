# Infrastructure Configuration

This directory contains all infrastructure-related configuration files for deploying and running BookGen.

## Contents

### 🐳 Docker Configuration

#### docker-compose.yml
Development Docker Compose configuration for local development:
- API service
- Worker service
- PostgreSQL database
- Redis cache

Usage:
```bash
docker-compose -f infrastructure/docker-compose.yml up -d
```

#### docker-compose.prod.yml
Production Docker Compose configuration for VPS deployment:
- API service with health checks and resource limits
- Multiple worker instances (content generator, source validator)
- Nginx reverse proxy with SSL support
- Production volume mappings

Usage:
```bash
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

#### Dockerfile
Multi-stage Docker image build configuration:
- Python 3.9+ base
- Dependency installation
- Application code
- Health checks

Build:
```bash
docker build -f infrastructure/Dockerfile -t bookgen:latest .
```

### 🌐 nginx/
Nginx reverse proxy configuration:
- **nginx.conf** - Production Nginx configuration with:
  - Reverse proxy to BookGen API
  - SSL/TLS configuration
  - Rate limiting
  - Security headers
  - Logging

### 📊 monitoring/
Monitoring stack configuration (Prometheus, Grafana, AlertManager):
- **docker-compose.yml** - Monitoring services
- **prometheus/** - Prometheus configuration and alerts
- **grafana/** - Grafana dashboards and provisioning
- **alertmanager/** - Alert routing configuration

See [monitoring/README.md](monitoring/README.md) for detailed setup.

## Directory Structure

```
infrastructure/
├── README.md                          # This file
├── Dockerfile                         # Application container image
├── docker-compose.yml                 # Development environment
├── docker-compose.prod.yml            # Production environment
├── nginx/
│   └── nginx.conf                     # Nginx configuration
└── monitoring/
    ├── docker-compose.yml             # Monitoring stack
    ├── prometheus/                    # Prometheus config
    ├── grafana/                       # Grafana dashboards
    └── alertmanager/                  # Alert configuration
```

## Quick Start

### Development
```bash
# Start development environment
docker-compose -f infrastructure/docker-compose.yml up -d

# View logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

### Production
```bash
# Deploy to production
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# Check status
docker-compose -f infrastructure/docker-compose.prod.yml ps

# View logs
docker-compose -f infrastructure/docker-compose.prod.yml logs -f
```

### Monitoring
```bash
# Start monitoring stack
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# AlertManager: http://localhost:9093
```

## Configuration Notes

### Volume Mappings

Development volumes (relative paths):
```yaml
- ./data:/app/data
- ./bios:/app/bios
- ./colecciones:/app/colecciones
- ./wordTemplate:/app/wordTemplate
```

Production volumes (absolute paths on VPS):
```yaml
- /opt/bookgen/data:/app/data
- /opt/bookgen/output:/app/bios
- /opt/bookgen/collections:/app/colecciones
- /opt/bookgen/templates:/app/wordTemplate
```

### Environment Variables

See `.env` (development) or `.env.production` (production) for required configuration.

### SSL/TLS Configuration

For production deployments with SSL:
1. Obtain certificates with Let's Encrypt
2. Configure certificate paths in `nginx/nginx.conf`
3. Update `docker-compose.prod.yml` volume mappings

See deployment documentation for details.

## Related Documentation

- [Deployment Guide](../docs/operations/deployment.md)
- [Monitoring Setup](monitoring/README.md)
- [Docker Setup](../docs/technical/components/DOCKER_README.md)
- [VPS Deployment](../docs/technical/deployment/VPS_SETUP.md)
