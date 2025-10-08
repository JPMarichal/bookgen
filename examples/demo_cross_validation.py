#!/usr/bin/env python3
"""
Demo script for Cross-Validation System
Demonstrates the cross-validation functionality for source quality assurance
"""
import sys
from src.services.cross_validator import CrossValidationSystem
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType


def create_sample_sources():
    """Create sample sources for demonstration"""
    sources = [
        SourceCandidate(
            source_item=SourceItem(
                title="Einstein: His Life and Universe",
                author="Walter Isaacson",
                publication_date="2007",
                url="https://archive.org/details/einstein-his-life",
                source_type=SourceType.BOOK
            ),
            quality_score=92.0,
            credibility_score=95.0,
            relevance_score=0.95,
            metadata={
                'content': "Albert Einstein was born on March 14, 1879, in Ulm, Germany. "
                          "Early life showed intellectual curiosity. Career focused on theoretical physics. "
                          "Developed theory of relativity in 1905. Won Nobel Prize in Physics in 1921. "
                          "Later years spent at Princeton. Died April 18, 1955. Legacy continues today."
            }
        ),
        SourceCandidate(
            source_item=SourceItem(
                title="Albert Einstein - Biography",
                author="Nobel Foundation",
                publication_date="1921",
                url="https://nobelprize.org/prizes/physics/1921/einstein/biographical/",
                source_type=SourceType.ARTICLE
            ),
            quality_score=95.0,
            credibility_score=98.0,
            relevance_score=0.9,
            metadata={
                'content': "Einstein was born in 1879 in Germany. Made fundamental contributions to physics. "
                          "Career achievements include special and general relativity. Nobel Prize awarded in 1921. "
                          "Professional work at universities. Later life in Princeton, USA."
            }
        ),
        SourceCandidate(
            source_item=SourceItem(
                title="The World as I See It",
                author="Albert Einstein",
                publication_date="1934",
                url="https://archive.org/details/worldasiseeit00eins",
                source_type=SourceType.BOOK
            ),
            quality_score=88.0,
            credibility_score=92.0,
            relevance_score=0.85,
            metadata={
                'content': "Personal writings and reflections. Born in Germany in late 19th century. "
                          "Career in theoretical physics. Development of revolutionary theories. "
                          "Work on relativity and quantum mechanics. Later years focused on unified field theory."
            }
        ),
        SourceCandidate(
            source_item=SourceItem(
                title="Einstein and the Quantum",
                author="A. Douglas Stone",
                publication_date="2013",
                url="https://press.princeton.edu/books/hardcover/einstein-quantum",
                source_type=SourceType.BOOK
            ),
            quality_score=90.0,
            credibility_score=94.0,
            relevance_score=0.88,
            metadata={
                'content': "Focus on Einstein's contributions to quantum theory. Birth and early education. "
                          "Career development in physics. Major achievements in theoretical work. "
                          "Professional collaborations and debates. Legacy in modern physics."
            }
        ),
        SourceCandidate(
            source_item=SourceItem(
                title="Einstein Archives Online",
                author="Hebrew University of Jerusalem",
                publication_date="2020",
                url="https://www.alberteinstein.info/",
                source_type=SourceType.DOCUMENT
            ),
            quality_score=94.0,
            credibility_score=97.0,
            relevance_score=0.92,
            metadata={
                'content': "Comprehensive collection of Einstein's papers and letters. Born March 14, 1879. "
                          "Early life and education documented. Career trajectory from patent clerk to professor. "
                          "Major scientific achievements throughout life. Final years in Princeton. Death in 1955."
            }
        ),
    ]
    return sources


def demo_cross_validation():
    """Demonstrate cross-validation system"""
    print("=" * 80)
    print("CROSS-VALIDATION SYSTEM DEMO")
    print("=" * 80)
    print()
    
    # Initialize system
    print("1. Initializing Cross-Validation System...")
    validator = CrossValidationSystem()
    print("   ✓ System initialized")
    print()
    
    # Create sample sources
    print("2. Creating sample source set for 'Albert Einstein'...")
    sources = create_sample_sources()
    print(f"   ✓ Created {len(sources)} sample sources")
    print()
    
    # List sources
    print("3. Source Summary:")
    for i, source in enumerate(sources, 1):
        print(f"   {i}. {source.source_item.title}")
        print(f"      Author: {source.source_item.author}")
        print(f"      Type: {source.source_item.source_type}")
        print(f"      Credibility: {source.credibility_score:.1f}")
        print()
    
    # Perform validation
    print("4. Performing Cross-Validation...")
    result = validator.validate_source_set_quality(sources, "Albert Einstein")
    print("   ✓ Validation complete")
    print()
    
    # Display results
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()
    
    print(f"Consistency Score:      {result.consistency_score:.2f} (threshold: 0.8)")
    status = "✓ PASS" if result.consistency_score >= 0.8 else "✗ FAIL"
    print(f"                        {status}")
    print()
    
    print(f"Temporal Coverage:      {result.temporal_coverage:.2f} (threshold: 0.7)")
    status = "✓ PASS" if result.temporal_coverage >= 0.7 else "✗ FAIL"
    print(f"                        {status}")
    print()
    
    print(f"Source Diversity:       {result.diversity_score:.2f}")
    print()
    
    print(f"Redundancy Level:       {result.redundancy_level:.2f} (threshold: ≤0.3)")
    status = "✓ PASS" if result.redundancy_level <= 0.3 else "✗ FAIL"
    print(f"                        {status}")
    print()
    
    print(f"Academic Compliance:    {result.academic_compliance:.2f}")
    print()
    
    print(f"Overall Quality:        {result.overall_quality:.2f}")
    print()
    
    # Display recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    for i, rec in enumerate(result.recommendations, 1):
        print(f"{i}. {rec}")
        print()
    
    # Display metadata
    if result.metadata:
        print("=" * 80)
        print("ADDITIONAL METADATA")
        print("=" * 80)
        print()
        print(f"Source Count: {result.metadata.get('source_count', 0)}")
        if 'temporal_analysis' in result.metadata:
            temp = result.metadata['temporal_analysis']
            print(f"Early Life Coverage: {temp.get('early_life', False)}")
            print(f"Career Coverage: {temp.get('career', False)}")
            print(f"Later Years Coverage: {temp.get('later_years', False)}")
            print(f"Legacy Coverage: {temp.get('legacy', False)}")
        print()
    
    # Acceptance criteria check
    print("=" * 80)
    print("ACCEPTANCE CRITERIA CHECK")
    print("=" * 80)
    print()
    
    criteria_met = True
    
    print(f"✓ consistency_score >= 0.8: {result.consistency_score >= 0.8}")
    if result.consistency_score < 0.8:
        criteria_met = False
    
    print(f"✓ temporal_coverage >= 0.7: {result.temporal_coverage >= 0.7}")
    if result.temporal_coverage < 0.7:
        criteria_met = False
    
    print(f"✓ redundancy_level <= 0.3: {result.redundancy_level <= 0.3}")
    if result.redundancy_level > 0.3:
        criteria_met = False
    
    print(f"✓ recommendations present: {len(result.recommendations) > 0}")
    if len(result.recommendations) == 0:
        criteria_met = False
    
    print()
    if criteria_met:
        print("🎉 ALL ACCEPTANCE CRITERIA MET!")
    else:
        print("⚠️  Some acceptance criteria not met")
    print()
    
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        demo_cross_validation()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during demo: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
