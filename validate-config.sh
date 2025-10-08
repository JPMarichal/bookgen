#!/bin/bash

# Quick validation script for BookGen VPS deployment configuration
# This script validates syntax and structure of deployment files

set -e

echo "🔍 Validating BookGen VPS Deployment Configuration..."
echo ""

ERRORS=0
WARNINGS=0

# 1. Validate shell scripts
echo "📝 Checking shell scripts..."
for script in deploy-vps.sh verify-vps-deployment.sh; do
    if [ -f "$script" ]; then
        if bash -n "$script" 2>/dev/null; then
            echo "  ✅ $script: Syntax OK"
        else
            echo "  ❌ $script: Syntax errors found"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  ⚠️  $script: Not found"
        WARNINGS=$((WARNINGS + 1))
    fi
done
echo ""

# 2. Validate Docker Compose file
echo "🐳 Checking Docker Compose configuration..."
if [ -f "docker-compose.prod.yml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('docker-compose.prod.yml'))" 2>/dev/null; then
        echo "  ✅ docker-compose.prod.yml: Valid YAML"
        
        # Check for required services
        for service in bookgen-api bookgen-worker-1 bookgen-worker-2 nginx-proxy; do
            if grep -q "^\s*${service}:" docker-compose.prod.yml; then
                echo "  ✅ Service '$service' defined"
            else
                echo "  ❌ Service '$service' missing"
                ERRORS=$((ERRORS + 1))
            fi
        done
    else
        echo "  ❌ docker-compose.prod.yml: Invalid YAML"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ docker-compose.prod.yml: Not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Validate Nginx configuration
echo "🌐 Checking Nginx configuration..."
if [ -f "nginx/nginx.conf" ]; then
    # Check for balanced braces
    BRACES=$(grep -E "^[^#]*\{[^}]*$|^[^#]*\}[^{]*$" nginx/nginx.conf | awk 'BEGIN{count=0} /{/{count++} /}/{count--} END{print count}')
    if [ "$BRACES" -eq 0 ]; then
        echo "  ✅ nginx/nginx.conf: Balanced braces"
    else
        echo "  ❌ nginx/nginx.conf: Unbalanced braces"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for upstream definition
    if grep -q "upstream bookgen_backend" nginx/nginx.conf; then
        echo "  ✅ Upstream 'bookgen_backend' defined"
    else
        echo "  ❌ Upstream 'bookgen_backend' missing"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for rate limiting
    if grep -q "limit_req_zone" nginx/nginx.conf; then
        echo "  ✅ Rate limiting configured"
    else
        echo "  ⚠️  Rate limiting not found"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check for SSL configuration
    if grep -q "ssl_protocols" nginx/nginx.conf; then
        echo "  ✅ SSL protocols configured"
    else
        echo "  ⚠️  SSL protocols not configured"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "  ❌ nginx/nginx.conf: Not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Check documentation files
echo "📚 Checking documentation..."
for doc in docs/technical/deployment/DEPLOYMENT.md docs/technical/deployment/VPS_SETUP.md docs/technical/testing/VERIFICATION_COMMANDS.md; do
    if [ -f "$doc" ]; then
        echo "  ✅ $doc: Found"
    else
        echo "  ⚠️  $doc: Not found"
        WARNINGS=$((WARNINGS + 1))
    fi
done
echo ""

# 5. Check environment example file
echo "⚙️  Checking environment configuration..."
if [ -f ".env.production.example" ]; then
    echo "  ✅ .env.production.example: Found"
    
    # Check for critical variables
    for var in OPENROUTER_API_KEY SITE_URL SECRET_KEY; do
        if grep -q "^${var}=" .env.production.example; then
            echo "  ✅ Variable '$var' defined"
        else
            echo "  ⚠️  Variable '$var' missing"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
else
    echo "  ⚠️  .env.production.example: Not found"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "================================"
echo "📊 Validation Summary"
echo "================================"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ All critical checks passed!"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  There are $WARNINGS warning(s) that should be reviewed."
    fi
    exit 0
else
    echo "❌ Validation failed with $ERRORS error(s)."
    echo "Please fix the errors before deploying."
    exit 1
fi
