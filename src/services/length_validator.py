"""
Intelligent chapter length validation service
Migrates and enhances functionality from check_lengths.py
"""
import os
import csv
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

from src.config.validation_config import ValidationConfig
from src.utils.text_analyzer import TextAnalyzer


@dataclass
class ValidationSuggestion:
    """A suggestion for improving chapter content"""
    type: str  # 'expansion', 'reduction', 'quality', 'repetition'
    severity: str  # 'critical', 'warning', 'info'
    message: str
    details: Optional[str] = None


@dataclass
class LengthValidationResult:
    """Result of chapter length validation"""
    is_valid: bool
    word_count: int
    expected_words: int
    target_min: int
    target_max: int
    quality_score: float  # 0-100
    length_score: float  # 0-100
    density_score: float  # 0-1
    repetition_score: float  # 0-1
    suggestions: List[ValidationSuggestion]
    keywords: List[tuple]  # Top keywords from content
    metrics: Dict[str, any]  # Additional metrics
    
    @property
    def percentage_of_target(self) -> float:
        """Calculate percentage of expected word count"""
        if self.expected_words == 0:
            return 0.0
        return round((self.word_count / self.expected_words) * 100, 2)
    
    @property
    def deviation_words(self) -> int:
        """Words above or below target (negative = too short)"""
        return self.word_count - self.expected_words


class LengthValidationService:
    """Service for intelligent chapter length validation"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize validation service
        
        Args:
            config: Validation configuration (defaults to loading from .env)
        """
        self.config = config or ValidationConfig.from_env()
        self.text_analyzer = TextAnalyzer(
            max_features=self.config.max_features_tfidf,
            ngram_size=self.config.ngram_size
        )
    
    def validate_chapter(
        self,
        chapter_text: str,
        target_length: Optional[int] = None,
        section_type: str = "chapter"
    ) -> LengthValidationResult:
        """
        Validate a chapter with intelligent analysis
        
        Args:
            chapter_text: The chapter text to validate
            target_length: Expected word count (defaults to config.words_per_chapter)
            section_type: Type of section for context
            
        Returns:
            LengthValidationResult with comprehensive analysis
        """
        # Use configured target if not specified
        if target_length is None:
            target_length = self.config.words_per_chapter
        
        # Get acceptable range
        target_min, target_max = self.config.get_target_range(section_type)
        
        # Count words
        word_count = self.text_analyzer.count_words(chapter_text)
        
        # Calculate length score
        length_score = self.config.calculate_length_score(word_count, target_length)
        
        # Analyze information density
        density_score = self.text_analyzer.calculate_information_density(chapter_text)
        
        # Detect repetition
        repetition_metrics = self.text_analyzer.detect_repetitive_content(chapter_text)
        repetition_score = repetition_metrics['repetition_score']
        
        # Extract keywords
        keywords = self.text_analyzer.extract_keywords(chapter_text, top_n=10)
        
        # Get readability metrics
        readability = self.text_analyzer.calculate_readability_metrics(chapter_text)
        
        # Get content balance
        balance = self.text_analyzer.analyze_content_balance(chapter_text)
        
        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(
            length_score=length_score,
            density_score=density_score,
            repetition_score=repetition_score,
            readability=readability,
            balance=balance
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            word_count=word_count,
            target_length=target_length,
            target_min=target_min,
            target_max=target_max,
            density_score=density_score,
            repetition_metrics=repetition_metrics,
            readability=readability,
            balance=balance,
            quality_score=quality_score
        )
        
        # Determine if valid
        is_valid = (
            target_min <= word_count <= target_max and
            quality_score >= self.config.min_quality_score
        )
        
        # Compile metrics
        metrics = {
            'readability': readability,
            'balance': balance,
            'repetition': repetition_metrics
        }
        
        return LengthValidationResult(
            is_valid=is_valid,
            word_count=word_count,
            expected_words=target_length,
            target_min=target_min,
            target_max=target_max,
            quality_score=quality_score,
            length_score=length_score,
            density_score=density_score,
            repetition_score=repetition_score,
            suggestions=suggestions,
            keywords=keywords,
            metrics=metrics
        )
    
    def validate_character_content(
        self,
        character_name: str,
        base_dir: str = "bios"
    ) -> Dict[str, LengthValidationResult]:
        """
        Validate all content for a character (migrates check_lengths.py functionality)
        
        Args:
            character_name: Name of the character
            base_dir: Base directory for biographies
            
        Returns:
            Dictionary mapping section names to validation results
        """
        character_dir = Path(base_dir) / character_name
        control_dir = character_dir / "control"
        csv_file = control_dir / "longitudes.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(
                f"Control file not found: {csv_file}. "
                "Must be generated during planning phase."
            )
        
        # Read CSV file
        results = {}
        rows = []
        
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        
        # Validate each section
        for row in rows:
            section_name = row["seccion"]
            expected_length = int(row["longitud_esperada"])
            file_path = character_dir / f"{section_name}.md"
            
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                
                # Validate the section
                result = self.validate_chapter(
                    chapter_text=text,
                    target_length=expected_length,
                    section_type="chapter" if "capitulo" in section_name else "special"
                )
                
                results[section_name] = result
                
                # Update CSV row with new data
                row["longitud_real"] = str(result.word_count)
                row["porcentaje"] = str(result.percentage_of_target)
            else:
                # File doesn't exist
                row["longitud_real"] = "0"
                row["porcentaje"] = "0.0"
        
        # Write updated CSV
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["seccion", "longitud_esperada", "longitud_real", "porcentaje"]
            )
            writer.writeheader()
            writer.writerows(rows)
        
        return results
    
    def _calculate_quality_score(
        self,
        length_score: float,
        density_score: float,
        repetition_score: float,
        readability: Dict[str, float],
        balance: Dict[str, any]
    ) -> float:
        """
        Calculate overall quality score (0-100)
        
        Weights:
        - Length compliance: 35%
        - Information density: 30%
        - Repetition (inverse): 20%
        - Content balance: 15%
        
        Args:
            length_score: Score from length compliance (0-100)
            density_score: Information density (0-1)
            repetition_score: Repetition score (0-1, higher = more repetitive)
            readability: Readability metrics
            balance: Content balance metrics
            
        Returns:
            Quality score (0-100)
        """
        # Weight components
        length_component = length_score * 0.35
        density_component = (density_score * 100) * 0.30
        
        # Repetition: lower is better, so invert
        repetition_component = ((1.0 - repetition_score) * 100) * 0.20
        
        # Balance: give full points if balanced, partial otherwise
        balance_component = (100 if balance.get('is_balanced', True) else 60) * 0.15
        
        total_score = (
            length_component +
            density_component +
            repetition_component +
            balance_component
        )
        
        return round(min(max(total_score, 0.0), 100.0), 2)
    
    def _generate_suggestions(
        self,
        word_count: int,
        target_length: int,
        target_min: int,
        target_max: int,
        density_score: float,
        repetition_metrics: Dict[str, any],
        readability: Dict[str, float],
        balance: Dict[str, any],
        quality_score: float
    ) -> List[ValidationSuggestion]:
        """
        Generate context-aware suggestions for improvement
        
        Args:
            word_count: Actual word count
            target_length: Target word count
            target_min: Minimum acceptable words
            target_max: Maximum acceptable words
            density_score: Information density score
            repetition_metrics: Repetition analysis results
            readability: Readability metrics
            balance: Content balance metrics
            quality_score: Overall quality score
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Length suggestions
        if word_count < target_min:
            shortage = target_min - word_count
            severity = 'critical' if shortage > 1000 else 'warning'
            suggestions.append(ValidationSuggestion(
                type='expansion',
                severity=severity,
                message=f'Chapter is {shortage} words short of minimum ({target_min} words)',
                details=f'Consider adding more details, examples, or expanding existing sections. '
                       f'Target: {target_length} words, Current: {word_count} words.'
            ))
        elif word_count > target_max:
            excess = word_count - target_max
            severity = 'critical' if excess > 1000 else 'warning'
            suggestions.append(ValidationSuggestion(
                type='reduction',
                severity=severity,
                message=f'Chapter is {excess} words over maximum ({target_max} words)',
                details=f'Consider condensing repetitive sections or removing tangential content. '
                       f'Target: {target_length} words, Current: {word_count} words.'
            ))
        else:
            # Within range
            suggestions.append(ValidationSuggestion(
                type='expansion',
                severity='info',
                message=f'Word count is within acceptable range ({word_count}/{target_length} words)',
                details=f'Current completion: {round((word_count/target_length)*100, 1)}%'
            ))
        
        # Density suggestions
        if density_score < self.config.min_density_score:
            suggestions.append(ValidationSuggestion(
                type='quality',
                severity='warning',
                message=f'Low information density ({density_score:.2f})',
                details='Content may be repetitive or lack substance. '
                       'Add more unique information, facts, or insights.'
            ))
        
        # Repetition suggestions
        if repetition_metrics['repetition_score'] > self.config.max_repetition_threshold:
            most_repeated = repetition_metrics.get('most_repeated_ngram', 'N/A')
            count = repetition_metrics.get('repetition_count', 0)
            suggestions.append(ValidationSuggestion(
                type='repetition',
                severity='warning',
                message=f'High repetition detected ({repetition_metrics["repetition_score"]:.2f})',
                details=f'Most repeated phrase appears {count} times. '
                       f'Consider varying sentence structure and word choice.'
            ))
        
        # Balance suggestions
        if not balance.get('is_balanced', True):
            dialogue_ratio = balance.get('dialogue_ratio', 0.0)
            if dialogue_ratio < 0.1:
                suggestions.append(ValidationSuggestion(
                    type='quality',
                    severity='info',
                    message='Very little dialogue detected',
                    details='Consider adding dialogue to make the content more engaging.'
                ))
            elif dialogue_ratio > 0.7:
                suggestions.append(ValidationSuggestion(
                    type='quality',
                    severity='info',
                    message='High dialogue ratio detected',
                    details='Consider balancing with more narrative or descriptive content.'
                ))
        
        # Overall quality suggestion
        if quality_score < self.config.min_quality_score:
            suggestions.append(ValidationSuggestion(
                type='quality',
                severity='critical',
                message=f'Quality score below threshold ({quality_score:.1f}/{self.config.min_quality_score})',
                details='Chapter needs improvement in multiple areas. Review all suggestions above.'
            ))
        
        return suggestions
