# Quick Start Guide

Get started with BookGen and create your first biography in minutes!

## ⚡ Prerequisites

Before starting, ensure you have:

- ✅ BookGen installed ([Installation Guide](installation.md))
- ✅ Services running (`docker-compose ps` shows all healthy)
- ✅ OpenRouter API key configured in `.env`

## 🎯 Your First Biography

### Step 1: Prepare Source URLs

Collect 40-60 high-quality sources about your subject:

```bash
# Example: Albert Einstein
sources=(
  "https://en.wikipedia.org/wiki/Albert_Einstein"
  "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
  "https://www.britannica.com/biography/Albert-Einstein"
  # Add 37+ more quality sources
)
```

**Source Quality Tips:**
- ✅ Academic sources (.edu, scholarly articles)
- ✅ Official biographies and archives
- ✅ Reputable encyclopedias
- ❌ Social media posts
- ❌ Unreliable blogs
- ❌ Paywalled content

### Step 2: Create Biography Job

**Using the API:**

```bash
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "sources": [
      "https://en.wikipedia.org/wiki/Albert_Einstein",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
      "https://www.britannica.com/biography/Albert-Einstein"
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

**Using Interactive API Docs:**

1. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click on `POST /api/v1/biographies`
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

### Step 3: Monitor Progress

**Option A: WebSocket (Real-time)**

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/ws/notifications?job_id=123e4567...');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}% - ${data.message}`);
};
```

**Option B: Polling (REST API)**

```bash
# Check job status
curl http://localhost:8000/api/v1/biographies/123e4567-e89b-12d3-a456-426614174000
```

**Option C: Logs**

```bash
# Watch worker logs
docker logs -f bookgen-worker

# Watch API logs
docker logs -f bookgen-api
```

### Step 4: Retrieve Completed Biography

**Get Biography Details:**

```bash
curl http://localhost:8000/api/v1/biographies/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "character": "Albert Einstein",
  "status": "completed",
  "progress": 100.0,
  "chapters": 20,
  "total_words": 51245,
  "output_file": "docx/albert_einstein/La biografia de Albert Einstein.docx",
  "created_at": "2025-01-07T12:00:00Z",
  "completed_at": "2025-01-07T14:30:00Z",
  "duration_seconds": 9000
}
```

**Download Word Document:**

The generated biography is available at:
- **Markdown**: `bios/albert_einstein/La biografia de Albert Einstein.md`
- **Word**: `docx/albert_einstein/La biografia de Albert Einstein.docx`

```bash
# Copy from Docker container (if using Docker)
docker cp bookgen-api:/app/docx/albert_einstein/La\ biografia\ de\ Albert\ Einstein.docx .
```

---

## 🔍 Understanding the Generation Process

BookGen follows a multi-phase workflow:

### Phase 1: Source Validation (5-10 min)
- Validates all provided URLs
- Checks content accessibility
- Analyzes relevance and quality
- Requires 40+ valid sources to proceed

### Phase 2: Research & Planning (2-5 min)
- Extracts key information from sources
- Identifies major life events
- Creates chapter outline
- Plans narrative structure

### Phase 3: Content Generation (1-3 hours)
- Generates 20 chapters in batches
- Each chapter: 2,500-3,000 words
- Includes citations and references
- Maintains narrative coherence

### Phase 4: Special Sections (20-30 min)
- Prologue and Epilogue
- Introduction and Conclusion
- Timeline (Cronología)
- Glossary (Glosario)
- Character Index (Dramatis Personae)
- Sources Bibliography (Fuentes)

### Phase 5: Quality Control (10-15 min)
- Word count validation
- Coherence checking
- Citation verification
- Content quality analysis

### Phase 6: Export (5 min)
- Concatenates all sections
- Applies Word template
- Generates final .docx file

**Total Time**: Typically 2-4 hours for a complete biography

---

## 📊 Monitoring Your Job

### Check System Status

```bash
# Overall system health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status
```

### View System Metrics

```bash
# Get current metrics
curl http://localhost:8000/api/v1/metrics
```

**Metrics Include:**
- Active jobs
- Completed jobs
- Failed jobs
- Average generation time
- Success rate

### Check Queue Status

```bash
# View Celery queue (Docker)
docker exec bookgen-worker celery -A src.worker inspect active

# View Redis queue
docker exec bookgen-redis redis-cli LLEN celery
```

---

## 🎨 Customizing Your Biography

### Adjust Chapter Count

Edit `.env`:
```bash
CHAPTERS_NUMBER=15          # Shorter biography
TOTAL_WORDS=38000          # Proportional word count
WORDS_PER_CHAPTER=2550     # Words per chapter
```

Then restart services:
```bash
docker-compose restart
```

### Change AI Model

Edit `.env`:
```bash
# Free models
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free

# Premium models (better quality, costs apply)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

### Adjust Quality Thresholds

Edit `.env`:
```bash
# Stricter validation
MIN_SOURCES=50
COHERENCE_THRESHOLD=0.85
RELEVANCE_THRESHOLD=0.75

# More lenient (faster, lower quality)
MIN_SOURCES=30
COHERENCE_THRESHOLD=0.7
RELEVANCE_THRESHOLD=0.6
```

---

## 🚀 Advanced Usage

### Batch Biography Generation

Create multiple biographies from a collection:

```bash
# Prepare character list
cat > characters.txt << EOF
Albert Einstein
Marie Curie
Isaac Newton
Charles Darwin
EOF

# Generate all biographies
while read character; do
  curl -X POST http://localhost:8000/api/v1/biographies \
    -H "Content-Type: application/json" \
    -d "{\"character\": \"$character\", \"sources\": [...]}"
  sleep 2
done < characters.txt
```

### Using Webhooks

Receive notifications when jobs complete:

```bash
# Set webhook URL in request
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "sources": [...],
    "webhook_url": "https://your-app.com/webhook",
    "user_email": "you@example.com"
  }'
```

Your webhook will receive:
```json
{
  "event": "biography.completed",
  "job_id": "123e4567...",
  "character": "Albert Einstein",
  "status": "completed",
  "output_file": "docx/albert_einstein/..."
}
```

### Email Notifications

Configure in `.env`:
```bash
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAILS=you@example.com
```

You'll receive emails for:
- Job completion
- Job failures
- Critical errors

---

## ❓ Common Questions

### How long does generation take?

- **Source validation**: 5-10 minutes
- **Content generation**: 1-3 hours
- **Total**: 2-4 hours on average

Factors affecting time:
- Number of sources
- Source quality
- AI model selected
- Server load

### How many sources do I need?

- **Minimum**: 40 valid sources
- **Recommended**: 50-60 sources
- **Maximum**: 100 sources (diminishing returns)

### Can I cancel a running job?

Not currently supported. Jobs run to completion or failure.

### What if my job fails?

Check the error message:
```bash
curl http://localhost:8000/api/v1/biographies/YOUR_JOB_ID
```

Common failures:
- Insufficient valid sources (< 40)
- API rate limits reached
- Network connectivity issues
- Invalid source URLs

### How much does it cost?

- **BookGen**: Free and open source
- **OpenRouter API**: 
  - Free models available (Qwen)
  - Premium models charged per token
  - Typical cost: $0.50-$5.00 per biography

---

## 🛠️ Troubleshooting Quick Start

### Job Stuck in "Pending"

```bash
# Check worker is running
docker ps | grep worker

# Check worker logs
docker logs bookgen-worker

# Restart worker
docker-compose restart worker
```

### Source Validation Fails

```bash
# Test sources manually
curl -I https://your-source-url.com

# Check validation settings in .env
echo $MIN_SOURCES
echo $URL_VALIDATION_TIMEOUT
```

### "Rate Limit Exceeded" Error

```bash
# Check your OpenRouter usage
# Wait a few minutes and retry
# Or upgrade to paid tier
```

### Output File Not Found

```bash
# Check generation completed
curl http://localhost:8000/api/v1/biographies/YOUR_JOB_ID

# Verify output directory
ls -la docx/

# Check Docker volume mounts
docker-compose config | grep volumes
```

---

## 📚 Next Steps

Now that you've created your first biography:

1. **[User Guide](../user-guide/creating-biographies.md)** - Detailed workflow
2. **[API Documentation](../api/endpoints.md)** - Complete API reference
3. **[Notifications Guide](../user-guide/notifications.md)** - Understanding updates
4. **[Troubleshooting](../operations/troubleshooting.md)** - Solve common issues

---

## 💡 Tips for Best Results

### Source Quality Matters
- Use academic and authoritative sources
- Include diverse perspectives
- Verify URLs are accessible
- Avoid duplicate content

### Optimize Configuration
- Start with defaults
- Adjust based on results
- Test with one biography first
- Monitor resource usage

### Monitor Progress
- Use WebSocket for real-time updates
- Check logs for issues
- Verify checkpoint saves
- Watch for errors early

---

[← Configuration Guide](configuration.md) | [User Guide →](../user-guide/creating-biographies.md)
