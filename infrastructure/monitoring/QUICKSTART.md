# Monitoring Quick Start Guide

This guide will help you quickly set up and verify the BookGen monitoring stack.

## Prerequisites

- Docker and Docker Compose installed
- BookGen API running on port 8000
- Network `bookgen-network` created

## Step 1: Create the Network (if needed)

```bash
docker network create bookgen-network
```

## Step 2: Configure Environment Variables

```bash
cd monitoring
cp .env.example .env

# Edit .env to add your Slack webhook URL (optional)
nano .env
```

## Step 3: Start Monitoring Stack

```bash
# From the project root
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d
```

Wait a few seconds for services to start.

## Step 4: Verify Services

```bash
# Check service status
docker-compose -f infrastructure/monitoring/docker-compose.yml ps

# Should show:
# - bookgen-prometheus   (port 9090)
# - bookgen-grafana      (port 3000)
# - bookgen-alertmanager (port 9093)
```

## Step 5: Access Dashboards

Open your browser and navigate to:

1. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin` (change on first login)
   - Navigate to: Dashboards → BookGen Monitoring Dashboard

2. **Prometheus**: http://localhost:9090
   - Check targets: http://localhost:9090/targets
   - Check alerts: http://localhost:9090/alerts

3. **Alertmanager**: http://localhost:9093

## Step 6: Verify Metrics

```bash
# Check BookGen metrics endpoint
curl http://localhost:8000/metrics

# Should return Prometheus-format metrics
```

## Step 7: Run Alert Tests

```bash
# From the project root
python development/scripts/test_alerts.py
```

Expected output should show:
- ✓ Prometheus is running
- ✓ Alertmanager is running
- ✓ Grafana is running
- ✓ All expected metrics are present
- ✓ All expected alert rules are loaded

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose -f infrastructure/monitoring/docker-compose.yml logs

# Restart services
docker-compose -f infrastructure/monitoring/docker-compose.yml restart
```

### Grafana shows "No Data"

1. Check Prometheus is scraping metrics:
   - Go to http://localhost:9090/targets
   - Verify `bookgen-api` target is "UP"

2. If target is "DOWN":
   ```bash
   # Check if BookGen API is running
   curl http://localhost:8000/health
   
   # Check network connectivity
   docker network inspect bookgen-network
   ```

### Metrics not appearing

```bash
# Check if BookGen API is in the same network
docker inspect bookgen-api | grep NetworkMode

# If not in bookgen-network, add it:
docker network connect bookgen-network bookgen-api
```

## Testing Alerts

To test that alerts work, you can:

1. **Test High Memory Alert**: 
   - Generate multiple large biographies simultaneously
   - Monitor memory usage in Grafana

2. **Test API Down Alert**:
   ```bash
   # Stop the API briefly
   docker stop bookgen-api
   # Wait 1 minute
   # Start it again
   docker start bookgen-api
   ```

3. **Check Alert Status**:
   - Prometheus: http://localhost:9090/alerts
   - Alertmanager: http://localhost:9093

## Next Steps

- Configure Slack notifications (see `monitoring/README.md`)
- Customize dashboards in Grafana
- Adjust alert thresholds in `monitoring/prometheus/alerts.yml`
- Set up email notifications in `monitoring/alertmanager/alertmanager.yml`

## Stopping the Stack

```bash
docker-compose -f infrastructure/monitoring/docker-compose.yml down

# To remove volumes as well (will delete historical data):
docker-compose -f infrastructure/monitoring/docker-compose.yml down -v
```

## Useful Commands

```bash
# View logs
docker-compose -f infrastructure/monitoring/docker-compose.yml logs -f prometheus
docker-compose -f infrastructure/monitoring/docker-compose.yml logs -f grafana

# Restart a specific service
docker-compose -f infrastructure/monitoring/docker-compose.yml restart prometheus

# Check resource usage
docker stats bookgen-prometheus bookgen-grafana bookgen-alertmanager
```
