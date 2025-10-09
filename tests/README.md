# BookGen Test Suite

This directory contains automated tests for the BookGen system.

## Test Organization

The test suite is organized into the following structure:

- `unit/` - Unit tests for individual modules and functions
- `integration/` - Integration tests for multi-service interactions
- `api/` - API endpoint tests
- `fixtures/` - Test fixtures and mock data
- Root level - Existing comprehensive tests

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-xdist

# Run all tests (excluding slow tests) with parallel execution
pytest -m "not slow" -n auto

# Run all tests with coverage
pytest -m "not slow" -n auto --cov=src --cov-report=html

# Run specific test category
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api           # API tests only
pytest -m slow          # Slow tests only (performance/stress tests)
pytest -m fast          # Fast tests only

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run with coverage threshold
pytest --cov=src --cov-fail-under=75

# Run all tests including slow ones (for comprehensive testing)
pytest -n auto --cov=src
```

## Performance Optimization

The test suite has been optimized to reduce execution time from ~25 minutes to ~5-10 minutes:

1. **Parallel Execution**: Tests run in parallel using `pytest-xdist` with `-n auto` flag
2. **Slow Test Marking**: Performance and stress tests are marked with `@pytest.mark.slow`
3. **Selective Execution**: CI/CD pipeline excludes slow tests by default using `-m "not slow"`
4. **Integration Testing**: Integration tests are clearly marked for optional execution

To run slow tests (performance/stress):
```bash
pytest -m slow -v
```

## Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for multi-service interactions
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Tests that take a long time to run
- `@pytest.mark.fast` - Quick tests
- `@pytest.mark.database` - Tests that require database
- `@pytest.mark.external` - Tests that require external services
- `@pytest.mark.mock` - Tests using mocks

## Test Configuration

Test configuration is managed through:

- `pytest.ini` - pytest configuration with markers and test discovery settings
- `conftest.py` - Global fixtures and test setup
- `fixtures/mock_fixtures.py` - Reusable mock objects and test data

## Test Structure

Each test module follows this structure:

```python
"""
Module description
"""
import pytest
from unittest.mock import Mock, patch

pytestmark = [pytest.mark.unit, pytest.mark.mock]  # Mark all tests in module

class TestFeature:
    """Test suite for specific feature"""
    
    def test_success_case(self):
        """Test successful execution"""
        # Arrange, Act, Assert
        pass
    
    def test_error_case(self):
        """Test error handling"""
        pass
```

## Coverage Requirements

- **Overall Coverage Target**: 85%+
- **Services**: 90%+
- **API Endpoints**: 95%+
- **Models**: 80%+
- **Utils**: 85%+

## Current Coverage

To view current coverage:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest --cov=src --cov-report=term-missing
```

## Adding New Tests

1. Create a new file with prefix `test_` or suffix `_test.py`
2. Use pytest fixtures from `conftest.py`
3. Add appropriate markers (unit, integration, api, etc.)
4. Follow existing test patterns
5. Ensure tests are independent and can run in any order
6. Use descriptive test names that explain what is being tested

## Fixtures

Common fixtures available in `conftest.py`:

- `db_session` - In-memory database session
- `test_client` - FastAPI TestClient
- `mock_openrouter_client` - Mocked OpenRouter API client
- `mock_celery_task` - Mocked Celery task
- `sample_biography_data` - Sample biography test data
- `sample_chapter_data` - Sample chapter test data
- `sample_source_data` - Sample source test data

Additional mock fixtures in `fixtures/mock_fixtures.py`:

- `mock_openrouter_response` - Mocked API responses
- `mock_redis_client` - Mocked Redis client
- `mock_celery_result` - Mocked Celery AsyncResult
- `validation_test_cases` - Common validation scenarios
- `api_test_data` - Common API test data

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Clear Names**: Use descriptive test names that explain the scenario
3. **Arrange-Act-Assert**: Follow the AAA pattern for test structure
4. **Mock External Services**: Use mocks for external APIs and services
5. **Test Edge Cases**: Include tests for boundary conditions and error cases
6. **Parametrized Tests**: Use `@pytest.mark.parametrize` for testing multiple inputs
7. **Fast Tests**: Keep unit tests fast by avoiding actual I/O operations

## Continuous Integration

Tests are automatically run on:
- Pull request creation and updates
- Commits to main branch
- Scheduled daily runs

CI configuration enforces:
- All tests must pass
- Coverage must meet minimum thresholds
- No linting errors
