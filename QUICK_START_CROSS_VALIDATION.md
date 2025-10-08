# Quick Start Guide: Cross-Validation System

## Installation

The cross-validation system is already integrated into the BookGen project. No additional installation required.

## Basic Usage

### 1. Import the System

```python
from src.services.cross_validator import CrossValidationSystem
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType
```

### 2. Create Source Candidates

```python
sources = [
    SourceCandidate(
        source_item=SourceItem(
            title="Einstein: His Life and Universe",
            author="Walter Isaacson",
            publication_date="2007",
            url="https://archive.org/einstein",
            source_type=SourceType.BOOK
        ),
        quality_score=92.0,
        credibility_score=95.0,
        relevance_score=0.95
    ),
    # Add more sources...
]
```

### 3. Run Validation

```python
validator = CrossValidationSystem()
result = validator.validate_source_set_quality(sources, "Albert Einstein")
```

### 4. Access Results

```python
# Core metrics
print(f"Consistency Score: {result.consistency_score:.2f}")
print(f"Temporal Coverage: {result.temporal_coverage:.2f}")
print(f"Source Diversity: {result.diversity_score:.2f}")
print(f"Redundancy Level: {result.redundancy_level:.2f}")
print(f"Academic Compliance: {result.academic_compliance:.2f}")
print(f"Overall Quality: {result.overall_quality:.2f}")

# Recommendations
for rec in result.recommendations:
    print(f"- {rec}")
```

## Understanding the Metrics

### Consistency Score (0-1)
Measures factual consistency across sources. Higher is better.
- **Target**: ≥ 0.8
- **Meaning**: How well facts align between sources

### Temporal Coverage (0-1)
Measures coverage of different life periods. Higher is better.
- **Target**: ≥ 0.7
- **Periods**: Early life, career, later years, legacy

### Source Diversity (0-1)
Measures variety in source types, domains, and authors. Higher is better.
- **Best**: Multiple source types, domains, and authors
- **Poor**: All sources from same domain or type

### Redundancy Level (0-1)
Measures information duplication. Lower is better.
- **Target**: ≤ 0.3
- **Meaning**: How much duplicate information exists

### Academic Compliance (0-1)
Measures academic quality standards. Higher is better.
- **Factors**: Peer-reviewed sources, academic domains, credibility

### Overall Quality (0-1)
Weighted combination of all metrics.
- **Formula**: 30% consistency + 20% temporal + 20% diversity + 15% (1-redundancy) + 15% academic

## Common Patterns

### Pattern 1: Validate Generated Sources

```python
# After generating sources automatically
from src.services.source_generator import AutomaticSourceGenerator

generator = AutomaticSourceGenerator()
generated = generator.generate_sources("Einstein", min_sources=40)

# Validate the generated sources
validator = CrossValidationSystem()
result = validator.validate_source_set_quality(
    generated.source_candidates,
    "Einstein"
)

if result.overall_quality >= 0.7:
    print("Source set meets quality standards")
else:
    print("Improvements needed:")
    for rec in result.recommendations:
        print(f"- {rec}")
```

### Pattern 2: Quality Gating

```python
def validate_and_filter_sources(sources, character, min_quality=0.8):
    """Validate sources and filter by quality threshold"""
    validator = CrossValidationSystem()
    result = validator.validate_source_set_quality(sources, character)
    
    if result.consistency_score < 0.8:
        raise ValueError("Sources fail consistency check")
    
    if result.temporal_coverage < 0.7:
        raise ValueError("Insufficient temporal coverage")
    
    if result.redundancy_level > 0.3:
        # Filter redundant sources
        sources = filter_redundant_sources(sources, result)
    
    return sources, result
```

### Pattern 3: Iterative Improvement

```python
def improve_source_set(sources, character, max_iterations=3):
    """Iteratively improve source set based on recommendations"""
    validator = CrossValidationSystem()
    
    for iteration in range(max_iterations):
        result = validator.validate_source_set_quality(sources, character)
        
        if result.overall_quality >= 0.8:
            print(f"Quality target reached in {iteration + 1} iterations")
            return sources, result
        
        # Apply recommendations
        sources = apply_recommendations(sources, result.recommendations)
    
    return sources, result
```

## Demos and Verification

### Run Interactive Demo

```bash
python3 demo_cross_validation.py
```

Shows a complete demonstration with sample data.

### Verify Acceptance Criteria

```bash
python3 verify_cross_validation.py
```

Verifies all acceptance criteria are met.

### Run Tests

```bash
# All cross-validation tests
python3 -m pytest tests/test_cross_validation.py -v

# Specific test class
python3 -m pytest tests/test_cross_validation.py::TestCrossValidationSystem -v

# Single test
python3 -m pytest tests/test_cross_validation.py::TestAcceptanceCriteria::test_acceptance_criteria -v
```

## Advanced Usage

### Custom OpenRouter Client

```python
from src.services.openrouter_client import OpenRouterClient

# Use custom AI client
custom_client = OpenRouterClient()
custom_client.config.temperature = 0.1  # More deterministic

validator = CrossValidationSystem(openrouter_client=custom_client)
```

### Access Detailed Metadata

```python
result = validator.validate_source_set_quality(sources, "Einstein")

# Access detailed metadata
if result.metadata:
    print(f"Source Count: {result.metadata['source_count']}")
    
    temporal = result.metadata.get('temporal_analysis', {})
    print(f"Early Life: {temporal.get('early_life', False)}")
    print(f"Career: {temporal.get('career', False)}")
    print(f"Later Years: {temporal.get('later_years', False)}")
    print(f"Legacy: {temporal.get('legacy', False)}")
```

## Troubleshooting

### Issue: Low Consistency Score

**Cause**: Facts from different sources contradict each other  
**Solution**: Review sources for accuracy, remove questionable sources

### Issue: Low Temporal Coverage

**Cause**: Sources focus on only one life period  
**Solution**: Add sources covering different time periods (early, mid, late life)

### Issue: High Redundancy

**Cause**: Many sources from same domain or with similar content  
**Solution**: Diversify sources across different domains and types

### Issue: Low Academic Compliance

**Cause**: Few peer-reviewed or academic sources  
**Solution**: Include more sources from .edu, .gov, or academic publishers

## Performance Tips

1. **Limit Source Count**: System processes up to 10 sources for fact extraction
2. **Provide Content**: Include `metadata['content']` for better fact extraction
3. **Use Fallbacks**: System gracefully degrades if AI is unavailable
4. **Batch Processing**: Validate multiple character source sets in parallel

## API Integration

If using the REST API (future enhancement):

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/sources/validate-cross",
    json={
        "sources": [...],
        "character": "Albert Einstein"
    }
)

result = response.json()
print(f"Quality: {result['overall_quality']}")
```

## Best Practices

1. **Minimum Sources**: Use at least 10-15 sources for reliable validation
2. **Source Diversity**: Mix books, articles, documents from different domains
3. **Quality First**: Prioritize high-credibility sources
4. **Iterative Validation**: Validate early and often during source collection
5. **Act on Recommendations**: Use generated recommendations to improve sources

## Related Documentation

- [Full Implementation Guide](CROSS_VALIDATION_IMPLEMENTATION.md)
- [Source Validation](QUICK_START_SOURCE_VALIDATION.md)
- [Content Analyzer](QUICK_START_CONTENT_ANALYZER.md)
- [Source Generation](AUTOMATIC_SOURCE_GENERATION.md)

## Support

For issues or questions:
- Check the test suite for usage examples
- Review the demo script for common patterns
- See implementation documentation for technical details
