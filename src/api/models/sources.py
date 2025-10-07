"""
Pydantic models for source validation endpoints
"""
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SourceType(str, Enum):
    """Type of source"""
    URL = "url"
    BOOK = "book"
    ARTICLE = "article"
    DOCUMENT = "document"
    OTHER = "other"


class SourceItem(BaseModel):
    """Individual source item"""
    url: Optional[str] = Field(default=None, description="Source URL if applicable")
    title: str = Field(..., min_length=1, description="Source title")
    author: Optional[str] = Field(default=None, description="Source author")
    publication_date: Optional[str] = Field(default=None, description="Publication date")
    source_type: SourceType = Field(default=SourceType.OTHER, description="Type of source")
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided"""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class SourceValidationRequest(BaseModel):
    """Request model for source validation"""
    sources: List[SourceItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of sources to validate"
    )
    check_accessibility: bool = Field(
        default=True,
        description="Whether to check if URLs are accessible"
    )


class SourceValidationResult(BaseModel):
    """Validation result for a single source"""
    source: SourceItem
    is_valid: bool = Field(..., description="Whether the source is valid")
    is_accessible: Optional[bool] = Field(
        default=None,
        description="Whether the URL is accessible (for URL sources)"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of validation issues"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata extracted from source"
    )


class SourceValidationResponse(BaseModel):
    """Response model for source validation"""
    total_sources: int = Field(..., description="Total number of sources validated")
    valid_sources: int = Field(..., description="Number of valid sources")
    invalid_sources: int = Field(..., description="Number of invalid sources")
    results: List[SourceValidationResult] = Field(
        ...,
        description="Detailed validation results for each source"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary statistics"
    )


# Advanced validation models
class AdvancedSourceValidationRequest(BaseModel):
    """Request model for advanced source validation with AI analysis"""
    sources: List[SourceItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of sources to validate"
    )
    biography_topic: str = Field(
        ...,
        min_length=1,
        description="Biography topic or character name for relevance analysis"
    )
    check_accessibility: bool = Field(
        default=True,
        description="Whether to check if URLs are accessible"
    )
    min_relevance: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score threshold (0-1)"
    )
    min_credibility: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Minimum credibility score threshold (0-100)"
    )


class AdvancedSourceValidationResult(BaseModel):
    """Advanced validation result for a single source"""
    source: SourceItem
    is_valid: bool = Field(..., description="Whether the source is valid")
    is_accessible: Optional[bool] = Field(
        default=None,
        description="Whether the URL is accessible"
    )
    relevance_score: Optional[float] = Field(
        default=None,
        description="Relevance score based on TF-IDF analysis (0-1)"
    )
    credibility_score: Optional[float] = Field(
        default=None,
        description="Credibility score (0-100)"
    )
    domain_category: Optional[str] = Field(
        default=None,
        description="Category of the domain (academic, government, etc.)"
    )
    is_trusted: Optional[bool] = Field(
        default=None,
        description="Whether the domain is in the trusted list"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of validation issues"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )


class AdvancedSourceValidationResponse(BaseModel):
    """Response model for advanced source validation"""
    total_sources: int = Field(..., description="Total number of sources validated")
    valid_sources: int = Field(..., description="Number of valid sources")
    invalid_sources: int = Field(..., description="Number of invalid sources")
    rejected_sources: int = Field(
        default=0,
        description="Number of sources rejected due to low relevance or credibility"
    )
    average_relevance: float = Field(
        default=0.0,
        description="Average relevance score across all sources"
    )
    average_credibility: float = Field(
        default=0.0,
        description="Average credibility score across all sources"
    )
    results: List[AdvancedSourceValidationResult] = Field(
        ...,
        description="Detailed validation results for each source"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improving source quality"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary statistics"
    )
