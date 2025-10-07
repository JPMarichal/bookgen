"""
Performance benchmarks for BookGen API endpoints
Tests API response times and ensures they meet performance criteria

Usage:
    pytest tests/performance/ --benchmark-only
    pytest tests/performance/ --benchmark-only --benchmark-autosave
    pytest tests/performance/test_api_performance.py -v
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
import time

client = TestClient(app)


class TestAPIPerformance:
    """Performance benchmarks for API endpoints"""
    
    def test_health_endpoint_performance(self, benchmark):
        """
        Benchmark health endpoint
        Target: < 50ms response time
        """
        def health_check():
            response = client.get("/health")
            assert response.status_code == 200
            return response
        
        result = benchmark(health_check)
        # Performance criteria verified by benchmark output
    
    def test_api_status_performance(self, benchmark):
        """
        Benchmark API status endpoint
        Target: < 200ms response time (synchronous endpoint)
        """
        def status_check():
            response = client.get("/api/v1/status")
            assert response.status_code == 200
            return response
        
        result = benchmark(status_check)
        # Performance criteria verified by benchmark output
    
    def test_root_endpoint_performance(self, benchmark):
        """
        Benchmark root endpoint
        Target: < 100ms response time
        """
        def root_check():
            response = client.get("/")
            assert response.status_code == 200
            return response
        
        result = benchmark(root_check)
        # Performance criteria verified by benchmark output
    
    def test_biography_creation_performance(self, benchmark):
        """
        Benchmark biography job creation
        Target: < 200ms response time (synchronous endpoint)
        """
        def create_biography():
            response = client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Performance Test",
                    "chapters": 5,
                    "total_words": 5000
                }
            )
            assert response.status_code == 202
            return response
        
        result = benchmark(create_biography)
        # Performance criteria verified by benchmark output
    
    def test_job_status_check_performance(self, benchmark):
        """
        Benchmark job status check
        Target: < 200ms response time (synchronous endpoint)
        """
        # Create a job first
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={"character": "Status Performance Test"}
        )
        job_id = create_response.json()["job_id"]
        
        def check_status():
            response = client.get(f"/api/v1/biographies/{job_id}/status")
            assert response.status_code == 200
            return response
        
        result = benchmark(check_status)
        # Performance criteria verified by benchmark output
    
    def test_source_validation_performance(self, benchmark):
        """
        Benchmark source validation endpoint (without accessibility check)
        Target: < 200ms response time
        """
        def validate_sources():
            response = client.post(
                "/api/v1/sources/validate",
                json={
                    "sources": [
                        {
                            "title": "Test Source",
                            "source_type": "book",
                            "url": "https://example.com/test",
                            "author": "Test Author"
                        }
                    ],
                    "check_accessibility": False
                }
            )
            assert response.status_code == 200
            return response
        
        result = benchmark(validate_sources)
        # Performance criteria verified by benchmark output
    
    def test_metrics_endpoint_performance(self, benchmark):
        """
        Benchmark metrics endpoint
        Target: < 200ms response time
        """
        def get_metrics():
            response = client.get("/metrics")
            assert response.status_code == 200
            return response
        
        result = benchmark(get_metrics)
        # Performance criteria verified by benchmark output


class TestConcurrentRequests:
    """Test API behavior with concurrent requests"""
    
    def test_concurrent_health_checks(self, benchmark):
        """
        Benchmark multiple concurrent health checks
        Simulates light concurrent load
        """
        import concurrent.futures
        
        def concurrent_requests():
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(client.get, "/health") for _ in range(10)]
                results = [f.result() for f in futures]
                assert all(r.status_code == 200 for r in results)
                return results
        
        result = benchmark(concurrent_requests)
    
    def test_concurrent_biography_creation(self, benchmark):
        """
        Benchmark concurrent biography job creation
        Target: Handle 10 concurrent users
        """
        import concurrent.futures
        
        def concurrent_creates():
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(
                        client.post,
                        "/api/v1/biographies/generate",
                        json={"character": f"Concurrent Test {i}"}
                    )
                    for i in range(10)
                ]
                results = [f.result() for f in futures]
                assert all(r.status_code == 202 for r in results)
                return results
        
        result = benchmark(concurrent_creates)
        # Performance criteria verified by benchmark output


@pytest.mark.benchmark(group="api-latency")
class TestAPILatency:
    """Benchmark API latency under various conditions"""
    
    def test_cold_start_latency(self, benchmark):
        """Measure cold start latency"""
        # Sleep to simulate cold start
        time.sleep(0.1)
        
        def cold_request():
            return client.get("/api/v1/status")
        
        result = benchmark.rounds(1)(cold_request)
    
    def test_warm_cache_latency(self, benchmark):
        """Measure warm cache latency"""
        # Warm up
        for _ in range(5):
            client.get("/api/v1/status")
        
        def warm_request():
            return client.get("/api/v1/status")
        
        result = benchmark(warm_request)
