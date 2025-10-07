"""
Configuration for length validation service
Reads thresholds and targets from environment variables
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ValidationConfig:
    """Configuration for chapter length validation"""
    
    # Core targets from .env
    total_words: int
    chapters_number: int
    words_per_chapter: int
    validation_tolerance: float
    
    # Quality thresholds
    min_quality_score: float = 70.0
    min_density_score: float = 0.6
    max_repetition_threshold: float = 0.3
    
    # Length boundaries
    absolute_min_words: int = 3000
    absolute_max_words: int = 15000
    
    # Analysis parameters
    ngram_size: int = 5
    max_features_tfidf: int = 1000
    
    @classmethod
    def from_env(cls) -> "ValidationConfig":
        """
        Create configuration from environment variables
        
        Returns:
            ValidationConfig instance with values from .env
        """
        total_words = int(os.getenv('TOTAL_WORDS', '51000'))
        chapters_number = int(os.getenv('CHAPTERS_NUMBER', '20'))
        words_per_chapter = int(os.getenv('WORDS_PER_CHAPTER', '2550'))
        validation_tolerance = float(os.getenv('VALIDATION_TOLERANCE', '0.05'))
        
        return cls(
            total_words=total_words,
            chapters_number=chapters_number,
            words_per_chapter=words_per_chapter,
            validation_tolerance=validation_tolerance
        )
    
    def get_target_range(self, section_type: str = "chapter") -> tuple[int, int]:
        """
        Get acceptable word count range for a section
        
        Args:
            section_type: Type of section (chapter, prologue, etc.)
            
        Returns:
            Tuple of (min_words, max_words)
        """
        if section_type == "chapter":
            target = self.words_per_chapter
        else:
            # Special sections might have different targets
            target = self.words_per_chapter
        
        tolerance_words = int(target * self.validation_tolerance)
        min_words = max(target - tolerance_words, self.absolute_min_words)
        max_words = min(target + tolerance_words, self.absolute_max_words)
        
        return (min_words, max_words)
    
    def is_within_tolerance(self, actual_words: int, expected_words: Optional[int] = None) -> bool:
        """
        Check if word count is within acceptable tolerance
        
        Args:
            actual_words: Actual word count
            expected_words: Expected word count (defaults to words_per_chapter)
            
        Returns:
            True if within tolerance
        """
        if expected_words is None:
            expected_words = self.words_per_chapter
        
        min_allowed = expected_words * (1 - self.validation_tolerance)
        max_allowed = expected_words * (1 + self.validation_tolerance)
        
        return min_allowed <= actual_words <= max_allowed
    
    def calculate_length_score(self, actual_words: int, expected_words: Optional[int] = None) -> float:
        """
        Calculate length compliance score (0-100)
        
        Args:
            actual_words: Actual word count
            expected_words: Expected word count (defaults to words_per_chapter)
            
        Returns:
            Score from 0 to 100
        """
        if expected_words is None:
            expected_words = self.words_per_chapter
        
        if expected_words == 0:
            return 0.0
        
        ratio = actual_words / expected_words
        
        # Perfect score at 100% compliance
        if 0.95 <= ratio <= 1.05:
            return 100.0
        
        # Within tolerance gets 80-100 points
        if self.is_within_tolerance(actual_words, expected_words):
            deviation = abs(ratio - 1.0)
            # Linear scale from 100 (perfect) to 80 (edge of tolerance)
            return 100.0 - (deviation / self.validation_tolerance) * 20.0
        
        # Outside tolerance gets 0-80 points based on severity
        if ratio < (1 - self.validation_tolerance):
            # Too short
            deviation = (1 - self.validation_tolerance) - ratio
            return max(0.0, 80.0 - deviation * 100.0)
        else:
            # Too long
            deviation = ratio - (1 + self.validation_tolerance)
            return max(0.0, 80.0 - deviation * 100.0)
