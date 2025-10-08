"""
Pydantic models for cross-validation system
Data models for cross-validation, fact checking, and source triangulation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RedundancyAnalysis(BaseModel):
    """Analysis of information redundancy across sources"""
    redundancy_percentage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall redundancy level (0-1)"
    )
    unique_information_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of unique information (0-1)"
    )
    overlapping_facts: int = Field(
        default=0,
        ge=0,
        description="Number of overlapping facts found"
    )
    unique_facts: int = Field(
        default=0,
        ge=0,
        description="Number of unique facts found"
    )
    details: Optional[str] = Field(
        default=None,
        description="Details about redundancy patterns"
    )


class AcademicStandards(BaseModel):
    """Analysis of academic standards compliance"""
    compliance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall academic compliance score (0-1)"
    )
    citation_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Quality of citations (0-100)"
    )
    peer_reviewed_sources: int = Field(
        default=0,
        ge=0,
        description="Number of peer-reviewed sources"
    )
    primary_sources: int = Field(
        default=0,
        ge=0,
        description="Number of primary sources"
    )
    academic_credibility: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Academic credibility score (0-100)"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="Academic standards issues found"
    )


class ValidationResult(BaseModel):
    """Comprehensive cross-validation result"""
    consistency_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Factual consistency score across sources (0-1)"
    )
    temporal_coverage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Temporal coverage score (0-1)"
    )
    diversity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Source diversity score (0-1)"
    )
    redundancy_level: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Information redundancy level (0-1)"
    )
    academic_compliance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Academic standards compliance (0-1)"
    )
    overall_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall quality score (0-1)"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata from validation"
    )


class KeyFact(BaseModel):
    """A key fact extracted from a source"""
    fact: str = Field(..., description="The factual statement")
    source_index: int = Field(..., description="Index of the source")
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in fact extraction (0-1)"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of the fact (date, event, relationship, etc.)"
    )


class TemporalCoverage(BaseModel):
    """Analysis of temporal coverage across sources"""
    coverage_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall temporal coverage (0-1)"
    )
    early_life: bool = Field(default=False, description="Coverage of early life")
    career: bool = Field(default=False, description="Coverage of career")
    later_years: bool = Field(default=False, description="Coverage of later years")
    legacy: bool = Field(default=False, description="Coverage of legacy")
    gaps: List[str] = Field(
        default_factory=list,
        description="Identified temporal gaps"
    )
