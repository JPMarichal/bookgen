"""
Pydantic models for collection-based biography generation endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .biographies import GenerationMode


class CollectionGenerateRequest(BaseModel):
    """Request model for collection-based biography generation"""
    collection_file: str = Field(
        default="personajes_guerra_fria.md",
        description="Collection file name (relative to colecciones/ directory)"
    )
    mode: GenerationMode = Field(
        default=GenerationMode.AUTOMATIC,
        description="Source generation mode: 'manual', 'automatic', or 'hybrid'"
    )
    chapters: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Number of chapters to generate"
    )
    total_words: Optional[int] = Field(
        default=51000,
        ge=1000,
        le=200000,
        description="Target total word count for the biography"
    )
    sources: Optional[list[str]] = Field(
        default=None,
        description="Source URLs for manual or hybrid mode"
    )
    min_sources: Optional[int] = Field(
        default=40,
        ge=10,
        le=100,
        description="Minimum sources for automatic/hybrid mode"
    )
    quality_threshold: Optional[float] = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Quality threshold for automatic source generation (0-1)"
    )
    mark_completed: bool = Field(
        default=True,
        description="Whether to mark the character as completed (✅) in the collection file"
    )


class CollectionGenerateResponse(BaseModel):
    """Response model for collection-based biography generation"""
    job_id: str = Field(..., description="Unique job identifier")
    character: str = Field(..., description="Character name being generated")
    character_normalized: str = Field(..., description="Normalized character name")
    collection_file: str = Field(..., description="Collection file used")
    line_number: str = Field(..., description="Line number/identifier in collection")
    status: str = Field(..., description="Job status")
    mode: str = Field(..., description="Generation mode used")
    chapters: int = Field(..., description="Number of chapters to generate")
    created_at: datetime = Field(..., description="Job creation timestamp")
    estimated_completion_time: Optional[str] = Field(None, description="Estimated time to completion")
    message: Optional[str] = Field(None, description="Additional message or information")


class CollectionStatsResponse(BaseModel):
    """Response model for collection statistics"""
    collection_file: str = Field(..., description="Collection file name")
    total_characters: int = Field(..., description="Total number of characters in collection")
    completed: int = Field(..., description="Number of completed characters")
    remaining: int = Field(..., description="Number of remaining characters")
    completion_percentage: float = Field(..., description="Completion percentage")


class CollectionListResponse(BaseModel):
    """Response model for listing collections"""
    collections: list[str] = Field(..., description="List of available collection files")
    count: int = Field(..., description="Total number of collections")
