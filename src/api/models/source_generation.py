"""
Pydantic models for automatic source generation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .sources import SourceItem


class CharacterAnalysis(BaseModel):
    """AI analysis result for a character"""
    character_name: str = Field(..., description="Name of the character analyzed")
    historical_period: Optional[str] = Field(
        default=None,
        description="Historical period (century, key years)"
    )
    nationality: Optional[str] = Field(
        default=None,
        description="Nationality and relevant places"
    )
    professional_field: Optional[str] = Field(
        default=None,
        description="Professional field (science, politics, arts, etc.)"
    )
    key_events: List[str] = Field(
        default_factory=list,
        description="Important events and achievements"
    )
    related_entities: List[str] = Field(
        default_factory=list,
        description="Related people and concepts"
    )
    search_terms: List[str] = Field(
        default_factory=list,
        description="Optimal search terms for finding sources"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata from analysis"
    )


class AutomaticSourceGenerationRequest(BaseModel):
    """Request model for automatic source generation"""
    character_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the historical character"
    )
    min_sources: int = Field(
        default=40,
        ge=10,
        le=100,
        description="Minimum number of sources to generate"
    )
    max_sources: int = Field(
        default=60,
        ge=10,
        le=150,
        description="Maximum number of sources to generate"
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


class AutomaticSourceGenerationResponse(BaseModel):
    """Response model for automatic source generation"""
    character_name: str = Field(..., description="Name of the character")
    sources: List[SourceItem] = Field(
        default_factory=list,
        description="Generated and validated sources"
    )
    character_analysis: Optional[CharacterAnalysis] = Field(
        default=None,
        description="AI analysis of the character"
    )
    validation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of source validation results"
    )
    strategies_used: List[str] = Field(
        default_factory=list,
        description="List of strategies used to generate sources"
    )
    generation_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the generation process"
    )
