# Quick Start: Advanced Content Analyzer

## Installation

No additional dependencies required. The content analyzer uses existing dependencies from `requirements.txt`:
- `requests` - for HTTP requests
- `beautifulsoup4` - for HTML parsing
- `pydantic` - for data models

## Basic Usage

```python
from src.services.content_analyzer import AdvancedContentAnalyzer

# Initialize the analyzer
analyzer = AdvancedContentAnalyzer()

# Analyze a source
score = analyzer.analyze_source_content_quality(
    source_url="https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
    character="Albert Einstein"
)

# Access results
print(f"Overall Quality Score: {score.overall_score:.2f}")
print(f"Biographical Depth: {score.biographical_depth:.2f}")
print(f"Factual Accuracy: {score.factual_accuracy:.2f}")
print(f"Neutrality: {score.neutrality_score:.2f}")
```

## Key Features

### 1. AI-Powered Analysis
Uses OpenRouterClient with multiple AI models:
- **Claude 3.5 Sonnet** - Biographical depth analysis
- **GPT-4o-mini** - Factual accuracy verification
- **Gemini Pro 1.5** - Biographical relevance

### 2. Comprehensive Metrics
- **Biographical Depth** (0-1): Coverage of life stages, context, and details
- **Factual Accuracy** (0-1): Verification of facts, dates, and consistency
- **Information Density**: Words per meaningful fact (lower is better)
- **Neutrality Score** (0-1): Bias detection and objectivity
- **Content Uniqueness** (0-1): Originality and primary source indicators

### 3. Automatic Content Processing
- Fetches content from URLs
- Cleans HTML (removes scripts, nav, footer)
- Handles errors gracefully with fallback scores

## Advanced Usage

### Custom Content Length

```python
score = analyzer.analyze_source_content_quality(
    source_url="https://example.com/biography",
    character="Marie Curie",
    max_content_length=15000  # Analyze up to 15k characters
)
```

### Access Detailed Analysis

```python
# Get detailed breakdown
if score.metadata:
    depth_details = score.metadata['depth_details']
    print(f"Early Life Coverage: {depth_details['early_life_coverage']}")
    print(f"Professional Development: {depth_details['professional_development']}")
    
    factual_details = score.metadata['factual_details']
    print(f"Citation Count: {factual_details['citation_count']}")
    print(f"Verifiable Facts: {factual_details['verifiable_facts']}")
    
    bias_details = score.metadata['bias_details']
    print(f"Detected Biases: {bias_details['detected_biases']}")
```

### Quality Thresholds

```python
# Check if source meets quality standards
if (score.biographical_depth >= 0.7 and 
    score.factual_accuracy >= 0.8 and
    score.neutrality_score >= 0.6):
    print("✓ Source meets quality standards")
    # Use this source
else:
    print("✗ Source quality insufficient")
    # Reject this source
```

## Testing

### Run Tests

```bash
# All tests
python -m pytest tests/test_content_analyzer.py -v

# Specific test
python -m pytest tests/test_content_analyzer.py::TestContentAnalyzer::test_acceptance_criteria -v

# With coverage
python -m pytest tests/test_content_analyzer.py --cov=src.services.content_analyzer
```

### Run Demo

```bash
python demo_content_analyzer.py
```

### Verify Implementation

```bash
python verify_issue_62.py
```

## Data Models

### ContentQualityScore

```python
from src.api.models.content_analysis import ContentQualityScore

score = ContentQualityScore(
    biographical_depth=0.85,
    factual_accuracy=0.90,
    information_density=25.0,
    neutrality_score=0.75,
    source_citations=5,
    content_uniqueness=0.70
)

# Calculate weighted overall score
overall = score.calculate_overall_score()
```

### BiographicalDepthAnalysis

```python
from src.api.models.content_analysis import BiographicalDepthAnalysis

depth = BiographicalDepthAnalysis(
    depth_score=0.85,
    early_life_coverage=80.0,
    professional_development=85.0,
    historical_context=75.0,
    personal_relationships=70.0,
    legacy_impact=90.0,
    specificity_score=85.0,
    concrete_details=80.0,
    justification="Excellent biographical coverage"
)
```

## Error Handling

The analyzer handles errors gracefully:

```python
try:
    score = analyzer.analyze_source_content_quality(url, character)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Returns default scores on error, never crashes
```

## Integration with Source Validation

```python
from src.services.source_validator import SourceValidator
from src.services.content_analyzer import AdvancedContentAnalyzer

# Validate basic source properties
validator = SourceValidator()
basic_validation = validator.validate_source(source_url)

# If basic validation passes, analyze content quality
if basic_validation.is_valid:
    analyzer = AdvancedContentAnalyzer()
    content_score = analyzer.analyze_source_content_quality(
        source_url,
        character_name
    )
    
    # Combine scores for final decision
    if content_score.overall_score >= 0.7:
        print("✓ Source approved for use")
```

## Performance Considerations

- **API Calls**: 3 calls per analysis (depth, accuracy, bias)
- **Rate Limiting**: Inherited from OpenRouterClient (1 req/sec free tier)
- **Timeout**: 10 seconds for content fetching
- **Content Limit**: 10,000 chars default (configurable)

## Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure you're running from the repository root:
```bash
cd /path/to/bookgen
python -c "from src.services import ContentAnalyzer; print('OK')"
```

### Issue: "OpenRouter API error"
**Solution**: Check your OpenRouter API key in environment variables:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### Issue: "Content too short"
**Solution**: The analyzer requires at least 100 characters. Check the URL content.

## Examples

See the following files for examples:
- `demo_content_analyzer.py` - Feature demonstration
- `verify_issue_62.py` - Acceptance criteria verification
- `tests/test_content_analyzer.py` - Unit test examples

## API Reference

### AdvancedContentAnalyzer

**Methods:**
- `analyze_source_content_quality(source_url, character, max_content_length=10000)` - Main analysis method
- Returns: `ContentQualityScore`

### ContentQualityScore

**Fields:**
- `biographical_depth: float` (0-1)
- `factual_accuracy: float` (0-1)
- `information_density: float` (words per fact)
- `neutrality_score: float` (0-1)
- `source_citations: int`
- `content_uniqueness: float` (0-1)
- `overall_score: float` (0-1)
- `metadata: Optional[Dict]`

**Methods:**
- `calculate_overall_score()` - Calculate weighted overall score

## Support

For issues or questions:
1. Check the implementation summary: `IMPLEMENTATION_SUMMARY_ISSUE_62.md`
2. Review tests: `tests/test_content_analyzer.py`
3. Run verification: `python verify_issue_62.py`
