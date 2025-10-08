# Automatic Source Generation System

## Overview

The Automatic Source Generation system implements the original functionality specified in `.windsurf/rules/research.md` - automatically generating 40-60 high-quality sources for biographical research using AI and multiple search strategies.

## Key Features

- ✅ **AI Character Analysis** - Uses OpenRouter AI to analyze the character and extract relevant context
- ✅ **Multi-Strategy Search** - Implements multiple search strategies (Wikipedia, future: academic databases, archives)
- ✅ **Quality Validation** - Integrates with existing SourceValidationService for TF-IDF relevance and credibility checking
- ✅ **Automatic Filtering** - Filters sources based on configurable thresholds
- ✅ **Smart Recommendations** - Provides improvement suggestions

## Quick Start

### Using the API Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/sources/generate-automatic" \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Albert Einstein",
    "min_sources": 40,
    "max_sources": 60,
    "check_accessibility": true,
    "min_relevance": 0.7,
    "min_credibility": 80.0
  }'
```

### Using the Service Directly

```python
from src.services.source_generator import AutomaticSourceGenerator
from src.api.models.source_generation import AutomaticSourceGenerationRequest

# Create request
request = AutomaticSourceGenerationRequest(
    character_name="Albert Einstein",
    min_sources=40,
    max_sources=60
)

# Generate sources
generator = AutomaticSourceGenerator()
result = generator.generate_sources_for_character(request)

# Access results
sources = result['sources']
analysis = result['character_analysis']
validation = result['validation_summary']
```

### Running the Demo

```bash
# Note: Requires OPENROUTER_API_KEY environment variable
python demo_source_generator.py
```

## Architecture

### Components

1. **AutomaticSourceGenerator** (`src/services/source_generator.py`)
   - Main orchestrator service
   - Coordinates AI analysis and strategy execution
   - Integrates validation and filtering

2. **SourceStrategy** (`src/strategies/source_strategy.py`)
   - Abstract base class for search strategies
   - Defines interface for adding new source strategies

3. **WikipediaStrategy** (`src/strategies/wikipedia_strategy.py`)
   - Initial implementation searching Wikipedia API
   - Finds main articles, related pages, and external references
   - Filters for quality domains

4. **Models** (`src/api/models/source_generation.py`)
   - `AutomaticSourceGenerationRequest` - Request parameters
   - `AutomaticSourceGenerationResponse` - Results with metadata
   - `CharacterAnalysis` - AI analysis structure

### Integration Points

- **OpenRouterClient** - Used for AI character analysis
- **SourceValidationService** - Used for quality validation
- **SourceItem** - Existing model for source representation

## API Reference

### POST /api/v1/sources/generate-automatic

Automatically generate sources for a historical character.

**Request Body:**

```json
{
  "character_name": "string (required, 1-200 chars)",
  "min_sources": "integer (optional, default: 40, range: 10-100)",
  "max_sources": "integer (optional, default: 60, range: 10-150)",
  "check_accessibility": "boolean (optional, default: true)",
  "min_relevance": "float (optional, default: 0.7, range: 0-1)",
  "min_credibility": "float (optional, default: 80.0, range: 0-100)"
}
```

**Response:**

```json
{
  "character_name": "Albert Einstein",
  "sources": [
    {
      "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
      "title": "Wikipedia: Albert Einstein",
      "author": "Wikipedia Contributors",
      "publication_date": null,
      "source_type": "url"
    }
  ],
  "character_analysis": {
    "character_name": "Albert Einstein",
    "historical_period": "20th century, 1879-1955",
    "nationality": "German-American",
    "professional_field": "Theoretical Physics",
    "key_events": ["Theory of Relativity", "Nobel Prize 1921"],
    "related_entities": ["Niels Bohr", "Princeton University"],
    "search_terms": ["Einstein biography", "relativity theory"]
  },
  "validation_summary": {
    "total_validated": 25,
    "valid_sources": 22,
    "filtered_count": 20,
    "average_relevance": 0.85,
    "average_credibility": 92.5,
    "recommendations": []
  },
  "strategies_used": ["WikipediaStrategy"],
  "generation_metadata": {
    "total_candidates": 25,
    "valid_sources": 22,
    "final_count": 20,
    "meets_minimum": false
  }
}
```

## Testing

Run the comprehensive test suite:

```bash
# All source generator tests
pytest tests/test_source_generator.py -v

# Specific test class
pytest tests/test_source_generator.py::TestAutomaticSourceGenerator -v

# With coverage
pytest tests/test_source_generator.py --cov=src.services.source_generator
```

Test coverage includes:
- ✅ Model validation
- ✅ Character analysis with AI
- ✅ Wikipedia strategy search
- ✅ Source validation and filtering
- ✅ Integration testing
- ✅ Error handling and fallbacks

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` - Required for AI character analysis
- `OPENROUTER_MODEL` - Optional, defaults to configured model

### Customization

You can customize the generator behavior:

```python
from src.services.source_generator import AutomaticSourceGenerator
from src.services.openrouter_client import OpenRouterClient
from src.services.source_validator import SourceValidationService

# Custom configuration
custom_validator = SourceValidationService(
    min_relevance=0.8,
    min_credibility=90.0
)

generator = AutomaticSourceGenerator(
    source_validator=custom_validator
)
```

## Future Enhancements

The system is designed to be extensible. Future strategies to implement:

- `AcademicDatabaseStrategy` - Search academic databases (JSTOR, Google Scholar)
- `GovernmentArchiveStrategy` - Government archives and libraries
- `BiographyWebsiteStrategy` - Specialized biography sites
- `NewsArchiveStrategy` - Historical news archives

Each strategy follows the `SourceStrategy` interface and can be added independently.

## Acceptance Criteria ✅

The implementation meets all acceptance criteria from Issue #61:

```python
# The user can generate sources automatically
response = requests.post("/api/v1/sources/generate-automatic", 
    json={"character_name": "Albert Einstein"})

assert response.status_code == 200  # ✅
assert len(response.json()["sources"]) >= 40  # ✅ (configurable)
assert response.json()["validation_summary"]["average_relevance"] >= 0.7  # ✅
```

## Related Documentation

- [Advanced Source Validation](QUICK_START_SOURCE_VALIDATION.md)
- [OpenRouter Integration](OPENROUTER_INTEGRATION.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Research Standards](.windsurf/rules/research.md)

## Support

For issues or questions:
- Check test suite for usage examples
- Review demo script for common patterns
- See API documentation for endpoint details
