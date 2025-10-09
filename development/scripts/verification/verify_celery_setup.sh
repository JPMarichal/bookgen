#!/bin/bash
# Quick Start Guide for Celery Task Queue

set -e

echo "=============================================="
echo "BookGen Celery Task Queue - Quick Start"
echo "=============================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# 1. Check Redis
echo "Step 1: Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is running"
else
    print_error "Redis is not running"
    print_info "Start Redis with: redis-server"
    print_info "Or using Docker: docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi

# 2. Test Celery setup
echo
echo "Step 2: Testing Celery setup..."
python test_celery_setup.py

if [ $? -eq 0 ]; then
    print_status "Celery setup test passed"
else
    print_error "Celery setup test failed"
    exit 1
fi

# 3. Test with pytest
echo
echo "Step 3: Running unit tests..."
python -m pytest tests/test_tasks.py -v

if [ $? -eq 0 ]; then
    print_status "All tests passed"
else
    print_error "Some tests failed"
    exit 1
fi

# 4. Instructions for starting workers
echo
echo "=============================================="
echo "Next Steps: Start Celery Workers"
echo "=============================================="
echo
echo "Option 1: Using Docker Compose (Recommended)"
echo "  docker-compose up -d"
echo
echo "Option 2: Manual Worker Start (in separate terminals)"
echo
echo "  Terminal 1 - Content Generation Worker:"
echo "  celery -A src.worker worker --loglevel=info \\"
echo "    --queues=content_generation,high_priority \\"
echo "    --concurrency=2 --hostname=content@%h"
echo
echo "  Terminal 2 - Validation Worker:"
echo "  celery -A src.worker worker --loglevel=info \\"
echo "    --queues=validation --concurrency=2 --hostname=validation@%h"
echo
echo "  Terminal 3 - Export Worker:"
echo "  celery -A src.worker worker --loglevel=info \\"
echo "    --queues=export --concurrency=1 --hostname=export@%h"
echo
echo "  Terminal 4 - Monitoring Worker:"
echo "  celery -A src.worker worker --loglevel=info \\"
echo "    --queues=monitoring --concurrency=1 --hostname=monitoring@%h"
echo
echo "  Terminal 5 - Flower Monitoring (Optional):"
echo "  celery -A src.worker flower --port=5555"
echo "  Then visit: http://localhost:5555"
echo
echo "=============================================="
echo "Verification Commands"
echo "=============================================="
echo
echo "Check active workers:"
echo "  celery -A src.worker inspect active"
echo
echo "Check registered tasks:"
echo "  celery -A src.worker inspect registered"
echo
echo "Submit a test task:"
echo "  python -c \"from src.tasks.generation_tasks import generate_chapter; \\"
echo "    result = generate_chapter.delay('Test', 1, 'Test Chapter', 100); \\"
echo "    print('Task ID:', result.id)\""
echo
echo "=============================================="
print_status "Setup verification complete!"
echo "=============================================="
