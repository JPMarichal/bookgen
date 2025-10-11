"""
BookGen Sistema Automatizado - Celery Worker
Background worker for content generation tasks using Celery
"""
import os
import logging
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery('bookgen')

# Load configuration from celery_config module
app.config_from_object('src.config.celery_config')

# Auto-discover tasks in tasks modules
app.autodiscover_tasks([
    'src.tasks.generation_tasks',
    'src.tasks.validation_tasks',
    'src.tasks.export_tasks',
    'src.tasks.monitoring_tasks',
])


@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    """Called when worker is ready to accept tasks"""
    worker_id = os.getenv("WORKER_ID", "unknown")
    worker_type = os.getenv("WORKER_TYPE", "general")
    logger.info(f"Worker {worker_id} ({worker_type}) is ready to accept tasks")


@worker_shutdown.connect
def on_worker_shutdown(sender=None, **kwargs):
    """Called when worker is shutting down"""
    worker_id = os.getenv("WORKER_ID", "unknown")
    logger.info(f"Worker {worker_id} is shutting down")


if __name__ == '__main__':
    # Start worker with appropriate settings
    worker_type = os.getenv("WORKER_TYPE", "general")
    
    # Configure worker based on type
    worker_config = {
        'loglevel': 'INFO',
        'traceback': True,
        'send_events': True,
        'without_gossip': False,
        'without_mingle': False,
        'without_heartbeat': False,
    }
    
    # Add queue configuration based on worker type
    if worker_type == 'content_generator':
        worker_config['queues'] = ['content_generation', 'high_priority']
    elif worker_type == 'validator':
        worker_config['queues'] = ['validation']
    elif worker_type == 'exporter':
        worker_config['queues'] = ['export']
    elif worker_type == 'monitor':
        worker_config['queues'] = ['monitoring']
    else:
        worker_config['queues'] = ['default']
    
    logger.info(f"Starting {worker_type} worker with queues: {worker_config['queues']}")

    # Build CLI arguments with correct flag placement
    worker_args: list[str] = []

    if worker_config.get('traceback'):
        worker_args.append('--traceback')

    worker_args.extend([
        'worker',
        f"--loglevel={worker_config['loglevel']}",
        f"--queues={','.join(worker_config['queues'])}"
    ])

    if worker_config.get('send_events'):
        worker_args.append('--events')
    if worker_config.get('without_gossip'):
        worker_args.append('--without-gossip')
    if worker_config.get('without_mingle'):
        worker_args.append('--without-mingle')
    if worker_config.get('without_heartbeat'):
        worker_args.append('--without-heartbeat')

    app.worker_main(worker_args)

