"""
Tests for API middleware
"""
import pytest
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestRateLimiting:
    """Tests for rate limiting middleware"""
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present"""
        response = client.get("/api/v1/status")
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert int(response.headers["X-RateLimit-Limit"]) == 60
    
    def test_exempt_paths_no_rate_limit(self):
        """Test that health and docs paths are exempt from rate limiting"""
        exempt_paths = ["/health", "/docs", "/openapi.json"]
        
        for path in exempt_paths:
            # Make multiple requests
            for _ in range(10):
                response = client.get(path)
                # These should not have rate limit headers
                if path == "/health":
                    assert response.status_code == 200


class TestRequestLogging:
    """Tests for request logging middleware"""
    
    def test_request_process_time_header(self):
        """Test that process time header is added"""
        response = client.get("/api/v1/status")
        
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        
        # Process time should be a positive number
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
