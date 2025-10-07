#!/usr/bin/env python
"""
Demo script for the intelligent chapter length validation service
Shows how to use the LengthValidationService with various scenarios
"""

from src.services.length_validator import LengthValidationService
from src.config.validation_config import ValidationConfig


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(result):
    """Print validation result in a nice format"""
    print(f"\n📊 Validation Result:")
    print(f"  • Valid: {'✅ Yes' if result.is_valid else '❌ No'}")
    print(f"  • Word Count: {result.word_count:,} words")
    print(f"  • Expected: {result.expected_words:,} words")
    print(f"  • Percentage: {result.percentage_of_target:.1f}%")
    print(f"  • Target Range: {result.target_min:,} - {result.target_max:,} words")
    print(f"  • Quality Score: {result.quality_score:.1f}/100")
    print(f"  • Density Score: {result.density_score:.2f}")
    print(f"  • Repetition Score: {result.repetition_score:.2f}")
    
    if result.keywords:
        print(f"\n🔑 Top Keywords:")
        for keyword, score in result.keywords[:5]:
            print(f"  • {keyword}: {score:.3f}")
    
    if result.suggestions:
        print(f"\n💡 Suggestions ({len(result.suggestions)}):")
        for i, suggestion in enumerate(result.suggestions, 1):
            icon = "🔴" if suggestion.severity == "critical" else "⚠️" if suggestion.severity == "warning" else "ℹ️"
            print(f"  {i}. {icon} [{suggestion.type.upper()}] {suggestion.message}")
            if suggestion.details:
                print(f"     {suggestion.details}")


def demo_basic_validation():
    """Demonstrate basic chapter validation"""
    print_section("1. Basic Chapter Validation")
    
    service = LengthValidationService()
    
    # Create a sample chapter
    sample_chapter = """
    Chapter 1: The Beginning
    
    This chapter introduces the main character and sets the stage for the story.
    The protagonist discovers something that will change their life forever.
    Through careful planning and determination, they begin their journey.
    
    The world around them is rich with detail and complexity.
    Every decision has consequences that ripple through the narrative.
    Character development is key to understanding their motivations.
    
    Dialogue brings the characters to life and reveals their personalities.
    "This is the start of something new," the protagonist said.
    "I can feel it in my bones. Change is coming."
    
    The setting is carefully crafted to immerse the reader.
    From the bustling streets to the quiet moments of reflection,
    every scene serves a purpose in the larger narrative arc.
    """ * 100  # Repeat to get ~2500 words
    
    result = service.validate_chapter(sample_chapter, target_length=2550)
    print_result(result)


def demo_too_short_chapter():
    """Demonstrate validation of a too-short chapter"""
    print_section("2. Too Short Chapter (Should Suggest Expansion)")
    
    service = LengthValidationService()
    
    short_chapter = """
    This is a very short chapter that doesn't meet the minimum requirements.
    It needs much more content to be considered complete.
    """ * 50  # Only ~1000 words
    
    result = service.validate_chapter(short_chapter, target_length=5000)
    print_result(result)


def demo_too_long_chapter():
    """Demonstrate validation of a too-long chapter"""
    print_section("3. Too Long Chapter (Should Suggest Reduction)")
    
    service = LengthValidationService()
    
    long_chapter = "This chapter has way too much content and should be condensed. " * 1000  # ~10000 words
    
    result = service.validate_chapter(long_chapter, target_length=5000)
    print_result(result)


def demo_repetitive_content():
    """Demonstrate detection of repetitive content"""
    print_section("4. Repetitive Content Detection")
    
    service = LengthValidationService()
    
    repetitive_chapter = """
    The same sentence appears over and over again.
    The same sentence appears over and over again.
    The same sentence appears over and over again.
    The same sentence appears over and over again.
    """ * 300  # Highly repetitive
    
    result = service.validate_chapter(repetitive_chapter, target_length=2550)
    print_result(result)


def demo_high_quality_content():
    """Demonstrate validation of high-quality, varied content"""
    print_section("5. High Quality Content")
    
    service = LengthValidationService()
    
    quality_chapter = """
    Albert Einstein revolutionized physics with his theory of relativity.
    His groundbreaking work fundamentally changed our understanding of space and time.
    
    The special theory of relativity, published in 1905, introduced revolutionary concepts.
    Time dilation and length contraction challenged classical Newtonian mechanics.
    Einstein's famous equation, E=mc², demonstrated mass-energy equivalence.
    
    General relativity, completed in 1915, explained gravity as curved spacetime.
    Massive objects bend the fabric of space and time around them.
    This elegant theory predicted phenomena like gravitational lensing and black holes.
    
    Einstein's contributions extended far beyond relativity theory alone.
    His work on the photoelectric effect earned him the Nobel Prize in 1921.
    He made fundamental advances in quantum mechanics and statistical physics.
    
    The scientific community initially resisted some of Einstein's radical ideas.
    However, experimental evidence gradually confirmed his theoretical predictions.
    Today, GPS satellites and particle accelerators rely on relativistic corrections.
    
    Einstein's philosophical views on science influenced generations of researchers.
    He believed in the power of thought experiments and mathematical beauty.
    His legacy continues to inspire physicists exploring the frontiers of knowledge.
    
    Beyond science, Einstein became an advocate for peace and social justice.
    He spoke out against nuclear weapons and supported civil rights movements.
    His humanitarian efforts reflected his deep concern for humanity's future.
    """ * 60  # Varied, informative content
    
    result = service.validate_chapter(quality_chapter, target_length=2550)
    print_result(result)


def demo_env_configuration():
    """Demonstrate usage with environment configuration"""
    print_section("6. Configuration from .env")
    
    config = ValidationConfig.from_env()
    print(f"\n📋 Configuration loaded from .env:")
    print(f"  • Total Words: {config.total_words:,}")
    print(f"  • Chapters Number: {config.chapters_number}")
    print(f"  • Words Per Chapter: {config.words_per_chapter:,}")
    print(f"  • Validation Tolerance: {config.validation_tolerance:.1%}")
    print(f"  • Absolute Min Words: {config.absolute_min_words:,}")
    print(f"  • Absolute Max Words: {config.absolute_max_words:,}")
    
    service = LengthValidationService(config=config)
    
    # Validate with env config
    chapter = "word " * config.words_per_chapter
    result = service.validate_chapter(chapter)
    
    print(f"\n✅ Chapter validated using .env configuration:")
    print(f"  • Target: {result.expected_words:,} words (from WORDS_PER_CHAPTER)")
    print(f"  • Actual: {result.word_count:,} words")
    print(f"  • Valid: {'✅ Yes' if result.is_valid else '❌ No'}")


def demo_character_validation():
    """Demonstrate character content validation (migrated from check_lengths.py)"""
    print_section("7. Character Content Validation (CSV Integration)")
    
    print("""
This feature validates all content for a character using the CSV workflow
from check_lengths.py:

Example usage:
    service = LengthValidationService()
    results = service.validate_character_content('albert_einstein', base_dir='bios')
    
This will:
1. Read bios/albert_einstein/control/longitudes.csv
2. Validate each section file (capitulo-01.md, capitulo-02.md, etc.)
3. Calculate quality metrics for each section
4. Update the CSV with actual word counts and percentages
5. Return detailed validation results for each section

The CSV format remains compatible with check_lengths.py:
    seccion,longitud_esperada,longitud_real,porcentaje
    capitulo-01,2550,2645,103.73
    capitulo-02,2550,2487,97.53
    ...
    """)


def main():
    """Run all demonstrations"""
    print("\n" + "🚀" * 40)
    print("  INTELLIGENT CHAPTER LENGTH VALIDATION SERVICE DEMO")
    print("🚀" * 40)
    
    try:
        demo_basic_validation()
        demo_too_short_chapter()
        demo_too_long_chapter()
        demo_repetitive_content()
        demo_high_quality_content()
        demo_env_configuration()
        demo_character_validation()
        
        print("\n" + "=" * 80)
        print("  ✅ Demo completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("  • Review the validation results above")
        print("  • Check tests/test_length_validation.py for more examples")
        print("  • Integrate into your chapter generation pipeline")
        print("  • Use validate_character_content() for batch validation")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
