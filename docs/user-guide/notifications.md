# Understanding Notifications

Complete guide to BookGen's notification system and how to interpret updates.

## 📬 Notification Overview

BookGen provides three notification channels:

1. **WebSocket** - Real-time bidirectional updates
2. **Webhook** - HTTP callbacks to your application
3. **Email** - Optional email notifications (SMTP)

---

## 🔌 WebSocket Notifications

### Connecting to WebSocket

**JavaScript:**
```javascript
const jobId = "your-job-id-here";
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?job_id=${jobId}`);

ws.onopen = () => {
  console.log('✅ Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleNotification(data);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
  console.log('🔌 WebSocket closed');
};
```

**Python:**
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Progress: {data['progress']}%")
    print(f"Phase: {data['message']}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("WebSocket closed")

job_id = "your-job-id-here"
ws = websocket.WebSocketApp(
    f"ws://localhost:8000/ws/notifications?job_id={job_id}",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

### WebSocket Message Types

#### Progress Update
```json
{
  "type": "progress_update",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "processing",
  "progress": 45.5,
  "message": "Generating Chapter 9 of 20",
  "timestamp": "2025-01-07T13:15:00Z"
}
```

**What it means:**
- Job is actively processing
- 45.5% complete
- Currently generating chapter 9
- Check `progress` field for percentage

**How to respond:**
- Update progress bar
- Display current phase
- Show estimated time remaining

#### Completion Notification
```json
{
  "type": "completion",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "completed",
  "progress": 100.0,
  "message": "Biography generation completed successfully",
  "output_file": "docx/albert_einstein/La biografia de Albert Einstein.docx",
  "total_words": 51245,
  "chapters": 20,
  "duration_seconds": 9000,
  "timestamp": "2025-01-07T14:30:00Z"
}
```

**What it means:**
- Biography is complete
- Files are ready for download
- Total generation time: 2.5 hours
- 51,245 words across 20 chapters

**How to respond:**
- Show success message
- Provide download link
- Close WebSocket connection
- Update job status to completed

#### Error Notification
```json
{
  "type": "error",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "failed",
  "message": "Biography generation failed",
  "error": "Insufficient valid sources: 25 of 40 required",
  "severity": "critical",
  "timestamp": "2025-01-07T12:15:00Z"
}
```

**What it means:**
- Job failed and won't continue
- Reason: Not enough valid sources
- User needs to take action

**How to respond:**
- Show error message to user
- Explain what went wrong
- Suggest remediation (add more sources)
- Close WebSocket connection

#### Phase Change Notification
```json
{
  "type": "phase_change",
  "job_id": "123e4567...",
  "status": "processing",
  "previous_phase": "Source Validation",
  "current_phase": "Chapter Generation",
  "progress": 15.0,
  "message": "Starting chapter generation",
  "timestamp": "2025-01-07T12:20:00Z"
}
```

**What it means:**
- Job moved to new phase
- Source validation complete
- Now generating chapters

**How to respond:**
- Update phase indicator
- Show new phase description
- May want to log phase timing

---

## 🔗 Webhook Notifications

### Configuring Webhooks

**In Biography Request:**
```bash
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "sources": [...],
    "webhook_url": "https://your-app.com/bookgen-webhook",
    "webhook_secret": "your-secret-key"
  }'
```

**Global Configuration (.env):**
```bash
WEBHOOK_URL=https://your-app.com/webhook
WEBHOOK_SECRET=your-secret-key
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
```

### Webhook Payload

BookGen sends POST requests to your webhook URL:

**Completion Webhook:**
```json
{
  "event": "biography.completed",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "completed",
  "output_file": "docx/albert_einstein/La biografia de Albert Einstein.docx",
  "total_words": 51245,
  "chapters": 20,
  "duration_seconds": 9000,
  "completed_at": "2025-01-07T14:30:00Z",
  "signature": "sha256=abcdef123456..."
}
```

**Error Webhook:**
```json
{
  "event": "biography.failed",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "failed",
  "error": "Insufficient valid sources",
  "failed_at": "2025-01-07T12:15:00Z",
  "signature": "sha256=abcdef123456..."
}
```

### Implementing Webhook Receiver

**Express.js (Node.js):**
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

function verifySignature(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(JSON.stringify(payload));
  const computed = 'sha256=' + hmac.digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(computed)
  );
}

app.post('/bookgen-webhook', (req, res) => {
  const signature = req.headers['x-bookgen-signature'];
  const secret = process.env.WEBHOOK_SECRET;
  
  // Verify signature
  if (!verifySignature(req.body, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process webhook
  const { event, job_id, status } = req.body;
  
  if (event === 'biography.completed') {
    console.log(`✅ Biography ${job_id} completed`);
    // Notify user, send email, etc.
  } else if (event === 'biography.failed') {
    console.log(`❌ Biography ${job_id} failed`);
    // Alert user, log error, etc.
  }
  
  res.status(200).json({ received: true });
});

app.listen(3000);
```

**Python (Flask):**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

def verify_signature(payload, signature, secret):
    computed = 'sha256=' + hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, computed)

@app.route('/bookgen-webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Bookgen-Signature')
    secret = os.environ['WEBHOOK_SECRET']
    
    # Verify signature
    if not verify_signature(request.json, signature, secret):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook
    event = request.json.get('event')
    job_id = request.json.get('job_id')
    
    if event == 'biography.completed':
        print(f"✅ Biography {job_id} completed")
        # Notify user, send email, etc.
    elif event == 'biography.failed':
        print(f"❌ Biography {job_id} failed")
        # Alert user, log error, etc.
    
    return jsonify({'received': True}), 200

if __name__ == '__main__':
    app.run(port=3000)
```

### Webhook Security

**Verify Signatures:**
Always verify the `X-Bookgen-Signature` header to ensure webhooks are from BookGen.

**Use HTTPS:**
```bash
# Require HTTPS in production
WEBHOOK_URL=https://your-app.com/webhook  # ✅
# Not: http://your-app.com/webhook        # ❌
```

**Implement Idempotency:**
```javascript
const processedWebhooks = new Set();

app.post('/webhook', (req, res) => {
  const { job_id, event } = req.body;
  const webhookId = `${job_id}-${event}`;
  
  // Check if already processed
  if (processedWebhooks.has(webhookId)) {
    return res.status(200).json({ received: true, duplicate: true });
  }
  
  // Process webhook
  processWebhook(req.body);
  
  // Mark as processed
  processedWebhooks.add(webhookId);
  
  res.status(200).json({ received: true });
});
```

---

## 📧 Email Notifications

### Configuring Email

```bash
# .env configuration
ENABLE_EMAIL_NOTIFICATIONS=true

# SMTP settings (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@bookgen.ai
SMTP_USE_TLS=true

# Recipients
ADMIN_EMAILS=admin@example.com,support@example.com
```

### Email Types

#### Completion Email
**Subject:** ✅ Biography Completed: Albert Einstein

**Body:**
```
Your biography generation for Albert Einstein has completed successfully!

Details:
- Job ID: 123e4567-e89b-12d3-a456-426614174000
- Character: Albert Einstein
- Total Words: 51,245
- Chapters: 20
- Duration: 2 hours 30 minutes

Output Files:
- Markdown: bios/albert_einstein/La biografia de Albert Einstein.md
- Word: docx/albert_einstein/La biografia de Albert Einstein.docx

Generated: 2025-01-07 14:30:00 UTC
```

#### Error Email
**Subject:** ❌ Biography Failed: Albert Einstein

**Body:**
```
Unfortunately, your biography generation for Albert Einstein has failed.

Error Details:
- Job ID: 123e4567-e89b-12d3-a456-426614174000
- Error: Insufficient valid sources: 25 of 40 required
- Failed At: 2025-01-07 12:15:00 UTC

Recommended Actions:
1. Review source URLs for accessibility
2. Add more quality sources (need 15+ more)
3. Remove broken or paywalled URLs
4. Submit a new generation request

Need help? Contact support@bookgen.ai
```

#### Admin Alert Email
**Subject:** 🚨 ALERT: BookGen System Issue

**Body:**
```
Critical system alert from BookGen:

Alert Type: Database Connection Failed
Severity: Critical
Time: 2025-01-07 15:45:00 UTC

Details:
- Service: bookgen-api
- Error: could not connect to server: Connection refused

Recommended Actions:
1. Check database service status
2. Verify network connectivity
3. Review database logs
4. Restart database if needed

Automated monitoring will continue.
```

### Email Notification Triggers

**User Notifications:**
- ✅ Biography completed
- ❌ Biography failed
- ⚠️ Source validation warnings

**Admin Notifications:**
- 🚨 System errors
- ⚠️ Service degradation
- 📊 Daily summary reports
- 🔒 Security alerts

---

## 🔔 Notification Best Practices

### For Application Developers

**Use WebSocket for UI:**
```javascript
// ✅ Good: Real-time updates
const ws = new WebSocket(`ws://...?job_id=${jobId}`);
ws.onmessage = (event) => updateProgressBar(event.data);
```

**Use Webhooks for Automation:**
```javascript
// ✅ Good: Reliable, retry-able
{
  "webhook_url": "https://your-app.com/webhook",
  "user_email": "user@example.com"
}
```

**Implement Exponential Backoff:**
```javascript
// ❌ Bad: Constant polling
setInterval(() => checkStatus(), 1000);

// ✅ Good: Exponential backoff
let delay = 5000;
function checkStatus() {
  // Check status...
  delay = Math.min(delay * 1.5, 60000);  // Max 1 minute
  setTimeout(checkStatus, delay);
}
```

### For End Users

**Monitor Progress:**
- WebSocket shows real-time updates
- Check every 30-60 seconds if polling
- Don't spam the API

**Understand Phases:**
- Source validation: Usually fast (5-10 min)
- Chapter generation: Longest phase (1-2 hours)
- Export: Quick final step (5 min)

**When to Take Action:**
- **Status: failed** → Review error, fix issues, retry
- **Status: completed** → Download files
- **Long processing time** → Normal, be patient

---

## 📊 Notification Examples

### Complete Lifecycle Example

```javascript
class BiographyMonitor {
  constructor(jobId) {
    this.jobId = jobId;
    this.ws = null;
    this.startTime = Date.now();
  }
  
  connect() {
    this.ws = new WebSocket(
      `ws://localhost:8000/ws/notifications?job_id=${this.jobId}`
    );
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleNotification(data);
    };
  }
  
  handleNotification(data) {
    const elapsed = (Date.now() - this.startTime) / 1000;
    
    console.log(`[${elapsed}s] ${data.type}:`);
    console.log(`  Status: ${data.status}`);
    console.log(`  Progress: ${data.progress}%`);
    console.log(`  Message: ${data.message}`);
    
    // Update UI
    this.updateProgressBar(data.progress);
    this.updatePhaseText(data.message);
    
    // Handle completion
    if (data.status === 'completed') {
      this.onComplete(data);
    }
    
    // Handle errors
    if (data.status === 'failed') {
      this.onError(data);
    }
  }
  
  updateProgressBar(progress) {
    const bar = document.getElementById('progress-bar');
    bar.style.width = `${progress}%`;
    bar.textContent = `${progress.toFixed(1)}%`;
  }
  
  updatePhaseText(message) {
    document.getElementById('phase').textContent = message;
  }
  
  onComplete(data) {
    console.log('✅ Biography completed!');
    console.log(`📄 Output: ${data.output_file}`);
    
    // Show success message
    alert('Biography completed! Ready for download.');
    
    // Close connection
    this.ws.close();
  }
  
  onError(data) {
    console.error('❌ Biography failed!');
    console.error(`Error: ${data.error}`);
    
    // Show error message
    alert(`Error: ${data.error}`);
    
    // Close connection
    this.ws.close();
  }
}

// Usage
const monitor = new BiographyMonitor('your-job-id');
monitor.connect();
```

---

## 🆘 Troubleshooting Notifications

### WebSocket Won't Connect
```bash
# Check WebSocket endpoint
curl http://localhost:8000/ws/notifications

# Verify job ID is valid
curl http://localhost:8000/api/v1/biographies/YOUR_JOB_ID

# Check CORS settings
# Add your origin to .env:
CORS_ORIGINS=http://localhost:3000,ws://localhost:8000
```

### Not Receiving Webhooks
```bash
# Test webhook URL is accessible
curl -X POST https://your-app.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check webhook logs in BookGen
docker logs bookgen-api | grep webhook

# Verify signature validation in your code
```

### Emails Not Arriving
```bash
# Check SMTP configuration
cat .env | grep SMTP

# Test SMTP connection
docker exec bookgen-api python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('user@gmail.com', 'password')
server.quit()
print('✅ SMTP works')
"
```

---

[← Creating Biographies](creating-biographies.md) | [Export Formats →](export-formats.md)
