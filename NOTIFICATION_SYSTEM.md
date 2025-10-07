# Notification System - BookGen

## Overview

The BookGen notification system provides comprehensive real-time notifications through multiple channels:
- **WebSocket** - Real-time updates for job progress
- **Webhooks** - HTTP callbacks for external system integration
- **Email** - Optional email notifications via SMTP

## Features

### ✅ Implemented Features

- [x] **WebSocket Support** - Real-time bidirectional communication
- [x] **Webhook Integration** - Configurable webhooks for external systems
- [x] **Email Notifications** - Optional SMTP-based email delivery
- [x] **Rate Limiting** - Prevent notification spam (configurable limits)
- [x] **Notification Logging** - Database persistence of all notifications
- [x] **Multiple Notification Types**:
  - Progress Updates
  - Completion Notifications
  - Error Alerts
  - Status Changes
  - Admin Alerts

### 📊 Architecture

```
NotificationService
├── WebSocket Manager (Real-time)
│   └── Connection pooling per user/job
├── Webhook Client (HTTP)
│   └── Retry logic & error handling
└── Email Sender (SMTP)
    └── HTML & plain text support
```

## Quick Start

### Basic Usage

```python
from src.services.notifications import NotificationService

# Initialize service
service = NotificationService()

# Send progress update
await service.send_progress_update(
    job_id="123",
    progress=50.0,
    phase="Processing chapter 10 of 20"
)

# Send completion notification
await service.send_completion_notification(
    job_id="123",
    biography_id=456,
    character_name="Albert Einstein",
    status="completed",
    webhook_url="https://your-app.com/webhook",  # Optional
    user_email="user@example.com"  # Optional
)

# Send error alert
await service.send_error_alert(
    job_id="123",
    error="Generation failed",
    severity="critical",
    admin_emails=["admin@example.com"]  # Optional
)
```

### WebSocket Connection

Connect to WebSocket endpoint for real-time updates:

```javascript
// JavaScript client example
const ws = new WebSocket('ws://localhost:8000/ws/notifications?job_id=123');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Notification:', data);
    // {
    //   "type": "progress_update",
    //   "job_id": "123",
    //   "progress": 50.0,
    //   "phase": "Processing...",
    //   "timestamp": "2024-01-01T12:00:00Z"
    // }
};
```

```python
# Python client example
import asyncio
import websockets

async def listen():
    async with websockets.connect('ws://localhost:8000/ws/notifications?job_id=123') as ws:
        async for message in ws:
            print(f"Notification: {message}")

asyncio.run(listen())
```

### Webhook Configuration

Webhooks receive POST requests with JSON payloads:

```json
{
  "event": "job.completed",
  "job_id": "123",
  "biography_id": 456,
  "status": "completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {}
}
```

Event types:
- `job.progress` - Progress updates
- `job.completed` - Job completion
- `job.error` - Error alerts

## Configuration

### Environment Variables

```bash
# WebSocket
WEBSOCKET_ENABLED=true

# Webhooks
WEBHOOK_TIMEOUT=30
WEBHOOK_MAX_RETRIES=3

# Email (optional)
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@bookgen.com
SMTP_USE_TLS=true

# Admin notifications
ADMIN_EMAILS=admin1@example.com,admin2@example.com

# Rate limiting
NOTIFICATION_RATE_LIMIT_PER_MINUTE=60
NOTIFICATION_RATE_LIMIT_PER_HOUR=500

# Logging
ENABLE_NOTIFICATION_LOGGING=true
```

### Code Configuration

```python
from src.services.notifications import NotificationService, NotificationRateLimiter
from src.websocket.manager import ConnectionManager
from src.webhooks.client import WebhookClient
from src.email.sender import EmailSender

# Custom rate limiter
rate_limiter = NotificationRateLimiter(
    max_per_minute=100,
    max_per_hour=1000
)

# Custom email sender
email_sender = EmailSender(
    smtp_host="smtp.example.com",
    smtp_port=587,
    smtp_user="user@example.com",
    smtp_password="password",
    enabled=True
)

# Initialize with custom components
service = NotificationService(
    rate_limiter=rate_limiter,
    email_sender=email_sender
)
```

## API Endpoints

### WebSocket

**Endpoint:** `ws://localhost:8000/ws/notifications`

**Query Parameters:**
- `user_id` (optional) - User identifier for user-specific notifications
- `job_id` (optional) - Job ID to watch specific job updates

**Example:**
```
ws://localhost:8000/ws/notifications?job_id=123&user_id=user456
```

### WebSocket Status

**Endpoint:** `GET /ws/status`

Returns current WebSocket connection statistics.

**Response:**
```json
{
  "status": "operational",
  "connections": {
    "total_users": 5,
    "total_user_connections": 8,
    "total_jobs": 3,
    "total_job_connections": 5
  }
}
```

## Notification Types

### 1. Progress Updates
Real-time updates on job progress.

```python
await service.send_progress_update(
    job_id="123",
    progress=75.0,
    phase="Chapter 15 of 20",
    message="Generating content..."
)
```

### 2. Completion Notifications
Sent when a biography generation completes.

```python
await service.send_completion_notification(
    job_id="123",
    biography_id=456,
    character_name="Marie Curie",
    status="completed",
    webhook_url="https://example.com/webhook",
    user_email="user@example.com"
)
```

### 3. Error Alerts
Critical error notifications.

```python
await service.send_error_alert(
    job_id="123",
    error="OpenRouter API timeout",
    severity="critical",
    webhook_url="https://example.com/webhook",
    admin_emails=["admin@example.com"]
)
```

### 4. Admin Alerts
Administrative notifications.

```python
await service.send_admin_alert(
    alert_type="System Overload",
    message="Queue depth exceeds 100 jobs",
    admin_emails=["admin@example.com"],
    metadata={"queue_depth": 150, "active_workers": 2}
)
```

## Rate Limiting

The notification system includes built-in rate limiting to prevent spam:

- **Per Minute**: 60 notifications per recipient (configurable)
- **Per Hour**: 500 notifications per recipient (configurable)

Rate limits are tracked per recipient (email address, webhook URL, etc.).

When a rate limit is exceeded:
- The notification is logged with `status="rate_limited"`
- No actual delivery is attempted
- A warning is logged

## Database Logging

All notifications are logged to the `notifications` table:

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    notification_type VARCHAR(50),  -- progress_update, completion, error_alert, etc.
    delivery_method VARCHAR(50),    -- websocket, webhook, email
    recipient VARCHAR(255),          -- email, webhook URL, job_id, etc.
    subject VARCHAR(255),
    message TEXT,
    status VARCHAR(50),              -- pending, delivered, failed, rate_limited
    delivery_attempts INTEGER,
    error_message TEXT,
    related_entity_type VARCHAR(50), -- job, biography, etc.
    related_entity_id INTEGER,
    notification_metadata JSON,
    is_rate_limited BOOLEAN,
    created_at TIMESTAMP,
    delivered_at TIMESTAMP
);
```

Query notification history:

```python
from src.database.config import SessionLocal
from src.models.notification import Notification

db = SessionLocal()

# Get all notifications for a job
notifications = db.query(Notification)\
    .filter(Notification.related_entity_id == 123)\
    .filter(Notification.related_entity_type == 'job')\
    .all()

# Get failed notifications
failed = db.query(Notification)\
    .filter(Notification.status == 'failed')\
    .all()
```

## Testing

### Run Tests

```bash
# Run notification tests
pytest tests/test_notifications.py -v

# Run all tests
pytest tests/ -v
```

### Verification Script

```bash
# Run verification
python verify_notifications.py

# Run demo with issue commands
python demo_notifications.py
```

## Email Setup (Gmail Example)

For Gmail, you need an "App Password":

1. Enable 2-factor authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create a new app password
4. Use this password in SMTP_PASSWORD

```bash
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

## Integration Examples

### With Celery Tasks

```python
from src.services.notifications import NotificationService
from src.tasks import celery_app

@celery_app.task
async def generate_biography(job_id, biography_id):
    service = NotificationService()
    
    try:
        # Send progress updates
        await service.send_progress_update(job_id, 0, "Starting")
        
        # ... generation logic ...
        
        await service.send_progress_update(job_id, 50, "Halfway")
        
        # ... more generation ...
        
        # Send completion
        await service.send_completion_notification(
            job_id=job_id,
            biography_id=biography_id,
            status="completed"
        )
    except Exception as e:
        await service.send_error_alert(
            job_id=job_id,
            error=str(e),
            severity="critical"
        )
        raise
```

### With FastAPI Dependencies

```python
from fastapi import APIRouter, Depends
from src.services.notifications import NotificationService

router = APIRouter()

async def get_notification_service():
    return NotificationService()

@router.post("/jobs/{job_id}/notify")
async def notify_job_update(
    job_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    await service.send_progress_update(
        job_id=job_id,
        progress=100,
        phase="Completed"
    )
    return {"status": "notified"}
```

## Troubleshooting

### WebSocket Connection Issues

**Problem:** WebSocket won't connect

**Solution:**
- Check that the server is running
- Verify the WebSocket URL is correct (ws:// or wss://)
- Check firewall/proxy settings

### Email Not Sending

**Problem:** Emails not being delivered

**Solution:**
- Verify SMTP credentials are correct
- Check EMAIL_ENABLED=true
- For Gmail, ensure you're using an App Password
- Check spam folder
- Review logs for error messages

### Webhook Failures

**Problem:** Webhooks timing out or failing

**Solution:**
- Verify the webhook URL is accessible
- Check webhook endpoint returns 2xx status
- Increase WEBHOOK_TIMEOUT if needed
- Review webhook client logs

### Rate Limiting Too Strict

**Problem:** Legitimate notifications being rate limited

**Solution:**
- Increase rate limits in configuration
- Adjust per-minute or per-hour limits
- Review notification patterns

## Performance Considerations

- **WebSocket**: Supports thousands of concurrent connections
- **Webhooks**: Async HTTP with retry logic, 3 retries by default
- **Email**: SMTP connection pooling, async delivery
- **Database**: Indexed queries, efficient notification logging

## Security

- **WebSocket**: No authentication by default (add JWT if needed)
- **Webhooks**: Consider signing requests with HMAC
- **Email**: Use TLS encryption, app passwords
- **Rate Limiting**: Prevents DoS attacks

## Future Enhancements

- [ ] WebSocket authentication (JWT)
- [ ] Webhook signature verification (HMAC-SHA256)
- [ ] SMS notifications via Twilio
- [ ] Slack/Discord integrations
- [ ] Notification templates
- [ ] Delivery scheduling
- [ ] Notification preferences per user

## Support

For issues or questions:
- Check logs: `tail -f logs/bookgen.log`
- Run verification: `python verify_notifications.py`
- Review tests: `pytest tests/test_notifications.py -v`

## License

Part of the BookGen project - see main LICENSE file.
