"""
Unit tests for monitoring tasks
"""
import pytest
from unittest.mock import patch, MagicMock
from src.tasks.monitoring_tasks import (
    MonitoringTask,
    health_check
)


pytestmark = [pytest.mark.unit, pytest.mark.mock]


class TestMonitoringTask:
    """Test MonitoringTask base class"""
    
    def test_monitoring_task_configuration(self):
        """Test MonitoringTask base configuration"""
        task = MonitoringTask()
        assert task.autoretry_for == (Exception,)
        assert task.retry_kwargs == {'max_retries': 2}
        assert task.retry_backoff is True
        assert task.retry_backoff_max == 120
        assert task.retry_jitter is True
    
    def test_on_failure_logging(self):
        """Test on_failure method logs errors"""
        task = MonitoringTask()
        exc = Exception("Monitoring error")
        task_id = "mon-task-123"
        
        with patch('src.tasks.monitoring_tasks.logger') as mock_logger:
            task.on_failure(exc, task_id, [], {}, None)
            mock_logger.error.assert_called_once()


class TestHealthCheck:
    """Test health_check task"""
    
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_success(self, mock_logger):
        """Test successful health check"""
        mock_self = MagicMock()
        mock_self.request.id = "health-123"
        
        result = health_check(mock_self)
        
        assert result['status'] == 'healthy'
        assert 'timestamp' in result
        assert 'task_id' in result
        assert 'checks' in result
    
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_includes_all_checks(self, mock_logger):
        """Test health check includes all required checks"""
        mock_self = MagicMock()
        mock_self.request.id = "health-124"
        
        result = health_check(mock_self)
        
        checks = result.get('checks', {})
        # Should have basic system checks
        assert isinstance(checks, dict)
        assert result['status'] in ['healthy', 'degraded', 'unhealthy']
    
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_multiple_calls(self, mock_logger):
        """Test multiple health check calls"""
        mock_self = MagicMock()
        
        results = []
        for i in range(3):
            mock_self.request.id = f"health-{i}"
            result = health_check(mock_self)
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert 'status' in result
            assert 'timestamp' in result
    
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_timestamp_format(self, mock_logger):
        """Test health check timestamp format"""
        mock_self = MagicMock()
        mock_self.request.id = "health-125"
        
        result = health_check(mock_self)
        
        assert 'timestamp' in result
        # Timestamp should be a string or number
        assert isinstance(result['timestamp'], (str, int, float))


class TestMonitoringTasksIntegration:
    """Integration tests for monitoring tasks"""
    
    @pytest.mark.integration
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_consistency(self, mock_logger):
        """Test health check consistency across calls"""
        mock_self = MagicMock()
        
        # Run multiple health checks
        results = []
        for i in range(5):
            mock_self.request.id = f"consistency-{i}"
            result = health_check(mock_self)
            results.append(result)
        
        # All should have same structure
        for result in results:
            assert set(result.keys()) >= {'status', 'timestamp', 'task_id'}
    
    @pytest.mark.integration
    @patch('src.tasks.monitoring_tasks.logger')
    def test_health_check_logging(self, mock_logger):
        """Test health check logging behavior"""
        mock_self = MagicMock()
        mock_self.request.id = "log-test-123"
        
        result = health_check(mock_self)
        
        # Should log info messages
        assert mock_logger.info.call_count >= 1
        assert result['status'] is not None
