# Quick Start: Quality Feedback System

## Overview

The Quality Feedback System is an automated learning system that improves source generation quality over time by analyzing successful biography generations and identifying patterns that lead to high-quality results.

## Installation

No additional dependencies required. The feedback system uses existing dependencies from `requirements.txt`.

## Basic Usage

```python
from src.services.feedback_system import QualityFeedbackSystem
from src.models.quality_metrics import BiographyQualityScore
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType

# Initialize the feedback system
feedback_system = QualityFeedbackSystem()

# After generating a biography, learn from the result
sources = [
    SourceCandidate(
        source_item=SourceItem(
            title="Einstein Biography",
            url="https://nobelprize.org/einstein",
            source_type=SourceType.DOCUMENT
        ),
        quality_score=92.0
    ),
    # ... more sources
]

biography_quality = BiographyQualityScore(
    overall_score=91.5,
    content_quality=92.0,
    factual_accuracy=93.0
)

# Learn from this successful generation
feedback_system.learn_from_generation_success(
    character="Einstein",
    sources=sources,
    quality_score=biography_quality
)

# Get improvement metrics
metrics = feedback_system.get_improvement_metrics()
print(f"Quality trend: {metrics.quality_trend:+.2f}")
print(f"Success rate: {metrics.success_rate:.2%}")
```

## Key Features

### 1. Automatic Pattern Detection

The system automatically identifies patterns in successful sources:
- **Domain patterns**: Which domains produce high-quality sources
- **Source type patterns**: Which types of sources are most effective
- **Quality thresholds**: What quality scores lead to success
- **Metadata patterns**: Which metadata features correlate with quality

### 2. Continuous Improvement Tracking

```python
metrics = feedback_system.get_improvement_metrics()

print(f"Total generations: {metrics.total_generations}")
print(f"Average quality: {metrics.avg_quality_score:.2f}")
print(f"Quality trend: {metrics.quality_trend:+.2f}")  # Positive = improving
print(f"Success rate: {metrics.success_rate:.2%}")
print(f"Patterns identified: {metrics.patterns_identified}")

# Top success patterns
for pattern in metrics.most_effective_patterns:
    print(f"- {pattern.pattern_type}: {pattern.pattern_value}")
    print(f"  Quality impact: {pattern.avg_quality_impact:.1f}")
```

### 3. Strategy Recommendations

```python
recommendations = feedback_system.get_strategy_recommendations()

# Priority domains to focus on
priority_domains = recommendations['priority_domains']

# Updated quality weights
weights = recommendations['quality_weights']

# Most effective patterns
top_patterns = recommendations['top_patterns']
```

### 4. Dashboard Data Export

```python
dashboard = feedback_system.export_dashboard_data()

# Dashboard includes:
# - metrics: Overall system performance
# - time_series: Quality over time
# - recommendations: Actionable improvements
# - total_cases: Number of learned cases
```

## Data Models

### BiographyQualityScore

Represents the quality of a generated biography:

```python
BiographyQualityScore(
    overall_score=91.5,        # 0-100
    content_quality=92.0,       # 0-100
    factual_accuracy=93.0,      # 0-100
    source_quality=90.0,        # 0-100
    coherence_score=91.0,       # 0-100
    completeness_score=90.5     # 0-100
)
```

### SuccessPattern

Represents a pattern identified in successful generations:

```python
SuccessPattern(
    pattern_type="domain",           # Type of pattern
    pattern_value="stanford.edu",    # Value
    frequency=5,                     # Times seen
    avg_quality_impact=90.0,        # Average quality when present
    confidence=0.8                   # Confidence in pattern
)
```

### ImprovementMetrics

Tracks system improvement over time:

```python
metrics = ImprovementMetrics(
    total_generations=50,
    avg_quality_score=89.5,
    quality_trend=+5.2,           # Positive = improving
    success_rate=0.85,            # 85% success rate
    patterns_identified=15,
    most_effective_patterns=[...]
)
```

## Storage

The system stores learned cases in JSON format:

```python
# Default storage location
feedback_system = QualityFeedbackSystem()  # Uses data/quality_tracking.json

# Custom storage location
feedback_system = QualityFeedbackSystem(
    storage_path="/path/to/custom/storage.json"
)
```

Storage file structure:
```json
{
  "cases": [
    {
      "character": "Einstein",
      "quality_score": 91.5,
      "source_count": 12,
      "patterns": [...],
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "last_updated": "2024-01-15T10:30:00"
}
```

## Advanced Usage

### Analyzing Recent Performance

```python
# Get cases from last 30 days
recent_cases = feedback_system.quality_tracker.get_recent_cases(days=30)

# Analyze trend
metrics = feedback_system.get_improvement_metrics(lookback_days=30)
```

### Custom Pattern Detection

```python
from src.utils.pattern_analyzer import SuccessPatternAnalyzer

# Initialize with custom frequency threshold
analyzer = SuccessPatternAnalyzer(min_pattern_frequency=3)

# Identify patterns
patterns = analyzer.identify_patterns(sources, character, quality_score)
```

### Aggregating Patterns Across Multiple Cases

```python
# Get patterns from multiple cases
all_patterns = [case.patterns for case in feedback_system.quality_tracker.get_all_cases()]

# Aggregate and rank
aggregated = feedback_system.success_patterns.aggregate_patterns(all_patterns)
```

## Integration Example

```python
def generate_and_learn_biography(character: str):
    """Generate biography and learn from the result"""
    
    # 1. Generate sources
    sources = source_generator.generate_sources(character)
    
    # 2. Generate biography
    biography = biography_generator.generate(character, sources)
    
    # 3. Evaluate quality
    quality = quality_evaluator.evaluate(biography)
    
    # 4. Learn from this generation
    feedback_system.learn_from_generation_success(
        character=character,
        sources=sources,
        quality_score=quality
    )
    
    # 5. Get updated recommendations for next generation
    recommendations = feedback_system.get_strategy_recommendations()
    
    return biography, recommendations
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_feedback_system.py -v
```

Run the demo:

```bash
python development/examples/demo_feedback_system.py
```

Verify acceptance criteria:

```bash
python development/scripts/verification/verify_feedback_system.py
```

## Performance Considerations

- **Storage**: JSON file grows with each learned case. Consider periodic archiving.
- **Pattern Analysis**: Analysis time increases with number of sources. Usually negligible (<1s for typical use).
- **Memory**: All cases loaded in memory. For production with thousands of cases, consider database backend.

## Troubleshooting

### Issue: "No improvement trend detected"
**Solution**: Ensure you have at least 10 cases with temporal variation. The system compares recent vs older cases.

### Issue: "No patterns identified"
**Solution**: Lower the `min_pattern_frequency` threshold:
```python
feedback_system = QualityFeedbackSystem(min_pattern_frequency=1)
```

### Issue: "Storage file not found"
**Solution**: The system creates storage automatically. Ensure parent directory exists and is writable:
```python
from pathlib import Path
storage_path = Path("data/quality_tracking.json")
storage_path.parent.mkdir(parents=True, exist_ok=True)
```

## API Reference

### QualityFeedbackSystem

**Methods:**

- `learn_from_generation_success(character, sources, quality_score)`: Learn from a successful generation
- `get_improvement_metrics(lookback_days=30)`: Get improvement metrics
- `get_strategy_recommendations()`: Get strategy recommendations
- `export_dashboard_data()`: Export dashboard visualization data

### SuccessPatternAnalyzer

**Methods:**

- `identify_patterns(sources, character, quality_score)`: Identify patterns in sources
- `aggregate_patterns(pattern_sets)`: Aggregate patterns from multiple cases

### QualityTracker

**Methods:**

- `store_success_case(character, sources, patterns, quality_score)`: Store a success case
- `get_recent_cases(days=30)`: Get recent success cases
- `get_all_cases()`: Get all success cases

## Examples

See the following files for working examples:

- `demo_feedback_system.py`: Full demonstration of the system
- `verify_feedback_system.py`: Acceptance criteria verification
- `tests/test_feedback_system.py`: Comprehensive test examples

## Support

For issues or questions:
1. Check the test files for usage examples
2. Run the demo script to see the system in action
3. Review the source code documentation
