# Smart Content Concatenation Service

## Overview

The Smart Content Concatenation Service provides intelligent biography concatenation with advanced features for narrative coherence, transition generation, and quality validation.

## Features

### ✨ Core Capabilities

1. **Narrative Coherence Analysis**
   - Character consistency checking
   - Temporal/chronological validation
   - Vocabulary coherence analysis
   - Narrative flow assessment

2. **Smart Transitions**
   - Natural section breaks
   - Header normalization
   - Transition quality validation

3. **Quality Validation**
   - Redundancy detection
   - Coherence scoring (0-1 scale)
   - Cross-reference validation
   - Automatic index generation

4. **Intelligent Metrics**
   - Total word count
   - Vocabulary richness
   - Transition quality scores
   - Missing file tracking

## Quick Start

### Basic Usage

```python
from src.services.concatenation import ConcatenationService

# Create service
service = ConcatenationService()

# Concatenate chapters
chapters_list = [
    {
        'title': 'Chapter 1',
        'content': '# Chapter 1\n\nContent here...'
    },
    {
        'title': 'Chapter 2',
        'content': '# Chapter 2\n\nMore content...'
    }
]

result = service.concatenate_chapters(chapters_list)

# Check results
print(f"Coherence Score: {result.coherence_score}")
print(f"Chronology Valid: {result.chronology_valid}")
print(f"Transition Errors: {len(result.transition_errors)}")
```

### Concatenate Biography from Files

```python
from src.services.concatenation import ConcatenationService
from src.api.models.concatenation import ConcatenationConfig

# Configure service
config = ConcatenationConfig(
    base_path="bios",
    enable_transition_generation=True,
    enable_redundancy_detection=True,
    min_coherence_score=0.8
)

service = ConcatenationService(config)

# Concatenate biography
result = service.concatenate_biography("winston_churchill")

# Review results
if result.is_high_quality:
    print("✓ High quality concatenation!")
else:
    print(f"Issues found: {len(result.coherence_issues)}")
    for issue in result.coherence_issues:
        print(f"  - {issue.description}")
```

## Acceptance Criteria Validation

The service meets all requirements from Issue #8:

```python
from src.services.concatenation import ConcatenationService

service = ConcatenationService()
result = service.concatenate_chapters(chapters_list)

# All acceptance criteria
assert result.coherence_score > 0.8  # Narrative coherence preserved
assert len(result.transition_errors) == 0  # Natural transitions
assert result.chronology_valid is True  # Correct chronology
assert result.success is True  # Cross-reference validation
```

## API Reference

### ConcatenationService

**Methods:**

- `concatenate_biography(character: str) -> ConcatenationResult`
  - Concatenates all files for a biography
  - Parameters:
    - `character`: Character name (normalized)
  - Returns: `ConcatenationResult` with metrics and analysis

- `concatenate_chapters(chapters_list: List[Dict]) -> ConcatenationResult`
  - Concatenates a list of chapter dictionaries
  - Parameters:
    - `chapters_list`: List of dicts with 'title' and 'content'
  - Returns: `ConcatenationResult`

### ConcatenationResult

**Properties:**

- `character`: Biography subject name
- `output_file`: Path to output file
- `success`: Whether concatenation succeeded
- `coherence_score`: Narrative coherence (0-1)
- `chronology_valid`: Chronological consistency
- `transition_errors`: List of transition issues
- `coherence_issues`: List of coherence problems
- `metrics`: Detailed metrics object
- `is_high_quality`: True if all quality criteria met

### NarrativeAnalyzer

Analyzes narrative coherence across chapters:

```python
from src.utils.narrative_analyzer import NarrativeAnalyzer

analyzer = NarrativeAnalyzer()
result = analyzer.analyze_coherence(chapters, "Character Name")

print(f"Coherence Score: {result['score']}")
print(f"Issues: {result['issues']}")
print(f"Metrics: {result['metrics']}")
```

### TransitionGenerator

Generates and validates transitions:

```python
from src.utils.transition_generator import TransitionGenerator

generator = TransitionGenerator()

# Generate transition
transition = generator.generate_transition(
    previous_section="...",
    next_section="..."
)

# Validate transition
validation = generator.validate_transition(prev_section, next_section)
print(f"Transition Quality: {validation['score']}")
```

## Configuration

### ConcatenationConfig

```python
from src.api.models.concatenation import ConcatenationConfig

config = ConcatenationConfig(
    base_path="bios",                          # Base directory for biographies
    output_filename_template="La biografia de {character}.md",
    enable_transition_generation=True,         # Generate smart transitions
    enable_redundancy_detection=True,          # Detect duplicate content
    enable_chronology_validation=True,         # Validate timeline
    min_coherence_score=0.8,                  # Minimum quality threshold
    separator_between_sections="\n\n",        # Section separator
    file_order=[...],                         # Custom file order
)
```

## Examples

### Example 1: Validate Biography Quality

```python
service = ConcatenationService()
result = service.concatenate_biography("alan_turing")

if not result.chronology_valid:
    print("⚠ Timeline issues detected:")
    for issue in result.coherence_issues:
        if issue.issue_type == 'timeline_conflict':
            print(f"  - {issue.description}")

if result.transition_errors:
    print("⚠ Transition problems:")
    for error in result.transition_errors:
        print(f"  - {error.message}")
```

### Example 2: Check Redundancy

```python
result = service.concatenate_biography("marie_curie")

if result.redundancies_removed > 0:
    print(f"✓ Removed {result.redundancies_removed} redundant sections")
    
print(f"Final word count: {result.metrics.total_words}")
print(f"Vocabulary richness: {result.metrics.vocabulary_richness:.2f}")
```

### Example 3: Custom Quality Thresholds

```python
config = ConcatenationConfig(
    min_coherence_score=0.9,  # Strict quality
    enable_redundancy_detection=True
)

service = ConcatenationService(config)
result = service.concatenate_biography("winston_churchill")

if result.is_high_quality:
    print("✓ Exceeds quality standards!")
```

## Testing

Run the test suite:

```bash
pytest tests/test_concatenation.py -v
```

Run the demo:

```bash
python demo_concatenation.py
```

## Architecture

### Component Overview

```
ConcatenationService
├── NarrativeAnalyzer
│   ├── Character consistency
│   ├── Temporal validation
│   ├── Vocabulary analysis
│   └── Redundancy detection
├── TransitionGenerator
│   ├── Transition generation
│   ├── Header normalization
│   └── Quality validation
└── TextAnalyzer (existing)
    ├── Word counting
    └── Text metrics
```

### Data Flow

1. Load chapter files or chapter list
2. Analyze narrative coherence
3. Validate chronology
4. Detect redundancies
5. Generate transitions
6. Concatenate with quality checks
7. Normalize headers
8. Generate index
9. Return comprehensive results

## Migration from concat.py

The service replaces the legacy `concat.py` script with enhanced functionality:

**Before (concat.py):**
```bash
python concat.py -personaje "Winston Churchill"
```

**After (ConcatenationService):**
```python
from src.services.concatenation import ConcatenationService

service = ConcatenationService()
result = service.concatenate_biography("winston_churchill")

# Now with quality metrics!
print(f"Coherence: {result.coherence_score:.2f}")
print(f"Chronology Valid: {result.chronology_valid}")
```

## Performance

- **Typical Processing Time**: < 2 seconds for 20 chapters
- **Memory Usage**: Minimal (streaming where possible)
- **Scalability**: Handles biographies with 50+ chapters

## Troubleshooting

### Low Coherence Score

If coherence score is below threshold:

1. Check character name consistency across chapters
2. Verify chronological ordering of events
3. Review vocabulary usage (too generic or too varied)
4. Ensure sufficient content in each chapter

### Transition Errors

If transition errors are reported:

1. Add proper headers to each section
2. Avoid repetitive openings/closings
3. Ensure smooth content flow between sections

### Missing Files

If files are missing:

1. Check file naming conventions (e.g., `capitulo-01.md`)
2. Verify base path configuration
3. Review file order in configuration

## Future Enhancements

Potential future improvements:

- [ ] Semantic embeddings for deeper coherence analysis
- [ ] AI-generated contextual transitions
- [ ] Advanced NER for better chronology validation
- [ ] Multi-language support
- [ ] PDF/DOCX output formats
- [ ] Interactive quality reports

## License

Part of the BookGen Sistema Automatizado project.
