# Celery Task Queue System

This document describes the asynchronous task queue system implemented using Celery and Redis for the BookGen project.

## Overview

The task queue system provides:
- **Asynchronous task execution** - Non-blocking content generation and processing
- **Specialized workers** - Different worker types for different task categories
- **Priority queues** - High-priority tasks are processed first
- **Automatic retry** - Failed tasks are retried with exponential backoff
- **Dead letter queue** - Failed tasks after all retries are logged and stored
- **Real-time monitoring** - Track task status and worker health via Flower

## Architecture

### Queues

The system uses 6 specialized queues:

1. **high_priority** - Urgent tasks that need immediate processing
2. **content_generation** - Chapter and content generation tasks
3. **validation** - Content and source validation tasks
4. **export** - Document export tasks (Markdown, Word, PDF)
5. **monitoring** - System health checks and maintenance tasks
6. **default** - Fallback queue for general tasks

All queues support priority levels from 0-10 (10 being highest priority).

### Workers

Four specialized worker types are configured:

1. **Content Generator Worker** - Processes content generation tasks
   - Listens to: `content_generation`, `high_priority`
   - Concurrency: 2

2. **Validator Worker** - Processes validation tasks
   - Listens to: `validation`
   - Concurrency: 2

3. **Exporter Worker** - Processes export tasks
   - Listens to: `export`
   - Concurrency: 1

4. **Monitor Worker** - Processes monitoring tasks
   - Listens to: `monitoring`
   - Concurrency: 1

## Setup

### Prerequisites

- Redis server (v5.0+)
- Python 3.8+
- Required packages: `celery>=5.3.4`, `redis>=5.0.1`, `flower>=2.0.1`

### Configuration

Redis configuration is set via environment variables:

```bash
REDIS_HOST=localhost      # Redis server host
REDIS_PORT=6379          # Redis server port
REDIS_DB=0               # Redis database number
REDIS_PASSWORD=          # Redis password (optional)
```

### Running with Docker Compose

The easiest way to start all services:

```bash
docker-compose up -d
```

This starts:
- Redis server
- BookGen API
- 4 specialized Celery workers
- Flower monitoring UI

### Manual Setup

#### 1. Start Redis

```bash
redis-server
```

Or using Docker:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### 2. Start Celery Workers

Start specialized workers in separate terminals:

```bash
# Content generation worker
celery -A src.worker worker --loglevel=info \
  --queues=content_generation,high_priority \
  --concurrency=2 --hostname=content@%h

# Validation worker
celery -A src.worker worker --loglevel=info \
  --queues=validation --concurrency=2 --hostname=validation@%h

# Export worker
celery -A src.worker worker --loglevel=info \
  --queues=export --concurrency=1 --hostname=export@%h

# Monitoring worker
celery -A src.worker worker --loglevel=info \
  --queues=monitoring --concurrency=1 --hostname=monitoring@%h
```

#### 3. Start Flower (Optional - for monitoring)

```bash
celery -A src.worker flower --port=5555
```

Access Flower UI at: http://localhost:5555

## Usage

### Submitting Tasks

#### From Python Code

```python
from src.tasks.generation_tasks import generate_chapter

# Submit task asynchronously
result = generate_chapter.delay(
    character_name="Albert Einstein",
    chapter_number=1,
    chapter_title="Early Life",
    target_words=2550
)

# Get task ID
task_id = result.id

# Check task state
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY

# Wait for result (blocking)
chapter_data = result.get(timeout=300)
```

#### With Priority

```python
# Submit with custom priority (0-10, higher is more urgent)
result = generate_chapter.apply_async(
    args=["Albert Einstein", 1, "Early Life", 2550],
    priority=9
)
```

#### Batch Operations

```python
from src.tasks.generation_tasks import batch_generate_chapters

chapter_specs = [
    {'number': 1, 'title': 'Early Life', 'target_words': 2550},
    {'number': 2, 'title': 'Education', 'target_words': 2550},
    {'number': 3, 'title': 'Career', 'target_words': 2550},
]

result = batch_generate_chapters.delay(
    character_name="Albert Einstein",
    chapter_specs=chapter_specs,
    batch_size=5
)
```

### Available Tasks

#### Generation Tasks

- `generate_chapter` - Generate a single chapter
- `generate_introduction` - Generate introduction section
- `generate_conclusion` - Generate conclusion section
- `regenerate_chapter` - Regenerate a chapter with feedback
- `batch_generate_chapters` - Generate multiple chapters in batch

#### Validation Tasks

- `validate_chapter_length` - Validate chapter word count
- `validate_sources` - Validate biographical sources
- `validate_content_quality` - Validate content formatting and quality
- `validate_complete_biography` - Validate entire biography

#### Export Tasks

- `export_to_markdown` - Export to Markdown format
- `export_to_word` - Export to Word (DOCX) format
- `export_to_pdf` - Export to PDF format
- `export_all_formats` - Export to all supported formats

#### Monitoring Tasks

- `health_check` - System health check
- `get_queue_stats` - Get queue statistics
- `get_worker_stats` - Get worker statistics
- `cleanup_expired_results` - Clean up old task results
- `process_dead_letter_queue` - Process failed tasks

## Monitoring

### Using Flower

Access the Flower web UI at http://localhost:5555 to:
- View active tasks
- Monitor worker status
- See task history
- View task details and results
- Restart workers

### Using Celery CLI

```bash
# View active tasks
celery -A src.worker inspect active

# View registered tasks
celery -A src.worker inspect registered

# View worker statistics
celery -A src.worker inspect stats

# View scheduled tasks
celery -A src.worker inspect scheduled

# View reserved tasks
celery -A src.worker inspect reserved

# Ping workers
celery -A src.worker inspect ping
```

### Using Redis CLI

```bash
# Connect to Redis
redis-cli

# View all keys
KEYS *

# Get queue length
LLEN celery

# Monitor commands in real-time
MONITOR
```

## Retry Behavior

Tasks are automatically retried on failure with exponential backoff:

- **Max retries**: 3
- **Initial delay**: 60 seconds
- **Backoff multiplier**: 2x (exponential)
- **Max delay**: 600 seconds (10 minutes)
- **Jitter**: Random variation to prevent thundering herd

Example retry timeline:
1. First attempt fails
2. Wait ~60s, retry (attempt 2)
3. Wait ~120s, retry (attempt 3)
4. Wait ~240s, final retry (attempt 4)
5. If still fails, move to dead letter queue

## Dead Letter Queue

Failed tasks (after all retries) are:
1. Logged with full error details
2. Stored in Redis for later analysis
3. Optionally sent to notification system
4. Can be manually retried or archived

Process dead letter queue:

```python
from src.tasks.monitoring_tasks import process_dead_letter_queue

result = process_dead_letter_queue.delay()
```

## Best Practices

1. **Use appropriate queues** - Route tasks to specialized queues
2. **Set priorities** - Use priority for time-sensitive tasks
3. **Monitor regularly** - Check Flower and logs for issues
4. **Handle failures** - Implement proper error handling in task code
5. **Limit task size** - Keep task payloads small, use references
6. **Use timeouts** - Set appropriate soft/hard time limits
7. **Clean up results** - Expired results are cleaned automatically

## Configuration Reference

Key configuration options in `src/config/celery_config.py`:

```python
# Retry settings
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_BACKOFF = True
CELERY_TASK_RETRY_BACKOFF_MAX = 600  # seconds
CELERY_TASK_RETRY_JITTER = True

# Time limits
CELERY_TASK_TIME_LIMIT = 3600  # 1 hour hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 3000  # 50 minutes soft limit

# Result expiry
CELERY_RESULT_EXPIRES = 86400  # 24 hours

# Worker settings
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart after N tasks
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Tasks to prefetch
```

## Troubleshooting

### Workers not processing tasks

1. Check Redis is running: `redis-cli ping`
2. Verify workers are active: `celery -A src.worker inspect active`
3. Check worker logs for errors
4. Verify queue names match between tasks and workers

### Tasks stuck in PENDING state

1. Ensure workers are running
2. Check workers are listening to correct queue
3. Verify Redis connection is working
4. Check for task serialization errors in logs

### High memory usage

1. Reduce `CELERY_WORKER_PREFETCH_MULTIPLIER`
2. Decrease worker concurrency
3. Enable `CELERY_WORKER_MAX_TASKS_PER_CHILD`
4. Clean up expired results more frequently

### Slow task processing

1. Increase worker concurrency
2. Add more worker instances
3. Use priority queues for urgent tasks
4. Check for database/API bottlenecks in task code

## Testing

Run task queue tests:

```bash
# Run all task tests
pytest tests/test_tasks.py -v

# Test Celery setup
python test_celery_setup.py
```

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Flower Documentation](https://flower.readthedocs.io/)
