# Personalized Search Strategies - Quick Start Guide

## Overview

The personalized search strategies system automatically selects the most appropriate search strategy based on the character's professional field, ensuring high-quality, domain-specific sources.

## Quick Start

### Basic Usage

```python
from src.strategies import get_personalized_strategy

# Automatic field detection and strategy selection
strategy = get_personalized_strategy("Albert Einstein")
sources = strategy.search("Einstein")

# All sources have quality scores >= 85
for source in sources:
    print(f"{source.source_item.url} (quality: {source.quality_score})")
```

### Manual Strategy Selection

```python
from src.strategies import (
    PersonalizedSearchStrategies,
    CharacterAnalysis
)

# Create character analysis
analysis = CharacterAnalysis(
    name="Marie Curie",
    field="science",
    specialty="physics"
)

# Get appropriate strategy
dispatcher = PersonalizedSearchStrategies()
strategy = dispatcher.get_search_strategy(analysis)

# Search for sources
sources = strategy.search("Marie Curie", analysis)
```

## Available Strategies

### 1. ScientificFigureStrategy

**For:** Scientists, researchers, physicists, chemists, biologists, mathematicians

**Priority Domains:**
- arxiv.org - Scientific preprints
- nobelprize.org - Nobel Prize organization
- nature.com - Nature journal
- science.org - Science journal
- nsf.gov - National Science Foundation
- pubmed.ncbi.nlm.nih.gov - Medical literature
- ieeexplore.ieee.org - Engineering & technology

**Example:**
```python
from src.strategies import ScientificFigureStrategy, CharacterAnalysis

analysis = CharacterAnalysis(name="Einstein", field="science", specialty="physics")
strategy = ScientificFigureStrategy(analysis)
sources = strategy.search("Einstein")
```

### 2. PoliticalFigureStrategy

**For:** Politicians, presidents, political leaders, government officials

**Priority Domains:**
- loc.gov - Library of Congress
- archives.gov - US National Archives
- presidency.ucsb.edu - American Presidency Project
- nationalarchives.gov.uk - UK National Archives
- un.org - United Nations

**Example:**
```python
from src.strategies import PoliticalFigureStrategy, CharacterAnalysis

analysis = CharacterAnalysis(
    name="Abraham Lincoln",
    field="politics",
    nationality="American"
)
strategy = PoliticalFigureStrategy(analysis)
sources = strategy.search("Abraham Lincoln")
```

### 3. ArtisticFigureStrategy

**For:** Artists, painters, sculptors, musicians, composers

**Priority Domains:**
- metmuseum.org - Metropolitan Museum of Art
- moma.org - Museum of Modern Art
- nga.gov - National Gallery of Art
- getty.edu - Getty Museum
- britishmuseum.org - British Museum
- louvre.fr - Louvre Museum

**Example:**
```python
from src.strategies import ArtisticFigureStrategy

strategy = ArtisticFigureStrategy()
sources = strategy.search("Pablo Picasso")
```

### 4. LiteraryFigureStrategy

**For:** Authors, poets, writers, playwrights

**Priority Domains:**
- gutenberg.org - Project Gutenberg
- bl.uk - British Library
- loc.gov - Library of Congress
- poetryfoundation.org - Poetry Foundation
- folger.edu - Folger Shakespeare Library

**Example:**
```python
from src.strategies import LiteraryFigureStrategy

strategy = LiteraryFigureStrategy()
sources = strategy.search("William Shakespeare")
```

### 5. MilitaryFigureStrategy

**For:** Military leaders, generals, admirals, commanders

**Priority Domains:**
- history.army.mil - US Army History
- archives.gov - National Archives (military records)
- usni.org - US Naval Institute
- iwm.org.uk - Imperial War Museum

**Example:**
```python
from src.strategies import MilitaryFigureStrategy, CharacterAnalysis

analysis = CharacterAnalysis(
    name="Napoleon",
    field="military",
    era="19th century"
)
strategy = MilitaryFigureStrategy(analysis)
sources = strategy.search("Napoleon Bonaparte")
```

## Field Detection

The system automatically detects character fields based on keywords:

- **Science:** science, physics, chemistry, biology, mathematics
- **Politics:** politics, political, government, politician
- **Arts:** arts, art, painting, sculpture, music, composer
- **Literature:** literature, writing, poetry, author, writer, poet
- **Military:** military, general, admiral, commander, war

## Quality Guarantees

All personalized strategies guarantee:

✅ Quality scores >= 85 for all sources
✅ Domain-specific, authoritative sources
✅ Specialized search terms for each field
✅ Minimum 3-5 sources per character

## Testing

Run the verification script to test all strategies:

```bash
python development/scripts/verification/verify_personalized_strategies.py
```

Or run the comprehensive test suite:

```bash
pytest tests/test_personalized_strategies.py -v
```

## Integration with Existing System

The personalized strategies integrate seamlessly with the existing source generation system:

```python
from src.services.source_generator import AutomaticSourceGenerator
from src.strategies import get_personalized_strategy

# In your source generation workflow
character_name = "Albert Einstein"

# Use personalized strategy
strategy = get_personalized_strategy(character_name)
sources = strategy.search(character_name)

# Sources are ready to use with quality scores >= 85
```

## Advanced Usage

### Custom Field Analysis

```python
from src.strategies import CharacterAnalysis, PersonalizedSearchStrategies

# Create detailed analysis
analysis = CharacterAnalysis(
    name="Marie Curie",
    field="science",
    specialty="radioactivity",
    era="20th century",
    nationality="Polish-French",
    institutions=["University of Paris", "Sorbonne"],
    keywords=["Nobel Prize", "radium", "polonium"]
)

# Get strategy
dispatcher = PersonalizedSearchStrategies()
strategy = dispatcher.get_search_strategy(analysis)

# Strategy will use all context for better results
sources = strategy.search("Marie Curie", analysis)
```

### Get Specialized Search Terms

```python
from src.strategies import ScientificFigureStrategy, CharacterAnalysis

analysis = CharacterAnalysis(
    name="Einstein",
    field="science",
    specialty="relativity"
)

strategy = ScientificFigureStrategy(analysis)

# Get specialized search terms
terms = strategy.get_specialized_search_terms("Einstein")
# Returns: ['"Einstein"', '"Einstein" scientist', '"Einstein" research', 
#           '"Einstein" relativity', '"Einstein" discovery', ...]
```

### Get Priority Domains

```python
from src.strategies import ScientificFigureStrategy

strategy = ScientificFigureStrategy()
domains = strategy.get_priority_domains()
# Returns: ['arxiv.org', 'pubmed.ncbi.nlm.nih.gov', 'ieeexplore.ieee.org', ...]
```

## References

- **Issue:** JPMarichal/bookgen#63
- **Documentation:** SISTEMA_GENERACION_FUENTES_ALTA_CALIDAD.md
- **Tests:** tests/test_personalized_strategies.py
- **Verification:** verify_personalized_strategies.py
