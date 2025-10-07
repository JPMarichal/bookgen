"""
Tests for Celery task queue functionality
"""
import pytest
from src.tasks.generation_tasks import (
    GenerationTask,
    generate_chapter,
    generate_introduction,
    generate_conclusion
)
from src.tasks.validation_tasks import (
    ValidationTask,
    validate_chapter_length,
    validate_sources,
    validate_content_quality
)
from src.tasks.export_tasks import (
    ExportTask,
    export_to_markdown,
    export_to_word
)
from src.tasks.monitoring_tasks import (
    MonitoringTask,
    health_check,
)


class TestTaskConfiguration:
    """Test task configuration and registration"""
    
    def test_generation_tasks_registered(self):
        """Verify generation tasks are registered"""
        from src.worker import app
        
        assert 'src.tasks.generation_tasks.generate_chapter' in app.tasks
        assert 'src.tasks.generation_tasks.generate_introduction' in app.tasks
        assert 'src.tasks.generation_tasks.generate_conclusion' in app.tasks
    
    def test_validation_tasks_registered(self):
        """Verify validation tasks are registered"""
        from src.worker import app
        
        assert 'src.tasks.validation_tasks.validate_chapter_length' in app.tasks
        assert 'src.tasks.validation_tasks.validate_sources' in app.tasks
        assert 'src.tasks.validation_tasks.validate_content_quality' in app.tasks
    
    def test_export_tasks_registered(self):
        """Verify export tasks are registered"""
        from src.worker import app
        
        assert 'src.tasks.export_tasks.export_to_markdown' in app.tasks
        assert 'src.tasks.export_tasks.export_to_word' in app.tasks
    
    def test_monitoring_tasks_registered(self):
        """Verify monitoring tasks are registered"""
        from src.worker import app
        
        assert 'src.tasks.monitoring_tasks.health_check' in app.tasks
        assert 'src.tasks.monitoring_tasks.get_queue_stats' in app.tasks


class TestTaskPriorities:
    """Test task priority configuration"""
    
    def test_task_priorities_configured(self):
        """Verify that tasks have appropriate priorities"""
        # Check that high-priority tasks have higher priority values
        assert generate_introduction.priority == 6
        assert generate_conclusion.priority == 6
        assert generate_chapter.priority == 5
        
        # Validation tasks should have appropriate priorities
        assert validate_sources.priority == 7
        assert validate_chapter_length.priority == 6


class TestTaskRetryConfiguration:
    """Test task retry configuration"""
    
    def test_generation_task_retry_config(self):
        """Verify generation tasks have retry configured"""
        assert generate_chapter.autoretry_for == (Exception,)
        assert generate_chapter.retry_backoff is True
        assert generate_chapter.retry_jitter is True
        assert generate_chapter.retry_backoff_max == 600
    
    def test_validation_task_retry_config(self):
        """Verify validation tasks have retry configured"""
        assert validate_chapter_length.autoretry_for == (Exception,)
        assert validate_chapter_length.retry_backoff is True
        assert validate_chapter_length.retry_backoff_max == 300


class TestTaskQueues:
    """Test task queue assignments"""
    
    def test_generation_task_queue(self):
        """Verify generation tasks use correct queue"""
        assert generate_chapter.queue == 'content_generation'
        assert generate_introduction.queue == 'content_generation'
    
    def test_validation_task_queue(self):
        """Verify validation tasks use correct queue"""
        assert validate_chapter_length.queue == 'validation'
        assert validate_sources.queue == 'validation'
    
    def test_export_task_queue(self):
        """Verify export tasks use correct queue"""
        assert export_to_markdown.queue == 'export'
        assert export_to_word.queue == 'export'
    
    def test_monitoring_task_queue(self):
        """Verify monitoring tasks use correct queue"""
        assert health_check.queue == 'monitoring'


class TestCeleryConfiguration:
    """Test Celery configuration"""
    
    def test_broker_configured(self):
        """Verify Redis broker is configured"""
        from src.config import celery_config
        
        assert celery_config.BROKER_URL.startswith('redis://')
        assert celery_config.RESULT_BACKEND.startswith('redis://')
    
    def test_queues_configured(self):
        """Verify all required queues are configured"""
        from src.config import celery_config
        
        queue_names = [q.name for q in celery_config.CELERY_TASK_QUEUES]
        
        assert 'high_priority' in queue_names
        assert 'content_generation' in queue_names
        assert 'validation' in queue_names
        assert 'export' in queue_names
        assert 'monitoring' in queue_names
        assert 'default' in queue_names
    
    def test_retry_settings_configured(self):
        """Verify retry settings are configured"""
        from src.config import celery_config
        
        assert celery_config.CELERY_TASK_MAX_RETRIES == 3
        assert celery_config.CELERY_TASK_RETRY_BACKOFF is True
        assert celery_config.CELERY_TASK_RETRY_JITTER is True
        assert celery_config.CELERY_TASK_RETRY_BACKOFF_MAX == 600
    
    def test_task_routes_configured(self):
        """Verify task routing is configured"""
        from src.config import celery_config
        
        routes = celery_config.CELERY_TASK_ROUTES
        
        assert 'src.tasks.generation_tasks.*' in routes
        assert 'src.tasks.validation_tasks.*' in routes
        assert 'src.tasks.export_tasks.*' in routes
        assert 'src.tasks.monitoring_tasks.*' in routes
    
    def test_serialization_configured(self):
        """Verify JSON serialization is configured"""
        from src.config import celery_config
        
        assert celery_config.CELERY_TASK_SERIALIZER == 'json'
        assert celery_config.CELERY_RESULT_SERIALIZER == 'json'
        assert 'json' in celery_config.CELERY_ACCEPT_CONTENT


class TestBaseTaskClasses:
    """Test base task class configuration"""
    
    def test_generation_task_base(self):
        """Verify GenerationTask base class is configured"""
        assert GenerationTask.autoretry_for == (Exception,)
        assert GenerationTask.retry_backoff is True
        assert GenerationTask.retry_jitter is True
    
    def test_validation_task_base(self):
        """Verify ValidationTask base class is configured"""
        assert ValidationTask.autoretry_for == (Exception,)
        assert ValidationTask.retry_backoff is True
        assert ValidationTask.retry_jitter is True
    
    def test_export_task_base(self):
        """Verify ExportTask base class is configured"""
        assert ExportTask.autoretry_for == (Exception,)
        assert ExportTask.retry_backoff is True
        assert ExportTask.retry_jitter is True
    
    def test_monitoring_task_base(self):
        """Verify MonitoringTask base class is configured"""
        assert MonitoringTask.autoretry_for == (Exception,)
        assert MonitoringTask.retry_backoff is True
