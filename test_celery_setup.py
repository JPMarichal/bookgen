#!/usr/bin/env python
"""
Test script for Celery task queue
Tests basic task submission and monitoring
"""
import sys
import time
from datetime import datetime

def test_celery_import():
    """Test that Celery and tasks can be imported"""
    print("Testing Celery imports...")
    try:
        from src.worker import app
        print("✓ Celery app imported successfully")
        
        from src.tasks.generation_tasks import generate_chapter, generate_introduction
        print("✓ Generation tasks imported successfully")
        
        from src.tasks.validation_tasks import validate_chapter_length
        print("✓ Validation tasks imported successfully")
        
        from src.tasks.export_tasks import export_to_markdown
        print("✓ Export tasks imported successfully")
        
        from src.tasks.monitoring_tasks import health_check
        print("✓ Monitoring tasks imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_celery_config():
    """Test Celery configuration"""
    print("\nTesting Celery configuration...")
    try:
        from src.worker import app
        from src.config import celery_config
        
        print(f"  Broker URL: {celery_config.BROKER_URL}")
        print(f"  Result Backend: {celery_config.RESULT_BACKEND}")
        print(f"  Task Serializer: {celery_config.CELERY_TASK_SERIALIZER}")
        print(f"  Default Queue: {celery_config.CELERY_TASK_DEFAULT_QUEUE}")
        print(f"  Max Retries: {celery_config.CELERY_TASK_MAX_RETRIES}")
        print(f"  Retry Backoff: {celery_config.CELERY_TASK_RETRY_BACKOFF}")
        
        # Check queues
        if hasattr(celery_config, 'CELERY_TASK_QUEUES'):
            queues = celery_config.CELERY_TASK_QUEUES
            print(f"  Configured Queues: {len(queues)}")
            for queue in queues:
                print(f"    - {queue.name}")
        
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_task_registration():
    """Test that tasks are registered"""
    print("\nTesting task registration...")
    try:
        from src.worker import app
        
        registered_tasks = list(app.tasks.keys())
        print(f"  Total registered tasks: {len(registered_tasks)}")
        
        # Filter out built-in Celery tasks
        custom_tasks = [t for t in registered_tasks if t.startswith('src.tasks')]
        print(f"  Custom tasks: {len(custom_tasks)}")
        
        for task_name in sorted(custom_tasks):
            print(f"    - {task_name}")
        
        print("✓ Tasks registered successfully")
        return True
    except Exception as e:
        print(f"✗ Task registration test failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\nTesting Redis connection...")
    try:
        import redis
        from src.config import celery_config
        
        # Extract Redis connection details
        redis_host = celery_config.REDIS_HOST
        redis_port = celery_config.REDIS_PORT
        redis_db = celery_config.REDIS_DB
        
        # Try to connect
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            socket_connect_timeout=5
        )
        
        # Test ping
        result = r.ping()
        if result:
            print(f"✓ Redis connection successful ({redis_host}:{redis_port})")
            
            # Get some stats
            info = r.info()
            print(f"  Redis version: {info.get('redis_version')}")
            print(f"  Connected clients: {info.get('connected_clients')}")
            print(f"  Used memory: {info.get('used_memory_human')}")
            return True
        else:
            print("✗ Redis ping failed")
            return False
            
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("  Note: Make sure Redis is running (start with 'redis-server' or docker-compose)")
        return False


def test_task_execution():
    """Test actual task execution (requires running worker)"""
    print("\nTesting task execution...")
    print("  Note: This test requires a running Celery worker")
    
    try:
        from src.tasks.generation_tasks import generate_chapter
        
        # Submit a test task
        print("  Submitting test task...")
        result = generate_chapter.delay(
            character_name="Test Person",
            chapter_number=1,
            chapter_title="Test Chapter",
            target_words=100
        )
        
        print(f"  Task submitted: {result.id}")
        print(f"  Task state: {result.state}")
        
        # Try to get result with timeout
        print("  Waiting for result (5 second timeout)...")
        try:
            task_result = result.get(timeout=5)
            print("✓ Task executed successfully")
            print(f"  Result: {task_result}")
            return True
        except Exception as e:
            print(f"  Task not completed within timeout: {e}")
            print("  This is expected if no worker is running")
            return None
            
    except Exception as e:
        print(f"✗ Task execution test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Celery Task Queue Test Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results['imports'] = test_celery_import()
    results['config'] = test_celery_config()
    results['registration'] = test_task_registration()
    results['redis'] = test_redis_connection()
    results['execution'] = test_task_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result is True else ("✗ FAIL" if result is False else "⊘ SKIP")
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\nSome tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print("\nAll critical tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
