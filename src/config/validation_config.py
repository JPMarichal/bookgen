"""
Configuration for chapter length validation service
"""
from typing import Dict, Any


class ValidationConfig:
    """Configuration for chapter length validation"""
    
    # Length thresholds (in words)
    MIN_CHAPTER_LENGTH = 3000
    MAX_CHAPTER_LENGTH = 15000
    TARGET_CHAPTER_LENGTH = 5000
    
    # Tolerance percentage (±5%)
    LENGTH_TOLERANCE = 0.05
    
    # Quality scoring thresholds
    MIN_QUALITY_SCORE = 0
    MAX_QUALITY_SCORE = 100
    
    # Information density thresholds
    MIN_INFORMATION_DENSITY = 0.3  # Minimum TF-IDF score for good content
    OPTIMAL_INFORMATION_DENSITY = 0.6  # Optimal TF-IDF score
    
    # Repetition detection thresholds
    MAX_ACCEPTABLE_REPETITION_RATIO = 0.15  # Max 15% repetitive content
    NGRAM_SIZE_MIN = 3  # Minimum n-gram size for repetition detection
    NGRAM_SIZE_MAX = 7  # Maximum n-gram size for repetition detection
    REPETITION_MIN_OCCURRENCES = 3  # Minimum occurrences to consider as repetitive
    
    # Content variety thresholds
    MIN_UNIQUE_WORDS_RATIO = 0.3  # Minimum 30% unique words
    OPTIMAL_UNIQUE_WORDS_RATIO = 0.5  # Optimal 50% unique words
    
    # Scoring weights (must sum to 1.0)
    WEIGHT_LENGTH_COMPLIANCE = 0.25
    WEIGHT_INFORMATION_DENSITY = 0.30
    WEIGHT_REPETITION_SCORE = 0.25
    WEIGHT_VOCABULARY_RICHNESS = 0.20
    
    @classmethod
    def get_length_range(cls, target_length: int = None) -> tuple:
        """
        Get valid length range for a chapter
        
        Args:
            target_length: Target length in words (optional)
            
        Returns:
            Tuple of (min_length, max_length)
        """
        if target_length is None:
            target_length = cls.TARGET_CHAPTER_LENGTH
        
        tolerance = int(target_length * cls.LENGTH_TOLERANCE)
        min_length = max(cls.MIN_CHAPTER_LENGTH, target_length - tolerance)
        max_length = min(cls.MAX_CHAPTER_LENGTH, target_length + tolerance)
        
        return (min_length, max_length)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """
        Get configuration as dictionary
        
        Returns:
            Dictionary with all configuration values
        """
        return {
            'min_chapter_length': cls.MIN_CHAPTER_LENGTH,
            'max_chapter_length': cls.MAX_CHAPTER_LENGTH,
            'target_chapter_length': cls.TARGET_CHAPTER_LENGTH,
            'length_tolerance': cls.LENGTH_TOLERANCE,
            'min_information_density': cls.MIN_INFORMATION_DENSITY,
            'optimal_information_density': cls.OPTIMAL_INFORMATION_DENSITY,
            'max_acceptable_repetition_ratio': cls.MAX_ACCEPTABLE_REPETITION_RATIO,
            'min_unique_words_ratio': cls.MIN_UNIQUE_WORDS_RATIO,
            'optimal_unique_words_ratio': cls.OPTIMAL_UNIQUE_WORDS_RATIO,
            'scoring_weights': {
                'length_compliance': cls.WEIGHT_LENGTH_COMPLIANCE,
                'information_density': cls.WEIGHT_INFORMATION_DENSITY,
                'repetition_score': cls.WEIGHT_REPETITION_SCORE,
                'vocabulary_richness': cls.WEIGHT_VOCABULARY_RICHNESS
            }
        }
