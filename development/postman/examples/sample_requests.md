# Ejemplos de Requests - BookGen API

Este documento contiene ejemplos completos de requests para todos los endpoints de la API de BookGen.

## 📋 Tabla de Contenido

- [Health & Status](#health--status)
- [Biografías](#biografías)
- [Fuentes](#fuentes)
- [WebSocket](#websocket)

---

## Health & Status

### Health Check

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-07T10:30:00.000000+00:00",
  "environment": "development",
  "debug": false
}
```

### API Status

**Request:**
```http
GET /api/v1/status HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
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

### Prometheus Metrics

**Request:**
```http
GET /metrics HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```
# HELP bookgen_uptime_seconds Application uptime in seconds
# TYPE bookgen_uptime_seconds gauge
bookgen_uptime_seconds 3600.45

# HELP bookgen_cpu_percent CPU usage percentage
# TYPE bookgen_cpu_percent gauge
bookgen_cpu_percent 25.3

# HELP bookgen_memory_percent Memory usage percentage
# TYPE bookgen_memory_percent gauge
bookgen_memory_percent 42.1
...
```

---

## Biografías

### 1. Generar Biografía - Modo Automático

El sistema genera automáticamente todas las fuentes necesarias.

**Request:**
```http
POST /api/v1/biographies/generate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "character": "Albert Einstein",
  "chapters": 10,
  "total_words": 10000,
  "mode": "automatic",
  "min_sources": 40,
  "quality_threshold": 0.8,
  "temperature": 0.7
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Biography generation job created successfully",
  "character": "Albert Einstein",
  "chapters": 10,
  "created_at": "2025-01-07T10:30:00.000000+00:00",
  "estimated_completion_time": "300 seconds",
  "mode": "automatic",
  "sources_generated_automatically": true,
  "source_count": 45
}
```

### 2. Generar Biografía - Modo Manual

El usuario proporciona todas las fuentes manualmente.

**Request:**
```http
POST /api/v1/biographies/generate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "character": "Marie Curie",
  "chapters": 15,
  "total_words": 15000,
  "mode": "manual",
  "sources": [
    "https://en.wikipedia.org/wiki/Marie_Curie",
    "https://www.nobelprize.org/prizes/physics/1903/marie-curie/biographical/",
    "https://www.britannica.com/biography/Marie-Curie",
    "https://www.aps.org/programs/outreach/history/historicsites/curie.cfm",
    "https://www.biography.com/scientist/marie-curie",
    "https://www.atomicheritage.org/profile/marie-curie",
    "https://www.sciencehistory.org/historical-profile/marie-curie",
    "https://www.amnh.org/explore/science-topics/marie-curie",
    "https://www.livescience.com/38907-marie-curie.html",
    "https://www.chemheritage.org/historical-profile/marie-curie"
  ],
  "temperature": 0.7
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "message": "Biography generation job created successfully",
  "character": "Marie Curie",
  "chapters": 15,
  "created_at": "2025-01-07T10:31:00.000000+00:00",
  "estimated_completion_time": "450 seconds",
  "mode": "manual",
  "sources_generated_automatically": false,
  "source_count": 10
}
```

### 3. Generar Biografía - Modo Híbrido

Combina fuentes del usuario con generación automática.

**Request:**
```http
POST /api/v1/biographies/generate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "character": "Leonardo da Vinci",
  "chapters": 20,
  "total_words": 20000,
  "mode": "hybrid",
  "sources": [
    "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
    "https://www.britannica.com/biography/Leonardo-da-Vinci",
    "https://www.leonardodavinci.net/",
    "https://www.metmuseum.org/toah/hd/leon/hd_leon.htm",
    "https://www.biography.com/artist/leonardo-da-vinci"
  ],
  "min_sources": 40,
  "quality_threshold": 0.8,
  "temperature": 0.7
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "pending",
  "message": "Biography generation job created successfully",
  "character": "Leonardo da Vinci",
  "chapters": 20,
  "created_at": "2025-01-07T10:32:00.000000+00:00",
  "estimated_completion_time": "600 seconds",
  "mode": "hybrid",
  "sources_generated_automatically": true,
  "source_count": 42
}
```

### 4. Obtener Estado del Trabajo

**Request:**
```http
GET /api/v1/biographies/550e8400-e29b-41d4-a716-446655440000/status HTTP/1.1
Host: localhost:8000
```

**Response (200 OK) - En Progreso:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "character": "Albert Einstein",
  "progress": {
    "chapters_completed": 5,
    "total_chapters": 10,
    "percentage": 50.0
  },
  "created_at": "2025-01-07T10:30:00.000000+00:00",
  "started_at": "2025-01-07T10:30:05.000000+00:00",
  "completed_at": null,
  "error": null,
  "download_url": null
}
```

**Response (200 OK) - Completado:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "character": "Albert Einstein",
  "progress": {
    "chapters_completed": 10,
    "total_chapters": 10,
    "percentage": 100.0
  },
  "created_at": "2025-01-07T10:30:00.000000+00:00",
  "started_at": "2025-01-07T10:30:05.000000+00:00",
  "completed_at": "2025-01-07T10:35:30.000000+00:00",
  "error": null,
  "download_url": "/api/v1/biographies/550e8400-e29b-41d4-a716-446655440000/download"
}
```

**Response (200 OK) - Fallido:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "character": "Albert Einstein",
  "progress": {
    "chapters_completed": 3,
    "total_chapters": 10,
    "percentage": 30.0
  },
  "created_at": "2025-01-07T10:30:00.000000+00:00",
  "started_at": "2025-01-07T10:30:05.000000+00:00",
  "completed_at": "2025-01-07T10:32:15.000000+00:00",
  "error": "OpenRouter API error: Rate limit exceeded",
  "download_url": null
}
```

### 5. Descargar Biografía

**Request:**
```http
GET /api/v1/biographies/550e8400-e29b-41d4-a716-446655440000/download HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```
Content-Type: text/plain
Content-Disposition: attachment; filename="biography_Albert_Einstein.txt"

Biography of Albert Einstein
==================================================

Chapter 1
------------------------------
[Chapter content...]

Chapter 2
------------------------------
[Chapter content...]

...
```

**Error Response (400 Bad Request) - No Completado:**
```json
{
  "detail": "Job is not completed yet. Current status: in_progress"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Job 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### 6. Descargar Output ZIP (Nuevo - Issue #87)

**Request:**
```http
GET /api/v1/biographies/harry_s_truman/download-output HTTP/1.1
Host: localhost:8000
Accept: application/zip
```

**Response (200 OK):**
```
Content-Type: application/zip
Content-Disposition: attachment; filename="harry_s_truman_output.zip"

[Binary ZIP content containing:
  - markdown/
  - word/
  - kdp/
]
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Output directory not found for character 'harry_s_truman'"
}
```

---

## Fuentes

### 1. Validar Fuentes - Básico

**Request:**
```http
POST /api/v1/sources/validate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "sources": [
    {
      "title": "Wikipedia: Albert Einstein",
      "author": "Wikipedia Contributors",
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "source_type": "url",
      "publication_date": "2024"
    },
    {
      "title": "Einstein Biography",
      "author": "Nobelprize.org",
      "url": "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
      "source_type": "url"
    },
    {
      "title": "Invalid Source",
      "author": "",
      "url": "not-a-valid-url",
      "source_type": "url"
    }
  ],
  "check_accessibility": true
}
```

**Response (200 OK):**
```json
{
  "total_sources": 3,
  "valid_sources": 2,
  "invalid_sources": 1,
  "results": [
    {
      "source": {
        "title": "Wikipedia: Albert Einstein",
        "author": "Wikipedia Contributors",
        "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
        "source_type": "url",
        "publication_date": "2024"
      },
      "is_valid": true,
      "is_accessible": true,
      "issues": [],
      "metadata": {
        "content_type": "text/html; charset=UTF-8",
        "last_modified": "Mon, 06 Jan 2025 15:30:00 GMT"
      }
    },
    {
      "source": {
        "title": "Einstein Biography",
        "author": "Nobelprize.org",
        "url": "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
        "source_type": "url"
      },
      "is_valid": true,
      "is_accessible": true,
      "issues": [],
      "metadata": {
        "content_type": "text/html; charset=UTF-8"
      }
    },
    {
      "source": {
        "title": "Invalid Source",
        "author": "",
        "url": "not-a-valid-url",
        "source_type": "url"
      },
      "is_valid": false,
      "is_accessible": false,
      "issues": [
        "Author field is empty",
        "Invalid URL format"
      ],
      "metadata": null
    }
  ],
  "summary": {
    "validation_rate": 66.67,
    "source_types": {
      "url": 3
    },
    "accessibility_checked": true,
    "accessible_urls": 2,
    "inaccessible_urls": 1,
    "unchecked_urls": 0
  }
}
```

### 2. Validar Fuentes - Avanzado con IA

**Request:**
```http
POST /api/v1/sources/validate-advanced HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "biography_topic": "Albert Einstein",
  "sources": [
    {
      "title": "Wikipedia: Albert Einstein",
      "author": "Wikipedia Contributors",
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "source_type": "url"
    },
    {
      "title": "Random Article",
      "author": "Unknown",
      "url": "https://example.com/random",
      "source_type": "url"
    }
  ],
  "check_accessibility": true,
  "min_relevance": 0.7,
  "min_credibility": 80.0
}
```

**Response (200 OK):**
```json
{
  "total_sources": 2,
  "valid_sources": 1,
  "invalid_sources": 0,
  "rejected_sources": 1,
  "average_relevance": 0.85,
  "average_credibility": 90.5,
  "results": [
    {
      "source": {
        "title": "Wikipedia: Albert Einstein",
        "author": "Wikipedia Contributors",
        "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
        "source_type": "url"
      },
      "is_valid": true,
      "is_accessible": true,
      "is_trusted": true,
      "relevance_score": 0.95,
      "credibility_score": 95.0,
      "domain_category": "encyclopedia",
      "issues": [],
      "metadata": {
        "content_type": "text/html; charset=UTF-8"
      }
    },
    {
      "source": {
        "title": "Random Article",
        "author": "Unknown",
        "url": "https://example.com/random",
        "source_type": "url"
      },
      "is_valid": true,
      "is_accessible": true,
      "is_trusted": false,
      "relevance_score": 0.15,
      "credibility_score": 50.0,
      "domain_category": "unknown",
      "issues": [
        "Low relevance score (0.15 < 0.70)",
        "Low credibility score (50.0 < 80.0)"
      ],
      "metadata": {
        "content_type": "text/html"
      }
    }
  ],
  "recommendations": [
    "Remove 1 source(s) with low relevance scores",
    "Consider adding more trusted academic sources",
    "Total valid sources: 1 (recommended minimum: 40)"
  ],
  "summary": {
    "validation_rate": 50.0,
    "rejection_rate": 50.0,
    "source_types": {
      "url": 2
    },
    "trusted_sources": 1,
    "untrusted_sources": 1,
    "domain_categories": {
      "encyclopedia": 1,
      "unknown": 1
    }
  }
}
```

### 3. Generar Fuentes - Automático

**Request:**
```http
POST /api/v1/sources/generate-automatic HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "character_name": "Albert Einstein",
  "min_sources": 40,
  "max_sources": 60,
  "check_accessibility": true,
  "min_relevance": 0.7,
  "min_credibility": 80.0
}
```

**Response (200 OK):**
```json
{
  "character_name": "Albert Einstein",
  "sources": [
    {
      "title": "Wikipedia: Albert Einstein",
      "author": "Wikipedia Contributors",
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "source_type": "url"
    },
    {
      "title": "Albert Einstein - Biographical",
      "author": "Nobelprize.org",
      "url": "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
      "source_type": "url"
    }
    // ... 38+ more sources
  ],
  "character_analysis": {
    "name": "Albert Einstein",
    "category": "scientist",
    "time_period": "20th century",
    "nationality": "German-American",
    "key_achievements": [
      "Theory of Relativity",
      "Nobel Prize in Physics",
      "Photoelectric Effect"
    ]
  },
  "validation_summary": {
    "total_sources": 45,
    "valid_sources": 45,
    "average_relevance": 0.87,
    "average_credibility": 88.5,
    "trusted_sources": 42,
    "rejection_rate": 0.0
  },
  "strategies_used": [
    "wikipedia_search",
    "academic_databases",
    "biographical_sources",
    "historical_archives"
  ],
  "generation_metadata": {
    "generation_time": "12.5 seconds",
    "ai_model_used": "qwen/qwen2.5-vl-72b-instruct:free",
    "total_candidates": 120,
    "filtered_candidates": 75
  }
}
```

### 4. Generar Fuentes - Híbrido

**Request:**
```http
POST /api/v1/sources/generate-hybrid HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "character_name": "Albert Einstein",
  "user_sources": [
    "https://en.wikipedia.org/wiki/Albert_Einstein",
    "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
  ],
  "auto_complete": true,
  "target_count": 50,
  "check_accessibility": true,
  "min_relevance": 0.7,
  "min_credibility": 80.0,
  "provide_suggestions": true
}
```

**Response (200 OK):**
```json
{
  "character_name": "Albert Einstein",
  "sources": [
    {
      "title": "Wikipedia: Albert Einstein",
      "author": "Wikipedia Contributors",
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "source_type": "url"
    }
    // ... 49 more sources (2 user + 48 auto-generated)
  ],
  "user_source_count": 2,
  "auto_generated_count": 48,
  "suggestions": [
    "Consider adding more academic journal articles",
    "Add biographical books for deeper context",
    "Include primary source documents from Einstein's archives"
  ],
  "validation_summary": {
    "total_sources": 50,
    "valid_sources": 50,
    "average_relevance": 0.85,
    "average_credibility": 87.0,
    "user_sources_validated": 2,
    "auto_sources_added": 48
  },
  "configuration": {
    "auto_complete": true,
    "target_count": 50,
    "min_relevance": 0.7,
    "min_credibility": 80.0
  },
  "metadata": {
    "generation_time": "15.2 seconds",
    "strategies_used": ["user_provided", "wikipedia_search", "academic_databases"]
  }
}
```

---

## WebSocket

### WebSocket Status

**Request:**
```http
GET /ws/status HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "status": "operational",
  "connections": {
    "total": 5,
    "by_user": 3,
    "by_job": 2
  }
}
```

### WebSocket Notifications Connection

**Connection URL:**
```
ws://localhost:8000/ws/notifications?user_id=test_user&job_id=550e8400-e29b-41d4-a716-446655440000
```

**Example with wscat:**
```bash
$ wscat -c "ws://localhost:8000/ws/notifications?user_id=test&job_id=123"

Connected

< {"type":"connection","status":"connected","user_id":"test","job_id":"123","message":"WebSocket connection established"}

> ping

< {"type":"pong"}

< {"type":"progress_update","job_id":"123","progress":25.0,"phase":"Generating chapter 3","timestamp":"2025-01-07T10:40:00Z"}

< {"type":"progress_update","job_id":"123","progress":50.0,"phase":"Generating chapter 6","timestamp":"2025-01-07T10:42:00Z"}

< {"type":"completion","job_id":"123","message":"Biography generation completed","timestamp":"2025-01-07T10:45:00Z"}
```

**Message Types:**

1. **Connection Confirmation:**
```json
{
  "type": "connection",
  "status": "connected",
  "user_id": "test",
  "job_id": "123",
  "message": "WebSocket connection established"
}
```

2. **Progress Update:**
```json
{
  "type": "progress_update",
  "job_id": "123",
  "progress": 50.0,
  "phase": "Generating chapter 6",
  "timestamp": "2025-01-07T10:42:00Z"
}
```

3. **Completion:**
```json
{
  "type": "completion",
  "job_id": "123",
  "message": "Biography generation completed",
  "download_url": "/api/v1/biographies/123/download",
  "timestamp": "2025-01-07T10:45:00Z"
}
```

4. **Error Alert:**
```json
{
  "type": "error_alert",
  "job_id": "123",
  "message": "Generation failed: Rate limit exceeded",
  "error": "OpenRouter API error",
  "timestamp": "2025-01-07T10:43:00Z"
}
```

---

## 🔐 Autenticación

> **Nota:** La versión actual de la API no requiere autenticación. Futuras versiones pueden incluir API keys o tokens JWT.

## ⚠️ Rate Limiting

La API tiene un límite de **60 requests por minuto por IP**.

**Response cuando se excede el límite (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## 🐛 Manejo de Errores

### Errores Comunes

**400 Bad Request:**
```json
{
  "detail": "Validation error: character field is required"
}
```

**404 Not Found:**
```json
{
  "detail": "Job 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error occurred"
}
```

---

**Última actualización:** Enero 2025  
**Versión de la API:** v1  
**Compatibilidad:** BookGen API 1.0.0
