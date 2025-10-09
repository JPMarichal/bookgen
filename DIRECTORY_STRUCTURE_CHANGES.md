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

### For Developers

**Old commands:**
```bash
python examples/demo_openrouter.py
docker-compose up -d
bash scripts/deploy-vps.sh
```

**New commands:**
```bash
python development/examples/demo_openrouter.py
docker-compose -f infrastructure/docker-compose.yml up -d
bash development/scripts/deploy-vps.sh
```

### For Deployment

**Production deployments** now reference:
```bash
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

This is a **breaking change** for:
- Existing deployment scripts that hardcode paths
- Local development setups with cached paths
- CI/CD pipelines (already updated in this PR)

**Action Required:** Users will need to update their local scripts and aliases to reference the new paths.

## Testing

All updated paths have been verified:
- ✅ Documentation references updated
- ✅ Script paths updated
- ✅ Docker compose paths updated
- ✅ CI/CD workflow updated
- ✅ Monitoring configuration updated

## Related Issue

Addresses: Issue #XX - Simplificar estructura de directorios en la raíz del proyecto
