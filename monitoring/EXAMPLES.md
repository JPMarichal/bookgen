# Monitoring and Observability - Visual Examples

This document shows real examples of the monitoring system in action.

## 1. Prometheus Metrics Export

The `/metrics` endpoint returns data in Prometheus format:

```prometheus
# TYPE bookgen_api_requests_total counter
bookgen_api_requests_total{endpoint="/api/v1/biographies",status="2xx"} 100.0
bookgen_api_requests_total{endpoint="/api/v1/biographies",status="5xx"} 5.0

# TYPE bookgen_biography_generation_total counter
bookgen_biography_generation_total{status="error"} 2.0
bookgen_biography_generation_total{status="success"} 10.0

# TYPE bookgen_errors_total counter
bookgen_errors_total{component="content_generation",error_type="api_error"} 1.0
bookgen_errors_total{component="source_validation",error_type="validation_error"} 3.0

# TYPE bookgen_cpu_percent gauge
bookgen_cpu_percent 42.5

# TYPE bookgen_memory_percent gauge
bookgen_memory_percent 67.3

# TYPE bookgen_disk_percent gauge
bookgen_disk_percent 45.8

# TYPE bookgen_jobs_total gauge
bookgen_jobs_total{status="completed"} 45
bookgen_jobs_total{status="failed"} 2
bookgen_jobs_total{status="in_progress"} 3
bookgen_jobs_total{status="pending"} 5

# TYPE bookgen_api_request_duration_seconds histogram
bookgen_api_request_duration_seconds_count{endpoint="/api/v1/biographies"} 100
bookgen_api_request_duration_seconds_sum{endpoint="/api/v1/biographies"} 9.95

# TYPE bookgen_biography_generation_seconds histogram
bookgen_biography_generation_seconds_count{status="success"} 10
bookgen_biography_generation_seconds_sum{status="success"} 14700
```

## 2. Structured JSON Logs

Example log stream showing a complete request with correlation ID:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "bookgen.api.biographies",
  "message": "Biography generation request received",
  "app": "bookgen",
  "correlation_id": "f54146ae-518e-4019-b67b-d0d84a573952",
  "character": "Albert Einstein",
  "user_id": 42,
  "request_id": "req-12345",
  "location": {
    "file": "/app/src/api/routers/biographies.py",
    "line": 123,
    "function": "create_biography"
  },
  "process": {
    "pid": 1234,
    "thread": 5678,
    "thread_name": "MainThread"
  }
}
```

```json
{
  "timestamp": "2025-01-15T10:30:46.234567+00:00",
  "level": "INFO",
  "logger": "bookgen.services.validation",
  "message": "Source validation started",
  "app": "bookgen",
  "correlation_id": "f54146ae-518e-4019-b67b-d0d84a573952",
  "source_count": 15,
  "validation_type": "deep"
}
```

```json
{
  "timestamp": "2025-01-15T10:30:47.345678+00:00",
  "level": "WARNING",
  "logger": "bookgen.services.content",
  "message": "API rate limit approaching",
  "app": "bookgen",
  "correlation_id": "f54146ae-518e-4019-b67b-d0d84a573952",
  "current_usage": 85,
  "limit": 100,
  "component": "openrouter"
}
```

## 3. Alert Examples

### Example 1: High Error Rate Alert

```yaml
Alert: HighErrorRate
Status: FIRING
Severity: critical
Description: Error rate is above 5% for the last 5 minutes (current: 8.2%)
Component: application
Duration: 5m 23s
```

### Example 2: Long Biography Generation

```yaml
Alert: LongBiographyGenerationTime
Status: FIRING  
Severity: warning
Description: Biography generation has exceeded 45 minutes (current: 52m 15s)
Component: content_generation
Duration: 7m 15s
```

### Example 3: High Memory Usage

```yaml
Alert: HighMemoryUsage
Status: FIRING
Severity: warning
Description: Memory usage is above 80% for the last 5 minutes (current: 84%)
Component: system
Duration: 5m 02s
```

## 4. Grafana Dashboard Panels

### Panel 1: System Health
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Uptime    │  CPU Usage  │Mem Usage    │ Disk Usage  │
│   3h 15m    │    42.5%    │   67.3%     │   45.8%     │
│    🟢       │    🟢       │    🟡       │    🟢       │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Panel 2: Jobs by Status
```
   Jobs
    60 │
    50 │              ████████
    40 │              ████████
    30 │              ████████
    20 │              ████████
    10 │    ████      ████████
     0 │────────────────────────────────────
         Pending  In Progress  Completed  Failed
```

### Panel 3: API Request Rate
```
Requests/sec
    50 │                      ╱╲
    40 │                    ╱    ╲
    30 │              ╱╲  ╱        ╲
    20 │          ╱╲╱  ╲╱            ╲
    10 │    ╱╲  ╱                      ╲
     0 │────────────────────────────────────
       10:00  10:15  10:30  10:45  11:00
```

### Panel 4: API Response Time (Percentiles)
```
Latency (ms)
   500 │                              
   400 │                        ━━━━ p99
   300 │                    ━━━━
   200 │              ━━━━━━        ━━━━ p95
   100 │        ━━━━━━              
    50 │  ━━━━━━                    ━━━━ p50
     0 │────────────────────────────────────
       10:00  10:15  10:30  10:45  11:00
```

## 5. Request Tracing Flow

Following a single request through the system using correlation ID:

```
Step 1: API receives request
→ correlation_id: f54146ae-518e-4019-b67b-d0d84a573952
→ endpoint: POST /api/v1/biographies/generate
→ timestamp: 10:30:45.123

Step 2: Source validation
→ correlation_id: f54146ae-518e-4019-b67b-d0d84a573952
→ component: source_validator
→ sources_found: 15
→ timestamp: 10:30:46.234

Step 3: Content generation
→ correlation_id: f54146ae-518e-4019-b67b-d0d84a573952
→ component: content_generator
→ api_calls: 12
→ timestamp: 10:30:47.345

Step 4: Response sent
→ correlation_id: f54146ae-518e-4019-b67b-d0d84a573952
→ status: 202
→ duration_ms: 2234.5
→ timestamp: 10:32:47.568
```

## 6. Alertmanager Notification (Slack)

```
🚨 CRITICAL: HighErrorRate

Summary: High error rate detected in BookGen
Description: Error rate is above 5% for the last 5 minutes (current: 8.2%)
Component: application
Severity: critical

View in Prometheus: http://prometheus:9090/alerts
Silence: http://alertmanager:9093/#/silences/new
```

## 7. Usage Examples

### In Application Code

```python
from src.monitoring import increment_counter, observe_histogram, get_structured_logger

# Track an API request
increment_counter(
    "bookgen_api_requests_total",
    labels={"endpoint": "/api/v1/biographies", "status": "2xx"}
)

# Record request duration
observe_histogram(
    "bookgen_api_request_duration_seconds",
    0.234,
    labels={"endpoint": "/api/v1/biographies"}
)

# Log with structured data
logger = get_structured_logger(__name__)
logger.info(
    "Biography generated successfully",
    character="Albert Einstein",
    word_count=12500,
    generation_time=1234.5
)
```

### Querying Prometheus

```promql
# Average API latency over 5 minutes
rate(bookgen_api_request_duration_seconds_sum[5m]) 
/ 
rate(bookgen_api_request_duration_seconds_count[5m])

# Error rate percentage
(
  rate(bookgen_api_requests_total{status="5xx"}[5m])
  /
  rate(bookgen_api_requests_total[5m])
) * 100

# Biography generation throughput
rate(bookgen_biography_generation_total{status="success"}[1h]) * 3600
```

## 8. Docker Compose Stack

```bash
$ docker-compose -f monitoring/docker-compose.yml ps

NAME                    STATUS    PORTS
bookgen-prometheus      Up        0.0.0.0:9090->9090/tcp
bookgen-grafana         Up        0.0.0.0:3000->3000/tcp
bookgen-alertmanager    Up        0.0.0.0:9093->9093/tcp

$ docker-compose -f monitoring/docker-compose.yml logs -f grafana
grafana_1      | t=2025-01-15T10:30:00+0000 lvl=info msg="HTTP Server Listen"
grafana_1      | t=2025-01-15T10:30:01+0000 lvl=info msg="Initializing provisioning"
grafana_1      | t=2025-01-15T10:30:02+0000 lvl=info msg="Dashboard provisioned" dashboard="BookGen Monitoring Dashboard"
```

## Summary

The monitoring system provides:
- ✅ **Real-time metrics** in Prometheus format
- ✅ **Structured logs** with correlation IDs for tracing
- ✅ **Automated alerts** with smart routing
- ✅ **Visual dashboards** in Grafana
- ✅ **End-to-end visibility** across the entire system
