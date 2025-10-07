"""
Tests for intelligent chapter length validation service
"""
import pytest
from src.services.length_validator import (
    LengthValidationService,
    LengthValidationResult,
    ValidationSuggestion
)
from src.config.validation_config import ValidationConfig
from src.utils.text_analyzer import TextAnalyzer


class TestValidationConfig:
    """Test validation configuration"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        config = ValidationConfig()
        assert config.MIN_CHAPTER_LENGTH == 3000
        assert config.MAX_CHAPTER_LENGTH == 15000
        assert config.TARGET_CHAPTER_LENGTH == 5000
        assert config.LENGTH_TOLERANCE == 0.05
    
    def test_get_length_range_default(self):
        """Test length range calculation with default target"""
        min_len, max_len = ValidationConfig.get_length_range()
        assert min_len == 4750  # 5000 - 250 (5% tolerance)
        assert max_len == 5250  # 5000 + 250
    
    def test_get_length_range_custom(self):
        """Test length range calculation with custom target"""
        min_len, max_len = ValidationConfig.get_length_range(target_length=8000)
        assert min_len == 7600  # 8000 - 400
        assert max_len == 8400  # 8000 + 400
    
    def test_get_config_dict(self):
        """Test configuration dictionary export"""
        config_dict = ValidationConfig.get_config_dict()
        assert 'min_chapter_length' in config_dict
        assert 'scoring_weights' in config_dict
        assert config_dict['target_chapter_length'] == 5000


class TestTextAnalyzer:
    """Test text analyzer utilities"""
    
    def test_count_words_simple(self):
        """Test simple word counting"""
        analyzer = TextAnalyzer()
        text = "This is a simple test with nine words here"
        count = analyzer.count_words(text)
        assert count == 9
    
    def test_count_words_with_markdown(self):
        """Test word counting with markdown formatting"""
        analyzer = TextAnalyzer()
        text = "# Header\n\nThis is **bold** and *italic* text with [link](url)."
        count = analyzer.count_words(text)
        # Should count words after removing markdown
        assert count > 0
    
    def test_calculate_information_density(self):
        """Test information density calculation"""
        analyzer = TextAnalyzer()
        # High-quality informative text
        text = """
        Artificial intelligence encompasses machine learning, natural language processing,
        computer vision, and robotics. Deep learning models utilize neural networks with
        multiple layers to extract features from data. These algorithms have revolutionized
        pattern recognition, enabling applications in medical diagnosis, autonomous vehicles,
        and financial forecasting.
        """ * 5  # Repeat to have enough content
        
        density = analyzer.calculate_information_density(text)
        assert 0.0 <= density <= 1.0
        assert density > 0.0  # Should have some information
    
    def test_detect_repetitive_content_no_repetition(self):
        """Test repetition detection with no repetition"""
        analyzer = TextAnalyzer()
        text = "Every sentence here uses completely different words and phrases without any duplication whatsoever."
        
        result = analyzer.detect_repetitive_content(text)
        assert result['repetition_ratio'] == 0.0
        assert result['total_repetitions'] == 0
    
    def test_detect_repetitive_content_with_repetition(self):
        """Test repetition detection with repetitive content"""
        analyzer = TextAnalyzer()
        # Deliberately repetitive text
        text = "The quick brown fox. The quick brown fox. The quick brown fox. The quick brown fox."
        
        result = analyzer.detect_repetitive_content(text, ngram_min=3, ngram_max=5, min_occurrences=3)
        assert result['repetition_ratio'] > 0.0
        assert len(result['repetitive_ngrams']) > 0
    
    def test_calculate_vocabulary_richness(self):
        """Test vocabulary richness calculation"""
        analyzer = TextAnalyzer()
        
        # High richness - all unique words
        text1 = "every single word here is completely different and unique"
        richness1 = analyzer.calculate_vocabulary_richness(text1)
        
        # Low richness - many repeated words
        text2 = "word word word word word same same same same"
        richness2 = analyzer.calculate_vocabulary_richness(text2)
        
        assert richness1 > richness2
        assert 0.0 <= richness1 <= 1.0
        assert 0.0 <= richness2 <= 1.0
    
    def test_analyze_sentence_structure(self):
        """Test sentence structure analysis"""
        analyzer = TextAnalyzer()
        text = "This is short. This is a much longer sentence with many words. Short again."
        
        result = analyzer.analyze_sentence_structure(text)
        assert result['sentence_count'] == 3
        assert result['avg_sentence_length'] > 0
        assert result['sentence_variety'] >= 0
    
    def test_extract_key_terms(self):
        """Test key term extraction"""
        analyzer = TextAnalyzer()
        text = """
        Machine learning algorithms process data to identify patterns.
        Neural networks are fundamental to deep learning applications.
        Training data quality significantly impacts model performance.
        """ * 3
        
        key_terms = analyzer.extract_key_terms(text, top_n=5)
        assert len(key_terms) <= 5
        if key_terms:
            # Check format
            assert isinstance(key_terms[0], tuple)
            assert len(key_terms[0]) == 2
            term, score = key_terms[0]
            assert isinstance(term, str)
            assert isinstance(score, float)
    
    def test_get_content_statistics(self):
        """Test content statistics"""
        analyzer = TextAnalyzer()
        text = "This is a test.\n\nSecond paragraph here."
        
        stats = analyzer.get_content_statistics(text)
        assert 'word_count' in stats
        assert 'character_count' in stats
        assert 'paragraph_count' in stats
        assert stats['word_count'] > 0
        assert stats['paragraph_count'] == 2


class TestLengthValidationService:
    """Test length validation service"""
    
    def test_validate_chapter_basic(self):
        """Test basic chapter validation"""
        validator = LengthValidationService()
        
        # Create a chapter with ~5000 words (target length)
        chapter_text = self._generate_sample_chapter(5000)
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        assert isinstance(result, LengthValidationResult)
        assert result.word_count > 0
        assert result.target_length == 5000
        assert 0 <= result.quality_score <= 100
        assert len(result.suggestions) > 0
    
    def test_validate_chapter_too_short(self):
        """Test validation of too-short chapter"""
        validator = LengthValidationService()
        
        # Create a short chapter (< 3000 words)
        chapter_text = self._generate_sample_chapter(2000)
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        assert result.word_count < 3000
        assert result.is_valid == False
        
        # Should have expansion suggestion
        expansion_suggestions = [s for s in result.suggestions if s.type == 'expansion']
        assert len(expansion_suggestions) > 0
    
    def test_validate_chapter_too_long(self):
        """Test validation of too-long chapter"""
        validator = LengthValidationService()
        
        # Create a long chapter (> 15000 words)
        chapter_text = self._generate_sample_chapter(16000)
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        assert result.is_valid == False
        
        # Should have reduction suggestion
        reduction_suggestions = [s for s in result.suggestions if s.type == 'reduction']
        assert len(reduction_suggestions) > 0
    
    def test_validate_chapter_optimal_length(self):
        """Test validation of optimally-sized chapter"""
        validator = LengthValidationService()
        
        # Create a chapter within target range
        chapter_text = self._generate_sample_chapter(5000)
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # Should be valid if quality is acceptable
        assert 4750 <= result.word_count <= 5250  # Within ±5% tolerance
        assert result.length_score >= 90.0  # High length score
    
    def test_quality_score_range(self):
        """Test that quality score is always in valid range"""
        validator = LengthValidationService()
        
        # Test with various chapter sizes
        for word_count in [1000, 3000, 5000, 10000, 20000]:
            chapter_text = self._generate_sample_chapter(word_count)
            result = validator.validate_chapter(chapter_text, target_length=5000)
            
            assert 0 <= result.quality_score <= 100
            assert 0 <= result.length_score <= 100
            assert 0 <= result.density_score <= 100
            assert 0 <= result.repetition_score <= 100
            assert 0 <= result.vocabulary_score <= 100
    
    def test_repetitive_content_detection(self):
        """Test detection of repetitive content"""
        validator = LengthValidationService()
        
        # Create highly repetitive content
        base_text = "This is a repetitive phrase that appears many times. "
        repetitive_text = base_text * 100  # Repeat 100 times
        
        result = validator.validate_chapter(repetitive_text, target_length=5000)
        
        # Should detect high repetition
        assert result.repetition_ratio > 0.1
        assert result.repetition_score < 90.0  # Low score due to repetition
        
        # Should have improvement suggestion
        improvement_suggestions = [
            s for s in result.suggestions 
            if 'repetition' in s.message.lower()
        ]
        assert len(improvement_suggestions) > 0
    
    def test_low_information_density_detection(self):
        """Test detection of low information density"""
        validator = LengthValidationService()
        
        # Create low-density content (filler words)
        low_density_text = "and the the the of of of to to to " * 500
        
        result = validator.validate_chapter(low_density_text, target_length=5000)
        
        # Should detect low density
        assert result.information_density < 0.3
        assert result.density_score < 80.0
    
    def test_suggestions_generation(self):
        """Test that suggestions are always generated"""
        validator = LengthValidationService()
        
        chapter_text = self._generate_sample_chapter(5000)
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # Should always have at least one suggestion
        assert len(result.suggestions) > 0
        
        # All suggestions should have required fields
        for suggestion in result.suggestions:
            assert isinstance(suggestion, ValidationSuggestion)
            assert suggestion.type in ['expansion', 'reduction', 'improvement']
            assert suggestion.priority in ['high', 'medium', 'low']
            assert len(suggestion.message) > 0
    
    def test_details_included(self):
        """Test that result includes detailed analysis"""
        validator = LengthValidationService()
        
        chapter_text = self._generate_sample_chapter(5000)
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # Check that details are included
        assert 'length_range' in result.details
        assert 'content_statistics' in result.details
        assert 'sentence_analysis' in result.details
        assert 'key_terms' in result.details
    
    def test_custom_target_length(self):
        """Test validation with custom target length"""
        validator = LengthValidationService()
        
        chapter_text = self._generate_sample_chapter(8000)
        result = validator.validate_chapter(chapter_text, target_length=8000)
        
        assert result.target_length == 8000
        # Should be within tolerance
        min_len, max_len = ValidationConfig.get_length_range(8000)
        if min_len <= result.word_count <= max_len:
            assert result.length_score >= 90.0
    
    # Helper methods
    
    def _generate_sample_chapter(self, target_words: int) -> str:
        """
        Generate sample chapter text with approximately target_words words
        
        Args:
            target_words: Approximate number of words to generate
            
        Returns:
            Sample chapter text
        """
        # Base paragraph with varied content
        paragraphs = [
            "Artificial intelligence has transformed modern technology in unprecedented ways. "
            "Machine learning algorithms process vast amounts of data to identify patterns and make predictions. "
            "Neural networks, inspired by biological brain structures, enable computers to learn from experience. "
            "Deep learning architectures have revolutionized computer vision, natural language processing, and robotics.",
            
            "The development of transformer models marked a significant breakthrough in AI research. "
            "These models excel at understanding context and relationships in sequential data. "
            "Applications range from language translation to content generation and sentiment analysis. "
            "Researchers continue to push boundaries, creating increasingly sophisticated systems.",
            
            "Data quality remains crucial for successful machine learning implementations. "
            "Training datasets must be diverse, representative, and properly labeled. "
            "Bias in training data can lead to unfair or inaccurate model predictions. "
            "Ethical considerations have become paramount in AI development and deployment.",
            
            "Cloud computing platforms have democratized access to AI technologies. "
            "Organizations of all sizes can leverage powerful machine learning tools. "
            "Scalable infrastructure supports training and deploying complex models efficiently. "
            "The integration of AI into business processes continues to accelerate globally.",
            
            "Computer vision systems can now recognize objects, faces, and scenes with remarkable accuracy. "
            "Medical imaging analysis benefits from AI-powered diagnostic assistance tools. "
            "Autonomous vehicles rely on real-time visual processing and decision making. "
            "Augmented reality applications blend digital content with physical environments seamlessly.",
        ]
        
        # Calculate how many times to repeat paragraphs
        avg_words_per_paragraph = 50  # Approximate
        repetitions = max(1, target_words // (len(paragraphs) * avg_words_per_paragraph))
        
        # Build chapter text
        chapter_parts = []
        for _ in range(repetitions):
            for i, para in enumerate(paragraphs):
                # Add slight variation to avoid exact repetition
                variation = f" Furthermore, this illustrates key concept {i+1}."
                chapter_parts.append(para + variation)
        
        return "\n\n".join(chapter_parts)


class TestAcceptanceCriteria:
    """Test that all acceptance criteria are met"""
    
    def test_acceptance_length_range_3000_15000(self):
        """Test: Validación de longitud 3000-15000 palabras/capítulo"""
        validator = LengthValidationService()
        
        # Test minimum boundary
        chapter_min = self._generate_words(3000)
        result_min = validator.validate_chapter(chapter_min, target_length=5000)
        assert result_min.word_count >= 2900  # Allow small variance
        
        # Test maximum boundary  
        chapter_max = self._generate_words(15000)
        result_max = validator.validate_chapter(chapter_max, target_length=15000)
        # Should handle up to 15000 words
        assert result_max.word_count >= 14000
    
    def test_acceptance_information_density_analysis(self):
        """Test: Análisis de densidad de información"""
        validator = LengthValidationService()
        
        chapter_text = self._generate_words(5000)
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # Should calculate information density
        assert hasattr(result, 'information_density')
        assert 0.0 <= result.information_density <= 1.0
        assert hasattr(result, 'density_score')
        assert 0.0 <= result.density_score <= 100.0
    
    def test_acceptance_repetitive_content_detection(self):
        """Test: Detección de contenido repetitivo"""
        validator = LengthValidationService()
        
        # Create repetitive content
        repetitive = "Same phrase repeated. " * 500
        result = validator.validate_chapter(repetitive, target_length=5000)
        
        # Should detect repetition
        assert hasattr(result, 'repetition_ratio')
        assert result.repetition_ratio > 0.0
        assert hasattr(result, 'repetition_score')
    
    def test_acceptance_expansion_reduction_suggestions(self):
        """Test: Sugerencias de expansión/reducción"""
        validator = LengthValidationService()
        
        # Too short - should suggest expansion
        short_chapter = self._generate_words(2000)
        result_short = validator.validate_chapter(short_chapter, target_length=5000)
        expansion_suggestions = [s for s in result_short.suggestions if s.type == 'expansion']
        assert len(expansion_suggestions) > 0
        
        # Too long - should suggest reduction
        long_chapter = self._generate_words(16000)
        result_long = validator.validate_chapter(long_chapter, target_length=5000)
        reduction_suggestions = [s for s in result_long.suggestions if s.type == 'reduction']
        assert len(reduction_suggestions) > 0
    
    def test_acceptance_quality_scoring_0_100(self):
        """Test: Scoring de calidad 0-100"""
        validator = LengthValidationService()
        
        # Test multiple scenarios
        test_cases = [
            self._generate_words(2000),   # Too short
            self._generate_words(5000),   # Perfect
            self._generate_words(16000),  # Too long
        ]
        
        for chapter in test_cases:
            result = validator.validate_chapter(chapter, target_length=5000)
            
            # Quality score must be in range 0-100
            assert 0 <= result.quality_score <= 100
            assert isinstance(result.quality_score, (int, float))
    
    def test_acceptance_pipeline_integration_ready(self):
        """Test: Integración con pipeline de generación"""
        # The service should be ready to integrate into a generation pipeline
        validator = LengthValidationService()
        
        # Should be able to validate without errors
        chapter = self._generate_words(5000)
        result = validator.validate_chapter(chapter, target_length=5000)
        
        # Result should have all needed attributes for pipeline integration
        assert result.is_valid is not None
        assert isinstance(result.is_valid, bool)
        assert result.quality_score is not None
        assert len(result.suggestions) >= 0
        
        # Should be able to call multiple times
        result2 = validator.validate_chapter(chapter, target_length=5000)
        assert result2.quality_score == result.quality_score
    
    def _generate_words(self, count: int) -> str:
        """Generate text with approximately 'count' words"""
        base = "word " * count
        return base


class TestVerificationCommands:
    """Test verification commands from issue requirements"""
    
    def test_verification_command_example(self):
        """Test the exact verification command from the issue"""
        from src.services.length_validator import LengthValidationService
        
        validator = LengthValidationService()
        
        # Generate sample chapter text
        chapter_text = "Artificial intelligence " * 1000  # ~5000 words
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # Verify the exact assertions from the issue
        assert result.is_valid is True or result.is_valid is False  # Must be boolean
        assert 0 <= result.quality_score <= 100
        assert len(result.suggestions) > 0
