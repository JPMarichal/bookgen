"""
Demo script for advanced source search strategies
"""
from src.strategies import (
    CharacterAnalysis,
    AcademicDatabaseStrategy,
    GovernmentArchiveStrategy,
    BiographyWebsiteStrategy,
    NewsArchiveStrategy
)


def print_separator():
    """Print a separator line"""
    print("\n" + "=" * 80 + "\n")


def demo_academic_strategy():
    """Demonstrate Academic Database Strategy"""
    print("🎓 ACADEMIC DATABASE STRATEGY DEMO")
    print_separator()
    
    strategy = AcademicDatabaseStrategy()
    context = CharacterAnalysis(
        name="Albert Einstein",
        field="physics",
        specialty="relativity theory",
        era="20th century"
    )
    
    print(f"Searching for: {context.name}")
    print(f"Field: {context.field}")
    print(f"Specialty: {context.specialty}")
    print()
    
    sources = strategy.search("Albert Einstein", context)
    
    print(f"Found {len(sources)} academic sources:")
    print()
    
    for i, candidate in enumerate(sources, 1):
        print(f"{i}. {candidate.source_item.title}")
        print(f"   URL: {candidate.source_item.url}")
        print(f"   Quality Score: {candidate.quality_score:.2f}")
        print(f"   Relevance: {candidate.relevance_score:.2f}")
        print(f"   Credibility: {candidate.credibility_score:.2f}")
        print(f"   Domain: {candidate.metadata.get('domain', 'N/A')}")
        print()


def demo_government_strategy():
    """Demonstrate Government Archive Strategy"""
    print("🏛️  GOVERNMENT ARCHIVE STRATEGY DEMO")
    print_separator()
    
    strategy = GovernmentArchiveStrategy()
    context = CharacterAnalysis(
        name="George Washington",
        nationality="American",
        era="18th century",
        field="politics"
    )
    
    print(f"Searching for: {context.name}")
    print(f"Nationality: {context.nationality}")
    print(f"Era: {context.era}")
    print()
    
    sources = strategy.search("George Washington", context)
    
    print(f"Found {len(sources)} government archive sources:")
    print()
    
    for i, candidate in enumerate(sources, 1):
        print(f"{i}. {candidate.source_item.title}")
        print(f"   URL: {candidate.source_item.url}")
        print(f"   Quality Score: {candidate.quality_score:.2f}")
        print(f"   Archive Type: {candidate.metadata.get('archive_type', 'N/A')}")
        print()


def demo_biography_strategy():
    """Demonstrate Biography Website Strategy"""
    print("📚 BIOGRAPHY WEBSITE STRATEGY DEMO")
    print_separator()
    
    strategy = BiographyWebsiteStrategy()
    context = CharacterAnalysis(
        name="Marie Curie",
        field="physics",
        specialty="radioactivity",
        era="19th-20th century"
    )
    
    print(f"Searching for: {context.name}")
    print(f"Field: {context.field}")
    print()
    
    sources = strategy.search("Marie Curie", context)
    
    print(f"Found {len(sources)} biographical sources:")
    print()
    
    for i, candidate in enumerate(sources, 1):
        print(f"{i}. {candidate.source_item.title}")
        print(f"   URL: {candidate.source_item.url}")
        print(f"   Quality Score: {candidate.quality_score:.2f}")
        print(f"   Category: {candidate.metadata.get('category', 'N/A')}")
        print()


def demo_news_strategy():
    """Demonstrate News Archive Strategy"""
    print("📰 NEWS ARCHIVE STRATEGY DEMO")
    print_separator()
    
    strategy = NewsArchiveStrategy()
    context = CharacterAnalysis(
        name="Nelson Mandela",
        era="20th century",
        field="politics",
        nationality="South African"
    )
    
    print(f"Searching for: {context.name}")
    print(f"Era: {context.era}")
    print()
    
    sources = strategy.search("Nelson Mandela", context)
    
    print(f"Found {len(sources)} news archive sources:")
    print()
    
    for i, candidate in enumerate(sources, 1):
        print(f"{i}. {candidate.source_item.title}")
        print(f"   URL: {candidate.source_item.url}")
        print(f"   Quality Score: {candidate.quality_score:.2f}")
        print(f"   Archive Type: {candidate.metadata.get('archive_type', 'N/A')}")
        print()


def demo_multi_strategy():
    """Demonstrate using multiple strategies together"""
    print("🌟 MULTI-STRATEGY DEMO")
    print_separator()
    
    character = "Isaac Newton"
    context = CharacterAnalysis(
        name=character,
        field="science",
        specialty="physics, mathematics",
        era="17th century",
        nationality="English"
    )
    
    print(f"Searching for: {character}")
    print(f"Using all strategies combined...")
    print()
    
    # Use all strategies
    strategies = [
        ("Academic", AcademicDatabaseStrategy()),
        ("Government", GovernmentArchiveStrategy()),
        ("Biography", BiographyWebsiteStrategy()),
        ("News", NewsArchiveStrategy()),
    ]
    
    all_sources = []
    for name, strategy in strategies:
        sources = strategy.search(character, context)
        all_sources.extend(sources)
        print(f"✓ {name} Strategy: {len(sources)} sources (avg quality: {sum(s.quality_score for s in sources) / len(sources):.2f})")
    
    print()
    print(f"Total sources found: {len(all_sources)}")
    
    # Sort by quality score
    all_sources.sort(key=lambda x: x.quality_score, reverse=True)
    
    print(f"\nTop 10 highest quality sources:")
    print()
    
    for i, candidate in enumerate(all_sources[:10], 1):
        print(f"{i}. {candidate.source_item.title}")
        print(f"   Quality: {candidate.quality_score:.2f} | {candidate.metadata.get('domain', 'N/A')}")


if __name__ == "__main__":
    print("\n" + "🚀 ADVANCED SOURCE SEARCH STRATEGIES DEMONSTRATION" + "\n")
    print("=" * 80)
    
    # Run all demos
    demo_academic_strategy()
    print_separator()
    
    demo_government_strategy()
    print_separator()
    
    demo_biography_strategy()
    print_separator()
    
    demo_news_strategy()
    print_separator()
    
    demo_multi_strategy()
    
    print("\n" + "=" * 80)
    print("\n✅ Demo completed successfully!")
    print("\nAll strategies generate high-quality sources (≥85 quality score)")
    print("from trusted academic, government, biographical, and news sources.")
    print()
