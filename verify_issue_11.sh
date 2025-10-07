#!/bin/bash
# Verification commands for Issue #11
# Tests the acceptance criteria for the Celery/Redis task queue

echo "=============================================="
echo "Issue #11 Verification - Task Queue System"
echo "=============================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "\n${YELLOW}Test:${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
}

# Counter for results
PASS=0
FAIL=0

# Test 1: Redis connection
print_test "Redis funcionando como message broker"
if redis-cli ping > /dev/null 2>&1; then
    print_pass "Redis is running and responding to ping"
    ((PASS++))
else
    print_fail "Redis is not running"
    echo "  Start with: redis-server"
    ((FAIL++))
fi

# Test 2: Celery configuration
print_test "Workers Celery especializados configurados"
python3 << 'EOF'
try:
    from src.worker import app
    
    # Force autodiscovery to ensure tasks are loaded
    app.autodiscover_tasks([
        'src.tasks.generation_tasks',
        'src.tasks.validation_tasks',
        'src.tasks.export_tasks',
        'src.tasks.monitoring_tasks'
    ], force=True)
    
    # Get all registered tasks
    all_tasks = list(app.tasks.keys())
    custom_tasks = [t for t in all_tasks if t.startswith('src.tasks')]
    
    print(f"✓ PASS: Celery app configured successfully")
    print(f"  Total registered tasks: {len(all_tasks)}")
    print(f"  Custom tasks: {len(custom_tasks)}")
    print(f"  Expected: 18 specialized tasks")
    
    if len(custom_tasks) >= 18:
        print("  ✓ All expected tasks registered")
        print("\n  Task categories:")
        print(f"    • Generation tasks: {len([t for t in custom_tasks if 'generation_tasks' in t])}")
        print(f"    • Validation tasks: {len([t for t in custom_tasks if 'validation_tasks' in t])}")
        print(f"    • Export tasks: {len([t for t in custom_tasks if 'export_tasks' in t])}")
        print(f"    • Monitoring tasks: {len([t for t in custom_tasks if 'monitoring_tasks' in t])}")
        exit(0)
    else:
        print(f"  ✗ Only {len(custom_tasks)} tasks found")
        exit(1)
        
except Exception as e:
    print(f"✗ FAIL: Error checking Celery configuration: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF

if [ $? -eq 0 ]; then
    ((PASS++))
else
    print_fail "Celery configuration incomplete"
    ((FAIL++))
fi

# Test 3: Priority system
print_test "Sistema de prioridades implementado"
python3 << 'EOF'
try:
    from src.config import celery_config
    
    # Check queue configuration
    queues = celery_config.CELERY_TASK_QUEUES
    queue_names = [q.name for q in queues]
    
    required_queues = ['high_priority', 'content_generation', 'validation', 'export', 'monitoring', 'default']
    all_present = all(q in queue_names for q in required_queues)
    
    if all_present:
        print("✓ PASS: All priority queues configured")
        print(f"  Queues: {', '.join(queue_names)}")
        
        # Check priority support
        has_priority = all('x-max-priority' in q.queue_arguments for q in queues)
        if has_priority:
            print("  ✓ Priority levels (0-10) enabled on all queues")
        else:
            print("  ✗ Some queues missing priority configuration")
    else:
        print("✗ FAIL: Missing required queues")
        print(f"  Required: {required_queues}")
        print(f"  Found: {queue_names}")
    
    exit(0 if all_present else 1)
except Exception as e:
    print(f"✗ FAIL: Error checking priority system: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    ((PASS++))
else
    ((FAIL++))
fi

# Test 4: Monitoring setup
print_test "Monitoring de tareas en tiempo real"
if command -v celery &> /dev/null; then
    print_pass "Celery CLI available for monitoring"
    echo "  Available commands:"
    echo "    • celery -A src.worker inspect active"
    echo "    • celery -A src.worker inspect stats"
    echo "    • celery -A src.worker flower"
    ((PASS++))
else
    print_fail "Celery CLI not available"
    ((FAIL++))
fi

# Test 5: Retry configuration
print_test "Retry automático con exponential backoff"
python3 << 'EOF'
try:
    from src.config import celery_config
    
    checks = [
        (celery_config.CELERY_TASK_MAX_RETRIES == 3, "Max retries: 3"),
        (celery_config.CELERY_TASK_RETRY_BACKOFF is True, "Exponential backoff enabled"),
        (celery_config.CELERY_TASK_RETRY_BACKOFF_MAX == 600, "Max backoff: 600s (10 min)"),
        (celery_config.CELERY_TASK_RETRY_JITTER is True, "Jitter enabled"),
    ]
    
    all_pass = all(check[0] for check in checks)
    
    if all_pass:
        print("✓ PASS: Retry system configured with exponential backoff")
        for check, desc in checks:
            print(f"  ✓ {desc}")
    else:
        print("✗ FAIL: Retry configuration incomplete")
        for check, desc in checks:
            status = "✓" if check else "✗"
            print(f"  {status} {desc}")
    
    exit(0 if all_pass else 1)
except Exception as e:
    print(f"✗ FAIL: Error checking retry config: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    ((PASS++))
else
    ((FAIL++))
fi

# Test 6: Dead letter queue
print_test "Dead letter queue para tareas fallidas"
python3 << 'EOF'
try:
    from src.config import celery_config
    from src.tasks.monitoring_tasks import process_dead_letter_queue
    
    # Check DLQ configuration
    has_dlq_config = hasattr(celery_config, 'CELERY_TASK_DEAD_LETTER_QUEUE')
    has_dlq_task = process_dead_letter_queue is not None
    
    if has_dlq_config and has_dlq_task:
        print("✓ PASS: Dead letter queue configured")
        print(f"  Queue: {celery_config.CELERY_TASK_DEAD_LETTER_QUEUE}")
        print(f"  Exchange: {celery_config.CELERY_TASK_DEAD_LETTER_EXCHANGE}")
        print("  Processing task: process_dead_letter_queue")
    else:
        print("✗ FAIL: Dead letter queue not fully configured")
    
    exit(0 if (has_dlq_config and has_dlq_task) else 1)
except Exception as e:
    print(f"✗ FAIL: Error checking DLQ: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    ((PASS++))
else
    ((FAIL++))
fi

# Test 7: Worker types
print_test "Workers especializados definidos"
python3 << 'EOF'
try:
    # Check task routing configuration
    from src.config import celery_config
    
    routes = celery_config.CELERY_TASK_ROUTES
    required_routes = [
        'src.tasks.generation_tasks.*',
        'src.tasks.validation_tasks.*',
        'src.tasks.export_tasks.*',
        'src.tasks.monitoring_tasks.*',
    ]
    
    all_routed = all(route in routes for route in required_routes)
    
    if all_routed:
        print("✓ PASS: Task routing configured for specialized workers")
        print("  Worker types:")
        print("    • Content Generator (content_generation queue)")
        print("    • Source Validator (validation queue)")
        print("    • Export Worker (export queue)")
        print("    • Monitoring Worker (monitoring queue)")
    else:
        print("✗ FAIL: Some task routes missing")
    
    exit(0 if all_routed else 1)
except Exception as e:
    print(f"✗ FAIL: Error checking worker configuration: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    ((PASS++))
else
    ((FAIL++))
fi

# Summary
echo
echo "=============================================="
echo "Verification Results"
echo "=============================================="
echo
echo "Passed: $PASS / $((PASS + FAIL))"
echo "Failed: $FAIL / $((PASS + FAIL))"
echo

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All acceptance criteria met!${NC}"
    echo
    echo "The task queue system is fully configured with:"
    echo "  ✓ Redis as message broker"
    echo "  ✓ Specialized Celery workers"
    echo "  ✓ Priority queue system"
    echo "  ✓ Real-time monitoring support"
    echo "  ✓ Automatic retry with exponential backoff"
    echo "  ✓ Dead letter queue for failed tasks"
    echo
    echo "Next steps:"
    echo "  1. Start Redis: redis-server"
    echo "  2. Start workers: docker-compose up -d"
    echo "  3. Monitor: celery -A src.worker flower (http://localhost:5555)"
    exit 0
else
    echo -e "${RED}✗ Some criteria not met${NC}"
    echo
    echo "Please review the failures above."
    echo "See CELERY_TASK_QUEUE.md for setup instructions."
    exit 1
fi
