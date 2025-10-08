"""
Quality metrics data models for feedback system
Data models for tracking quality patterns and improvement metrics
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class BiographyQualityScore(BaseModel):
    """Quality score for a generated biography"""
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall biography quality score (0-100)"
    )
    content_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Content quality score (0-100)"
    )
    factual_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Factual accuracy score (0-100)"
    )
    source_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Source quality score (0-100)"
    )
    coherence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Narrative coherence score (0-100)"
    )
    completeness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Biographical completeness score (0-100)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional quality metadata"
    )


class SuccessPattern(BaseModel):
    """Pattern identified in successful generations"""
    pattern_type: str = Field(
        ...,
        description="Type of pattern (e.g., 'domain', 'source_type', 'content_feature')"
    )
    pattern_value: str = Field(
        ...,
        description="Value of the pattern (e.g., 'stanford.edu', 'academic', 'primary_source')"
    )
    frequency: int = Field(
        default=1,
        ge=1,
        description="Number of times this pattern appeared in successful cases"
    )
    avg_quality_impact: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Average quality score when this pattern is present"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this pattern (0-1)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional pattern metadata"
    )


class SuccessCase(BaseModel):
    """Successful generation case for learning"""
    character: str = Field(
        ...,
        description="Character name"
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall quality score achieved"
    )
    source_count: int = Field(
        default=0,
        ge=0,
        description="Number of sources used"
    )
    patterns: List[SuccessPattern] = Field(
        default_factory=list,
        description="Patterns identified in this success case"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this case was recorded"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional case metadata"
    )


class ImprovementMetrics(BaseModel):
    """Metrics tracking system improvement over time"""
    total_generations: int = Field(
        default=0,
        ge=0,
        description="Total number of generations tracked"
    )
    avg_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Average quality score across all generations"
    )
    quality_trend: float = Field(
        default=0.0,
        description="Quality trend (positive = improving, negative = declining)"
    )
    success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Rate of successful generations (quality >= 85)"
    )
    patterns_identified: int = Field(
        default=0,
        ge=0,
        description="Number of success patterns identified"
    )
    most_effective_patterns: List[SuccessPattern] = Field(
        default_factory=list,
        description="Most effective patterns identified"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When these metrics were calculated"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metrics metadata"
    )


class QualityWeights(BaseModel):
    """Weights for quality scoring components"""
    domain_authority: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Weight for domain authority (0-1)"
    )
    content_quality: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Weight for content quality (0-1)"
    )
    source_type: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for source type (0-1)"
    )
    recency: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Weight for source recency (0-1)"
    )
    citations: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Weight for citations and references (0-1)"
    )
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0"""
        total = (
            self.domain_authority +
            self.content_quality +
            self.source_type +
            self.recency +
            self.citations
        )
        return abs(total - 1.0) < 0.01
    
    def normalize(self):
        """Normalize weights to sum to 1.0"""
        total = (
            self.domain_authority +
            self.content_quality +
            self.source_type +
            self.recency +
            self.citations
        )
        if total > 0:
            self.domain_authority /= total
            self.content_quality /= total
            self.source_type /= total
            self.recency /= total
            self.citations /= total
