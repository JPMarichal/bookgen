#!/usr/bin/env python
"""
Demo script for Quality Feedback System
Demonstrates the continuous learning and improvement capabilities
"""
import tempfile
from pathlib import Path

from src.services.feedback_system import QualityFeedbackSystem
from src.models.quality_metrics import BiographyQualityScore
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType


def main():
    """Demonstrate the Quality Feedback System"""
    print("=" * 70)
    print("Quality Feedback System Demo")
    print("=" * 70)
    
    # Use temporary storage for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "demo_tracking.json"
        
        # Initialize the feedback system
        print("\n1. Initializing Quality Feedback System...")
        feedback_system = QualityFeedbackSystem(storage_path=str(storage_path))
        print("   ✓ System initialized")
        
        # Simulate a successful generation for Einstein
        print("\n2. Learning from Einstein biography generation...")
        einstein_sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Albert Einstein - Nobel Prize Biography",
                    url="https://nobelprize.org/prizes/physics/1921/einstein/biographical/",
                    source_type=SourceType.DOCUMENT,
                    author="Nobel Committee",
                    publication_date="1921"
                ),
                quality_score=95.0,
                relevance_score=0.98,
                credibility_score=0.99
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein Archives Online",
                    url="https://www.einstein-website.de/",
                    source_type=SourceType.URL,
                    author="Hebrew University",
                    publication_date="2020"
                ),
                quality_score=92.0,
                relevance_score=0.96,
                credibility_score=0.95
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein: His Life and Universe",
                    source_type=SourceType.BOOK,
                    author="Walter Isaacson",
                    publication_date="2007"
                ),
                quality_score=90.0,
                relevance_score=0.94,
                credibility_score=0.92
            )
        ]
        
        einstein_quality = BiographyQualityScore(
            overall_score=93.5,
            content_quality=94.0,
            factual_accuracy=95.0,
            source_quality=92.0,
            coherence_score=93.0,
            completeness_score=94.0
        )
        
        feedback_system.learn_from_generation_success(
            character="Albert Einstein",
            sources=einstein_sources,
            quality_score=einstein_quality
        )
        print(f"   ✓ Learned from Einstein generation (score: {einstein_quality.overall_score})")
        
        # Simulate more generations
        print("\n3. Learning from additional generations...")
        characters = [
            ("Marie Curie", 91.0),
            ("Isaac Newton", 92.5),
            ("Nikola Tesla", 89.0),
            ("Ada Lovelace", 90.5)
        ]
        
        for character, score in characters:
            sources = [
                SourceCandidate(
                    source_item=SourceItem(
                        title=f"{character} Biography",
                        url=f"https://university.edu/{character.lower().replace(' ', '-')}",
                        source_type=SourceType.ARTICLE,
                        author="Academic Institution"
                    ),
                    quality_score=score
                )
                for _ in range(8)
            ]
            
            quality = BiographyQualityScore(
                overall_score=score,
                content_quality=score + 1,
                factual_accuracy=score + 2
            )
            
            feedback_system.learn_from_generation_success(
                character=character,
                sources=sources,
                quality_score=quality
            )
            print(f"   ✓ Learned from {character} generation (score: {score})")
        
        # Get improvement metrics
        print("\n4. Analyzing improvement metrics...")
        metrics = feedback_system.get_improvement_metrics()
        
        print(f"\n   📊 System Performance Metrics:")
        print(f"   - Total generations: {metrics.total_generations}")
        print(f"   - Average quality score: {metrics.avg_quality_score:.2f}")
        print(f"   - Quality trend: {metrics.quality_trend:+.2f} (positive = improving)")
        print(f"   - Success rate: {metrics.success_rate:.2%}")
        print(f"   - Patterns identified: {metrics.patterns_identified}")
        
        # Show top patterns
        if metrics.most_effective_patterns:
            print(f"\n   🎯 Top Success Patterns:")
            for i, pattern in enumerate(metrics.most_effective_patterns[:3], 1):
                print(f"   {i}. {pattern.pattern_type}: {pattern.pattern_value}")
                print(f"      - Quality impact: {pattern.avg_quality_impact:.1f}")
                print(f"      - Confidence: {pattern.confidence:.2f}")
        
        # Get recommendations
        print("\n5. Getting strategy recommendations...")
        recommendations = feedback_system.get_strategy_recommendations()
        
        if recommendations['priority_domains']:
            print(f"\n   📚 Priority Domains:")
            for domain in recommendations['priority_domains'][:5]:
                print(f"   - {domain}")
        
        print(f"\n   ⚖️ Quality Weights:")
        weights = recommendations['quality_weights']
        print(f"   - Domain Authority: {weights['domain_authority']:.2f}")
        print(f"   - Content Quality: {weights['content_quality']:.2f}")
        print(f"   - Source Type: {weights['source_type']:.2f}")
        print(f"   - Recency: {weights['recency']:.2f}")
        print(f"   - Citations: {weights['citations']:.2f}")
        
        # Export dashboard data
        print("\n6. Exporting dashboard data...")
        dashboard = feedback_system.export_dashboard_data()
        print(f"   ✓ Dashboard data exported")
        print(f"   - Time series data points: {len(dashboard['time_series'])}")
        print(f"   - Generated at: {dashboard['generated_at']}")
        
        print("\n" + "=" * 70)
        print("✅ Demo completed successfully!")
        print("=" * 70)
        print("\nThe Quality Feedback System:")
        print("  • Learns from successful biography generations")
        print("  • Identifies patterns in high-quality sources")
        print("  • Adjusts search strategies automatically")
        print("  • Tracks improvement over time")
        print("  • Provides actionable recommendations")
        print("=" * 70)


if __name__ == "__main__":
    main()
