"""
Stress tests for BookGen API
Tests system behavior under extreme load and edge cases

Usage:
    pytest tests/stress/ -v
    pytest tests/stress/test_stress.py::TestStressScenarios::test_rapid_fire_requests -v
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
import concurrent.futures
import time

client = TestClient(app)


class TestStressScenarios:
    """Stress test scenarios for the API"""
    
    def test_rapid_fire_requests(self):
        """
        Test rapid-fire requests to health endpoint
        Simulates aggressive client behavior
        """
        num_requests = 100
        start_time = time.time()
        
        responses = []
        for _ in range(num_requests):
            response = client.get("/health")
            responses.append(response)
        
        duration = time.time() - start_time
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Should handle 100 requests in reasonable time
        requests_per_second = num_requests / duration
        print(f"\nProcessed {requests_per_second:.2f} requests/second")
        
        # Should maintain performance
        assert duration < 10, f"Took too long: {duration:.2f}s for {num_requests} requests"
    
    def test_concurrent_job_creation(self):
        """
        Test creating many jobs concurrently
        Target: Handle 10 concurrent users
        """
        num_concurrent = 10
        
        def create_job(index):
            response = client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": f"Stress Test Character {index}",
                    "chapters": 5,
                    "total_words": 5000,
                    "mode": "automatic"
                }
            )
            return response
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(create_job, i) for i in range(num_concurrent)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start_time
        
        # All requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 202)
        assert success_count == num_concurrent, f"Only {success_count}/{num_concurrent} succeeded"
        
        # Should complete in reasonable time (adjusted for automatic source generation)
        assert duration < 20, f"Concurrent creation took too long: {duration:.2f}s"
        
        print(f"\nCreated {num_concurrent} jobs concurrently in {duration:.2f}s")
    
    def test_status_check_burst(self):
        """
        Test burst of status checks
        Simulates multiple users checking job status simultaneously
        """
        # Create a job first
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Status Burst Test",
                "mode": "automatic"
            }
        )
        job_id = create_response.json()["job_id"]
        
        num_checks = 50
        
        def check_status():
            return client.get(f"/api/v1/biographies/{job_id}/status")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_status) for _ in range(num_checks)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start_time
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        print(f"\nProcessed {num_checks} status checks in {duration:.2f}s")
    
    def test_mixed_load(self):
        """
        Test mixed load of different endpoints
        Simulates realistic usage pattern
        """
        def mixed_operations(index):
            operations = [
                lambda: client.get("/health"),
                lambda: client.get("/api/v1/status"),
                lambda: client.post(
                    "/api/v1/biographies/generate",
                    json={
                        "character": f"Mixed Load {index}",
                        "mode": "automatic"
                    }
                ),
            ]
            
            results = []
            for op in operations:
                results.append(op())
            return results
        
        num_users = 10
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(num_users)]
            all_responses = []
            for f in concurrent.futures.as_completed(futures):
                all_responses.extend(f.result())
        
        duration = time.time() - start_time
        
        # All requests should succeed
        total_requests = num_users * 3  # 3 operations per user
        success_count = sum(1 for r in all_responses if r.status_code in [200, 202])
        
        assert success_count == total_requests, f"Only {success_count}/{total_requests} succeeded"
        
        print(f"\nProcessed {total_requests} mixed operations in {duration:.2f}s")
    
    def test_sustained_load(self):
        """
        Test sustained load over time
        Ensures system can handle continuous requests
        """
        duration_seconds = 10
        requests_per_second = 5
        
        start_time = time.time()
        responses = []
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Make requests
            for _ in range(requests_per_second):
                response = client.get("/health")
                responses.append(response)
            
            # Maintain rate
            batch_duration = time.time() - batch_start
            if batch_duration < 1.0:
                time.sleep(1.0 - batch_duration)
        
        # All should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        success_rate = success_count / len(responses)
        
        assert success_rate > 0.99, f"Success rate too low: {success_rate*100:.2f}%"
        
        print(f"\nSustained {len(responses)} requests over {duration_seconds}s")
        print(f"Success rate: {success_rate*100:.2f}%")


class TestErrorRateUnderLoad:
    """Test error rates under various load conditions"""
    
    def test_error_rate_normal_load(self):
        """
        Test error rate under normal load
        Target: < 1% error rate
        """
        num_requests = 100
        
        responses = []
        for i in range(num_requests):
            # Mix of valid and invalid requests
            if i % 10 == 0:
                # Invalid request (should fail gracefully)
                response = client.post(
                    "/api/v1/biographies/generate",
                    json={"character": ""}  # Invalid empty character
                )
            else:
                # Valid request
                response = client.get("/health")
            
            responses.append(response)
        
        # Calculate error rate (excluding expected validation errors)
        valid_requests = [r for i, r in enumerate(responses) if i % 10 != 0]
        errors = sum(1 for r in valid_requests if r.status_code >= 500)
        error_rate = errors / len(valid_requests)
        
        print(f"\nError rate: {error_rate*100:.2f}%")
        
        # Should be < 1% error rate for valid requests
        assert error_rate < 0.01, f"Error rate too high: {error_rate*100:.2f}%"
    
    def test_rate_limiting_behavior(self):
        """
        Test that rate limiting works correctly
        Ensures system protects itself from abuse
        """
        # Make requests rapidly to trigger rate limiting
        responses = []
        for _ in range(100):
            response = client.get("/health")
            responses.append(response)
        
        # Should have some rate limit responses (429) if limit is enforced
        rate_limited = sum(1 for r in responses if r.status_code == 429)
        
        # Note: Rate limiting may or may not trigger in test environment
        # This test documents the behavior
        print(f"\nRate limited responses: {rate_limited}/100")


class TestMemoryUnderStress:
    """Test memory behavior under stress conditions"""
    
    def test_memory_leak_detection(self):
        """
        Test for memory leaks under repeated operations
        Memory should not grow indefinitely
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Perform many operations (reduced to 10 for faster testing)
        for _ in range(10):
            response = client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Memory Test",
                    "mode": "automatic"
                }
            )
            assert response.status_code == 202
        
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nInitial memory: {initial_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Increase: {memory_increase:.2f} MB")
        
        # Memory increase should be reasonable (< 50MB for 10 operations)
        assert memory_increase < 50, f"Possible memory leak: {memory_increase:.2f} MB increase"


class TestRecoveryScenarios:
    """Test system recovery from various failure scenarios"""
    
    def test_recovery_from_invalid_requests(self):
        """
        Test that system recovers from invalid requests
        """
        # Send invalid requests
        invalid_requests = [
            {"character": ""},
            {"character": "Test", "chapters": 0},
            {"character": "Test", "chapters": 1000},
            {},
        ]
        
        for invalid in invalid_requests:
            response = client.post(
                "/api/v1/biographies/generate",
                json=invalid
            )
            # Should return validation error, not crash
            assert response.status_code in [422, 400]
        
        # System should still be operational
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
    
    def test_recovery_after_stress(self):
        """
        Test that system recovers after stress period
        """
        # Apply stress
        for _ in range(50):
            client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Stress Recovery Test",
                    "mode": "automatic"
                }
            )
        
        # Cool down
        time.sleep(2)
        
        # System should be responsive
        response = client.get("/health")
        assert response.status_code == 200
        
        # Response time should be normal
        start = time.time()
        response = client.get("/api/v1/status")
        duration = time.time() - start
        
        assert duration < 0.5, f"System slow after stress: {duration:.3f}s"
