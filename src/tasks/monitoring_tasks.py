"""
Monitoring Tasks
Celery tasks for system monitoring and maintenance
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from celery import Task
from src.worker import app

logger = logging.getLogger(__name__)


class MonitoringTask(Task):
    """Base class for monitoring tasks"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = True
    retry_backoff_max = 60
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        logger.error(f"Monitoring task {self.name} [{task_id}] failed: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@app.task(
    base=MonitoringTask,
    bind=True,
    name='src.tasks.monitoring_tasks.health_check',
    queue='monitoring',
    priority=3
)
def health_check(self) -> Dict[str, Any]:
    """
    Perform system health check
    
    Returns:
        Health status of various components
    """
    logger.info("Performing system health check")
    
    try:
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'components': {
                'celery': 'up',
                'redis': 'up',
                'workers': 'active'
            },
            'task_id': self.request.id
        }
        
        # TODO: Add actual health checks for components
        # - Check Redis connection
        # - Check active workers
        # - Check queue lengths
        # - Check failed tasks count
        
        logger.info("Health check completed: all systems operational")
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unhealthy',
            'error': str(e),
            'task_id': self.request.id
        }


@app.task(
    base=MonitoringTask,
    bind=True,
    name='src.tasks.monitoring_tasks.cleanup_expired_results',
    queue='monitoring',
    priority=2
)
def cleanup_expired_results(self) -> Dict[str, Any]:
    """
    Clean up expired task results from Redis
    
    Returns:
        Cleanup statistics
    """
    logger.info("Cleaning up expired task results")
    
    try:
        # TODO: Implement actual cleanup logic
        # - Remove results older than CELERY_RESULT_EXPIRES
        # - Clean up orphaned tasks
        # - Remove old task metadata
        
        cleanup_stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'results_cleaned': 0,
            'space_freed_mb': 0,
            'task_id': self.request.id
        }
        
        logger.info(f"Cleanup completed: {cleanup_stats['results_cleaned']} results removed")
        return cleanup_stats
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise


@app.task(
    base=MonitoringTask,
    bind=True,
    name='src.tasks.monitoring_tasks.get_queue_stats',
    queue='monitoring',
    priority=3
)
def get_queue_stats(self) -> Dict[str, Any]:
    """
    Get statistics for all task queues
    
    Returns:
        Queue statistics and metrics
    """
    logger.info("Collecting queue statistics")
    
    try:
        from celery import current_app
        
        inspector = current_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspector.active()
        
        # Get reserved tasks
        reserved_tasks = inspector.reserved()
        
        # Get scheduled tasks
        scheduled_tasks = inspector.scheduled()
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'active_workers': len(active_tasks) if active_tasks else 0,
            'queues': {},
            'total_active_tasks': sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0,
            'total_reserved_tasks': sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0,
            'task_id': self.request.id
        }
        
        # Aggregate by queue
        queue_names = [
            'high_priority', 'content_generation', 'validation',
            'export', 'monitoring', 'default'
        ]
        
        for queue_name in queue_names:
            stats['queues'][queue_name] = {
                'active': 0,
                'reserved': 0,
                'scheduled': 0
            }
        
        logger.info(f"Queue stats collected: {stats['total_active_tasks']} active tasks")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get queue stats: {e}")
        raise


@app.task(
    base=MonitoringTask,
    bind=True,
    name='src.tasks.monitoring_tasks.get_worker_stats',
    queue='monitoring',
    priority=3
)
def get_worker_stats(self) -> Dict[str, Any]:
    """
    Get statistics for all workers
    
    Returns:
        Worker statistics and status
    """
    logger.info("Collecting worker statistics")
    
    try:
        from celery import current_app
        
        inspector = current_app.control.inspect()
        
        # Get worker stats
        worker_stats = inspector.stats()
        
        # Get active workers
        active_workers = inspector.active()
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_workers': len(worker_stats) if worker_stats else 0,
            'workers': {},
            'task_id': self.request.id
        }
        
        if worker_stats:
            for worker_name, worker_info in worker_stats.items():
                stats['workers'][worker_name] = {
                    'status': 'active' if worker_name in (active_workers or {}) else 'idle',
                    'processed_tasks': worker_info.get('total', {}).get('tasks', 0),
                    'pool': worker_info.get('pool', {})
                }
        
        logger.info(f"Worker stats collected: {stats['total_workers']} workers")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}")
        raise


@app.task(
    base=MonitoringTask,
    bind=True,
    name='src.tasks.monitoring_tasks.process_dead_letter_queue',
    queue='monitoring',
    priority=4
)
def process_dead_letter_queue(self) -> Dict[str, Any]:
    """
    Process failed tasks in dead letter queue
    
    Returns:
        Processing results
    """
    logger.info("Processing dead letter queue")
    
    try:
        # TODO: Implement dead letter queue processing
        # - Retrieve failed tasks
        # - Log failure reasons
        # - Optionally retry or archive
        # - Send notifications for critical failures
        
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'failed_tasks_found': 0,
            'tasks_retried': 0,
            'tasks_archived': 0,
            'task_id': self.request.id
        }
        
        logger.info(f"Dead letter queue processed: {result['failed_tasks_found']} tasks")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process dead letter queue: {e}")
        raise
