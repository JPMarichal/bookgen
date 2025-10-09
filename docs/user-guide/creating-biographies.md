# Creating Biographies

Complete guide to creating biographies with BookGen.

## 📖 Overview

Creating a biography with BookGen involves:
1. Collecting quality sources
2. Submitting a generation request
3. Monitoring progress
4. Retrieving the completed biography

**Typical Timeline:**
- Source validation: 5-10 minutes
- Content generation: 1-3 hours
- Total: 2-4 hours

---

## 🎯 Step-by-Step Guide

### Step 1: Prepare Source Material

Quality sources are critical for a good biography.

**What Makes a Good Source:**

✅ **Academic and Authoritative**
- University websites (.edu domains)
- Scholarly articles and journals
- Official archives and museums
- Government databases
- Published books (accessible online)

✅ **Reliable Publishers**
- Encyclopedia Britannica
- Biography.com
- National biography databases
- Historical societies
- Academic publishers

✅ **Primary Sources**
- Official documents
- Letters and correspondence
- Government records
- Contemporary newspaper articles

❌ **Avoid These:**
- Social media posts
- Personal blogs (unless expert)
- Paywalled content
- Broken links
- Sites requiring login

**How Many Sources:**
- **Minimum**: 40 valid sources
- **Recommended**: 50-60 sources
- **Maximum**: 100 sources

**Source Quality Tips:**
```bash
# Test a source before including
curl -I https://source-url.com

# Should return: HTTP/1.1 200 OK
# Avoid: 403, 404, 500 errors
```

### Step 2: Organize Your Sources

Create a source list file:

```bash
# Create sources file
cat > einstein_sources.txt << 'EOF'
https://en.wikipedia.org/wiki/Albert_Einstein
https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/
https://www.britannica.com/biography/Albert-Einstein
https://www.biography.com/scientist/albert-einstein
https://www.history.com/topics/inventions/albert-einstein
# ... add 35-55 more sources
EOF
```

**Source Organization Template:**

```
General Biography Sources:
- Wikipedia
- Encyclopedia Britannica
- Biography.com

Academic Sources:
- University biographies
- Scholarly articles
- Academic databases

Historical Archives:
- National archives
- Museum websites
- Historical societies

Contemporary Sources:
- Period newspapers
- Original documents
- Letters and correspondence
```

### Step 3: Validate Your Sources

Before submitting, validate your sources:

**Using the API:**
```bash
curl -X POST http://localhost:8000/api/v1/sources/validate \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://en.wikipedia.org/wiki/Albert_Einstein",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
    ]
  }'
```

**Response:**
```json
{
  "total_sources": 2,
  "valid_sources": 2,
  "invalid_sources": 0,
  "validation_results": [
    {
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "valid": true,
      "status_code": 200,
      "content_length": 450000,
      "relevance_score": 0.95
    },
    {
      "url": "https://www.nobelprize.org/...",
      "valid": true,
      "status_code": 200,
      "content_length": 12000,
      "relevance_score": 0.92
    }
  ]
}
```

**Manual Validation:**
```bash
# Test each source
while read url; do
  echo "Testing: $url"
  status=$(curl -o /dev/null -s -w "%{http_code}" -L "$url")
  if [ $status -eq 200 ]; then
    echo "✅ Valid"
  else
    echo "❌ Invalid (Status: $status)"
  fi
done < einstein_sources.txt
```

### Step 4: Submit Biography Request

**Via API:**

```bash
# Read sources into array
SOURCES=$(cat einstein_sources.txt | jq -R . | jq -s .)

# Submit request
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d "{
    \"character\": \"Albert Einstein\",
    \"sources\": $SOURCES
  }" | jq .
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

**Save the Job ID:**
```bash
# Save for later use
echo "123e4567-e89b-12d3-a456-426614174000" > current_job_id.txt
```

**Via Interactive Docs:**

1. Navigate to http://localhost:8000/docs
2. Find `POST /api/v1/biographies`
3. Click "Try it out"
4. Fill in the request:
   ```json
   {
     "character": "Albert Einstein",
     "sources": [
       "https://en.wikipedia.org/wiki/Albert_Einstein",
       "... more sources ..."
     ]
   }
   ```
5. Click "Execute"
6. Copy the `job_id` from the response

### Step 5: Monitor Progress

**Option A: WebSocket (Real-time)**

Most responsive, recommended for user interfaces.

```javascript
const jobId = "123e4567-e89b-12d3-a456-426614174000";
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?job_id=${jobId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  console.log(`Status: ${data.status}`);
  console.log(`Progress: ${data.progress}%`);
  console.log(`Phase: ${data.message}`);
  
  if (data.status === 'completed') {
    console.log('Biography completed!');
    console.log(`Output: ${data.output_file}`);
    ws.close();
  }
  
  if (data.status === 'failed') {
    console.log('Biography failed!');
    console.log(`Error: ${data.error}`);
    ws.close();
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Option B: Polling (Simple)**

Good for scripts and simple applications.

```bash
#!/bin/bash
JOB_ID="123e4567-e89b-12d3-a456-426614174000"

while true; do
  # Get current status
  RESPONSE=$(curl -s http://localhost:8000/api/v1/biographies/$JOB_ID)
  
  STATUS=$(echo $RESPONSE | jq -r '.status')
  PROGRESS=$(echo $RESPONSE | jq -r '.progress')
  PHASE=$(echo $RESPONSE | jq -r '.current_phase')
  
  echo "$(date): $STATUS - $PROGRESS% - $PHASE"
  
  # Check if complete
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Biography completed!"
    OUTPUT=$(echo $RESPONSE | jq -r '.output_file')
    echo "📄 Output file: $OUTPUT"
    break
  fi
  
  # Check if failed
  if [ "$STATUS" = "failed" ]; then
    echo "❌ Biography failed!"
    ERROR=$(echo $RESPONSE | jq -r '.error')
    echo "Error: $ERROR"
    break
  fi
  
  # Wait before next check
  sleep 30
done
```

**Option C: Logs**

Watch the worker logs directly.

```bash
# Follow worker logs
docker logs -f bookgen-worker

# Filter for your job
docker logs -f bookgen-worker | grep "123e4567"
```

### Step 6: Understanding Progress Phases

The generation process goes through several phases:

**Phase 1: Source Validation (5-10 min)**
```
Progress: 0-10%
Message: "Validating sources..."
```
- Checks all URLs are accessible
- Validates content relevance
- Requires 40+ valid sources
- Analyzes source quality

**Phase 2: Research Planning (2-5 min)**
```
Progress: 10-15%
Message: "Planning biography structure..."
```
- Extracts key information
- Identifies major life events
- Creates chapter outline
- Plans narrative arc

**Phase 3: Chapter Generation (1-2 hours)**
```
Progress: 15-75%
Message: "Generating Chapter X of 20..."
```
- Generates chapters in batches
- Each chapter: 2,500-3,000 words
- Includes citations
- Maintains coherence

**Phase 4: Special Sections (20-30 min)**
```
Progress: 75-90%
Message: "Generating special sections..."
```
- Prologue and Epilogue
- Introduction and Conclusion
- Timeline (Cronología)
- Glossary (Glosario)
- Character Index (Dramatis Personae)
- Sources (Fuentes)

**Phase 5: Quality Control (10-15 min)**
```
Progress: 90-95%
Message: "Validating content quality..."
```
- Word count validation
- Coherence checking
- Citation verification
- Content quality analysis

**Phase 6: Export (5 min)**
```
Progress: 95-100%
Message: "Exporting to Word format..."
```
- Concatenates all sections
- Applies formatting
- Generates .docx file

### Step 7: Retrieve Completed Biography

Once status shows "completed":

**Check Final Details:**
```bash
curl http://localhost:8000/api/v1/biographies/$JOB_ID | jq
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
  "markdown_file": "bios/albert_einstein/La biografia de Albert Einstein.md",
  "created_at": "2025-01-07T12:00:00Z",
  "completed_at": "2025-01-07T14:30:00Z",
  "duration_seconds": 9000
}
```

**Access Generated Files:**

**Markdown Version:**
```bash
# Docker
docker cp bookgen-api:/app/bios/albert_einstein/La\ biografia\ de\ Albert\ Einstein.md .

# Local
cat bios/albert_einstein/La\ biografia\ de\ Albert\ Einstein.md
```

**Word Version:**
```bash
# Docker
docker cp bookgen-api:/app/docx/albert_einstein/La\ biografia\ de\ Albert\ Einstein.docx .

# Local
open docx/albert_einstein/La\ biografia\ de\ Albert\ Einstein.docx
```

---

## 🎨 Customization Options

### Adjust Chapter Count

```bash
# Edit .env before submitting
CHAPTERS_NUMBER=15          # Fewer chapters
TOTAL_WORDS=38000          # Proportional words
WORDS_PER_CHAPTER=2550     # Words per chapter

# Restart services
docker-compose restart
```

### Change AI Model

```bash
# Edit .env
OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct:free  # Free
# OR
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet        # Premium
# OR
OPENROUTER_MODEL=openai/gpt-4-turbo-preview         # Premium

# Restart services
docker-compose restart
```

### Include Webhooks

```bash
# Add webhook to request
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "sources": [...],
    "webhook_url": "https://your-app.com/webhook",
    "user_email": "you@example.com"
  }'
```

---

## ❓ Frequently Asked Questions

### How long does it take?

Typical timeline:
- **Fast**: 1.5-2 hours (good sources, low load)
- **Average**: 2-4 hours (normal conditions)
- **Slow**: 4-6 hours (API rate limits, high load)

### Can I cancel a job?

Not currently supported. Jobs run to completion or failure.

### What if validation fails?

Common causes:
- Fewer than 40 valid sources
- Too many broken URLs
- Sources behind paywalls
- Network issues

**Solution**: Add more quality sources and retry.

### Can I edit the biography?

Yes! Edit the Markdown file and re-export:

```bash
# Edit Markdown
nano bios/albert_einstein/La\ biografia\ de\ Albert\ Einstein.md

# Re-export to Word (using modern service)
docker exec bookgen-api python development/scripts/legacy/concat.py albert_einstein
# Or use the API endpoint (recommended):
# curl -X POST http://localhost:8000/api/v1/biographies/albert_einstein/export
```

### How much does it cost?

- BookGen: Free (open source)
- OpenRouter API:
  - Free models: $0 (with rate limits)
  - Premium models: ~$0.50-$5.00 per biography

---

## 💡 Best Practices

### Source Selection
✅ Use diverse, authoritative sources
✅ Include both general and specific sources
✅ Mix contemporary and modern sources
✅ Verify all URLs work before submitting

### Quality Control
✅ Start with one test biography
✅ Review output quality
✅ Adjust settings based on results
✅ Monitor for errors

### Resource Management
✅ Limit concurrent jobs (MAX_CONCURRENT_JOBS=3)
✅ Monitor disk space
✅ Clean old biographies regularly
✅ Use webhooks instead of polling when possible

---

## 🔄 Example Workflows

### Single Biography
```bash
# 1. Prepare sources
cat > sources.txt << 'EOF'
url1
url2
...
EOF

# 2. Submit
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d "{\"character\":\"Name\",\"sources\":$(cat sources.txt | jq -R . | jq -s .)}" \
  | jq -r '.job_id')

# 3. Monitor
watch -n 30 "curl -s http://localhost:8000/api/v1/biographies/$JOB_ID | jq '.progress, .current_phase'"
```

### Batch Processing
```bash
# Process multiple characters
for character in "Einstein" "Curie" "Newton"; do
  echo "Starting: $character"
  
  curl -X POST http://localhost:8000/api/v1/biographies \
    -H "Content-Type: application/json" \
    -d "{\"character\":\"$character\",\"sources\":[...]}"
  
  sleep 10  # Avoid rate limits
done
```

---

[← API Overview](../api/overview.md) | [Managing Sources →](managing-sources.md)
