# Notification System - Quick Reference

## 🚀 Quick Start

```python
from src.services.notifications import NotificationService

# Initialize
service = NotificationService()

# Send progress update
await service.send_progress_update(
    job_id="123",
    progress=50.0,
    phase="Processing"
)

# Send completion
await service.send_completion_notification(
    job_id="123",
    biography_id=456,
    character_name="Name",
    webhook_url="https://your-webhook.com",  # optional
    user_email="user@example.com"  # optional
)

# Send error alert
await service.send_error_alert(
    job_id="123",
    error="Error message",
    severity="critical"
)
```

## 🔌 WebSocket Connection

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/notifications?job_id=123');

// Listen for messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // data.type: "progress_update", "completion", "error_alert"
    // data.progress, data.phase, data.message, etc.
};
```

## 🌐 Webhook Integration

Your webhook endpoint will receive POST requests:

```json
{
  "event": "job.completed",
  "job_id": "123",
  "biography_id": 456,
  "status": "completed",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📧 Email Configuration

```bash
# .env file
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@bookgen.com
ADMIN_EMAILS=admin@example.com
```

## 🎚️ Rate Limiting

Default limits (configurable):
- 60 notifications per minute per recipient
- 500 notifications per hour per recipient

```bash
NOTIFICATION_RATE_LIMIT_PER_MINUTE=60
NOTIFICATION_RATE_LIMIT_PER_HOUR=500
```

## 📊 API Endpoints

| Endpoint | Type | Description |
|----------|------|-------------|
| `/ws/notifications` | WebSocket | Real-time notifications |
| `/ws/status` | GET | Connection statistics |

## 🧪 Testing

```bash
# Run tests
pytest tests/test_notifications.py -v

# Verify system
python development/scripts/verification/verify_notifications.py

# Demo commands
python development/examples/demo_notifications.py
```

## 🔍 Notification Types

| Type | Description | Channels |
|------|-------------|----------|
| `progress_update` | Job progress | WebSocket, Webhook |
| `completion` | Job completed | WebSocket, Webhook, Email |
| `error_alert` | Error occurred | WebSocket, Webhook, Email (admin) |
| `status_change` | Status update | WebSocket, Webhook |
| `admin_alert` | Admin notification | Email |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/services/notifications.py` | Main service |
| `src/websocket/manager.py` | WebSocket manager |
| `src/webhooks/client.py` | Webhook client |
| `src/email/sender.py` | Email sender |
| `NOTIFICATION_SYSTEM.md` | Full documentation |

## 🛠️ Common Operations

### Get WebSocket client
```python
ws_client = service.get_websocket_client()
is_connected = ws_client.is_connected(job_id="123")
stats = ws_client.get_connection_count()
```

### Check delivery status
```python
status = service.get_delivery_status()  # "DELIVERED", "UNKNOWN", etc.
```

### Query notification logs
```python
from src.database.config import SessionLocal
from src.models.notification import Notification

db = SessionLocal()
notifications = db.query(Notification)\
    .filter(Notification.related_entity_id == 123)\
    .all()
```

## 📚 More Info

- Full documentation: `NOTIFICATION_SYSTEM.md`
- Implementation details: `IMPLEMENTATION_SUMMARY_ISSUE_13.md`
- Examples: `example_notification_integration.py`
