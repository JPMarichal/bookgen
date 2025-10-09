# Directory Structure Simplification - Summary

This document summarizes the changes made to simplify the BookGen root directory structure.

## Overview

The root directory structure has been reorganized to reduce clutter and improve organization by grouping related resources into logical categories.

## Changes Made

### New Directory Structure

**Before (14+ directories):**
```
alembic/
bios/
colecciones/
config/
data/
docs/
examples/          ← Moved
monitoring/        ← Moved
nginx/            ← Moved
postman/          ← Moved
scripts/          ← Moved
src/
tests/
wordTemplate/
Dockerfile        ← Moved
docker-compose.yml    ← Moved
docker-compose.prod.yml  ← Moved
```

**After (10 visible directories + organized infrastructure):**
```
alembic/
bios/
colecciones/
development/       ← NEW: Contains examples/, postman/, scripts/
docs/
infrastructure/    ← NEW: Contains monitoring/, nginx/, Dockerfile, docker-compose.*
src/
tests/
wordTemplate/
```

### Directories Moved

#### To `development/`
- **examples/** - Demo scripts and usage examples
- **postman/** - Postman collections for API testing
- **scripts/** - Development, deployment, and utility scripts

#### To `infrastructure/`
- **monitoring/** - Prometheus, Grafana, AlertManager configuration
- **nginx/** - Nginx reverse proxy configuration
- **Dockerfile** - Docker image build configuration
- **docker-compose.yml** - Development Docker Compose
- **docker-compose.prod.yml** - Production Docker Compose

## Updated References

All references to moved directories have been updated across the codebase:

### Scripts Updated
- `development/scripts/deploy-vps.sh`
- `development/scripts/verify-vps-deployment.sh`
- `development/scripts/validate-config.sh`

### Documentation Updated
- All markdown files in `docs/` with path references
- Quickstart guides
- Deployment guides
- Monitoring documentation
- README files

### Configuration Updated
- `.github/workflows/ci-cd.yml` - CI/CD pipeline
- `infrastructure/docker-compose.prod.yml` - Production nginx volume paths
- Monitoring documentation paths

## Benefits

1. **Clearer Organization**: Related resources are now grouped logically
2. **Reduced Root Clutter**: From 14+ to 10 visible directories
3. **Easier Navigation**: Development vs Infrastructure vs Core code
4. **Better Separation of Concerns**: 
   - Development tools in one place
   - Infrastructure config in another
   - Core code remains clean

## Documentation

New README files have been added:
- `development/README.md` - Explains development resources
- `infrastructure/README.md` - Explains infrastructure configuration

## Migration Notes

### Backward Compatibility

**Symbolic links** have been created in the project root to maintain backward compatibility:
- `docker-compose.yml` → `infrastructure/docker-compose.yml`
- `docker-compose.prod.yml` → `infrastructure/docker-compose.prod.yml`
- `Dockerfile` → `infrastructure/Dockerfile`

This means **existing Docker commands continue to work** without modification!

### For Developers

**Docker commands (unchanged):**
```bash
docker-compose up -d                           # Still works!
docker-compose -f docker-compose.prod.yml up -d # Still works!
docker build -t bookgen:latest .               # Still works!
```

**Example scripts (updated paths):**
```bash
# Old
python examples/demo_openrouter.py

# New
python development/examples/demo_openrouter.py
```

**Deployment scripts (updated paths):**
```bash
# Old
bash scripts/deploy-vps.sh

# New
bash development/scripts/deploy-vps.sh
```

### For Deployment

**Production deployments** can use either style:
```bash
# Short form (via symlink)
docker-compose -f docker-compose.prod.yml up -d

# Full path
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

**Nginx configuration** is now at:
```
infrastructure/nginx/nginx.conf
```

**Monitoring stack** is now at:
```bash
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d
```

## Backward Compatibility

**Docker commands:** ✅ Fully backward compatible via symbolic links
- `docker-compose up -d` still works
- `docker-compose -f docker-compose.prod.yml up -d` still works
- `docker build -t bookgen .` still works

**Breaking changes only for:**
- Example scripts: `examples/` → `development/examples/`
- Deployment scripts: `scripts/` → `development/scripts/`
- Postman collections: `postman/` → `development/postman/`

**No action required** for Docker-based workflows. Scripts and examples need path updates.

## Testing

All updated paths have been verified:
- ✅ Documentation references updated
- ✅ Script paths updated
- ✅ Docker compose paths updated
- ✅ CI/CD workflow updated
- ✅ Monitoring configuration updated

## Related Issue

Addresses: Issue #XX - Simplificar estructura de directorios en la raíz del proyecto
