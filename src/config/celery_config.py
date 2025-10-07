"""
Celery Configuration
Configuration for Celery workers and task queue
"""
import os
from kombu import Queue, Exchange

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Build Redis URL
if REDIS_PASSWORD:
    BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

RESULT_BACKEND = BROKER_URL

# Task serialization
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task routing and priority queues
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'tasks'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'task.default'

# Define specialized queues with priorities
CELERY_TASK_QUEUES = (
    Queue('high_priority', Exchange('tasks'), routing_key='task.high',
          queue_arguments={'x-max-priority': 10}),
    Queue('content_generation', Exchange('tasks'), routing_key='task.generation',
          queue_arguments={'x-max-priority': 10}),
    Queue('validation', Exchange('tasks'), routing_key='task.validation',
          queue_arguments={'x-max-priority': 10}),
    Queue('export', Exchange('tasks'), routing_key='task.export',
          queue_arguments={'x-max-priority': 10}),
    Queue('monitoring', Exchange('tasks'), routing_key='task.monitoring',
          queue_arguments={'x-max-priority': 10}),
    Queue('default', Exchange('tasks'), routing_key='task.default',
          queue_arguments={'x-max-priority': 10}),
)

# Task routes - map tasks to specific queues
CELERY_TASK_ROUTES = {
    'src.tasks.generation_tasks.*': {'queue': 'content_generation'},
    'src.tasks.validation_tasks.*': {'queue': 'validation'},
    'src.tasks.export_tasks.*': {'queue': 'export'},
    'src.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
}

# Retry configuration with exponential backoff
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Retry settings
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
CELERY_TASK_RETRY_BACKOFF = True
CELERY_TASK_RETRY_BACKOFF_MAX = 600  # 10 minutes
CELERY_TASK_RETRY_JITTER = True

# Task time limits
CELERY_TASK_TIME_LIMIT = 3600  # 1 hour hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 3000  # 50 minutes soft limit

# Result backend settings
CELERY_RESULT_EXPIRES = 86400  # Results expire after 24 hours
CELERY_RESULT_PERSISTENT = True
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'master_name': 'mymaster',
    'visibility_timeout': 3600,
}

# Worker settings
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after 1000 tasks
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Dead Letter Queue configuration
CELERY_TASK_DEAD_LETTER_QUEUE = 'failed_tasks'
CELERY_TASK_DEAD_LETTER_EXCHANGE = 'failed'

# Monitoring
CELERY_SEND_EVENTS = True
CELERY_TRACK_STARTED = True

# Beat schedule for periodic tasks (if needed)
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-results': {
        'task': 'src.tasks.monitoring_tasks.cleanup_expired_results',
        'schedule': 3600.0,  # Every hour
    },
    'health-check': {
        'task': 'src.tasks.monitoring_tasks.health_check',
        'schedule': 300.0,  # Every 5 minutes
    },
}
