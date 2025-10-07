# BookGen Test Suite

This directory contains automated tests for the BookGen system.

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_api.py` - API endpoint tests
- `conftest.py` - Test configuration and fixtures

## Adding New Tests

1. Create a new file with prefix `test_` or suffix `_test.py`
2. Use pytest fixtures from `conftest.py`
3. Follow existing test patterns
4. Ensure tests are independent and can run in any order
