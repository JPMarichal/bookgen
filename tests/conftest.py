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
    yield
    # Cleanup after tests
