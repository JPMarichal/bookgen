# Quick Start: Chapter Length Validation

This guide shows you how to quickly use the intelligent chapter length validation service.

## 🚀 Basic Usage

### Simple Validation

```python
from src.services.length_validator import LengthValidationService

# Initialize the service
validator = LengthValidationService()

# Validate a chapter
chapter_text = "Your chapter content here..."
result = validator.validate_chapter(chapter_text, target_length=5000)

# Check if valid
if result.is_valid:
    print(f"✅ Chapter is valid! Quality score: {result.quality_score}/100")
else:
    print(f"❌ Chapter needs improvement. Quality score: {result.quality_score}/100")
```

### View Suggestions

```python
# Get improvement suggestions
for suggestion in result.suggestions:
    print(f"[{suggestion.priority.upper()}] {suggestion.message}")
```

### Access Detailed Metrics

```python
# View component scores
print(f"Length Compliance: {result.length_score}/100")
print(f"Information Density: {result.density_score}/100")
print(f"Repetition Score: {result.repetition_score}/100")
print(f"Vocabulary Richness: {result.vocabulary_score}/100")

# View raw metrics
print(f"\nWord Count: {result.word_count}")
print(f"Information Density: {result.information_density:.3f}")
print(f"Repetition Ratio: {result.repetition_ratio:.1%}")
print(f"Vocabulary Richness: {result.vocabulary_richness:.1%}")
```

## 📊 Common Scenarios

### Validating Multiple Chapters

```python
validator = LengthValidationService()

chapters = {
    "Chapter 1": chapter1_text,
    "Chapter 2": chapter2_text,
    "Chapter 3": chapter3_text,
}

for title, text in chapters.items():
    result = validator.validate_chapter(text, target_length=5000)
    print(f"{title}: Quality {result.quality_score}/100")
```

### Custom Target Lengths

```python
# Different chapters can have different target lengths
intro_result = validator.validate_chapter(intro_text, target_length=3000)
main_result = validator.validate_chapter(main_text, target_length=8000)
conclusion_result = validator.validate_chapter(conclusion_text, target_length=4000)
```

### Filtering High-Priority Issues

```python
result = validator.validate_chapter(chapter_text, target_length=5000)

# Get only high-priority suggestions
high_priority = [s for s in result.suggestions if s.priority == 'high']

print(f"Critical issues: {len(high_priority)}")
for suggestion in high_priority:
    print(f"- {suggestion.message}")
```

## 🎯 Understanding Results

### ValidationResult Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_valid` | bool | Whether chapter meets quality standards |
| `word_count` | int | Total word count |
| `target_length` | int | Target word count |
| `quality_score` | float | Overall quality (0-100) |
| `length_score` | float | Length compliance (0-100) |
| `density_score` | float | Information density (0-100) |
| `repetition_score` | float | Low repetition (0-100) |
| `vocabulary_score` | float | Vocabulary richness (0-100) |
| `information_density` | float | TF-IDF density (0-1) |
| `repetition_ratio` | float | Repetition percentage |
| `vocabulary_richness` | float | Unique words ratio (0-1) |
| `suggestions` | list | List of ValidationSuggestion objects |
| `details` | dict | Additional analysis details |

### Quality Score Interpretation

| Score | Interpretation | Action |
|-------|----------------|--------|
| 80-100 | Excellent | Minor improvements only |
| 60-79 | Good | Some improvements recommended |
| 40-59 | Fair | Significant improvements needed |
| 0-39 | Poor | Major revision required |

### Suggestion Priorities

- **🔴 HIGH**: Critical issues that must be addressed
- **🟡 MEDIUM**: Important improvements recommended
- **🟢 LOW**: Minor enhancements for excellence

## ⚙️ Configuration

### Using Custom Config

```python
from src.config.validation_config import ValidationConfig
from src.services.length_validator import LengthValidationService

# Create custom configuration
config = ValidationConfig()
config.MIN_CHAPTER_LENGTH = 4000
config.MAX_CHAPTER_LENGTH = 12000
config.TARGET_CHAPTER_LENGTH = 6000

# Use custom config
validator = LengthValidationService(config=config)
```

### Key Configuration Parameters

```python
# Length thresholds
MIN_CHAPTER_LENGTH = 3000
MAX_CHAPTER_LENGTH = 15000
TARGET_CHAPTER_LENGTH = 5000
LENGTH_TOLERANCE = 0.05  # ±5%

# Quality thresholds
MIN_INFORMATION_DENSITY = 0.3
OPTIMAL_INFORMATION_DENSITY = 0.6
MAX_ACCEPTABLE_REPETITION_RATIO = 0.15
MIN_UNIQUE_WORDS_RATIO = 0.3
OPTIMAL_UNIQUE_WORDS_RATIO = 0.5
```

## 🔍 Detailed Analysis

### Accessing Content Statistics

```python
result = validator.validate_chapter(chapter_text, target_length=5000)

stats = result.details['content_statistics']
print(f"Paragraphs: {stats['paragraph_count']}")
print(f"Avg word length: {stats['avg_word_length']:.1f}")
print(f"Avg words per paragraph: {stats['avg_words_per_paragraph']:.1f}")
```

### Viewing Repetitive Phrases

```python
repetitive = result.details['repetitive_ngrams']
print("Most repetitive phrases:")
for item in repetitive[:5]:
    print(f"  '{item['ngram']}' appears {item['occurrences']} times")
```

### Extracting Key Terms

```python
key_terms = result.details['key_terms']
print("Key terms in chapter:")
for term, score in key_terms:
    print(f"  {term}: {score:.3f}")
```

## 📝 Example: Complete Workflow

```python
from src.services.length_validator import LengthValidationService

def validate_and_report(chapter_text, target_length=5000):
    """Complete validation workflow with reporting"""
    
    # Initialize validator
    validator = LengthValidationService()
    
    # Validate chapter
    result = validator.validate_chapter(chapter_text, target_length)
    
    # Print summary
    print("=" * 60)
    print("CHAPTER VALIDATION REPORT")
    print("=" * 60)
    print(f"Status: {'✅ VALID' if result.is_valid else '❌ NEEDS WORK'}")
    print(f"Quality Score: {result.quality_score:.1f}/100")
    print(f"Word Count: {result.word_count:,} / {target_length:,}")
    print()
    
    # Print component scores
    print("Component Scores:")
    print(f"  Length Compliance: {result.length_score:.1f}/100")
    print(f"  Information Density: {result.density_score:.1f}/100")
    print(f"  Repetition Score: {result.repetition_score:.1f}/100")
    print(f"  Vocabulary Richness: {result.vocabulary_score:.1f}/100")
    print()
    
    # Print high-priority suggestions
    high_priority = [s for s in result.suggestions if s.priority == 'high']
    if high_priority:
        print("🔴 Critical Issues:")
        for suggestion in high_priority:
            print(f"  • {suggestion.message}")
        print()
    
    # Print medium-priority suggestions
    medium_priority = [s for s in result.suggestions if s.priority == 'medium']
    if medium_priority:
        print("🟡 Recommended Improvements:")
        for suggestion in medium_priority:
            print(f"  • {suggestion.message}")
        print()
    
    return result

# Use the function
with open('chapter1.md', 'r') as f:
    chapter_text = f.read()

result = validate_and_report(chapter_text, target_length=5000)
```

## 🎬 Run the Demo

Try the interactive demo to see all features:

```bash
python development/examples/demo_length_validation.py
```

This demonstrates:
- ✅ Optimal chapter validation
- ✅ Too short chapter detection
- ✅ Too long chapter detection
- ✅ Repetitive content detection
- ✅ Low information density detection

## 📚 Next Steps

1. **Integrate into Pipeline**: Use in your content generation workflow
2. **Monitor Quality**: Track quality scores over time
3. **Tune Thresholds**: Adjust configuration for your specific needs
4. **Review Suggestions**: Act on validation recommendations

## 💡 Tips

1. **Use Consistent Targets**: Keep target lengths consistent across similar chapters
2. **Review Suggestions**: Don't ignore medium-priority suggestions
3. **Track Metrics**: Monitor trends in information density and repetition
4. **Iterate**: Validate after each major revision
5. **Balance Factors**: Don't optimize one metric at the expense of others

## 🐛 Troubleshooting

### Low Information Density Score
- Add more specific facts and details
- Reduce filler words and generic phrases
- Include concrete examples and data

### High Repetition Score
- Vary sentence structure
- Use synonyms and paraphrasing
- Remove redundant phrases

### Low Vocabulary Richness
- Use more varied vocabulary
- Avoid overusing common words
- Incorporate domain-specific terminology

## 📖 Learn More

- See `IMPLEMENTATION_SUMMARY_ISSUE_7.md` for technical details
- Check `tests/test_length_validation.py` for more usage examples
- Review `src/config/validation_config.py` for all configuration options
