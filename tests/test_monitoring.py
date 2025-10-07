"""
Tests for monitoring and observability features
"""
import pytest
import time
from src.monitoring.prometheus_metrics import (
    MetricsCollector,
    get_metrics_collector,
    increment_counter,
    set_gauge,
    observe_histogram,
    track_generation_time,
    track_api_request,
    track_error
)
from src.monitoring.structured_logger import (
    get_structured_logger,
    set_correlation_id,
    get_correlation_id,
    clear_correlation_id,
    setup_logging
)


class TestPrometheusMetrics:
    """Tests for Prometheus metrics collection"""
    
    def setup_method(self):
        """Reset metrics before each test"""
        collector = get_metrics_collector()
        collector.reset()
    
    def test_counter_increment(self):
        """Test counter increment"""
        increment_counter("test_counter")
        collector = get_metrics_collector()
        assert collector.get_counter("test_counter") == 1.0
        
        increment_counter("test_counter", 5.0)
        assert collector.get_counter("test_counter") == 6.0
    
    def test_counter_with_labels(self):
        """Test counter with labels"""
        increment_counter("test_counter", labels={"type": "success"})
        increment_counter("test_counter", labels={"type": "error"})
        
        collector = get_metrics_collector()
        assert collector.get_counter("test_counter", labels={"type": "success"}) == 1.0
        assert collector.get_counter("test_counter", labels={"type": "error"}) == 1.0
    
    def test_gauge_set(self):
        """Test gauge setting"""
        set_gauge("test_gauge", 42.5)
        collector = get_metrics_collector()
        assert collector.get_gauge("test_gauge") == 42.5
        
        set_gauge("test_gauge", 100.0)
        assert collector.get_gauge("test_gauge") == 100.0
    
    def test_gauge_with_labels(self):
        """Test gauge with labels"""
        set_gauge("test_gauge", 10.0, labels={"service": "api"})
        set_gauge("test_gauge", 20.0, labels={"service": "worker"})
        
        collector = get_metrics_collector()
        assert collector.get_gauge("test_gauge", labels={"service": "api"}) == 10.0
        assert collector.get_gauge("test_gauge", labels={"service": "worker"}) == 20.0
    
    def test_histogram_observe(self):
        """Test histogram observations"""
        observe_histogram("test_histogram", 1.5)
        observe_histogram("test_histogram", 2.5)
        observe_histogram("test_histogram", 3.5)
        
        collector = get_metrics_collector()
        stats = collector.get_histogram_stats("test_histogram")
        
        assert stats["count"] == 3
        assert stats["sum"] == 7.5
        assert stats["min"] == 1.5
        assert stats["max"] == 3.5
        assert stats["avg"] == 2.5
    
    def test_histogram_with_labels(self):
        """Test histogram with labels"""
        observe_histogram("test_histogram", 1.0, labels={"endpoint": "/api/v1"})
        observe_histogram("test_histogram", 2.0, labels={"endpoint": "/api/v1"})
        observe_histogram("test_histogram", 5.0, labels={"endpoint": "/api/v2"})
        
        collector = get_metrics_collector()
        stats_v1 = collector.get_histogram_stats("test_histogram", labels={"endpoint": "/api/v1"})
        stats_v2 = collector.get_histogram_stats("test_histogram", labels={"endpoint": "/api/v2"})
        
        assert stats_v1["count"] == 2
        assert stats_v1["avg"] == 1.5
        assert stats_v2["count"] == 1
        assert stats_v2["avg"] == 5.0
    
    def test_export_prometheus_format(self):
        """Test Prometheus format export"""
        increment_counter("test_counter", labels={"status": "success"})
        set_gauge("test_gauge", 42.0)
        observe_histogram("test_histogram", 1.5)
        
        collector = get_metrics_collector()
        output = collector.export_prometheus_format()
        
        assert "# TYPE test_counter counter" in output
        assert "# TYPE test_gauge gauge" in output
        assert "# TYPE test_histogram histogram" in output
        assert 'test_counter{status="success"} 1' in output
        assert "test_gauge 42.0" in output
        assert "test_histogram_count 1" in output
    
    @pytest.mark.asyncio
    async def test_track_generation_time_success(self):
        """Test generation time tracking decorator - success"""
        @track_generation_time
        async def mock_generation():
            await asyncio.sleep(0.1)
            return "success"
        
        import asyncio
        result = await mock_generation()
        
        assert result == "success"
        
        collector = get_metrics_collector()
        counter = collector.get_counter(
            "bookgen_biography_generation_total",
            labels={"status": "success"}
        )
        assert counter == 1.0
        
        stats = collector.get_histogram_stats(
            "bookgen_biography_generation_seconds",
            labels={"status": "success"}
        )
        assert stats["count"] == 1
        assert stats["avg"] >= 0.1
    
    @pytest.mark.asyncio
    async def test_track_generation_time_error(self):
        """Test generation time tracking decorator - error"""
        @track_generation_time
        async def mock_generation_error():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")
        
        import asyncio
        
        with pytest.raises(ValueError):
            await mock_generation_error()
        
        collector = get_metrics_collector()
        counter = collector.get_counter(
            "bookgen_biography_generation_total",
            labels={"status": "error"}
        )
        assert counter == 1.0
    
    def test_track_error(self):
        """Test error tracking"""
        track_error("validation_error", "source_validation")
        track_error("api_error", "content_generation")
        
        collector = get_metrics_collector()
        
        validation_errors = collector.get_counter(
            "bookgen_errors_total",
            labels={"error_type": "validation_error", "component": "source_validation"}
        )
        api_errors = collector.get_counter(
            "bookgen_errors_total",
            labels={"error_type": "api_error", "component": "content_generation"}
        )
        
        assert validation_errors == 1.0
        assert api_errors == 1.0


class TestStructuredLogger:
    """Tests for structured logging"""
    
    def test_correlation_id_set_and_get(self):
        """Test setting and getting correlation ID"""
        correlation_id = set_correlation_id("test-correlation-id")
        assert correlation_id == "test-correlation-id"
        assert get_correlation_id() == "test-correlation-id"
    
    def test_correlation_id_auto_generate(self):
        """Test auto-generation of correlation ID"""
        correlation_id = set_correlation_id()
        assert correlation_id is not None
        assert len(correlation_id) == 36  # UUID format
        assert get_correlation_id() == correlation_id
    
    def test_correlation_id_clear(self):
        """Test clearing correlation ID"""
        set_correlation_id("test-id")
        assert get_correlation_id() == "test-id"
        
        clear_correlation_id()
        assert get_correlation_id() is None
    
    def test_structured_logger_creation(self):
        """Test creating structured logger"""
        logger = get_structured_logger("test.logger")
        assert logger is not None
        assert logger.logger.name == "test.logger"
    
    def test_structured_logger_methods(self):
        """Test structured logger logging methods"""
        logger = get_structured_logger("test.logger")
        
        # These should not raise exceptions
        logger.debug("Debug message", key="value")
        logger.info("Info message", user_id=123)
        logger.warning("Warning message", component="test")
        logger.error("Error message", error_code="500")
        logger.critical("Critical message", severity="high")
    
    def test_setup_logging(self):
        """Test logging setup"""
        # Should not raise exceptions
        setup_logging(level="INFO", json_format=True, app_name="test-app")
        setup_logging(level="DEBUG", json_format=False, app_name="test-app")


class TestMetricsIntegration:
    """Integration tests for metrics"""
    
    def setup_method(self):
        """Reset metrics before each test"""
        collector = get_metrics_collector()
        collector.reset()
    
    def test_multiple_metrics_together(self):
        """Test using multiple metric types together"""
        # Simulate API requests
        for i in range(10):
            increment_counter("api_requests", labels={"endpoint": "/api/v1", "status": "2xx"})
            observe_histogram("api_duration", 0.1 * (i + 1), labels={"endpoint": "/api/v1"})
        
        # Add some errors
        for i in range(2):
            increment_counter("api_requests", labels={"endpoint": "/api/v1", "status": "5xx"})
            observe_histogram("api_duration", 0.5, labels={"endpoint": "/api/v1"})
        
        # Set system metrics
        set_gauge("cpu_usage", 45.5)
        set_gauge("memory_usage", 62.3)
        
        collector = get_metrics_collector()
        
        # Verify counters
        success_count = collector.get_counter("api_requests", labels={"endpoint": "/api/v1", "status": "2xx"})
        error_count = collector.get_counter("api_requests", labels={"endpoint": "/api/v1", "status": "5xx"})
        assert success_count == 10.0
        assert error_count == 2.0
        
        # Verify histogram
        stats = collector.get_histogram_stats("api_duration", labels={"endpoint": "/api/v1"})
        assert stats["count"] == 12
        
        # Verify gauges
        assert collector.get_gauge("cpu_usage") == 45.5
        assert collector.get_gauge("memory_usage") == 62.3
        
        # Verify export
        output = collector.export_prometheus_format()
        assert "api_requests" in output
        assert "api_duration" in output
        assert "cpu_usage" in output
        assert "memory_usage" in output
