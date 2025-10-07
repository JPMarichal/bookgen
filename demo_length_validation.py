"""
Demo script for intelligent chapter length validation service
"""
from src.services.length_validator import LengthValidationService


def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)


def demo_validation():
    """Demonstrate the length validation service"""
    print_separator()
    print("DEMO: Intelligent Chapter Length Validation Service")
    print_separator()
    print()
    
    # Initialize service
    validator = LengthValidationService()
    
    # Demo 1: Optimal chapter
    print("📊 DEMO 1: Optimal Chapter (~5000 words)")
    print_separator('-')
    
    optimal_chapter = generate_quality_chapter(5000)
    result1 = validator.validate_chapter(optimal_chapter, target_length=5000)
    
    print_result_summary(result1)
    print()
    
    # Demo 2: Too short chapter
    print("📊 DEMO 2: Too Short Chapter (~2000 words)")
    print_separator('-')
    
    short_chapter = generate_quality_chapter(2000)
    result2 = validator.validate_chapter(short_chapter, target_length=5000)
    
    print_result_summary(result2)
    print()
    
    # Demo 3: Too long chapter
    print("📊 DEMO 3: Too Long Chapter (~16000 words)")
    print_separator('-')
    
    long_chapter = generate_quality_chapter(16000)
    result3 = validator.validate_chapter(long_chapter, target_length=5000)
    
    print_result_summary(result3)
    print()
    
    # Demo 4: Repetitive content
    print("📊 DEMO 4: Repetitive Content Detection")
    print_separator('-')
    
    repetitive_chapter = "This is a repetitive phrase that appears many times. " * 100
    result4 = validator.validate_chapter(repetitive_chapter, target_length=5000)
    
    print_result_summary(result4)
    print()
    
    # Demo 5: Low information density
    print("📊 DEMO 5: Low Information Density")
    print_separator('-')
    
    low_density_chapter = "the and of to a in is it that was " * 600
    result5 = validator.validate_chapter(low_density_chapter, target_length=5000)
    
    print_result_summary(result5)
    print()
    
    print_separator()
    print("✅ Demo completed successfully!")
    print_separator()


def print_result_summary(result):
    """Print a summary of validation result"""
    print(f"Valid: {'✅ YES' if result.is_valid else '❌ NO'}")
    print(f"Word Count: {result.word_count:,} / {result.target_length:,}")
    print(f"Quality Score: {result.quality_score:.1f}/100")
    print()
    
    print("Component Scores:")
    print(f"  - Length Compliance: {result.length_score:.1f}/100")
    print(f"  - Information Density: {result.density_score:.1f}/100")
    print(f"  - Repetition Score: {result.repetition_score:.1f}/100")
    print(f"  - Vocabulary Richness: {result.vocabulary_score:.1f}/100")
    print()
    
    print("Analysis Metrics:")
    print(f"  - Information Density: {result.information_density:.3f}")
    print(f"  - Repetition Ratio: {result.repetition_ratio:.3f} ({result.repetition_ratio*100:.1f}%)")
    print(f"  - Vocabulary Richness: {result.vocabulary_richness:.3f} ({result.vocabulary_richness*100:.1f}%)")
    print()
    
    print(f"Top {min(3, len(result.suggestions))} Suggestions:")
    for i, suggestion in enumerate(result.suggestions[:3], 1):
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(suggestion.priority, '⚪')
        print(f"  {i}. {priority_emoji} [{suggestion.priority.upper()}] {suggestion.message}")
    print()


def generate_quality_chapter(target_words: int) -> str:
    """Generate a quality chapter with varied content"""
    paragraphs = [
        "Artificial intelligence has fundamentally transformed modern technology in unprecedented ways. "
        "Machine learning algorithms efficiently process vast amounts of data to identify complex patterns. "
        "Neural networks, inspired by biological brain structures, enable computers to learn from experience. "
        "Deep learning architectures have revolutionized computer vision and natural language processing.",
        
        "The development of transformer models marked a significant breakthrough in AI research capabilities. "
        "These sophisticated models excel at understanding context and relationships in sequential data streams. "
        "Applications range from language translation to content generation and sentiment analysis tasks. "
        "Researchers worldwide continue pushing boundaries, creating increasingly sophisticated intelligent systems.",
        
        "Data quality remains absolutely crucial for successful machine learning implementations everywhere. "
        "Training datasets must be diverse, representative, and properly labeled for optimal results. "
        "Bias in training data can lead to unfair or inaccurate model predictions downstream. "
        "Ethical considerations have become paramount in AI development and deployment strategies.",
        
        "Cloud computing platforms have democratized access to powerful AI technologies globally. "
        "Organizations of all sizes can now leverage sophisticated machine learning tools effectively. "
        "Scalable infrastructure supports training and deploying complex models efficiently at scale. "
        "The integration of AI into business processes continues to accelerate worldwide.",
        
        "Computer vision systems can now recognize objects, faces, and scenes with remarkable accuracy. "
        "Medical imaging analysis benefits tremendously from AI-powered diagnostic assistance tools today. "
        "Autonomous vehicles rely heavily on real-time visual processing and intelligent decision making. "
        "Augmented reality applications blend digital content with physical environments seamlessly together.",
    ]
    
    # Calculate repetitions needed
    avg_words_per_paragraph = 50
    repetitions = max(1, target_words // (len(paragraphs) * avg_words_per_paragraph))
    
    # Build chapter with variations
    chapter_parts = []
    for rep in range(repetitions):
        for i, para in enumerate(paragraphs):
            variation = f" This demonstrates key concept {i+1} in context {rep+1}."
            chapter_parts.append(para + variation)
    
    return "\n\n".join(chapter_parts)


if __name__ == "__main__":
    demo_validation()
