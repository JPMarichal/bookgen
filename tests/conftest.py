"""
Test configuration and fixtures for BookGen tests
"""
import pytest
import os
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.database.base import Base

# Set test environment variables at import time (before app is loaded)
os.environ["ENV"] = "test"
os.environ["DEBUG"] = "false"
os.environ["OPENROUTER_API_KEY"] = "test-key-12345"
os.environ["OPENROUTER_BASE_URL"] = "https://api.test.openrouter.ai"
os.environ["OPENROUTER_MODEL"] = "test-model"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
# Set high rate limit for tests to avoid rate limiting during benchmarks
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"


@pytest.fixture(autouse=True)
def setup_test_env():
    """Ensure test environment variables are set (redundant but safe)"""
    # Variables already set at module import time
    yield
    # Cleanup after tests


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory database session for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client():
    """Create a FastAPI test client"""
    from src.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client for testing"""
    mock = MagicMock()
    mock.generate_text.return_value = "Generated text response"
    mock.get_usage_stats.return_value = {
        "requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "total_tokens": 0
    }
    return mock


@pytest.fixture
def mock_celery_task():
    """Mock Celery task for testing"""
    mock = MagicMock()
    mock.delay.return_value.id = "test-task-id-12345"
    mock.apply_async.return_value.id = "test-task-id-12345"
    return mock


@pytest.fixture
def sample_biography_data():
    """Sample biography data for testing"""
    return {
        "character_name": "Winston Churchill",
        "chapters": 8,
        "length_type": "normal",
        "include_sources": True
    }


@pytest.fixture
def sample_chapter_data():
    """Sample chapter data for testing"""
    return {
        "number": 1,
        "title": "Early Life",
        "content": "This is the chapter content with sufficient words to meet the minimum requirements. " * 20,
        "word_count": 500,
        "sources": []
    }


@pytest.fixture
def sample_source_data():
    """Sample source data for testing"""
    return {
        "title": "Winston Churchill Biography",
        "url": "https://www.britannica.com/biography/Winston-Churchill",
        "source_type": "article",
        "author": "Encyclopedia Britannica",
        "publication_date": "2023-01-15",
        "relevance_score": 0.95,
        "credibility_score": 0.98
    }
