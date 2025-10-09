# Development Resources

This directory contains development-related resources including examples, testing tools, and deployment scripts.

## Contents

### 📝 examples/
Demonstration scripts and usage examples for various BookGen features:
- Content generation demos
- API usage examples
- Integration examples
- Performance testing examples

### 📮 postman/
Postman collections for API testing:
- Complete API test collection
- Environment configurations
- Example requests

### 🛠️ scripts/
Development and deployment scripts:
- **deploy-vps.sh** - VPS deployment automation
- **verify-vps-deployment.sh** - Deployment verification
- **validate-config.sh** - Configuration validation
- **test-docker-setup.sh** - Docker setup testing
- **benchmark_generation.py** - Performance benchmarking
- **profile_memory.py** - Memory profiling
- **test_alerts.py** - Alert system testing

#### scripts/legacy/
Legacy scripts for backward compatibility

#### scripts/verification/
Verification scripts for specific issues and features

## Usage

### Running Examples
```bash
# Run any example script
python development/examples/demo_openrouter.py
python development/examples/demo_content_analyzer.py
```

### Using Postman Collection
1. Import `development/postman/BookGen_API_Collection.json` into Postman
2. Configure environment with `development/postman/BookGen_Environment.json`
3. Run requests against your BookGen instance

### Deployment Scripts
```bash
# Deploy to VPS
sudo development/scripts/deploy-vps.sh

# Verify deployment
development/scripts/verify-vps-deployment.sh

# Validate configuration
development/scripts/validate-config.sh
```

## Note

These resources are for development, testing, and deployment purposes. They are not part of the core application runtime.
