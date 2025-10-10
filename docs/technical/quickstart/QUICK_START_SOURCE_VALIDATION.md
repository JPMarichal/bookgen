# Quick Start: Advanced Source Validation

## Overview
This guide helps you quickly get started with the advanced source validation system.

## Basic Usage

### 1. Using the Service Directly

```python
from src.services.source_validator import SourceValidationService
from src.api.models.sources import SourceItem, SourceType

# Initialize validator
validator = SourceValidationService(
    min_relevance=0.7,      # Minimum relevance threshold
    min_credibility=80.0    # Minimum credibility threshold
)

# Create sources
sources = [
    SourceItem(
        title="Einstein: His Life and Universe",
        author="Walter Isaacson",
        publication_date="2007",
        url="https://archive.org/details/einstein",
        source_type=SourceType.BOOK
    )
]

# Validate
result = validator.validate_sources(
    biography_topic="Albert Einstein",
    sources_list=sources,
    check_accessibility=False  # Set to True to check URLs
)

# Check results
print(f"Average Credibility: {result['average_credibility']}")
print(f"Recommendations: {result['recommendations']}")
```

### 2. Using the API Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/sources/validate-advanced" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {
        "title": "Einstein Biography",
        "author": "Author Name",
        "publication_date": "2020",
        "url": "https://example.com",
        "source_type": "book"
      }
    ],
    "biography_topic": "Albert Einstein",
    "check_accessibility": false,
    "min_relevance": 0.7,
    "min_credibility": 80.0
  }'
```

## Running the Demo

```bash
python development/examples/demo_source_validation.py
```

## Running Tests

```bash
# All source validation tests
pytest tests/test_source_validation.py -v

# All tests
pytest tests/ -v
```

## Key Features

1. **TF-IDF Relevance Analysis** - Semantic similarity scoring
2. **Domain Credibility** - Trusted domain verification
3. **Recency Scoring** - Publication date age analysis
4. **Automatic Filtering** - Reject low-quality sources
5. **Smart Recommendations** - Improvement suggestions

## Common Scenarios

### High-Quality Academic Sources
Sources from .edu, .gov, or trusted academic sites automatically receive:
- High credibility scores (90-95)
- Trusted domain status
- Academic category classification

### Checking Relevance
To analyze content relevance:
- Set `check_accessibility=True`
- Provide clear `biography_topic`
- URL content will be fetched and analyzed

### Custom Thresholds
Adjust quality requirements:
```python
validator = SourceValidationService(
    min_relevance=0.8,    # Higher relevance requirement
    min_credibility=90.0  # Higher credibility requirement
)
```

## Troubleshooting

**Q: Relevance scores are 0**  
A: Enable URL checking with `check_accessibility=True`

**Q: All sources marked untrusted**  
A: Add domains to `src/config/trusted_domains.py`

**Q: Timeout errors**  
A: Set `check_accessibility=False` or increase timeout

## Next Steps

- Read [ADVANCED_SOURCE_VALIDATION.md](ADVANCED_SOURCE_VALIDATION.md) for detailed documentation
- Explore `demo_source_validation.py` for examples
- Check `tests/test_source_validation.py` for test patterns
