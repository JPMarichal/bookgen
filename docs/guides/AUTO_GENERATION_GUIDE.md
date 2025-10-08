# Automatic Source Generation Guide

## Overview

BookGen's automatic source generation system is a powerful AI-driven feature that eliminates the manual work of collecting and validating biographical sources. This guide explains how to use the three generation modes effectively.

---

## 🎯 Generation Modes

BookGen offers three modes to suit different workflows:

| Mode | Description | Use Case | Source Collection |
|------|-------------|----------|-------------------|
| **Automatic** | Fully automated source discovery | Quick generation, unfamiliar subjects | 100% AI-generated |
| **Hybrid** | Mix of user + AI sources | Key sources + auto-completion | User + AI mix |
| **Manual** | User provides all sources | Full control, specialized sources | 100% user-provided |

---

## 🤖 Automatic Mode

### What is Automatic Mode?

In automatic mode, BookGen's AI:
1. Analyzes the character (historical period, field, nationality)
2. Generates optimized search terms
3. Searches multiple data sources (Wikipedia, academic databases, archives)
4. Validates sources for quality, relevance, and accessibility
5. Selects the best 40-60 sources automatically

### When to Use Automatic Mode

✅ **Perfect for:**
- Quick biography generation without research
- Subjects you're unfamiliar with
- Proof of concepts and demos
- Time-constrained projects

❌ **Not ideal for:**
- Highly specialized or obscure subjects
- When you have proprietary sources
- Academic work requiring specific citations

### Basic Usage

```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Marie Curie",
    "mode": "automatic"
  }'
```

### Advanced Configuration

```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Marie Curie",
    "mode": "automatic",
    "min_sources": 50,
    "quality_threshold": 0.85,
    "chapters": 20,
    "total_words": 51000,
    "temperature": 0.7
  }'
```

**Parameters:**
- `min_sources` (default: 40): Minimum sources to generate
- `quality_threshold` (default: 0.8): Quality score threshold (0-1)
  - Higher values = stricter quality control
  - Recommended: 0.7-0.9
- `chapters`: Number of biography chapters
- `total_words`: Target word count
- `temperature`: AI generation temperature

### Response Example

```json
{
  "job_id": "abc-123-def",
  "status": "pending",
  "character": "Marie Curie",
  "mode": "automatic",
  "sources_generated_automatically": true,
  "source_count": 52,
  "chapters": 20,
  "created_at": "2025-01-07T12:00:00Z",
  "estimated_completion_time": "600 seconds",
  "message": "Biography generation job created successfully"
}
```

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│ 1. AI Character Analysis                                │
│    - Historical period, nationality, profession         │
│    - Key events and achievements                        │
│    - Related people and concepts                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Multi-Strategy Source Discovery                      │
│    - Wikipedia API (biographical pages, references)     │
│    - Academic databases (future: JSTOR, Google Scholar) │
│    - Government archives (future: Library of Congress)  │
│    - Biography websites (future: Biography.com, etc.)   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Advanced Validation                                  │
│    - URL accessibility check                            │
│    - Relevance scoring (TF-IDF algorithm)              │
│    - Domain credibility assessment                      │
│    - Diversity analysis (avoid duplicates)             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Source Selection                                     │
│    - Filter by quality threshold                        │
│    - Ensure diversity (multiple source types)           │
│    - Meet minimum source count                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 Hybrid Mode

### What is Hybrid Mode?

Hybrid mode combines the best of both worlds:
- You provide critical/specialized sources
- BookGen auto-completes to meet the target count
- All sources are validated together

### When to Use Hybrid Mode

✅ **Perfect for:**
- You have 5-20 key sources but need 40-60 total
- Specialized sources + general background
- Academic work with some required citations
- Maintaining quality while saving time

### Basic Usage

```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "mode": "hybrid",
    "sources": [
      "https://einsteinpapers.press.princeton.edu/",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
    ],
    "min_sources": 50
  }'
```

### Advanced Configuration

```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein",
    "mode": "hybrid",
    "sources": [
      "https://einsteinpapers.press.princeton.edu/",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
      "https://archive.org/einstein-collection"
    ],
    "min_sources": 50,
    "quality_threshold": 0.8
  }'
```

**How it works:**
1. Your 3 sources are validated
2. System generates 47 additional sources
3. All 50 sources are ranked and filtered
4. Best sources are selected for biography

### Response Example

```json
{
  "job_id": "def-456-ghi",
  "status": "pending",
  "character": "Albert Einstein",
  "mode": "hybrid",
  "sources_generated_automatically": true,
  "source_count": 50,
  "created_at": "2025-01-07T12:00:00Z",
  "message": "Biography generation job created successfully"
}
```

---

## 📝 Manual Mode

### What is Manual Mode?

You provide all sources manually. BookGen validates but doesn't generate sources.

### When to Use Manual Mode

✅ **Perfect for:**
- Complete control over sources
- Proprietary or specialized databases
- Academic citations with specific requirements
- Sources not discoverable by AI

### Basic Usage

```bash
curl -X POST http://localhost:8000/api/v1/biographies/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Isaac Newton",
    "mode": "manual",
    "sources": [
      "https://en.wikipedia.org/wiki/Isaac_Newton",
      "https://www.britannica.com/biography/Isaac-Newton",
      "https://mathshistory.st-andrews.ac.uk/Biographies/Newton/",
      "https://www.newtonproject.ox.ac.uk/",
      "... (at least 10 sources required)"
    ]
  }'
```

**Requirements:**
- Minimum: 10 sources
- Recommended: 40-60 sources for best results
- All sources must be valid URLs

---

## 🎛️ Quality Control Parameters

### Quality Threshold

Controls the minimum quality score for sources:

```python
quality_threshold: 0.7  # Lenient - more sources, faster
quality_threshold: 0.8  # Balanced (default)
quality_threshold: 0.9  # Strict - fewer sources, higher quality
```

**Impact:**
- **0.7**: Accepts most sources, faster generation
- **0.8**: Good balance (recommended)
- **0.9**: Very selective, may reduce source count

### Minimum Sources

```python
min_sources: 30   # Minimum viable
min_sources: 40   # Recommended (default)
min_sources: 60   # Maximum diversity
```

**Guidelines:**
- 30-40: Sufficient for most biographies
- 40-50: Good diversity and depth
- 50-60: Maximum diversity, diminishing returns beyond this

---

## 📊 Monitoring Source Generation

### Check Job Status

```bash
curl http://localhost:8000/api/v1/biographies/{job_id}/status
```

**Response includes source metadata:**
```json
{
  "job_id": "abc-123-def",
  "status": "in_progress",
  "character": "Marie Curie",
  "progress": {
    "chapters_completed": 5,
    "total_chapters": 20,
    "percentage": 25.0
  },
  "source_metadata": {
    "user_source_count": 0,
    "auto_generated_count": 52,
    "validation_summary": {
      "average_relevance": 0.87,
      "average_credibility": 85.3,
      "valid_sources": 52,
      "rejected_sources": 3
    }
  }
}
```

---

## 🔍 Understanding Source Quality

### Relevance Score (0-1)

Measures how relevant a source is to the character:
- Calculated using TF-IDF algorithm
- Compares source content to character name/topics
- Higher = more relevant

**Example:**
- 0.9+: Primary biography or major work about the person
- 0.7-0.9: Relevant historical context, related topics
- 0.5-0.7: Tangentially related
- <0.5: Low relevance, likely rejected

### Credibility Score (0-100)

Assesses source trustworthiness:
- Based on domain reputation
- Academic/government sources score highest
- Social media/blogs score lowest

**Domain Categories:**
- **90-100**: `.edu`, `.gov`, major academic publishers
- **80-90**: Wikipedia, Encyclopedia Britannica, established media
- **70-80**: Reputable news outlets, biography sites
- **60-70**: General websites with good reputation
- **<60**: Unverified or low-credibility sources

---

## 🚀 Best Practices

### 1. Start with Automatic Mode

For your first biography, use automatic mode to understand the system:

```bash
{
  "character": "Test Subject",
  "mode": "automatic"
}
```

### 2. Use Hybrid for Important Work

When quality matters, provide key sources:

```bash
{
  "character": "Important Subject",
  "mode": "hybrid",
  "sources": ["key-source-1", "key-source-2"],
  "quality_threshold": 0.85
}
```

### 3. Adjust Quality Threshold Based on Results

If you get too few sources:
```python
quality_threshold: 0.7  # Lower threshold
```

If quality is insufficient:
```python
quality_threshold: 0.9  # Higher threshold
min_sources: 60          # Request more sources
```

### 4. Monitor Source Metadata

Always check the validation summary:
```bash
curl http://localhost:8000/api/v1/biographies/{job_id}/status
```

Look for:
- `average_relevance` > 0.75
- `average_credibility` > 80
- `rejected_sources` < 10%

---

## ⚙️ Advanced Topics

### Custom Source Strategies

Future versions will support:
- Custom domain whitelists/blacklists
- Language-specific sources
- Geographic filtering
- Time period constraints

### API Integration

Integrate with your application:

```python
import requests

def generate_biography_automatic(character_name):
    """Generate biography with automatic source discovery"""
    response = requests.post(
        "http://localhost:8000/api/v1/biographies/generate",
        json={
            "character": character_name,
            "mode": "automatic",
            "quality_threshold": 0.8
        }
    )
    return response.json()

# Usage
job = generate_biography_automatic("Marie Curie")
print(f"Job created: {job['job_id']}")
print(f"Sources: {job['source_count']}")
```

---

## 🐛 Troubleshooting

### "Insufficient sources generated"

**Problem:** System couldn't find enough quality sources

**Solutions:**
1. Lower quality threshold: `quality_threshold: 0.7`
2. Reduce minimum sources: `min_sources: 30`
3. Switch to hybrid mode and provide some sources

### "Source generation failed"

**Problem:** Error during source discovery

**Solutions:**
1. Check OpenRouter API key is configured
2. Verify internet connectivity
3. Check logs: `docker logs bookgen-api`

### "Low relevance scores"

**Problem:** Generated sources not relevant enough

**Solutions:**
1. Use hybrid mode with specific sources
2. Check character name spelling
3. Provide more context in future versions

---

## 📚 Related Documentation

- **[Quick Start Guide](../getting-started/quick-start.md)** - Getting started
- **[API Documentation](../api/overview.md)** - Complete API reference
- **[Hybrid Generation Guide](../../QUICK_START_HYBRID_GENERATION.md)** - Detailed hybrid mode docs

---

## 💡 Examples

See [automatic_generation_examples.py](../examples/automatic_generation_examples.py) for complete code examples.

---

## 🤝 Support

For issues or questions:
- Create an issue on [GitHub](https://github.com/JPMarichal/bookgen/issues)
- Check the [Troubleshooting Guide](../operations/troubleshooting.md)
