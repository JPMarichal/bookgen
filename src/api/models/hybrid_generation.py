"""
Pydantic models for hybrid source generation (automatic + manual)
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from .sources import SourceItem


class SuggestionItem(BaseModel):
    """Intelligent suggestion for additional sources"""
    suggested_source: SourceItem = Field(
        ...,
        description="The suggested source"
    )
    reason: str = Field(
        ...,
        description="Why this source is suggested"
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How relevant this suggestion is"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of suggestion (e.g., 'similar_domain', 'fills_gap', 'higher_quality')"
    )


class HybridSourceGenerationRequest(BaseModel):
    """Request model for hybrid source generation (automatic + manual)"""
    character_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the historical character"
    )
    user_sources: List[str] = Field(
        default_factory=list,
        description="User-provided source URLs to include"
    )
    auto_complete: bool = Field(
        default=True,
        description="Whether to auto-complete with generated sources"
    )
    target_count: int = Field(
        default=50,
        ge=1,
        le=150,
        description="Target total number of sources (user + auto)"
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
    provide_suggestions: bool = Field(
        default=True,
        description="Whether to provide intelligent suggestions for improvement"
    )
    
    @field_validator('user_sources')
    @classmethod
    def validate_user_sources(cls, v):
        """Validate user sources are URLs"""
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")
        return v


class HybridSourceGenerationResponse(BaseModel):
    """Response model for hybrid source generation"""
    character_name: str = Field(..., description="Name of the character")
    sources: List[SourceItem] = Field(
        default_factory=list,
        description="Combined sources (user + auto-generated)"
    )
    user_source_count: int = Field(
        ...,
        description="Number of user-provided sources included"
    )
    auto_generated_count: int = Field(
        ...,
        description="Number of auto-generated sources added"
    )
    suggestions: List[SuggestionItem] = Field(
        default_factory=list,
        description="Intelligent suggestions for additional sources"
    )
    validation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of source validation results"
    )
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration options used for generation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the hybrid generation process"
    )
