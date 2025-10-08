# Quick Start: Advanced Source Search Strategies

## Overview

The Advanced Source Search Strategies system provides intelligent, context-aware source discovery across academic databases, government archives, biographical websites, and news archives.

## Quick Usage

### 1. Basic Search

```python
from src.strategies import AcademicDatabaseStrategy

# Create strategy
strategy = AcademicDatabaseStrategy()

# Search for sources
sources = strategy.search("Albert Einstein")

# Display results
for source in sources:
    print(f"{source.source_item.title} - Quality: {source.quality_score:.2f}")
```

### 2. Context-Aware Search

```python
from src.strategies import (
    CharacterAnalysis,
    AcademicDatabaseStrategy,
    GovernmentArchiveStrategy,
    BiographyWebsiteStrategy
)

# Define character context
context = CharacterAnalysis(
    name="Marie Curie",
    field="physics",
    specialty="radioactivity",
    nationality="Polish-French",
    era="19th-20th century"
)

# Use multiple strategies
academic = AcademicDatabaseStrategy()
government = GovernmentArchiveStrategy()
biography = BiographyWebsiteStrategy()

# Collect sources
all_sources = []
all_sources.extend(academic.search("Marie Curie", context))
all_sources.extend(government.search("Marie Curie", context))
all_sources.extend(biography.search("Marie Curie", context))

# Sort by quality
all_sources.sort(key=lambda x: x.quality_score, reverse=True)

# Top 5 sources
for source in all_sources[:5]:
    print(f"{source.quality_score:.2f} - {source.source_item.title}")
    print(f"  {source.source_item.url}")
```

### 3. Premium Domain Lookup

```python
from src.config.premium_domains import PremiumDomainRegistry

# Check domain info
info = PremiumDomainRegistry.get_domain_info('harvard.edu')
print(f"Authority: {info['authority']}")
print(f"Specialties: {info['specialty']}")

# Get authority score
score = PremiumDomainRegistry.get_authority_score('jstor.org')
print(f"JSTOR authority: {score}")  # 95.0

# Check if premium
is_premium = PremiumDomainRegistry.is_premium_domain('archive.org')
print(f"Is archive.org premium? {is_premium}")  # True

# Get all academic domains
academic_domains = PremiumDomainRegistry.get_all_domains_by_category('academic')
print(f"Academic domains: {academic_domains}")
```

## Available Strategies

### AcademicDatabaseStrategy
**Sources**: Archive.org, JSTOR, Harvard, Stanford, MIT, Yale, Princeton, Oxford, Cambridge  
**Best for**: Scientists, researchers, academics, scholars  
**Quality**: 87.60-89.85  

```python
from src.strategies import AcademicDatabaseStrategy

strategy = AcademicDatabaseStrategy()
sources = strategy.search("Isaac Newton", context)
```

### GovernmentArchiveStrategy
**Sources**: Library of Congress, NARA, British Library, National Archives UK, UNESCO  
**Best for**: Politicians, historical figures, government officials  
**Quality**: 89.45-92.40  

```python
from src.strategies import GovernmentArchiveStrategy

strategy = GovernmentArchiveStrategy()
context = CharacterAnalysis(name="Lincoln", nationality="American")
sources = strategy.search("Abraham Lincoln", context)
```

### BiographyWebsiteStrategy
**Sources**: Britannica, Biography.com, History.com, Nobel Prize  
**Best for**: General biographies, historical figures, Nobel laureates  
**Quality**: 85.50-91.40  

```python
from src.strategies import BiographyWebsiteStrategy

strategy = BiographyWebsiteStrategy()
context = CharacterAnalysis(name="Einstein", field="physics")
sources = strategy.search("Albert Einstein", context)
```

### NewsArchiveStrategy
**Sources**: NYTimes, Reuters, BBC, Guardian, AP News  
**Best for**: Contemporary figures, politicians, recent historical events  
**Quality**: 83.25-85.95  

```python
from src.strategies import NewsArchiveStrategy

strategy = NewsArchiveStrategy()
context = CharacterAnalysis(name="Mandela", era="20th century")
sources = strategy.search("Nelson Mandela", context)
```

## Running Examples

### Demo Script
```bash
python demo_source_strategies.py
```

Shows comprehensive examples of all strategies with different historical figures.

### Verification Script
```bash
python verify_source_strategies.py
```

Verifies all acceptance criteria and displays test results.

### Run Tests
```bash
# All strategy tests
pytest tests/test_source_strategies.py -v

# Specific strategy
pytest tests/test_source_strategies.py::TestAcademicDatabaseStrategy -v

# Integration tests
pytest tests/test_source_strategies.py::TestIntegrationAcceptanceCriteria -v
```

## Quality Scoring

All sources include multi-dimensional quality metrics:

```python
source = sources[0]

print(f"Quality Score: {source.quality_score}")      # 0-100
print(f"Relevance Score: {source.relevance_score}")  # 0-1
print(f"Credibility Score: {source.credibility_score}")  # 0-100
print(f"Metadata: {source.metadata}")

# Quality calculation:
# Quality = (Credibility×30% + Relevance×35% + Technical×25% + Uniqueness×10%) × 100
```

## Context Fields

The `CharacterAnalysis` class supports these fields for context-aware searching:

- **name** (required): Character's full name
- **field**: Field of work (e.g., "science", "politics", "arts")
- **specialty**: Specific specialty (e.g., "physics", "military history")
- **era**: Time period (e.g., "20th century", "Renaissance")
- **nationality**: Country/nationality (affects archive selection)
- **institutions**: List of affiliated institutions
- **keywords**: Additional search keywords

## Premium Domains by Category

### Academic (9 domains)
harvard.edu, oxford.ac.uk, cambridge.org, jstor.org, archive.org, stanford.edu, mit.edu, yale.edu, princeton.edu

### Government (7 domains)
loc.gov, bl.uk, bnf.fr, nationalarchives.gov.uk, nara.gov, unesco.org, un.org

### Encyclopedic (3 domains)
britannica.com, oxfordreference.com, encyclopedia.com

### Biographical (4 domains)
nobelprize.org, biography.com, historynet.com, history.com

### News (6 domains)
nytimes.com, reuters.com, apnews.com, bbc.com, washingtonpost.com, theguardian.com

## Tips

1. **Use Context**: Always provide context for better results
2. **Combine Strategies**: Use multiple strategies for comprehensive coverage
3. **Check Quality**: Filter by quality_score >= 85 for highest quality
4. **Sort Results**: Sort by quality_score for best sources first
5. **Nationality Matters**: GovernmentArchiveStrategy adapts to nationality
6. **Nobel Prize**: BiographyWebsiteStrategy includes Nobel for science/peace/literature

## Support

For more details, see:
- `IMPLEMENTATION_SUMMARY_ISSUE_62.md` - Full implementation details
- `tests/test_source_strategies.py` - Integration test examples
- `demo_source_strategies.py` - Complete demo with examples
