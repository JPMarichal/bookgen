# Quick Start: Hybrid Source Generation

## Overview

The Hybrid Source Generation endpoint (`/api/v1/sources/generate-hybrid`) combines user-provided sources with AI-powered automatic generation, offering maximum flexibility.

## Three Modes of Operation

### 1. Manual Mode (User Sources Only)

Use when you have all the sources you want and just need validation/suggestions.

```bash
curl -X POST http://localhost:8000/api/v1/sources/generate-hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Albert Einstein",
    "user_sources": [
      "https://en.wikipedia.org/wiki/Albert_Einstein",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
    ],
    "auto_complete": false,
    "provide_suggestions": true
  }'
```

**Result**: Your 2 sources validated + suggestions for improvement

### 2. Hybrid Mode (Mix of User + Auto)

Use when you have some key sources and want the system to complete the rest.

```bash
curl -X POST http://localhost:8000/api/v1/sources/generate-hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Albert Einstein",
    "user_sources": [
      "https://special-archive.org/einstein-papers",
      "https://family-collection.org/einstein-letters"
    ],
    "auto_complete": true,
    "target_count": 50
  }'
```

**Result**: Your 2 special sources + 48 auto-generated high-quality sources

### 3. Automatic Mode (No User Sources)

Use when you want fully automated source discovery.

```bash
curl -X POST http://localhost:8000/api/v1/sources/generate-hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Marie Curie",
    "auto_complete": true,
    "target_count": 50
  }'
```

**Result**: 50 automatically generated and validated sources

## Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `character_name` | string | required | Name of the historical character |
| `user_sources` | array[string] | `[]` | URLs of user-provided sources |
| `auto_complete` | boolean | `true` | Enable automatic source completion |
| `target_count` | integer | `50` | Target total number of sources (1-150) |
| `check_accessibility` | boolean | `true` | Validate URL accessibility |
| `min_relevance` | float | `0.7` | Minimum relevance score (0-1) |
| `min_credibility` | float | `80.0` | Minimum credibility score (0-100) |
| `provide_suggestions` | boolean | `true` | Generate intelligent suggestions |

## Response Structure

```json
{
  "character_name": "Albert Einstein",
  "sources": [...],                 // Array of SourceItem
  "user_source_count": 2,           // Number from user
  "auto_generated_count": 48,       // Number auto-generated
  "suggestions": [...],             // Intelligent recommendations
  "validation_summary": {
    "total_sources": 50,
    "valid_sources": 50,
    "average_relevance": 0.85,
    "average_credibility": 88.5
  },
  "configuration": {
    "auto_complete": true,
    "target_count": 50,
    "min_relevance": 0.7,
    "min_credibility": 80.0
  },
  "metadata": {
    "target_met": true,
    "suggestions_provided": 3
  }
}
```

## Common Patterns

### Pattern 1: Start with Key Sources, Auto-Complete

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/sources/generate-hybrid",
    json={
        "character_name": "Isaac Newton",
        "user_sources": [
            "https://archive.org/details/principia-mathematica",
            "https://royal-society.org/newton-papers"
        ],
        "auto_complete": True,
        "target_count": 50
    }
)

data = response.json()
print(f"✓ {len(data['sources'])} sources ready")
print(f"  - {data['user_source_count']} from you")
print(f"  - {data['auto_generated_count']} auto-generated")
```

### Pattern 2: Validate Existing Sources

```python
response = requests.post(
    "http://localhost:8000/api/v1/sources/generate-hybrid",
    json={
        "character_name": "Ada Lovelace",
        "user_sources": my_source_list,  # Your existing list
        "auto_complete": False,
        "provide_suggestions": True
    }
)

# Check validation
summary = response.json()['validation_summary']
print(f"Valid: {summary['valid_sources']}/{summary['total_sources']}")
print(f"Quality: {summary['average_relevance']:.2f} relevance")

# Get suggestions
for suggestion in response.json()['suggestions']:
    print(f"💡 {suggestion['reason']}")
```

### Pattern 3: Quick Auto-Generate

```python
response = requests.post(
    "http://localhost:8000/api/v1/sources/generate-hybrid",
    json={
        "character_name": "Alan Turing",
        "target_count": 50
    }
)

sources = response.json()['sources']
# Save to file, database, etc.
```

## Intelligent Suggestions

The system provides context-aware suggestions:

### Suggestion Types

1. **Fills Gap** - Missing source types
   ```
   "No academic sources found. Consider adding scholarly articles."
   ```

2. **Diversity** - Too many from same domain
   ```
   "You have 10 sources from example.com. Consider diversifying."
   ```

3. **Configuration** - Setup recommendations
   ```
   "You need 40 more sources to reach target of 50. Consider enabling auto_complete."
   ```

### Using Suggestions

```python
response = requests.post(
    "http://localhost:8000/api/v1/sources/generate-hybrid",
    json={
        "character_name": "Nikola Tesla",
        "user_sources": ["https://example.com/tesla"],
        "auto_complete": False,
        "target_count": 50,
        "provide_suggestions": True
    }
)

for suggestion in response.json()['suggestions']:
    print(f"\nCategory: {suggestion['category']}")
    print(f"Relevance: {suggestion['relevance_score']}")
    print(f"Reason: {suggestion['reason']}")
    
    # Optionally add the suggested source
    suggested_url = suggestion['suggested_source']['url']
    print(f"Suggested URL: {suggested_url}")
```

## Quality Control

### Adjust Quality Thresholds

```python
response = requests.post(
    "http://localhost:8000/api/v1/sources/generate-hybrid",
    json={
        "character_name": "Einstein",
        "auto_complete": True,
        "target_count": 50,
        "min_relevance": 0.8,      # Higher threshold
        "min_credibility": 90.0    # Only highly credible sources
    }
)
```

### Check Validation Results

```python
summary = response.json()['validation_summary']

print(f"Quality Metrics:")
print(f"  Average Relevance: {summary['average_relevance']:.2f}")
print(f"  Average Credibility: {summary['average_credibility']:.1f}")
print(f"  Valid Sources: {summary['valid_sources']}/{summary['total_sources']}")

if summary.get('recommendations'):
    print(f"\nRecommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")
```

## Error Handling

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/v1/sources/generate-hybrid",
        json={
            "character_name": "Einstein",
            "user_sources": ["invalid-url"]  # Will fail validation
        }
    )
    
    if response.status_code == 422:
        print("Validation error:", response.json()['detail'])
    elif response.status_code == 200:
        data = response.json()
        print(f"Success: {len(data['sources'])} sources")
    else:
        print(f"Error {response.status_code}: {response.text}")
        
except requests.RequestException as e:
    print(f"Request failed: {e}")
```

## Best Practices

### ✅ Do's

1. **Start Small**: Begin with a few key sources, let auto-complete fill the rest
2. **Use Suggestions**: Enable suggestions to improve source quality
3. **Validate URLs**: Always check_accessibility=True in production
4. **Set Quality Thresholds**: Adjust min_relevance and min_credibility for your needs
5. **Review Results**: Check validation_summary before using sources

### ❌ Don'ts

1. **Don't Skip Validation**: Always validate user-provided sources
2. **Don't Ignore Suggestions**: They help improve source quality
3. **Don't Set Target Too Low**: Less than 20 sources may not be comprehensive
4. **Don't Mix URLs**: Ensure all user_sources are valid URLs starting with http:// or https://
5. **Don't Disable Auto-Complete Without Enough Sources**: If target_count is 50 and you have 5 sources, enable auto-complete

## Examples by Use Case

### Academic Research

```python
{
    "character_name": "Marie Curie",
    "user_sources": [
        "https://nobel-archive.org/curie-papers"
    ],
    "auto_complete": True,
    "target_count": 60,
    "min_relevance": 0.8,
    "min_credibility": 85.0
}
```

### Quick Biography

```python
{
    "character_name": "Leonardo da Vinci",
    "auto_complete": True,
    "target_count": 40,
    "check_accessibility": False  # Faster, skip URL checks
}
```

### Quality Control Review

```python
{
    "character_name": "Winston Churchill",
    "user_sources": my_existing_sources,
    "auto_complete": False,
    "provide_suggestions": True
}
```

## Testing

Run the demo:

```bash
python development/examples/demo_hybrid_generator.py
```

Run unit tests:

```bash
pytest tests/test_hybrid_generation.py -v
```

Run API tests:

```bash
pytest tests/api/test_sources_hybrid.py -v
```

## Related Endpoints

- `/api/v1/sources/generate-automatic` - Fully automatic generation
- `/api/v1/sources/validate` - Basic source validation
- `/api/v1/sources/validate-advanced` - Advanced validation with AI

## Support

For issues or questions:
- Check test suite for usage examples
- Review demo script for common patterns
- See IMPLEMENTATION_SUMMARY_ISSUE_63.md for detailed documentation
