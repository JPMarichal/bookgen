#!/usr/bin/env python
"""
Example usage of Celery task queue for BookGen
Demonstrates submitting and monitoring tasks
"""
import time
from datetime import datetime

def example_basic_task():
    """Example 1: Submit a basic chapter generation task"""
    print("\n" + "="*60)
    print("Example 1: Basic Task Submission")
    print("="*60)
    
    from src.tasks.generation_tasks import generate_chapter
    
    print("Submitting chapter generation task...")
    result = generate_chapter.delay(
        character_name="Albert Einstein",
        chapter_number=1,
        chapter_title="Early Life and Education",
        target_words=2550
    )
    
    print(f"✓ Task submitted successfully!")
    print(f"  Task ID: {result.id}")
    print(f"  Task State: {result.state}")
    print(f"  Task Ready: {result.ready()}")
    
    return result


def example_priority_task():
    """Example 2: Submit a high-priority task"""
    print("\n" + "="*60)
    print("Example 2: High-Priority Task")
    print("="*60)
    
    from src.tasks.generation_tasks import generate_introduction
    
    print("Submitting high-priority introduction task...")
    result = generate_introduction.apply_async(
        args=["Marie Curie", 1000],
        priority=9  # High priority
    )
    
    print(f"✓ High-priority task submitted!")
    print(f"  Task ID: {result.id}")
    print(f"  Priority: 9 (high)")
    
    return result


def example_batch_task():
    """Example 3: Submit batch chapter generation"""
    print("\n" + "="*60)
    print("Example 3: Batch Task Submission")
    print("="*60)
    
    from src.tasks.generation_tasks import batch_generate_chapters
    
    chapter_specs = [
        {'number': 1, 'title': 'Early Life', 'target_words': 2550},
        {'number': 2, 'title': 'Education', 'target_words': 2550},
        {'number': 3, 'title': 'Scientific Career', 'target_words': 2550},
        {'number': 4, 'title': 'Major Discoveries', 'target_words': 2550},
        {'number': 5, 'title': 'Legacy', 'target_words': 2550},
    ]
    
    print(f"Submitting batch generation for {len(chapter_specs)} chapters...")
    result = batch_generate_chapters.delay(
        character_name="Isaac Newton",
        chapter_specs=chapter_specs,
        batch_size=5
    )
    
    print(f"✓ Batch task submitted!")
    print(f"  Task ID: {result.id}")
    print(f"  Chapters: {len(chapter_specs)}")
    
    return result


def example_validation_task():
    """Example 4: Submit validation task"""
    print("\n" + "="*60)
    print("Example 4: Validation Task")
    print("="*60)
    
    from src.tasks.validation_tasks import validate_chapter_length
    
    # Sample content
    content = " ".join(["word"] * 2550)
    
    print("Submitting chapter length validation task...")
    result = validate_chapter_length.delay(
        chapter_content=content,
        target_length=2550,
        tolerance=0.05
    )
    
    print(f"✓ Validation task submitted!")
    print(f"  Task ID: {result.id}")
    
    return result


def example_export_task():
    """Example 5: Submit export task"""
    print("\n" + "="*60)
    print("Example 5: Export Task")
    print("="*60)
    
    from src.tasks.export_tasks import export_to_markdown
    
    print("Submitting markdown export task...")
    result = export_to_markdown.delay(
        character_name="Ada Lovelace",
        content={'chapters': [], 'metadata': {}}
    )
    
    print(f"✓ Export task submitted!")
    print(f"  Task ID: {result.id}")
    
    return result


def example_monitoring_task():
    """Example 6: Submit monitoring task"""
    print("\n" + "="*60)
    print("Example 6: Monitoring Task")
    print("="*60)
    
    from src.tasks.monitoring_tasks import health_check
    
    print("Submitting health check task...")
    result = health_check.delay()
    
    print(f"✓ Health check task submitted!")
    print(f"  Task ID: {result.id}")
    
    return result


def example_get_result():
    """Example 7: Wait for and retrieve task result"""
    print("\n" + "="*60)
    print("Example 7: Retrieving Task Results")
    print("="*60)
    
    from src.tasks.generation_tasks import generate_chapter
    
    print("Submitting task and waiting for result...")
    result = generate_chapter.delay(
        character_name="Test Person",
        chapter_number=1,
        chapter_title="Test Chapter",
        target_words=100
    )
    
    print(f"  Task ID: {result.id}")
    print(f"  Task State: {result.state}")
    
    try:
        print("\n  Waiting for result (timeout: 10 seconds)...")
        task_result = result.get(timeout=10)
        
        print(f"\n✓ Task completed successfully!")
        print(f"  Character: {task_result['character_name']}")
        print(f"  Chapter: {task_result['chapter_number']}")
        print(f"  Status: {task_result['status']}")
        print(f"  Content preview: {task_result['content'][:100]}...")
        
        return task_result
        
    except Exception as e:
        print(f"\n⚠ Task not completed within timeout: {e}")
        print("  This is expected if no worker is running")
        return None


def example_task_chaining():
    """Example 8: Chain tasks together"""
    print("\n" + "="*60)
    print("Example 8: Task Chaining")
    print("="*60)
    
    from celery import chain
    from src.tasks.generation_tasks import generate_chapter
    from src.tasks.validation_tasks import validate_chapter_length
    
    print("Creating task chain: generate -> validate...")
    
    # Note: This is a simplified example
    # In reality, you'd need to adapt the task signatures
    print("  1. Generate chapter")
    print("  2. Validate chapter length")
    
    # For demonstration only - actual chaining would need task signature adaptation
    result = generate_chapter.delay(
        character_name="Example Person",
        chapter_number=1,
        chapter_title="Example Chapter",
        target_words=100
    )
    
    print(f"\n✓ Chain started!")
    print(f"  Task ID: {result.id}")
    
    return result


def check_celery_connection():
    """Check if Celery can connect to Redis"""
    try:
        import redis
        from src.config import celery_config
        
        # First check Redis connection
        r = redis.Redis(
            host=celery_config.REDIS_HOST,
            port=celery_config.REDIS_PORT,
            db=celery_config.REDIS_DB,
            socket_connect_timeout=2
        )
        
        if not r.ping():
            print("\n✗ Cannot connect to Redis")
            print("  Start Redis with: redis-server")
            print("  Or using Docker: docker run -d -p 6379:6379 redis:7-alpine")
            return False
        
        print(f"\n✓ Connected to Redis ({celery_config.REDIS_HOST}:{celery_config.REDIS_PORT})")
        
        # Then check for active workers
        from src.worker import app
        
        inspector = app.control.inspect(timeout=2.0)
        active_workers = inspector.active()
        
        if active_workers:
            print(f"✓ Connected to Celery")
            print(f"  Active workers: {len(active_workers)}")
            for worker_name in active_workers.keys():
                print(f"    - {worker_name}")
            return True
        else:
            print("\n⚠ No active workers found")
            print("  Start workers with: docker-compose up -d")
            print("  Or see CELERY_TASK_QUEUE.md for manual setup")
            return False
            
    except redis.exceptions.ConnectionError:
        print("\n✗ Cannot connect to Redis")
        print("  Start Redis with: redis-server")
        print("  Or using Docker: docker run -d -p 6379:6379 redis:7-alpine")
        return False
    except Exception as e:
        print(f"\n✗ Error checking connection: {e}")
        return False


def main():
    """Run all examples"""
    print("="*60)
    print("Celery Task Queue - Usage Examples")
    print(f"Started at: {datetime.now().isoformat()}")
    print("="*60)
    
    # Check connection first
    has_connection = check_celery_connection()
    
    if not has_connection:
        print("\n" + "="*60)
        print("⚠ Running in demo mode (Redis not available)")
        print("="*60)
        print("\nTo run these examples with actual execution:")
        print("1. Start Redis: redis-server")
        print("2. Start workers: docker-compose up -d")
        print("3. Run this script again")
        print("\nNote: Task examples below will show how to submit tasks,")
        print("but they won't actually execute without Redis and workers.")
    
    # Run examples with error handling
    tasks = []
    
    try:
        print("\n" + "="*60)
        print("Task Submission Examples")
        print("="*60)
        
        if has_connection:
            tasks.append(("Basic Task", example_basic_task()))
            tasks.append(("Priority Task", example_priority_task()))
            tasks.append(("Batch Task", example_batch_task()))
            tasks.append(("Validation Task", example_validation_task()))
            tasks.append(("Export Task", example_export_task()))
            tasks.append(("Monitoring Task", example_monitoring_task()))
            
            # Try to get a result (requires running worker)
            example_get_result()
            
            # Task chaining example
            example_task_chaining()
        else:
            print("\nSkipping task submissions (no Redis connection)")
            print("See CELERY_TASK_QUEUE.md for setup instructions")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        if not has_connection:
            print("  This is expected without Redis and workers running")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    if tasks:
        print(f"\nSubmitted {len(tasks)} tasks:")
        for name, result in tasks:
            print(f"  • {name}: {result.id} ({result.state})")
    else:
        print("\nNo tasks submitted (Redis not available)")
    
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("\n1. Start Redis: redis-server")
    print("2. Start workers: docker-compose up -d")
    print("3. Monitor tasks in Flower: http://localhost:5555")
    print("4. Check task status:")
    print("   celery -A src.worker inspect active")
    print("5. See CELERY_TASK_QUEUE.md for complete documentation")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
