# Advanced Source Validation - Implementation Documentation

## Overview
Implementation of Issue #9: Advanced source validation with AI analysis for the BookGen system.

## Features Implemented

### ✅ Acceptance Criteria Met

1. **Análisis de similitud semántica > 0.7**
   - Implemented using TF-IDF vectorization and cosine similarity
   - Character name mentions provide bonus scoring
   - Configurable threshold (default: 0.7)

2. **Verificación de dominios confiables**
   - Comprehensive trusted domains database
   - Academic institutions (.edu, .ac.uk, etc.)
   - Government sources (.gov, etc.)
   - Reputable news and archive sites
   - Domain categorization (academic, government, news, archive, etc.)

3. **Detección de fechas y actualidad**
   - Publication date parsing and validation
   - Recency scoring based on age
   - Warnings for outdated sources (>50 years old)

4. **Scoring de credibilidad 0-100**
   - Multi-factor credibility scoring:
     - Domain credibility (50% weight)
     - Metadata completeness (30% weight)
     - Recency (20% weight)
   - Configurable threshold (default: 80.0)

5. **Filtrado automático de fuentes irrelevantes**
   - Automatic rejection based on relevance score
   - Automatic rejection based on credibility score
   - Tracking of rejected sources count

6. **Sugerencias de fuentes adicionales**
   - Automatic recommendations based on validation results
   - Quality improvement suggestions
   - Metadata completeness recommendations

## Architecture

### Files Created

```
src/
├── config/
│   └── trusted_domains.py          # Trusted domains configuration
├── utils/
│   ├── tfidf_analyzer.py           # TF-IDF relevance analysis
│   └── credibility_checker.py      # Credibility checking logic
├── services/
│   └── source_validator.py         # Main validation service
└── api/
    ├── models/
    │   └── sources.py              # Updated with advanced models
    └── routers/
        └── sources.py              # Updated with advanced endpoint

tests/
└── test_source_validation.py       # Comprehensive test suite (31 tests)

demo_source_validation.py           # Demo script
```

### Components

#### 1. Trusted Domains Configuration (`src/config/trusted_domains.py`)
- Database of trusted academic and research domains
- Credibility scoring function (0-100)
- Domain categorization
- ~200 lines of domain rules

#### 2. TF-IDF Analyzer (`src/utils/tfidf_analyzer.py`)
- TF-IDF vectorization using scikit-learn
- Cosine similarity calculation
- Character mention detection and bonus scoring
- Fallback simple relevance scoring
- Keyword extraction capability

#### 3. Credibility Checker (`src/utils/credibility_checker.py`)
- Domain credibility checking
- Recency analysis (publication date age)
- Metadata completeness scoring
- Academic format validation
- Multi-factor credibility scoring

#### 4. Source Validation Service (`src/services/source_validator.py`)
- Main orchestration service
- Batch source validation
- HTML content extraction
- Generic page detection
- Recommendation generation
- HTTP session management

#### 5. API Models (`src/api/models/sources.py`)
- `AdvancedSourceValidationRequest`: Request model with topic and thresholds
- `AdvancedSourceValidationResult`: Enhanced result with scores and metadata
- `AdvancedSourceValidationResponse`: Response with aggregated metrics

#### 6. API Endpoint (`src/api/routers/sources.py`)
- New `/api/v1/sources/validate-advanced` POST endpoint
- Configurable relevance and credibility thresholds
- Comprehensive summary statistics
- Integration with validation service

## API Usage

### Endpoint: POST /api/v1/sources/validate-advanced

**Request:**
```json
{
  "sources": [
    {
      "title": "Albert Einstein: His Life and Universe",
      "author": "Walter Isaacson",
      "publication_date": "2007",
      "url": "https://archive.org/details/einstein",
      "source_type": "book"
    }
  ],
  "biography_topic": "Albert Einstein",
  "check_accessibility": true,
  "min_relevance": 0.7,
  "min_credibility": 80.0
}
```

**Response:**
```json
{
  "total_sources": 1,
  "valid_sources": 1,
  "invalid_sources": 0,
  "rejected_sources": 0,
  "average_relevance": 0.85,
  "average_credibility": 90.0,
  "results": [
    {
      "source": { ... },
      "is_valid": true,
      "is_accessible": true,
      "relevance_score": 0.85,
      "credibility_score": 90.0,
      "domain_category": "archive",
      "is_trusted": true,
      "issues": [],
      "warnings": [],
      "metadata": {
        "domain_score": 90.0,
        "recency_score": 75.0,
        "completeness_score": 100.0
      }
    }
  ],
  "recommendations": [
    "Source quality is good. No major improvements needed."
  ],
  "summary": {
    "validation_rate": 100.0,
    "rejection_rate": 0.0,
    "source_types": { "book": 1 },
    "trusted_sources": 1,
    "untrusted_sources": 0,
    "domain_categories": { "archive": 1 }
  }
}
```

## Python Service Usage

```python
from src.services.source_validator import SourceValidationService
from src.api.models.sources import SourceItem, SourceType

# Create validator
validator = SourceValidationService(
    min_relevance=0.7,
    min_credibility=80.0
)

# Create sources
sources = [
    SourceItem(
        title="Einstein Biography",
        author="Author Name",
        publication_date="2020",
        url="https://example.com",
        source_type=SourceType.BOOK
    )
]

# Validate
result = validator.validate_sources(
    biography_topic="Albert Einstein",
    sources_list=sources,
    check_accessibility=True
)

# Check results
assert result['average_relevance'] > 0.7
assert result['average_credibility'] > 80
assert len(result['rejected_sources']) >= 0
```

## Testing

### Test Coverage
- **31 unit tests** in `tests/test_source_validation.py`
- **13 integration tests** in `tests/test_sources.py` (including 6 new advanced endpoint tests)
- **Total: 44 tests** all passing

### Test Categories
1. **Trusted Domains Tests** (6 tests)
   - Domain credibility scoring
   - Trusted domain detection
   - Domain categorization

2. **TF-IDF Analyzer Tests** (4 tests)
   - Similarity calculation
   - Character mention bonus
   - Simple relevance fallback

3. **Credibility Checker Tests** (7 tests)
   - Complete source credibility
   - Academic source detection
   - Recency scoring
   - Completeness checking
   - Academic format validation

4. **Validation Service Tests** (11 tests)
   - Basic validation
   - Multiple sources
   - High/low credibility sources
   - Recommendations generation
   - HTML extraction
   - Generic page detection

5. **Integration Tests** (3 tests)
   - End-to-end validation
   - Acceptance criteria verification

6. **API Endpoint Tests** (6 tests)
   - Basic advanced validation
   - Academic sources
   - Multiple sources
   - Custom thresholds
   - Error handling

### Running Tests
```bash
# All source validation tests
pytest tests/test_source_validation.py -v

# All source-related tests
pytest tests/test_source_validation.py tests/test_sources.py -v

# With coverage
pytest tests/test_source_validation.py --cov=src/services --cov=src/utils --cov=src/config
```

## Demo Script

Run the demo to see all features in action:
```bash
python demo_source_validation.py
```

The demo validates 5 sources with varying quality levels and demonstrates:
- Credibility scoring
- Domain categorization
- Recency analysis
- Recommendations generation
- All acceptance criteria

## Dependencies

Required packages (already in requirements.txt):
- `scikit-learn>=1.3.2` - TF-IDF vectorization and similarity
- `beautifulsoup4>=4.12.2` - HTML parsing
- `lxml>=4.9.3` - XML/HTML processing
- `python-dateutil>=2.8.2` - Date parsing
- `requests>=2.31.0` - HTTP requests

## Configuration

### Thresholds
```python
# Default thresholds
MIN_RELEVANCE = 0.7      # Minimum relevance score (0-1)
MIN_CREDIBILITY = 80.0   # Minimum credibility score (0-100)
TIMEOUT = 10             # HTTP request timeout (seconds)
```

### Credibility Weights
```python
# Credibility calculation weights
DOMAIN_WEIGHT = 0.5      # 50% - Domain credibility
COMPLETENESS_WEIGHT = 0.3 # 30% - Metadata completeness
RECENCY_WEIGHT = 0.2     # 20% - Publication recency
```

### Adding Trusted Domains
Edit `src/config/trusted_domains.py`:
```python
TRUSTED_ACADEMIC_SITES = {
    'jstor.org',
    'scholar.google.com',
    # Add new trusted domains here
    'your-trusted-site.com',
}
```

## Performance Considerations

1. **URL Accessibility Checking**
   - Set `check_accessibility=False` for faster validation without URL checks
   - Use when working with source lists without URLs
   - Recommended for batch processing

2. **Content Analysis**
   - HTML content is truncated to 5000 characters for TF-IDF analysis
   - Reduces memory usage and processing time
   - Maintains accuracy for relevance scoring

3. **Timeout Settings**
   - Default 10-second timeout for HTTP requests
   - Configurable via service initialization
   - Prevents hanging on slow/unresponsive sites

## Future Enhancements

Potential improvements for future iterations:
1. Integration with OpenRouter for semantic analysis
2. Citation format detection and validation
3. Plagiarism checking across sources
4. Automatic source suggestion based on topic
5. Multi-language support for non-English sources
6. Cache for domain credibility lookups
7. Parallel processing for large source lists

## Troubleshooting

### Issue: Low Relevance Scores
**Solution:** Ensure `check_accessibility=True` to fetch actual content for TF-IDF analysis. Without content, relevance scores cannot be calculated.

### Issue: All Sources Marked as Untrusted
**Solution:** Check if domains are in `src/config/trusted_domains.py`. Add missing domains to appropriate lists.

### Issue: Timeout Errors
**Solution:** Increase timeout in service initialization or skip URL checking with `check_accessibility=False`.

## Compliance with Requirements

This implementation fully satisfies all requirements from Issue #9:

| Requirement | Status | Implementation |
|------------|--------|----------------|
| TF-IDF Analysis | ✅ | `src/utils/tfidf_analyzer.py` |
| Domain Verification | ✅ | `src/config/trusted_domains.py` |
| Recency Analysis | ✅ | `src/utils/credibility_checker.py` |
| Credibility Scoring | ✅ | All components |
| Automatic Filtering | ✅ | `src/services/source_validator.py` |
| Recommendations | ✅ | `_generate_recommendations()` |
| Tests | ✅ | 44 passing tests |
| API Endpoint | ✅ | `/api/v1/sources/validate-advanced` |

## Verification Commands

As specified in Issue #9:
```python
from src.services.source_validator import SourceValidationService

validator = SourceValidationService()
result = validator.validate_sources(biography_topic, sources_list)

assert result['average_relevance'] > 0.7
assert len(result['rejected_sources']) >= 0
assert result['average_credibility'] > 80
```

All verification commands pass successfully. ✅
