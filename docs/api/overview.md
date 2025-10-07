# API Overview

BookGen provides a comprehensive REST API for biography generation and management.

## 🌐 API Introduction

The BookGen API is built with FastAPI, providing:

- ✅ **RESTful Design**: Standard HTTP methods and status codes
- ✅ **OpenAPI Standard**: Auto-generated interactive documentation
- ✅ **Type Safety**: Pydantic models for request/response validation
- ✅ **Real-time Updates**: WebSocket support for live progress
- ✅ **Rate Limited**: Protected against abuse
- ✅ **Well Documented**: Interactive Swagger UI and ReDoc

## 📡 Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://yourdomain.com
```

## 🔐 Authentication

Currently, BookGen API does not require authentication for basic operations. For production deployments, you can enable API key authentication:

```bash
# Enable in .env
API_KEY_REQUIRED=true
VALID_API_KEYS=key1,key2,key3
```

**Using API Keys:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/biographies
```

## 📋 API Endpoints Summary

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint - API information |
| `GET` | `/health` | Health check for monitoring |
| `GET` | `/api/v1/status` | Detailed system status |

### Biography Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/biographies` | Create new biography job |
| `GET` | `/api/v1/biographies/{job_id}` | Get biography status |
| `GET` | `/api/v1/biographies` | List all biographies |
| `DELETE` | `/api/v1/biographies/{job_id}` | Delete biography (future) |

### Source Validation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sources/validate` | Validate source URLs |
| `POST` | `/api/v1/sources/batch-validate` | Validate multiple sources |

### Metrics Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/metrics` | System metrics and statistics |

### WebSocket Endpoints

| Type | Endpoint | Description |
|------|----------|-------------|
| `WS` | `/ws/notifications` | Real-time job updates |

## 🚀 Quick Start

### Creating a Biography

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "sources": [
      "https://en.wikipedia.org/wiki/Albert_Einstein",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
    ]
  }'
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "character": "Albert Einstein",
  "status": "pending",
  "created_at": "2025-01-07T12:00:00Z",
  "message": "Biography generation job created successfully"
}
```

### Checking Status

**Request:**
```bash
curl http://localhost:8000/api/v1/biographies/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "character": "Albert Einstein",
  "status": "processing",
  "progress": 45.0,
  "current_phase": "Generating Chapter 9 of 20",
  "chapters_completed": 8,
  "total_chapters": 20,
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T13:15:00Z"
}
```

## 📖 Interactive Documentation

BookGen provides two types of interactive documentation:

### Swagger UI
Full interactive API explorer with try-it-out functionality.

**URL:** `http://localhost:8000/docs`

**Features:**
- ✅ Try API calls directly from browser
- ✅ See request/response examples
- ✅ Download OpenAPI spec
- ✅ Authentication testing

### ReDoc
Clean, professional API documentation.

**URL:** `http://localhost:8000/redoc`

**Features:**
- ✅ Better for reading and learning
- ✅ Search functionality
- ✅ Code samples in multiple languages
- ✅ Printable documentation

## 🔄 API Workflow

### Standard Biography Generation Flow

```
1. Submit Biography Request
   POST /api/v1/biographies
   ↓
2. Job Created (job_id returned)
   ↓
3. Monitor Progress
   - Option A: WebSocket connection
   - Option B: Polling GET /api/v1/biographies/{job_id}
   ↓
4. Job Completes
   ↓
5. Download Generated Files
   - Markdown: bios/{character}/La biografia de {character}.md
   - Word: docx/{character}/La biografia de {character}.docx
```

### Source Validation Flow

```
1. Collect Source URLs
   ↓
2. Validate Sources
   POST /api/v1/sources/validate
   ↓
3. Review Validation Results
   ↓
4. Use Valid Sources in Biography Request
```

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 202 | Accepted | Job accepted for processing |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

**Standard Error:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Error:**
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

### Common Errors

**Insufficient Sources:**
```json
{
  "detail": "At least 40 valid sources required. Provided: 25"
}
```

**Invalid Job ID:**
```json
{
  "detail": "Job not found: invalid-job-id"
}
```

**Rate Limit Exceeded:**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

## 🚦 Rate Limiting

The API includes rate limiting to prevent abuse:

**Default Limits:**
- 60 requests per minute per IP address
- Burst allowance: 10 requests

**Configuration:**
```bash
# Update in .env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704636000
```

## 📊 Response Formats

### Job Status Response

**Pending:**
```json
{
  "job_id": "...",
  "status": "pending",
  "progress": 0.0,
  "current_phase": "Queued for processing"
}
```

**Processing:**
```json
{
  "job_id": "...",
  "status": "processing",
  "progress": 65.0,
  "current_phase": "Generating Chapter 13 of 20",
  "chapters_completed": 12,
  "estimated_completion": "2025-01-07T15:30:00Z"
}
```

**Completed:**
```json
{
  "job_id": "...",
  "status": "completed",
  "progress": 100.0,
  "chapters": 20,
  "total_words": 51245,
  "output_file": "docx/albert_einstein/La biografia de Albert Einstein.docx",
  "completed_at": "2025-01-07T14:30:00Z",
  "duration_seconds": 9000
}
```

**Failed:**
```json
{
  "job_id": "...",
  "status": "failed",
  "error": "Source validation failed: insufficient valid sources",
  "failed_at": "2025-01-07T12:15:00Z"
}
```

## 🔌 Integration Examples

### Python

```python
import requests

# Create biography
response = requests.post(
    "http://localhost:8000/api/v1/biographies",
    json={
        "character": "Albert Einstein",
        "sources": ["url1", "url2", ...]
    }
)

job_id = response.json()["job_id"]

# Check status
status = requests.get(
    f"http://localhost:8000/api/v1/biographies/{job_id}"
)

print(f"Progress: {status.json()['progress']}%")
```

### JavaScript

```javascript
// Create biography
const response = await fetch('http://localhost:8000/api/v1/biographies', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    character: 'Albert Einstein',
    sources: ['url1', 'url2', ...]
  })
});

const { job_id } = await response.json();

// WebSocket for real-time updates
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?job_id=${job_id}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%`);
};
```

### cURL

```bash
# Create biography
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{"character":"Albert Einstein","sources":["..."]}' \
  | jq -r '.job_id')

# Poll status
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/biographies/$JOB_ID \
    | jq -r '.status')
  
  if [ "$STATUS" = "completed" ]; then
    echo "Done!"
    break
  fi
  
  sleep 30
done
```

## 📚 Next Steps

- **[Endpoints Reference](endpoints.md)** - Detailed endpoint documentation
- **[WebSocket Guide](websocket.md)** - Real-time updates
- **[API Examples](../examples/api-usage.md)** - Code examples
- **[Error Handling](error-handling.md)** - Comprehensive error guide

---

[← Getting Started](../getting-started/quick-start.md) | [Endpoints Reference →](endpoints.md)
