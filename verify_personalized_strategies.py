#!/usr/bin/env python
"""
Verification script for Issue #63 - Personalized Search Strategies
Tests all acceptance criteria from the issue
"""

from src.strategies import (
    get_personalized_strategy,
    ScientificFigureStrategy,
    PoliticalFigureStrategy,
    ArtisticFigureStrategy,
    LiteraryFigureStrategy,
    MilitaryFigureStrategy,
)


def verify_acceptance_criteria():
    """Verify all acceptance criteria from the issue"""
    
    print("=" * 80)
    print("VERIFICATION: Issue #63 - Personalized Search Strategies")
    print("=" * 80)
    print()
    
    # Acceptance Criteria from Issue:
    # For a scientist, debe priorizar fuentes científicas
    # strategy = get_personalized_strategy("Albert Einstein")
    # assert isinstance(strategy, ScientificFigureStrategy)
    # sources = strategy.search("Einstein")
    # scientific_domains = ["arxiv.org", "nobelprize.org", "nature.com"]
    # assert any(domain in s.url for s in sources for domain in scientific_domains)
    
    print("✓ Testing Acceptance Criteria for Scientists")
    print("-" * 80)
    
    strategy = get_personalized_strategy("Albert Einstein")
    
    # Test 1: Returns correct strategy type
    assert isinstance(strategy, ScientificFigureStrategy), \
        f"Expected ScientificFigureStrategy, got {type(strategy).__name__}"
    print("1. ✓ get_personalized_strategy('Albert Einstein') returns ScientificFigureStrategy")
    
    # Test 2: Search returns sources
    sources = strategy.search("Einstein")
    print(f"2. ✓ Strategy returns {len(sources)} sources")
    
    # Test 3: Sources prioritize scientific domains
    scientific_domains = ["arxiv.org", "nobelprize.org", "nature.com"]
    matching_sources = [
        s for s in sources 
        if any(domain in s.source_item.url for domain in scientific_domains)
    ]
    
    assert len(matching_sources) > 0, "No scientific domains found in sources"
    print(f"3. ✓ Sources include scientific domains:")
    for source in matching_sources:
        print(f"   - {source.source_item.url} (quality: {source.quality_score})")
    
    # Test 4: All sources have high quality scores
    assert all(s.quality_score >= 85 for s in sources), \
        f"Some sources have quality < 85: {[s.quality_score for s in sources]}"
    print(f"4. ✓ All sources have quality_score >= 85")
    
    print()
    
    # Test other character types
    print("✓ Testing All Character Types")
    print("-" * 80)
    
    test_cases = [
        ("Albert Einstein", ScientificFigureStrategy, "scientific"),
        ("George Washington", PoliticalFigureStrategy, "political"),
        ("Pablo Picasso", ArtisticFigureStrategy, "artistic"),
        ("William Shakespeare", LiteraryFigureStrategy, "literary"),
        ("Napoleon Bonaparte", MilitaryFigureStrategy, "military"),
    ]
    
    for character_name, expected_strategy_type, category in test_cases:
        strategy = get_personalized_strategy(character_name)
        
        assert isinstance(strategy, expected_strategy_type), \
            f"Expected {expected_strategy_type.__name__} for {character_name}, got {type(strategy).__name__}"
        
        sources = strategy.search(character_name)
        
        assert len(sources) >= 3, \
            f"Expected at least 3 sources for {character_name}, got {len(sources)}"
        
        assert all(s.quality_score >= 85 for s in sources), \
            f"Some sources for {character_name} have quality < 85"
        
        print(f"✓ {character_name:25} → {expected_strategy_type.__name__:30} ({len(sources)} sources, {category})")
    
    print()
    print("=" * 80)
    print("✅ ALL ACCEPTANCE CRITERIA VERIFIED SUCCESSFULLY!")
    print("=" * 80)
    print()
    
    return 0


if __name__ == "__main__":
    exit_code = verify_acceptance_criteria()
    exit(exit_code)
