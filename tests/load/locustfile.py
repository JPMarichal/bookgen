"""
Locust load testing for BookGen API
Tests concurrent users, API latency, and system behavior under load

Usage:
    locust -f tests/load/locustfile.py --host=http://localhost:8000
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2
"""
from locust import HttpUser, task, between, events
import json
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BookGenUser(HttpUser):
    """Simulates a BookGen API user"""
    
    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)
    
    # Store created job IDs for status checks
    job_ids = []
    
    def on_start(self):
        """Called when a simulated user starts"""
        logger.info(f"User {self.client.base_url} started")
        self.job_ids = []
    
    @task(10)
    def health_check(self):
        """
        Test health check endpoint (lightweight, high frequency)
        Expected: < 50ms response time
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data}")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(5)
    def api_status(self):
        """
        Test API status endpoint
        Expected: < 200ms response time (synchronous endpoint)
        """
        with self.client.get("/api/v1/status", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "operational":
                    response.success()
                else:
                    response.failure(f"Non-operational status: {data}")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def create_biography_job(self):
        """
        Test biography generation job creation
        Expected: < 200ms response time (synchronous endpoint)
        """
        characters = [
            "Albert Einstein",
            "Marie Curie",
            "Leonardo da Vinci",
            "Isaac Newton",
            "Ada Lovelace",
            "Test Character {}".format(random.randint(1000, 9999))
        ]
        
        payload = {
            "character": random.choice(characters),
            "chapters": random.randint(5, 10),  # Smaller for testing
            "total_words": random.randint(5000, 10000)  # Smaller for testing
        }
        
        with self.client.post(
            "/api/v1/biographies/generate",
            json=payload,
            catch_response=True,
            name="/api/v1/biographies/generate"
        ) as response:
            if response.status_code == 202:
                data = response.json()
                if "job_id" in data:
                    self.job_ids.append(data["job_id"])
                    response.success()
                else:
                    response.failure("Missing job_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(8)
    def check_job_status(self):
        """
        Test job status endpoint
        Expected: < 200ms response time (synchronous endpoint)
        """
        if not self.job_ids:
            # If no jobs created yet, create one
            self.create_biography_job()
            return
        
        job_id = random.choice(self.job_ids)
        
        with self.client.get(
            f"/api/v1/biographies/{job_id}/status",
            catch_response=True,
            name="/api/v1/biographies/[id]/status"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "job_id" in data:
                    response.success()
                else:
                    response.failure("Missing required fields in response")
            elif response.status_code == 404:
                # Job might not exist anymore, remove from list
                self.job_ids.remove(job_id)
                response.success()  # 404 is valid if job expired
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def validate_sources(self):
        """
        Test source validation endpoint
        Expected: < 200ms response time (synchronous endpoint)
        """
        payload = {
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
        
        with self.client.post(
            "/api/v1/sources/validate",
            json=payload,
            catch_response=True,
            name="/api/v1/sources/validate"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def metrics_endpoint(self):
        """
        Test metrics endpoint
        Expected: < 200ms response time
        """
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Stress test user - more aggressive testing
    For stress testing scenarios with higher concurrency
    """
    
    wait_time = between(0.5, 1.5)
    
    @task
    def rapid_health_checks(self):
        """Rapid health check requests"""
        self.client.get("/health")
    
    @task
    def rapid_status_checks(self):
        """Rapid status requests"""
        self.client.get("/api/v1/status")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    logger.info("=" * 60)
    logger.info("BookGen Load Test Starting")
    logger.info(f"Target: {environment.host}")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    logger.info("=" * 60)
    logger.info("BookGen Load Test Completed")
    logger.info(f"Time: {datetime.now().isoformat()}")
    
    # Get stats
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Median response time: {stats.total.median_response_time:.2f}ms")
    logger.info(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    logger.info(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    logger.info("=" * 60)
    
    # Check acceptance criteria
    avg_response_time = stats.total.avg_response_time
    failure_rate = stats.total.fail_ratio
    
    if avg_response_time > 200:
        logger.warning(f"⚠️  Average response time ({avg_response_time:.2f}ms) exceeds 200ms target")
    else:
        logger.info(f"✅ Average response time ({avg_response_time:.2f}ms) meets target")
    
    if failure_rate > 0.01:  # 1% error rate threshold
        logger.warning(f"⚠️  Failure rate ({failure_rate*100:.2f}%) exceeds 1% target")
    else:
        logger.info(f"✅ Failure rate ({failure_rate*100:.2f}%) meets target")
