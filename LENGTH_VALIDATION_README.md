# Intelligent Chapter Length Validation Service

This service migrates and enhances the functionality from `check_lengths.py` with intelligent semantic analysis, quality scoring, and actionable suggestions.

## 📚 Overview

The Length Validation Service provides:
- **Length compliance checking** with configurable targets from `.env`
- **Information density analysis** using TF-IDF
- **Repetitive content detection** with n-gram analysis
- **Quality scoring** (0-100 scale)
- **Smart suggestions** for expansion, reduction, and quality improvement
- **CSV integration** compatible with existing `check_lengths.py` workflow

## 🚀 Quick Start

### Basic Usage

```python
from src.services.length_validator import LengthValidationService

# Initialize service (loads config from .env)
validator = LengthValidationService()

# Validate a chapter
chapter_text = "Your chapter content here..."
result = validator.validate_chapter(chapter_text, target_length=5000)

# Check results
print(f"Valid: {result.is_valid}")
print(f"Quality Score: {result.quality_score}/100")
print(f"Word Count: {result.word_count}/{result.expected_words}")

# Review suggestions
for suggestion in result.suggestions:
    print(f"[{suggestion.severity}] {suggestion.message}")
```

### Character Content Validation (CSV Workflow)

```python
# Validate all sections for a character (like check_lengths.py)
results = validator.validate_character_content('albert_einstein', base_dir='bios')

# Review each section
for section_name, result in results.items():
    print(f"{section_name}: {result.word_count} words, Quality: {result.quality_score}/100")
```

## ⚙️ Configuration

The service reads configuration from `.env`:

```bash
# Chapter Planning
TOTAL_WORDS=51000              # Total words for the book
CHAPTERS_NUMBER=20             # Number of chapters
WORDS_PER_CHAPTER=2550         # Target words per chapter (TOTAL_WORDS / CHAPTERS_NUMBER)
VALIDATION_TOLERANCE=0.05      # ±5% tolerance

# These variables are automatically loaded by ValidationConfig.from_env()
```

### Custom Configuration

```python
from src.config.validation_config import ValidationConfig

# Create custom config
config = ValidationConfig(
    total_words=51000,
    chapters_number=20,
    words_per_chapter=2550,
    validation_tolerance=0.05,
    min_quality_score=70.0,
    absolute_min_words=3000,
    absolute_max_words=15000
)

# Use with service
validator = LengthValidationService(config=config)
```

## 📊 Validation Results

### LengthValidationResult Object

```python
result = validator.validate_chapter(chapter_text, target_length=5000)

# Core metrics
result.is_valid              # bool: Overall validation status
result.word_count            # int: Actual word count
result.expected_words        # int: Target word count
result.quality_score         # float: Overall quality (0-100)

# Analysis scores
result.density_score         # float: Information density (0-1)
result.repetition_score      # float: Repetition level (0-1)
result.length_score          # float: Length compliance (0-100)

# Additional data
result.keywords              # List[tuple]: Top keywords with scores
result.suggestions           # List[ValidationSuggestion]: Improvement suggestions
result.metrics               # Dict: Detailed metrics (readability, balance, etc.)

# Computed properties
result.percentage_of_target  # float: Percentage of expected words
result.deviation_words       # int: Words above/below target
```

### Quality Scoring

The quality score (0-100) is calculated from:
- **Length compliance** (35%): How close to target word count
- **Information density** (30%): Uniqueness and informativeness of content
- **Repetition** (20%): Inverse of repetition score (lower repetition = higher score)
- **Content balance** (15%): Dialogue/narrative balance

### Suggestions

Suggestions are categorized by:
- **Type**: `expansion`, `reduction`, `quality`, `repetition`
- **Severity**: `critical`, `warning`, `info`

```python
for suggestion in result.suggestions:
    print(f"[{suggestion.type}] {suggestion.severity.upper()}")
    print(f"  {suggestion.message}")
    if suggestion.details:
        print(f"  Details: {suggestion.details}")
```

## 🔬 Analysis Features

### Information Density

Uses TF-IDF to measure how informative and unique the content is:
- High density (>0.7): Rich, varied content
- Medium density (0.4-0.7): Acceptable variety
- Low density (<0.4): Repetitive or generic content

### Repetition Detection

Uses n-gram analysis (default: 5-grams) to detect repeated phrases:
- Low repetition (<0.3): Good variety
- Medium repetition (0.3-0.5): Some repetition
- High repetition (>0.5): Excessive repetition

### Keyword Extraction

Extracts top keywords using TF-IDF:
```python
for keyword, score in result.keywords[:5]:
    print(f"{keyword}: {score:.3f}")
```

### Content Balance

Analyzes dialogue vs. narrative ratio:
- Balanced: 20-60% dialogue
- Too much dialogue: >60%
- Too little dialogue: <20%

## 🔄 Migration from check_lengths.py

The new service maintains **full compatibility** with the existing CSV workflow:

### Before (check_lengths.py)
```bash
python check_lengths.py albert_einstein
```

### After (LengthValidationService)
```python
from src.services.length_validator import LengthValidationService

validator = LengthValidationService()
results = validator.validate_character_content('albert_einstein')
```

Both methods:
1. Read `bios/albert_einstein/control/longitudes.csv`
2. Validate each section file
3. Update CSV with word counts and percentages
4. Maintain the same CSV format

**Enhanced features** in the new service:
- Quality scoring for each section
- Detailed suggestions for improvement
- Information density analysis
- Repetition detection
- Keyword extraction

## 📝 Examples

### Example 1: Validate Single Chapter

```python
from src.services.length_validator import LengthValidationService

validator = LengthValidationService()

chapter = """
Your chapter content here. This should be substantial text
with varied vocabulary and good information density.
""" * 300  # Repeat to get desired length

result = validator.validate_chapter(chapter, target_length=2550)

if result.is_valid:
    print(f"✅ Chapter passes validation!")
    print(f"Quality Score: {result.quality_score}/100")
else:
    print(f"❌ Chapter needs improvement")
    for suggestion in result.suggestions:
        if suggestion.severity == 'critical':
            print(f"  - {suggestion.message}")
```

### Example 2: Batch Validation

```python
# Validate all chapters for a character
results = validator.validate_character_content('character_name')

# Find chapters that need work
low_quality = {
    name: result 
    for name, result in results.items() 
    if result.quality_score < 70
}

for section, result in low_quality.items():
    print(f"{section}: {result.quality_score}/100")
    print(f"  Issues:")
    for suggestion in result.suggestions:
        if suggestion.severity != 'info':
            print(f"    - {suggestion.message}")
```

### Example 3: Custom Analysis

```python
from src.utils.text_analyzer import TextAnalyzer

analyzer = TextAnalyzer()

# Analyze specific aspects
density = analyzer.calculate_information_density(text)
repetition = analyzer.detect_repetitive_content(text)
keywords = analyzer.extract_keywords(text, top_n=10)
readability = analyzer.calculate_readability_metrics(text)

print(f"Density: {density:.2f}")
print(f"Repetition: {repetition['repetition_score']:.2f}")
print(f"Keywords: {keywords}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all validation tests
pytest tests/test_length_validation.py -v

# Run specific test categories
pytest tests/test_length_validation.py::TestValidationConfig -v
pytest tests/test_length_validation.py::TestTextAnalyzer -v
pytest tests/test_length_validation.py::TestLengthValidationService -v
pytest tests/test_length_validation.py::TestAcceptanceCriteria -v

# Run the demo
python demo_length_validation.py
```

## 📋 Acceptance Criteria

All acceptance criteria from Issue #7 are met:

- ✅ **Length validation (3000-15000 words/chapter)**: Configurable absolute boundaries
- ✅ **Information density analysis**: TF-IDF based scoring
- ✅ **Repetitive content detection**: N-gram analysis with thresholds
- ✅ **Expansion/reduction suggestions**: Context-aware recommendations
- ✅ **Quality scoring (0-100)**: Weighted multi-factor scoring
- ✅ **Pipeline integration**: Compatible with existing workflow

## 🔗 Integration

### With Generation Pipeline

```python
from src.services.length_validator import LengthValidationService
from src.services.openrouter_client import OpenRouterClient

validator = LengthValidationService()
ai_client = OpenRouterClient()

# Generate chapter
chapter = ai_client.generate_chapter(prompt)

# Validate
result = validator.validate_chapter(chapter, target_length=2550)

# Regenerate if needed
while not result.is_valid and result.quality_score < 70:
    # Use suggestions to improve prompt
    improved_prompt = enhance_prompt(prompt, result.suggestions)
    chapter = ai_client.generate_chapter(improved_prompt)
    result = validator.validate_chapter(chapter)
```

### With File System

```python
# Read chapter from file
with open('bios/character/capitulo-01.md', 'r') as f:
    chapter = f.read()

# Validate
result = validator.validate_chapter(chapter, target_length=2550)

# Write report
with open('bios/character/control/validation_report.txt', 'w') as f:
    f.write(f"Quality Score: {result.quality_score}/100\n")
    f.write(f"Word Count: {result.word_count}\n")
    for suggestion in result.suggestions:
        f.write(f"- {suggestion.message}\n")
```

## 🛠️ Architecture

```
src/
├── config/
│   └── validation_config.py    # Configuration with .env integration
├── services/
│   └── length_validator.py     # Main validation service
└── utils/
    └── text_analyzer.py         # Text analysis utilities

tests/
└── test_length_validation.py    # Comprehensive test suite (30 tests)
```

## 📚 API Reference

See the docstrings in the source files for detailed API documentation:
- `src/config/validation_config.py` - Configuration classes and methods
- `src/services/length_validator.py` - Validation service and result objects
- `src/utils/text_analyzer.py` - Text analysis utilities

## 🤝 Contributing

When extending the validation service:
1. Add tests to `tests/test_length_validation.py`
2. Update this README with new features
3. Ensure backward compatibility with `check_lengths.py` CSV format
4. Follow the existing code style and patterns

## 📄 License

Part of the BookGen AI System project.
