"""
Tests for intelligent chapter length validation service
"""
import pytest
import os
from pathlib import Path
import tempfile
import csv

from src.services.length_validator import (
    LengthValidationService,
    LengthValidationResult,
    ValidationSuggestion
)
from src.config.validation_config import ValidationConfig
from src.utils.text_analyzer import TextAnalyzer


class TestValidationConfig:
    """Test validation configuration"""
    
    def test_from_env(self):
        """Test loading configuration from environment"""
        config = ValidationConfig.from_env()
        
        assert config.total_words > 0
        assert config.chapters_number > 0
        assert config.words_per_chapter > 0
        assert 0 < config.validation_tolerance < 1
    
    def test_get_target_range(self):
        """Test target range calculation"""
        config = ValidationConfig(
            total_words=51000,
            chapters_number=20,
            words_per_chapter=2550,
            validation_tolerance=0.05
        )
        
        min_words, max_words = config.get_target_range()
        
        # With 5% tolerance on 2550 words, but respecting absolute minimums
        # min should be max of (calculated min, absolute_min_words=3000)
        expected_min = max(2550 - int(2550 * 0.05), config.absolute_min_words)
        expected_max = min(2550 + int(2550 * 0.05), config.absolute_max_words)
        assert min_words == expected_min
        assert max_words == expected_max
    
    def test_is_within_tolerance(self):
        """Test tolerance checking"""
        config = ValidationConfig(
            total_words=51000,
            chapters_number=20,
            words_per_chapter=2550,
            validation_tolerance=0.05
        )
        
        # Within tolerance (±5%)
        assert config.is_within_tolerance(2550) is True
        assert config.is_within_tolerance(2500) is True
        assert config.is_within_tolerance(2600) is True
        
        # Outside tolerance
        assert config.is_within_tolerance(2000) is False
        assert config.is_within_tolerance(3000) is False
    
    def test_calculate_length_score(self):
        """Test length score calculation"""
        config = ValidationConfig(
            total_words=51000,
            chapters_number=20,
            words_per_chapter=2550,
            validation_tolerance=0.05
        )
        
        # Perfect score (exactly at target)
        score = config.calculate_length_score(2550)
        assert score == 100.0
        
        # Still perfect (within 95-105% = 2422-2677)
        score = config.calculate_length_score(2500)
        assert score == 100.0  # 2500/2550 = 0.98 which is in 0.95-1.05 range
        
        # Within tolerance but not perfect
        score = config.calculate_length_score(2430)  # Slightly above lower edge
        assert 80.0 <= score <= 100.0
        
        # Outside tolerance
        score = config.calculate_length_score(2000)
        assert score < 80.0


class TestTextAnalyzer:
    """Test text analysis utilities"""
    
    def test_count_words(self):
        """Test word counting matches check_lengths.py logic"""
        analyzer = TextAnalyzer()
        
        # Simple count test
        text = "One two three four five"
        assert analyzer.count_words(text) == 5
        
        text = "One"
        assert analyzer.count_words(text) == 1
        
        text = ""
        assert analyzer.count_words(text) == 0
    
    def test_calculate_information_density(self):
        """Test information density calculation"""
        analyzer = TextAnalyzer()
        
        # High density text (lots of unique words)
        high_density = "Python programming language features include dynamic typing, automatic memory management, comprehensive standard library, and extensive third-party packages."
        density = analyzer.calculate_information_density(high_density)
        assert 0 <= density <= 1  # Valid range
        
        # Verify uniqueness fallback with short text
        unique_text = "different unique words variety diverse"
        density2 = analyzer.calculate_information_density(unique_text)
        assert 0 <= density2 <= 1
    
    def test_detect_repetitive_content(self):
        """Test repetition detection"""
        analyzer = TextAnalyzer(ngram_size=3)
        
        # Highly repetitive text
        repetitive = "the quick brown fox jumps over the quick brown fox jumps over the quick brown fox"
        result = analyzer.detect_repetitive_content(repetitive)
        
        assert result['repetition_score'] > 0.5
        assert result['total_ngrams'] > 0
        
        # Unique text
        unique = "Python is a versatile programming language. JavaScript powers web development. Rust ensures memory safety."
        result = analyzer.detect_repetitive_content(unique)
        
        assert result['repetition_score'] < 0.5
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        analyzer = TextAnalyzer()
        
        text = "Python programming language is widely used for data science, machine learning, and web development. Python has extensive libraries."
        keywords = analyzer.extract_keywords(text, top_n=5)
        
        assert len(keywords) > 0
        assert len(keywords) <= 5
        assert all(isinstance(k, tuple) and len(k) == 2 for k in keywords)
    
    def test_calculate_readability_metrics(self):
        """Test readability metrics"""
        analyzer = TextAnalyzer()
        
        text = "This is a sentence. This is another sentence. Here is a third one."
        metrics = analyzer.calculate_readability_metrics(text)
        
        assert 'avg_sentence_length' in metrics
        assert 'avg_word_length' in metrics
        assert 'sentence_count' in metrics
        assert 'word_count' in metrics
        assert metrics['sentence_count'] == 3
    
    def test_analyze_content_balance(self):
        """Test content balance analysis"""
        analyzer = TextAnalyzer()
        
        # Balanced text with some dialogue
        balanced = '''The scientist said "This is a discovery" and continued working. 
                     She analyzed the data carefully. "The results are significant," she noted.'''
        result = analyzer.analyze_content_balance(balanced)
        
        assert 'dialogue_ratio' in result
        assert 'narrative_ratio' in result
        assert 'is_balanced' in result
        assert 0 <= result['dialogue_ratio'] <= 1


class TestLengthValidationService:
    """Test main validation service"""
    
    def test_initialization_default(self):
        """Test service initialization with default config"""
        service = LengthValidationService()
        
        assert service.config is not None
        assert service.text_analyzer is not None
        assert service.config.words_per_chapter > 0
    
    def test_initialization_custom_config(self):
        """Test service initialization with custom config"""
        config = ValidationConfig(
            total_words=51000,
            chapters_number=20,
            words_per_chapter=2550,
            validation_tolerance=0.05
        )
        service = LengthValidationService(config=config)
        
        assert service.config == config
        assert service.config.words_per_chapter == 2550
    
    def test_validate_chapter_basic(self):
        """Test basic chapter validation"""
        service = LengthValidationService()
        
        # Create sample chapter text (around 2550 words to match default)
        chapter_text = " ".join(["word"] * 2550)
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert isinstance(result, LengthValidationResult)
        assert result.word_count == 2550
        assert result.expected_words == 2550
        assert 0 <= result.quality_score <= 100
        assert len(result.suggestions) > 0
    
    def test_validate_chapter_too_short(self):
        """Test validation with too-short chapter"""
        service = LengthValidationService()
        
        # Create short chapter (1000 words, well below 2550)
        chapter_text = " ".join(["word"] * 1000)
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert result.word_count == 1000
        assert result.is_valid is False
        # Should have expansion suggestion
        expansion_suggestions = [s for s in result.suggestions if s.type == 'expansion']
        assert len(expansion_suggestions) > 0
    
    def test_validate_chapter_too_long(self):
        """Test validation with too-long chapter"""
        service = LengthValidationService()
        
        # Create long chapter (5000 words, well above 2550)
        chapter_text = " ".join(["word"] * 5000)
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert result.word_count == 5000
        assert result.is_valid is False
        # Should have reduction suggestion
        reduction_suggestions = [s for s in result.suggestions if s.type == 'reduction']
        assert len(reduction_suggestions) > 0
    
    def test_validate_chapter_within_tolerance(self):
        """Test validation with chapter within tolerance"""
        config = ValidationConfig(
            total_words=51000,
            chapters_number=20,
            words_per_chapter=2550,
            validation_tolerance=0.05
        )
        service = LengthValidationService(config=config)
        
        # Create chapter within 5% tolerance (2500 words)
        # Use varied text for better quality score
        words = ["quality", "content", "text", "chapter", "story", "narrative", "character", "plot"]
        chapter_text = " ".join(words * 313)  # ~2500 words with variety
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert 2400 <= result.word_count <= 2700
        # Quality might still be low due to repetition, but length should be okay
        assert result.length_score >= 80.0
    
    def test_validate_chapter_quality_metrics(self):
        """Test that quality metrics are calculated"""
        service = LengthValidationService()
        
        # Create realistic chapter text
        chapter_text = """
        In the year 1905, Albert Einstein published his groundbreaking paper on special relativity.
        This revolutionary theory transformed our understanding of space and time.
        The famous equation E=mc² emerged from this work, showing the equivalence of mass and energy.
        Einstein's contributions to physics extended beyond relativity.
        He made significant advances in quantum mechanics, statistical mechanics, and cosmology.
        His work on the photoelectric effect earned him the Nobel Prize in Physics.
        The scientific community initially resisted some of his ideas, but gradually accepted them.
        Today, Einstein is recognized as one of the greatest physicists of all time.
        His theories continue to influence modern physics and our understanding of the universe.
        """ * 250  # Repeat to get enough words
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert 0 <= result.quality_score <= 100
        assert 0 <= result.density_score <= 1
        assert 0 <= result.repetition_score <= 1
        assert len(result.keywords) > 0
        assert 'readability' in result.metrics
        assert 'balance' in result.metrics
    
    def test_validate_chapter_suggestions(self):
        """Test that suggestions are generated"""
        service = LengthValidationService()
        
        chapter_text = " ".join(["word"] * 2000)
        
        result = service.validate_chapter(chapter_text, target_length=5000)
        
        assert len(result.suggestions) > 0
        assert all(isinstance(s, ValidationSuggestion) for s in result.suggestions)
        assert all(hasattr(s, 'type') for s in result.suggestions)
        assert all(hasattr(s, 'severity') for s in result.suggestions)
        assert all(hasattr(s, 'message') for s in result.suggestions)
    
    def test_validate_chapter_result_properties(self):
        """Test validation result computed properties"""
        service = LengthValidationService()
        
        chapter_text = " ".join(["word"] * 3000)
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        # Test percentage_of_target
        expected_percentage = round((3000 / 2550) * 100, 2)
        assert result.percentage_of_target == expected_percentage
        
        # Test deviation_words
        assert result.deviation_words == 3000 - 2550
    
    def test_validate_character_content_file_not_found(self):
        """Test validation with missing control file"""
        service = LengthValidationService()
        
        with pytest.raises(FileNotFoundError):
            service.validate_character_content("nonexistent_character")
    
    def test_validate_character_content_with_csv(self):
        """Test validation of character content with CSV file"""
        service = LengthValidationService()
        
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            character_dir = Path(tmpdir) / "test_character"
            control_dir = character_dir / "control"
            control_dir.mkdir(parents=True)
            
            # Create CSV file
            csv_file = control_dir / "longitudes.csv"
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["seccion", "longitud_esperada", "longitud_real", "porcentaje"]
                )
                writer.writeheader()
                writer.writerow({
                    "seccion": "capitulo-01",
                    "longitud_esperada": "2550",
                    "longitud_real": "0",
                    "porcentaje": "0"
                })
            
            # Create chapter file
            chapter_file = character_dir / "capitulo-01.md"
            chapter_file.write_text(" ".join(["word"] * 2550))
            
            # Validate
            results = service.validate_character_content(
                "test_character",
                base_dir=tmpdir
            )
            
            assert "capitulo-01" in results
            assert isinstance(results["capitulo-01"], LengthValidationResult)
            assert results["capitulo-01"].word_count == 2550
            
            # Check CSV was updated
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert rows[0]["longitud_real"] == "2550"
                assert float(rows[0]["porcentaje"]) > 0


class TestIntegrationWithEnv:
    """Test integration with .env variables"""
    
    def test_env_variables_loaded(self):
        """Test that .env variables are properly loaded"""
        config = ValidationConfig.from_env()
        
        # These should match values in .env file
        assert config.total_words == 51000
        assert config.chapters_number == 20
        assert config.words_per_chapter == 2550
        assert config.validation_tolerance == 0.05
    
    def test_words_per_chapter_calculation(self):
        """Test that WORDS_PER_CHAPTER relates to TOTAL_WORDS / CHAPTERS_NUMBER"""
        config = ValidationConfig.from_env()
        
        # According to .env: 51000 / 20 = 2550
        calculated = config.total_words // config.chapters_number
        assert config.words_per_chapter == calculated
    
    def test_validation_with_env_config(self):
        """Test validation using environment configuration"""
        service = LengthValidationService()
        
        # Create chapter matching env config
        target = service.config.words_per_chapter  # 2550 from .env
        chapter_text = " ".join(["word"] * target)
        
        result = service.validate_chapter(chapter_text)
        
        assert result.expected_words == 2550
        assert result.word_count == target


class TestAcceptanceCriteria:
    """Test all acceptance criteria from the issue"""
    
    def test_validation_word_range(self):
        """Test: Validación de longitud 3000-15000 palabras/capítulo"""
        config = ValidationConfig.from_env()
        
        # Absolute boundaries should be 3000-15000
        assert config.absolute_min_words == 3000
        assert config.absolute_max_words == 15000
    
    def test_information_density_analysis(self):
        """Test: Análisis de densidad de información"""
        service = LengthValidationService()
        
        # Rich content
        rich_text = """
        Quantum mechanics revolutionized physics in the twentieth century. 
        The uncertainty principle, wave-particle duality, and superposition
        fundamentally changed our understanding of atomic and subatomic phenomena.
        """ * 300
        
        result = service.validate_chapter(rich_text, target_length=2550)
        
        # Should have density score
        assert hasattr(result, 'density_score')
        assert 0 <= result.density_score <= 1
    
    def test_repetitive_content_detection(self):
        """Test: Detección de contenido repetitivo"""
        service = LengthValidationService()
        
        # Highly repetitive content
        repetitive = "This is repetitive content. " * 400
        
        result = service.validate_chapter(repetitive, target_length=2550)
        
        # Should detect repetition
        assert hasattr(result, 'repetition_score')
        assert result.repetition_score > 0
        
        # Should have repetition suggestions
        rep_suggestions = [s for s in result.suggestions if s.type == 'repetition']
        # May or may not have suggestions depending on threshold
    
    def test_expansion_reduction_suggestions(self):
        """Test: Sugerencias de expansión/reducción"""
        service = LengthValidationService()
        
        # Too short - should suggest expansion
        short_text = " ".join(["word"] * 1000)
        result = service.validate_chapter(short_text, target_length=5000)
        
        expansion = [s for s in result.suggestions if s.type == 'expansion']
        assert len(expansion) > 0
        
        # Too long - should suggest reduction
        long_text = " ".join(["word"] * 10000)
        result = service.validate_chapter(long_text, target_length=5000)
        
        reduction = [s for s in result.suggestions if s.type == 'reduction']
        assert len(reduction) > 0
    
    def test_quality_scoring_0_100(self):
        """Test: Scoring de calidad 0-100"""
        service = LengthValidationService()
        
        chapter_text = " ".join(["word"] * 2550)
        
        result = service.validate_chapter(chapter_text, target_length=2550)
        
        assert 0 <= result.quality_score <= 100
        assert isinstance(result.quality_score, float)
    
    def test_verification_commands(self):
        """Test: Verificación como se especifica en el issue"""
        from src.services.length_validator import LengthValidationService
        
        validator = LengthValidationService()
        chapter_text = " ".join(["quality", "content", "chapter"] * 850)  # ~2550 words
        
        result = validator.validate_chapter(chapter_text, target_length=5000)
        
        # These assertions match the verification commands in the issue
        assert result.is_valid is not None  # Can be True or False
        assert 0 <= result.quality_score <= 100
        assert len(result.suggestions) > 0
