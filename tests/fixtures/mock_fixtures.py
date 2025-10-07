"""
Mock fixtures for external services
"""
import pytest
from unittest.mock import MagicMock, Mock


@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response"""
    return {
        "id": "gen-123456",
        "model": "test-model",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a generated biography chapter about the subject's early life and formative years."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 500,
            "total_tokens": 600
        }
    }


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    return mock_redis


@pytest.fixture
def mock_celery_result():
    """Mock Celery AsyncResult"""
    mock_result = MagicMock()
    mock_result.id = "test-task-id-12345"
    mock_result.state = "SUCCESS"
    mock_result.ready.return_value = True
    mock_result.successful.return_value = True
    mock_result.get.return_value = {"status": "completed"}
    return mock_result


@pytest.fixture
def sample_biography_metadata():
    """Sample biography metadata"""
    return {
        "character_name": "Winston Churchill",
        "birth_year": 1874,
        "death_year": 1965,
        "nationality": "British",
        "occupation": "Politician, Statesman, Author",
        "known_for": "Prime Minister of UK during WWII",
        "themes": ["leadership", "resilience", "oratory", "history"]
    }


@pytest.fixture
def sample_chapters_collection():
    """Collection of sample chapters"""
    return [
        {
            "number": 1,
            "title": "Early Life and Education",
            "content": " ".join(["word"] * 2550),
            "word_count": 2550,
            "sources": ["source1", "source2"]
        },
        {
            "number": 2,
            "title": "Military Career",
            "content": " ".join(["word"] * 2550),
            "word_count": 2550,
            "sources": ["source3", "source4"]
        },
        {
            "number": 3,
            "title": "Political Rise",
            "content": " ".join(["word"] * 2550),
            "word_count": 2550,
            "sources": ["source5", "source6"]
        }
    ]


@pytest.fixture
def sample_sources_collection():
    """Collection of sample sources"""
    return [
        {
            "title": "Winston Churchill: A Biography",
            "url": "https://www.britannica.com/biography/Winston-Churchill",
            "source_type": "article",
            "author": "Encyclopedia Britannica",
            "publication_date": "2023-01-15",
            "relevance_score": 0.98,
            "credibility_score": 0.99,
            "is_accessible": True
        },
        {
            "title": "Churchill: Walking with Destiny",
            "url": "https://example.edu/churchill-biography",
            "source_type": "book",
            "author": "Andrew Roberts",
            "publication_date": "2018-11-06",
            "relevance_score": 0.95,
            "credibility_score": 0.97,
            "is_accessible": True
        },
        {
            "title": "The Churchill Factor",
            "url": "https://example.org/churchill-factor",
            "source_type": "book",
            "author": "Boris Johnson",
            "publication_date": "2014-10-23",
            "relevance_score": 0.92,
            "credibility_score": 0.90,
            "is_accessible": True
        }
    ]


@pytest.fixture
def mock_http_response_success():
    """Mock successful HTTP response"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = "Success response"
    mock_response.headers = {"Content-Type": "application/json"}
    return mock_response


@pytest.fixture
def mock_http_response_error():
    """Mock error HTTP response"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.ok = False
    mock_response.json.return_value = {"error": "Internal server error"}
    mock_response.text = "Error response"
    mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
    return mock_response


@pytest.fixture
def mock_database_session():
    """Mock database session"""
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.query.return_value.filter.return_value.all.return_value = []
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    return mock_session


@pytest.fixture
def validation_test_cases():
    """Test cases for validation scenarios"""
    return {
        "valid_chapter": {
            "content": " ".join(["word"] * 2550),
            "expected_valid": True
        },
        "too_short_chapter": {
            "content": " ".join(["word"] * 2000),
            "expected_valid": False
        },
        "too_long_chapter": {
            "content": " ".join(["word"] * 3000),
            "expected_valid": False
        },
        "empty_chapter": {
            "content": "",
            "expected_valid": False
        }
    }


@pytest.fixture
def api_test_data():
    """Common test data for API tests"""
    return {
        "valid_biography_request": {
            "character": "Winston Churchill",
            "chapters": 8,
            "length_type": "normal",
            "include_sources": True
        },
        "invalid_biography_request": {
            "character": "",
            "chapters": 0
        },
        "valid_source_validation": {
            "sources": [
                {
                    "title": "Test Source",
                    "url": "https://example.edu/article",
                    "source_type": "article"
                }
            ],
            "topic": "Test Topic"
        }
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        "max_response_time_ms": 5000,
        "max_generation_time_s": 300,
        "max_validation_time_s": 30,
        "concurrent_requests": 10,
        "timeout_s": 60
    }
