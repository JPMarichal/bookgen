"""
Test configuration and fixtures for BookGen tests
"""
import pytest
import os


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["ENV"] = "test"
    os.environ["DEBUG"] = "false"
    # Disable rate limiting for tests
    os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"
    yield
    # Cleanup after tests
