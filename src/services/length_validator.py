"""
Intelligent chapter length validation service with semantic analysis
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ..config.validation_config import ValidationConfig
from ..utils.text_analyzer import TextAnalyzer


logger = logging.getLogger(__name__)


@dataclass
class ValidationSuggestion:
    """Suggestion for improving content"""
    type: str  # 'expansion', 'reduction', 'improvement'
    priority: str  # 'high', 'medium', 'low'
    message: str
    details: Optional[str] = None


@dataclass
class LengthValidationResult:
    """Result of chapter length validation"""
    is_valid: bool
    word_count: int
    target_length: int
    quality_score: float
    
    # Component scores
    length_score: float
    density_score: float
    repetition_score: float
    vocabulary_score: float
    
    # Analysis details
    information_density: float
    repetition_ratio: float
    vocabulary_richness: float
    
    # Suggestions
    suggestions: List[ValidationSuggestion] = field(default_factory=list)
    
    # Additional details
    details: Dict[str, Any] = field(default_factory=dict)


class LengthValidationService:
    """Service for intelligent chapter length validation"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize length validation service
        
        Args:
            config: Validation configuration (uses default if not provided)
        """
        self.config = config or ValidationConfig()
        self.text_analyzer = TextAnalyzer()
    
    def validate_chapter(
        self,
        chapter_text: str,
        target_length: Optional[int] = None
    ) -> LengthValidationResult:
        """
        Validate chapter length and quality
        
        Args:
            chapter_text: Chapter text to validate
            target_length: Target word count (uses default if not provided)
            
        Returns:
            LengthValidationResult with validation details
        """
        # Use default target if not provided
        if target_length is None:
            target_length = self.config.TARGET_CHAPTER_LENGTH
        
        # Count words
        word_count = self.text_analyzer.count_words(chapter_text)
        
        # Calculate individual component scores
        length_score = self._calculate_length_score(word_count, target_length)
        density_score = self._calculate_density_score(chapter_text)
        repetition_score = self._calculate_repetition_score(chapter_text)
        vocabulary_score = self._calculate_vocabulary_score(chapter_text)
        
        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(
            length_score,
            density_score,
            repetition_score,
            vocabulary_score
        )
        
        # Determine if valid
        min_length, max_length = self.config.get_length_range(target_length)
        is_valid = (
            min_length <= word_count <= max_length and
            quality_score >= 60.0  # Minimum acceptable quality
        )
        
        # Get detailed analysis
        repetition_analysis = self.text_analyzer.detect_repetitive_content(
            chapter_text,
            self.config.NGRAM_SIZE_MIN,
            self.config.NGRAM_SIZE_MAX,
            self.config.REPETITION_MIN_OCCURRENCES
        )
        
        information_density = self.text_analyzer.calculate_information_density(chapter_text)
        vocabulary_richness = self.text_analyzer.calculate_vocabulary_richness(chapter_text)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            word_count=word_count,
            target_length=target_length,
            quality_score=quality_score,
            information_density=information_density,
            repetition_ratio=repetition_analysis['repetition_ratio'],
            vocabulary_richness=vocabulary_richness,
            repetitive_ngrams=repetition_analysis['repetitive_ngrams']
        )
        
        # Get additional statistics
        content_stats = self.text_analyzer.get_content_statistics(chapter_text)
        sentence_analysis = self.text_analyzer.analyze_sentence_structure(chapter_text)
        key_terms = self.text_analyzer.extract_key_terms(chapter_text, top_n=5)
        
        return LengthValidationResult(
            is_valid=is_valid,
            word_count=word_count,
            target_length=target_length,
            quality_score=quality_score,
            length_score=length_score,
            density_score=density_score,
            repetition_score=repetition_score,
            vocabulary_score=vocabulary_score,
            information_density=information_density,
            repetition_ratio=repetition_analysis['repetition_ratio'],
            vocabulary_richness=vocabulary_richness,
            suggestions=suggestions,
            details={
                'length_range': (min_length, max_length),
                'content_statistics': content_stats,
                'sentence_analysis': sentence_analysis,
                'key_terms': key_terms,
                'repetitive_ngrams': repetition_analysis['repetitive_ngrams'][:5]
            }
        )
    
    def _calculate_length_score(self, word_count: int, target_length: int) -> float:
        """
        Calculate score based on length compliance
        
        Args:
            word_count: Actual word count
            target_length: Target word count
            
        Returns:
            Score from 0 to 100
        """
        min_length, max_length = self.config.get_length_range(target_length)
        
        # Perfect score if within tolerance
        if min_length <= word_count <= max_length:
            # Even better score if very close to target
            deviation = abs(word_count - target_length)
            max_deviation = target_length * self.config.LENGTH_TOLERANCE
            if max_deviation > 0:
                return 100 - (deviation / max_deviation * 10)
            return 100.0
        
        # Penalty for being outside range
        if word_count < min_length:
            # Too short
            deficit = min_length - word_count
            penalty = min(deficit / min_length * 100, 100)
            return max(0, 100 - penalty)
        else:
            # Too long
            excess = word_count - max_length
            penalty = min(excess / max_length * 100, 100)
            return max(0, 100 - penalty)
    
    def _calculate_density_score(self, text: str) -> float:
        """
        Calculate score based on information density
        
        Args:
            text: Text to analyze
            
        Returns:
            Score from 0 to 100
        """
        density = self.text_analyzer.calculate_information_density(text)
        
        # Score based on proximity to optimal density
        optimal = self.config.OPTIMAL_INFORMATION_DENSITY
        min_density = self.config.MIN_INFORMATION_DENSITY
        
        if density >= optimal:
            # At or above optimal - excellent
            return 100.0
        elif density >= min_density:
            # Between minimum and optimal - scale linearly
            range_size = optimal - min_density
            score_range = 100 - 60  # 60-100 range
            return 60 + (density - min_density) / range_size * score_range
        else:
            # Below minimum - poor quality
            if min_density > 0:
                return (density / min_density) * 60
            return 0.0
    
    def _calculate_repetition_score(self, text: str) -> float:
        """
        Calculate score based on content repetition
        
        Args:
            text: Text to analyze
            
        Returns:
            Score from 0 to 100
        """
        repetition_analysis = self.text_analyzer.detect_repetitive_content(
            text,
            self.config.NGRAM_SIZE_MIN,
            self.config.NGRAM_SIZE_MAX,
            self.config.REPETITION_MIN_OCCURRENCES
        )
        
        repetition_ratio = repetition_analysis['repetition_ratio']
        max_acceptable = self.config.MAX_ACCEPTABLE_REPETITION_RATIO
        
        # Perfect score if no or minimal repetition
        if repetition_ratio <= max_acceptable:
            # Better score for less repetition
            return 100 - (repetition_ratio / max_acceptable * 10)
        
        # Penalty for excessive repetition
        excess = repetition_ratio - max_acceptable
        penalty = min(excess / max_acceptable * 100, 100)
        return max(0, 90 - penalty)
    
    def _calculate_vocabulary_score(self, text: str) -> float:
        """
        Calculate score based on vocabulary richness
        
        Args:
            text: Text to analyze
            
        Returns:
            Score from 0 to 100
        """
        richness = self.text_analyzer.calculate_vocabulary_richness(text)
        
        optimal = self.config.OPTIMAL_UNIQUE_WORDS_RATIO
        min_ratio = self.config.MIN_UNIQUE_WORDS_RATIO
        
        if richness >= optimal:
            # At or above optimal - excellent
            return 100.0
        elif richness >= min_ratio:
            # Between minimum and optimal - scale linearly
            range_size = optimal - min_ratio
            score_range = 100 - 60  # 60-100 range
            return 60 + (richness - min_ratio) / range_size * score_range
        else:
            # Below minimum - poor vocabulary
            if min_ratio > 0:
                return (richness / min_ratio) * 60
            return 0.0
    
    def _calculate_quality_score(
        self,
        length_score: float,
        density_score: float,
        repetition_score: float,
        vocabulary_score: float
    ) -> float:
        """
        Calculate overall quality score using weighted average
        
        Args:
            length_score: Score for length compliance
            density_score: Score for information density
            repetition_score: Score for lack of repetition
            vocabulary_score: Score for vocabulary richness
            
        Returns:
            Overall quality score from 0 to 100
        """
        quality = (
            length_score * self.config.WEIGHT_LENGTH_COMPLIANCE +
            density_score * self.config.WEIGHT_INFORMATION_DENSITY +
            repetition_score * self.config.WEIGHT_REPETITION_SCORE +
            vocabulary_score * self.config.WEIGHT_VOCABULARY_RICHNESS
        )
        
        return round(quality, 2)
    
    def _generate_suggestions(
        self,
        word_count: int,
        target_length: int,
        quality_score: float,
        information_density: float,
        repetition_ratio: float,
        vocabulary_richness: float,
        repetitive_ngrams: List[Dict]
    ) -> List[ValidationSuggestion]:
        """
        Generate suggestions for improving content
        
        Args:
            word_count: Current word count
            target_length: Target word count
            quality_score: Overall quality score
            information_density: Information density score
            repetition_ratio: Repetition ratio
            vocabulary_richness: Vocabulary richness score
            repetitive_ngrams: List of repetitive n-grams
            
        Returns:
            List of suggestions
        """
        suggestions = []
        min_length, max_length = self.config.get_length_range(target_length)
        
        # Length-based suggestions
        if word_count < min_length:
            deficit = min_length - word_count
            suggestions.append(ValidationSuggestion(
                type='expansion',
                priority='high',
                message=f'Chapter is {deficit} words too short',
                details=f'Current: {word_count} words. Target range: {min_length}-{max_length} words. '
                       f'Consider adding more examples, explanations, or details to reach the target.'
            ))
        elif word_count > max_length:
            excess = word_count - max_length
            suggestions.append(ValidationSuggestion(
                type='reduction',
                priority='high',
                message=f'Chapter is {excess} words too long',
                details=f'Current: {word_count} words. Target range: {min_length}-{max_length} words. '
                       f'Consider condensing content, removing redundancies, or splitting into multiple chapters.'
            ))
        else:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='low',
                message='Chapter length is within acceptable range',
                details=f'Current: {word_count} words. Target: {target_length} words.'
            ))
        
        # Information density suggestions
        if information_density < self.config.MIN_INFORMATION_DENSITY:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='high',
                message='Low information density detected',
                details=f'Density score: {information_density:.2f}. Add more specific details, facts, '
                       f'or unique insights to improve content quality.'
            ))
        elif information_density < self.config.OPTIMAL_INFORMATION_DENSITY:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='medium',
                message='Information density could be improved',
                details=f'Density score: {information_density:.2f}. Consider adding more substantive '
                       f'content to increase information value.'
            ))
        
        # Repetition suggestions
        if repetition_ratio > self.config.MAX_ACCEPTABLE_REPETITION_RATIO:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='high',
                message=f'High content repetition detected ({repetition_ratio:.1%})',
                details='Review and remove repetitive phrases. Vary sentence structure and word choice.'
            ))
            
            # Add specific repetitive phrases
            if repetitive_ngrams:
                top_repetitions = ', '.join([
                    f'"{ng["ngram"]}" ({ng["occurrences"]}x)'
                    for ng in repetitive_ngrams[:3]
                ])
                suggestions.append(ValidationSuggestion(
                    type='improvement',
                    priority='medium',
                    message='Specific repetitive phrases found',
                    details=f'Most repeated: {top_repetitions}'
                ))
        
        # Vocabulary suggestions
        if vocabulary_richness < self.config.MIN_UNIQUE_WORDS_RATIO:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='high',
                message=f'Low vocabulary richness ({vocabulary_richness:.1%})',
                details='Use more varied vocabulary and synonyms to improve readability and engagement.'
            ))
        elif vocabulary_richness < self.config.OPTIMAL_UNIQUE_WORDS_RATIO:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='medium',
                message='Vocabulary richness could be improved',
                details=f'Richness: {vocabulary_richness:.1%}. Consider using more diverse vocabulary.'
            ))
        
        # Overall quality suggestion
        if quality_score < 60:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='high',
                message=f'Overall quality score is low ({quality_score:.1f}/100)',
                details='Review all suggestions above to improve chapter quality.'
            ))
        elif quality_score < 80:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='medium',
                message=f'Quality score is acceptable but could be improved ({quality_score:.1f}/100)',
                details='Address the suggestions above to achieve excellent quality.'
            ))
        else:
            suggestions.append(ValidationSuggestion(
                type='improvement',
                priority='low',
                message=f'Excellent quality score ({quality_score:.1f}/100)',
                details='Chapter meets high quality standards. Minor improvements may still be possible.'
            ))
        
        return suggestions
