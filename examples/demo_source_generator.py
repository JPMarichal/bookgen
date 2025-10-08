#!/usr/bin/env python3
"""
Demo script for automatic source generation
Shows how to use the AutomaticSourceGenerator to generate sources for a character
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.source_generator import AutomaticSourceGenerator
from src.api.models.source_generation import AutomaticSourceGenerationRequest


async def main():
    """Demo of automatic source generation"""
    
    print("=" * 70)
    print("Automatic Source Generator Demo")
    print("=" * 70)
    
    # Example 1: Basic usage
    print("\n1. Basic automatic source generation for Albert Einstein")
    print("-" * 70)
    
    request = AutomaticSourceGenerationRequest(
        character_name="Albert Einstein",
        min_sources=10,
        max_sources=20,
        check_accessibility=False,  # Disable for faster demo
        min_relevance=0.6,
        min_credibility=70.0
    )
    
    generator = AutomaticSourceGenerator()
    
    try:
        print(f"Generating sources for '{request.character_name}'...")
        print(f"  Min sources: {request.min_sources}")
        print(f"  Max sources: {request.max_sources}")
        print(f"  Min relevance: {request.min_relevance}")
        print(f"  Min credibility: {request.min_credibility}")
        print()
        
        result = generator.generate_sources_for_character(request)
        
        print(f"\n✓ Generation Complete!")
        print(f"\nCharacter Analysis:")
        analysis = result['character_analysis']
        print(f"  Name: {analysis.character_name}")
        print(f"  Period: {analysis.historical_period or 'N/A'}")
        print(f"  Nationality: {analysis.nationality or 'N/A'}")
        print(f"  Field: {analysis.professional_field or 'N/A'}")
        print(f"  Key Events: {len(analysis.key_events)}")
        print(f"  Search Terms: {len(analysis.search_terms)}")
        
        print(f"\nGeneration Results:")
        print(f"  Total candidates found: {result['generation_metadata']['total_candidates']}")
        print(f"  Valid sources: {result['generation_metadata']['valid_sources']}")
        print(f"  Final sources: {result['generation_metadata']['final_count']}")
        print(f"  Meets minimum: {result['generation_metadata']['meets_minimum']}")
        
        print(f"\nValidation Summary:")
        summary = result['validation_summary']
        print(f"  Average relevance: {summary.get('average_relevance', 0):.2f}")
        print(f"  Average credibility: {summary.get('average_credibility', 0):.1f}")
        
        print(f"\nStrategies Used:")
        for strategy in result['strategies_used']:
            print(f"  - {strategy}")
        
        print(f"\nSample Sources (first 5):")
        for i, source in enumerate(result['sources'][:5], 1):
            print(f"  {i}. {source.title}")
            if source.url:
                print(f"     URL: {source.url[:80]}...")
            print(f"     Type: {source.source_type}")
            print()
        
        print(f"\nRecommendations:")
        for rec in summary.get('recommendations', []):
            print(f"  - {rec}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
