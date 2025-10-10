# BookGen Monitoring and Observability

This directory contains the complete monitoring and observability stack for BookGen, implementing comprehensive metrics collection, visualization, and alerting.

## 📊 Overview

The monitoring stack includes:

- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization dashboards
- **Alertmanager** - Alert routing and notification
- **Structured Logging** - JSON-formatted logs with correlation IDs
- **Request Tracing** - End-to-end request tracking

## 🚀 Quick Start

### Start the Monitoring Stack

```bash
# Ensure the bookgen-network exists
docker network create bookgen-network 2>/dev/null || true

# Start monitoring services
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d

# Verify services are running
docker-compose -f infrastructure/monitoring/docker-compose.yml ps
```

### Access the Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **Alertmanager**: http://localhost:9093
- **BookGen Metrics**: http://localhost:8000/metrics

### Test the Setup

```bash
# Run alert tests
python development/scripts/test_alerts.py

# Check metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

## 📈 Metrics

### System Metrics

- **bookgen_uptime_seconds** - Application uptime
- **bookgen_cpu_percent** - CPU usage percentage
- **bookgen_memory_percent** - Memory usage percentage
- **bookgen_memory_available_bytes** - Available memory in bytes
- **bookgen_disk_percent** - Disk usage percentage

### Application Metrics

- **bookgen_jobs_total{status}** - Total jobs by status (pending, in_progress, completed, failed)
- **bookgen_api_requests_total{endpoint, status}** - Total API requests by endpoint and status
- **bookgen_api_request_duration_seconds** - API request duration histogram
- **bookgen_biography_generation_total{status}** - Total biography generations by status
- **bookgen_biography_generation_seconds** - Biography generation time histogram
- **bookgen_errors_total{error_type, component}** - Total errors by type and component

### Custom Metrics

You can add custom metrics in your code:

```python
from src.monitoring import increment_counter, observe_histogram, set_gauge

# Increment a counter
increment_counter("my_custom_counter", labels={"type": "example"})

# Record a histogram observation
observe_histogram("my_custom_duration", 1.5, labels={"operation": "test"})

# Set a gauge value
set_gauge("my_custom_gauge", 42.0)
```

## 🔔 Alerts

### Configured Alerts

1. **HighErrorRate** - Triggers when error rate > 5% for 5 minutes
2. **LongBiographyGenerationTime** - Triggers when generation > 45 minutes
3. **HighMemoryUsage** - Triggers when memory usage > 80% for 5 minutes
4. **CriticalMemoryUsage** - Triggers when memory usage > 90% for 2 minutes
5. **HighCPUUsage** - Triggers when CPU usage > 85% for 10 minutes
6. **QueueBackup** - Triggers when pending jobs > 50 for 5 minutes
7. **APIDown** - Triggers when API is unreachable for 1 minute
8. **HighAPILatency** - Triggers when 95th percentile latency > 500ms for 5 minutes
9. **HighDiskUsage** - Triggers when disk usage > 80% for 5 minutes
10. **CriticalDiskUsage** - Triggers when disk usage > 90% for 1 minute

### SLA Monitoring

- **SLAUptimeViolation** - Triggers when uptime < 99% over 1 hour
- **SLASuccessRateViolation** - Triggers when success rate < 95% over 1 hour

### Alert Notification Channels

Configure alert notifications via environment variables:

```bash
# Slack notifications
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Email notifications (configure in alertmanager.yml)
export SMTP_PASSWORD="your-smtp-password"
```

Then restart Alertmanager:

```bash
docker-compose -f infrastructure/monitoring/docker-compose.yml restart alertmanager
```

## 📊 Grafana Dashboards

### BookGen Monitoring Dashboard

The main dashboard includes:

1. **System Health** - Uptime, CPU, Memory, Disk gauges
2. **Job Status** - Jobs by status over time
3. **API Performance** - Request rate and response times
4. **Biography Generation** - Generation time percentiles
5. **Error Tracking** - Error rate by component

Access at: http://localhost:3000/d/bookgen-main

### Creating Custom Dashboards

1. Log into Grafana (http://localhost:3000)
2. Click "+" → "Dashboard"
3. Add panels with Prometheus queries
4. Save the dashboard

## 📝 Structured Logging

### Setup Structured Logging

```python
from src.monitoring import setup_logging, get_structured_logger

# Setup logging (call once at application startup)
setup_logging(level="INFO", json_format=True, app_name="bookgen")

# Get a logger
logger = get_structured_logger(__name__)

# Log with context
logger.info("Processing request", user_id=123, action="generate_biography")
logger.error("Failed to process", error_code="500", component="content_gen")
```

### Correlation IDs for Request Tracing

Correlation IDs allow you to trace requests end-to-end across services:

```python
from src.monitoring import set_correlation_id, get_correlation_id

# Set correlation ID (usually in middleware)
correlation_id = set_correlation_id()  # Auto-generates UUID

# Or use existing correlation ID from request header
correlation_id = set_correlation_id(request.headers.get("X-Correlation-ID"))

# Get current correlation ID
current_id = get_correlation_id()

# Logs will automatically include the correlation ID
logger.info("Processing request")  # Will include correlation_id in JSON output
```

### JSON Log Format

Structured logs are output in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "src.api.routers.biographies",
  "message": "Biography generation started",
  "app": "bookgen",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123,
  "biography_id": "bio-456",
  "location": {
    "file": "/app/src/api/routers/biographies.py",
    "line": 45,
    "function": "generate_biography"
  },
  "process": {
    "pid": 1234,
    "thread": 5678,
    "thread_name": "MainThread"
  }
}
```

## 🔧 Configuration

### Prometheus Configuration

Edit `infrastructure/monitoring/prometheus/prometheus.yml` to:

- Add new scrape targets
- Adjust scrape intervals
- Configure external labels

### Alert Rules

Edit `infrastructure/monitoring/prometheus/alerts.yml` to:

- Add new alert rules
- Modify thresholds
- Adjust evaluation intervals

### Grafana Configuration

Dashboards are provisioned from `infrastructure/monitoring/grafana/dashboards/`

Data sources are configured in `infrastructure/monitoring/grafana/provisioning/datasources/`

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose -f infrastructure/monitoring/docker-compose.yml logs prometheus
docker-compose -f infrastructure/monitoring/docker-compose.yml logs grafana
docker-compose -f infrastructure/monitoring/docker-compose.yml logs alertmanager

# Restart services
docker-compose -f infrastructure/monitoring/docker-compose.yml restart
```

### Metrics Not Appearing

1. Check that BookGen API is running: `curl http://localhost:8000/health`
2. Check metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus targets: http://localhost:9090/targets
4. Verify network connectivity: `docker network ls`

### Alerts Not Firing

1. Check alert rules are loaded: http://localhost:9090/alerts
2. Verify Alertmanager is receiving alerts: http://localhost:9093
3. Check Alertmanager configuration
4. Test with: `python development/scripts/test_alerts.py`

### Grafana Dashboard Not Loading

1. Verify Prometheus data source: http://localhost:3000/datasources
2. Check that Prometheus is accessible from Grafana
3. Reload provisioning: Restart Grafana container

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## ✅ Verification Commands

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Start monitoring stack
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d

# Access Grafana dashboard
curl http://localhost:3000  # Grafana (admin/admin)
curl http://localhost:9090  # Prometheus

# Test alerting
python development/scripts/test_alerts.py

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Check active alerts
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {name: .labels.alertname, state: .state}'

# Verify structured logging
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{"character": "Test"}' \
  && docker-compose logs --tail=10 bookgen-api
```

## 🎯 Acceptance Criteria Status

- ✅ Métricas exportadas a Prometheus
- ✅ Dashboard Grafana funcional
- ✅ Alertas configuradas para errores críticos
- ✅ Logs estructurados en JSON
- ✅ Tracing de requests end-to-end (correlation IDs)
- ✅ SLA monitoring automatizado
