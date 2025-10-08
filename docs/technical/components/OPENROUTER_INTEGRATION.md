# OpenRouter API Integration

Complete implementation of OpenRouter API client for BookGen AI System.

## 📁 Files Created

### Core Implementation
- `src/config/openrouter_config.py` - Configuration class for OpenRouter API
- `src/services/openrouter_client.py` - Main OpenRouter client with all features
- `src/utils/retry_handler.py` - Exponential backoff retry system

### Tests
- `tests/test_openrouter.py` - Comprehensive unit tests

### Demo
- `demo_openrouter.py` - Usage examples and demonstration

## ✅ Features Implemented

### ✓ Robust API Client
- Full OpenRouter API integration
- Support for Qwen2.5 VL 72B model
- Configurable via environment variables
- Type hints and comprehensive documentation

### ✓ Rate Limiting
- Respects free tier limits
- Minimum 1 second between requests
- Automatic waiting between calls

### ✓ Error Handling
- Custom exception hierarchy (`OpenRouterException`, `RateLimitException`, `APIException`)
- Detailed error logging
- HTTP error handling (429, timeouts, etc.)

### ✓ Retry System
- Exponential backoff with configurable parameters
- Maximum 3 retries by default
- Jitter support to prevent thundering herd
- Retry on specific exception types

### ✓ Configurable Timeouts
- Default: 300 seconds
- Configurable per request
- Proper timeout exception handling

### ✓ Detailed Logging
- Structured logging for all requests/responses
- Debug mode for payload inspection
- Error tracking with timestamps

### ✓ Usage Statistics
- Total requests tracked
- Success/failure rates
- Token usage (prompt, completion, total)
- Cost tracking (ready for future billing)
- Uptime tracking

### ✓ Streaming Support
- `generate_text_streaming()` method
- Yields chunks for long responses
- Server-Sent Events (SSE) parsing

## 🔧 Configuration

The client uses environment variables (from `.env` file):

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Optional (with defaults)
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free
SITE_URL=https://bookgen.ai
SITE_TITLE=BookGen AI System
OPENROUTER_MAX_TOKENS=8192
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_TOP_P=0.9
OPENROUTER_TIMEOUT=300
```

## 📖 Usage Examples

### Basic Text Generation

```python
from src.services.openrouter_client import OpenRouterClient

client = OpenRouterClient()
response = client.generate_text("Write a creative opening for a biography")
print(response)
```

### With System Prompt

```python
response = client.generate_text(
    prompt="Describe the Renaissance period",
    system_prompt="You are an expert historian",
    temperature=0.7,
    max_tokens=1000
)
```

### Streaming Response

```python
for chunk in client.generate_text_streaming("Write a long essay"):
    print(chunk, end='', flush=True)
```

### Custom Configuration

```python
from src.config.openrouter_config import OpenRouterConfig

config = OpenRouterConfig(
    api_key="your-key",
    temperature=0.5,
    timeout=600
)
client = OpenRouterClient(config)
```

### Usage Statistics

```python
stats = client.get_usage_stats()
print(f"Requests: {stats['requests']}")
print(f"Success rate: {stats['success_rate'] * 100:.1f}%")
print(f"Total tokens: {stats['total_tokens']}")
```

## 🧪 Testing

Run tests:
```bash
pytest tests/test_openrouter.py -v
```

Run all tests:
```bash
pytest tests/ -v
```

### Test Coverage
- Configuration validation
- Retry handler logic
- Client initialization
- Text generation (mocked)
- Error handling
- Rate limiting
- Statistics tracking
- Custom parameters

## 📊 Technical Details

### Model Configuration
- **Model**: `qwen/qwen2.5-72b-instruct:free`
- **Max Tokens**: 8192 per request
- **Temperature**: 0.7 (balanced creativity)
- **Top-p**: 0.9 (controlled diversity)

### Rate Limiting
- Minimum 1 second between requests
- Automatic waiting before each request
- Tracks last request time

### Retry Strategy
- Max retries: 3
- Base delay: 1 second
- Max delay: 60 seconds
- Exponential base: 2.0
- Random jitter enabled

### Error Types
- `OpenRouterException`: Base exception
- `RateLimitException`: HTTP 429 errors
- `APIException`: Other API errors
- `RetryException`: Retry exhaustion

## 🔍 Verification

The implementation satisfies all acceptance criteria from Issue #4:

```python
# Verification command from issue
from src.services.openrouter_client import OpenRouterClient
client = OpenRouterClient()
response = client.generate_text("Test prompt")
assert len(response) > 0
assert client.get_usage_stats()['requests'] > 0
```

All tests pass ✅

## 📝 Notes

- The client is designed for production use with the BookGen system
- All datetime usage is timezone-aware (UTC)
- Logging is structured and configurable
- Ready for integration with FastAPI endpoints
- Supports both sync operations (current) and can be extended for async

## 🚀 Next Steps

This implementation is ready to be used by:
- Chapter generation service
- Biography content creation
- Any AI-powered content generation in BookGen

The client can be easily integrated into FastAPI endpoints or used directly in background workers.
