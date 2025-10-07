"""
Tests for metrics and monitoring endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestMetrics:
    """Tests for metrics endpoint"""
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint returns Prometheus format"""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        
        content = response.text
        
        # Check for required metrics
        assert "bookgen_uptime_seconds" in content
        assert "bookgen_cpu_percent" in content
        assert "bookgen_memory_percent" in content
        assert "bookgen_disk_percent" in content
        assert "bookgen_jobs_total" in content
        
        # Check for Prometheus format
        assert "# HELP" in content
        assert "# TYPE" in content
    
    def test_metrics_no_rate_limit(self):
        """Test that metrics endpoint is exempt from rate limiting"""
        # Make multiple requests quickly
        for _ in range(10):
            response = client.get("/metrics")
            assert response.status_code == 200
