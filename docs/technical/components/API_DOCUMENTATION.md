# BookGen REST API Documentation

## Overview

The BookGen REST API is a FastAPI-based service for automated biography generation using AI. This API provides endpoints for generating biographies, validating sources, monitoring jobs, and downloading generated documents.

## Features

- ✅ **Biography Generation**: Create AI-generated biographies with configurable chapters and word counts
- ✅ **Source Validation**: Validate bibliographic sources with accessibility checking
- ✅ **Job Monitoring**: Track generation progress and status
- ✅ **Rate Limiting**: IP-based rate limiting (60 requests/minute)
- ✅ **Structured Logging**: Comprehensive request/response logging
- ✅ **Prometheus Metrics**: System and application metrics
- ✅ **Automatic Documentation**: Swagger UI at `/docs`
- ✅ **CORS Support**: Configurable cross-origin requests

## Quick Start

### Starting the Server

```bash
# Development mode
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free
CHAPTERS_NUMBER=20
TOTAL_WORDS=51000
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=60
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENV=production
```

## API Endpoints

### Health & Status

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T11:32:27.138654+00:00",
  "environment": "development",
  "debug": false
}
```

#### GET `/api/v1/status`
Detailed API status with configuration.

**Response:**
```json
{
  "api_version": "v1",
  "status": "operational",
  "services": {
    "api": "running",
    "worker": "ready"
  },
  "configuration": {
    "chapters": 20,
    "total_words": 51000,
    "model": "qwen/qwen2.5-vl-72b-instruct:free"
  }
}
```

### Biography Generation

#### POST `/api/v1/biographies/generate`
Initiate biography generation job.

**Request Body:**
```json
{
  "character": "Albert Einstein",
  "chapters": 10,
  "total_words": 10000,
  "model": "qwen/qwen2.5-vl-72b-instruct:free",
  "temperature": 0.7
}
```

**Parameters:**
- `character` (required): Name/identifier of the person
- `chapters` (optional, default: 20): Number of chapters (1-50)
- `total_words` (optional, default: 51000): Target word count (1000-200000)
- `model` (optional): AI model to use
- `temperature` (optional, default: 0.7): Generation temperature (0.0-2.0)

**Response (202 Accepted):**
```json
{
  "job_id": "f7fd47f4-69f5-4ffd-992b-cbde3f7da334",
  "status": "pending",
  "message": "Biography generation job created successfully",
  "character": "Albert Einstein",
  "chapters": 10,
  "created_at": "2025-10-07T11:32:47.112103Z",
  "estimated_completion_time": "300 seconds"
}
```

#### GET `/api/v1/biographies/{job_id}/status`
Check job status and progress.

**Response:**
```json
{
  "job_id": "f7fd47f4-69f5-4ffd-992b-cbde3f7da334",
  "status": "in_progress",
  "character": "Albert Einstein",
  "progress": {
    "chapters_completed": 5,
    "total_chapters": 10,
    "percentage": 50.0
  },
  "created_at": "2025-10-07T11:32:47.112103Z",
  "started_at": "2025-10-07T11:32:48.500000Z",
  "completed_at": null,
  "error": null,
  "download_url": null
}
```

**Status Values:**
- `pending`: Job created, waiting to start
- `in_progress`: Generation in progress
- `completed`: Successfully completed
- `failed`: Generation failed (check `error` field)

#### GET `/api/v1/biographies/{job_id}/download`
Download completed biography.

**Response:**
- Content-Type: `text/plain` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Downloads the generated biography file

**Errors:**
- `404`: Job not found
- `400`: Job not completed yet

### Source Validation

#### POST `/api/v1/sources/validate`
Validate bibliographic sources.

**Request Body:**
```json
{
  "sources": [
    {
      "title": "Wikipedia Article on AI",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
      "author": "Wikipedia Contributors",
      "publication_date": "2023",
      "source_type": "url"
    },
    {
      "title": "The Elements of Style",
      "author": "William Strunk Jr.",
      "publication_date": "1918",
      "source_type": "book"
    }
  ],
  "check_accessibility": false
}
```

**Source Types:**
- `url`: Web URL
- `book`: Book
- `article`: Article
- `document`: Document
- `other`: Other source type

**Response:**
```json
{
  "total_sources": 2,
  "valid_sources": 2,
  "invalid_sources": 0,
  "results": [
    {
      "source": {
        "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "title": "Wikipedia Article on AI",
        "author": "Wikipedia Contributors",
        "publication_date": "2023",
        "source_type": "url"
      },
      "is_valid": true,
      "is_accessible": null,
      "issues": [],
      "metadata": null
    }
  ],
  "summary": {
    "validation_rate": 100.0,
    "source_types": {
      "url": 1,
      "book": 1
    },
    "accessibility_checked": false
  }
}
```

### Monitoring

#### GET `/metrics`
Prometheus-compatible metrics endpoint.

**Response (text/plain):**
```
# HELP bookgen_uptime_seconds Application uptime in seconds
# TYPE bookgen_uptime_seconds gauge
bookgen_uptime_seconds 29.09

# HELP bookgen_cpu_percent CPU usage percentage
# TYPE bookgen_cpu_percent gauge
bookgen_cpu_percent 0.0

# HELP bookgen_memory_percent Memory usage percentage
# TYPE bookgen_memory_percent gauge
bookgen_memory_percent 9.2

# HELP bookgen_jobs_total Total number of jobs by status
# TYPE bookgen_jobs_total gauge
bookgen_jobs_total{status="pending"} 2
bookgen_jobs_total{status="in_progress"} 1
bookgen_jobs_total{status="completed"} 10
bookgen_jobs_total{status="failed"} 1
```

## Rate Limiting

The API implements IP-based rate limiting:

- **Limit**: 60 requests per minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `Retry-After`: Seconds to wait before retrying (on 429 error)

**Exempt Paths:**
- `/health`
- `/docs`
- `/openapi.json`
- `/redoc`
- `/metrics`

**Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Retry after 30 seconds."
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `202 Accepted`: Job created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

**Validation Error Format:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "character"],
      "msg": "Value error, Character name cannot be empty",
      "input": ""
    }
  ]
}
```

## Interactive Documentation

Access the interactive Swagger UI documentation:

```
http://localhost:8000/docs
```

Or the ReDoc documentation:

```
http://localhost:8000/redoc
```

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Test Specific Endpoints

```bash
# Test biography endpoints
python -m pytest tests/test_biographies.py -v

# Test source validation
python -m pytest tests/test_sources.py -v

# Test middleware
python -m pytest tests/test_middleware.py -v

# Test metrics
python -m pytest tests/test_metrics.py -v
```

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api/v1/status

# Generate biography
curl -X POST "http://localhost:8000/api/v1/biographies/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Marie Curie",
    "chapters": 5,
    "total_words": 5000
  }'

# Check job status
curl http://localhost:8000/api/v1/biographies/{job_id}/status

# Download completed biography
curl -O http://localhost:8000/api/v1/biographies/{job_id}/download

# Validate sources
curl -X POST "http://localhost:8000/api/v1/sources/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {
        "title": "Example Book",
        "author": "John Doe",
        "source_type": "book"
      }
    ],
    "check_accessibility": false
  }'

# Get metrics
curl http://localhost:8000/metrics
```

## Architecture

### Project Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── biographies.py   # Biography request/response models
│   │   └── sources.py       # Source validation models
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── biographies.py   # Biography generation endpoints
│   │   ├── sources.py       # Source validation endpoints
│   │   └── metrics.py       # Metrics endpoint
│   └── middleware/          # Custom middleware
│       ├── __init__.py
│       ├── rate_limiter.py  # Rate limiting
│       └── request_logger.py # Request logging
├── config/                  # Configuration
├── services/                # Business logic
│   └── openrouter_client.py # OpenRouter API client
├── utils/                   # Utilities
└── main.py                  # FastAPI application

tests/
├── test_api.py
├── test_biographies.py
├── test_sources.py
├── test_middleware.py
└── test_metrics.py
```

### Middleware Stack

1. **CORS Middleware**: Handles cross-origin requests
2. **Request Logger Middleware**: Logs all requests with timing
3. **Rate Limit Middleware**: Enforces IP-based rate limits

### Background Tasks

Biography generation runs as a background task using FastAPI's `BackgroundTasks`. The job status can be monitored via the status endpoint.

## Security Considerations

1. **API Key Protection**: Store OpenRouter API key in environment variables
2. **Rate Limiting**: Prevents API abuse (60 req/min per IP)
3. **Input Validation**: Pydantic models validate all inputs
4. **CORS Configuration**: Configure allowed origins in production
5. **Error Handling**: Sanitized error messages, no sensitive data exposure

## Performance

- **Async/Await**: FastAPI's async support for concurrent requests
- **Background Tasks**: Long-running tasks don't block API responses
- **Rate Limiting**: Protects against overload
- **Lightweight**: Minimal dependencies, fast startup

## Deployment

### Docker

```bash
docker build -t bookgen-api .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=your_key bookgen-api
```

### Production Recommendations

1. Use a reverse proxy (nginx, Traefik)
2. Enable HTTPS/TLS
3. Configure proper CORS origins
4. Use a process manager (systemd, supervisord)
5. Set up log rotation
6. Monitor metrics with Prometheus
7. Use a database for job persistence (currently in-memory)
8. Implement job cleanup/archiving

## Future Enhancements

- [ ] Database integration for job persistence
- [ ] Authentication/Authorization (JWT tokens)
- [ ] WebSocket support for real-time progress updates
- [ ] Job queue with Redis/Celery
- [ ] File upload for custom templates
- [ ] Multiple output formats (EPUB, PDF)
- [ ] Batch job processing
- [ ] Job scheduling and cron support
- [ ] Advanced caching strategies
- [ ] GraphQL API endpoint

## Support

For issues or questions:
- Review this documentation
- Check `/docs` for interactive API documentation
- Review test files for usage examples
- Check application logs for debugging

## License

See LICENSE file in repository root.
