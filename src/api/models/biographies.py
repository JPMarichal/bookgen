"""
Pydantic models for biography generation endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Status of a biography generation job"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationMode(str, Enum):
    """Mode of source generation for biography"""
    MANUAL = "manual"  # User provides sources manually
    AUTOMATIC = "automatic"  # System generates sources automatically
    HYBRID = "hybrid"  # Mix of user sources + automatic generation


class BiographyGenerateRequest(BaseModel):
    """Request model for biography generation"""
    character: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name or identifier of the character/person for the biography"
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
    model: Optional[str] = Field(
        default=None,
        description="AI model to use (defaults to configured model)"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for text generation"
    )
    
    # Source generation mode (new feature)
    mode: GenerationMode = Field(
        default=GenerationMode.MANUAL,
        description="Source generation mode: 'manual' (user provides sources), 'automatic' (system generates sources), or 'hybrid' (mix of both)"
    )
    sources: Optional[List[str]] = Field(
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
    
    @field_validator("character")
    @classmethod
    def validate_character(cls, v: str) -> str:
        """Validate character name"""
        if not v.strip():
            raise ValueError("Character name cannot be empty")
        return v.strip()
    
    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate sources based on mode"""
        if v is None:
            return v
        
        # Validate URLs
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")
        
        return v


class BiographyGenerateResponse(BaseModel):
    """Response model for biography generation initiation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status")
    message: str = Field(..., description="Status message")
    character: str = Field(..., description="Character name")
    chapters: int = Field(..., description="Number of chapters")
    created_at: datetime = Field(..., description="Job creation timestamp")
    estimated_completion_time: Optional[str] = Field(
        default=None,
        description="Estimated time to completion"
    )
    mode: GenerationMode = Field(..., description="Source generation mode used")
    sources_generated_automatically: Optional[bool] = Field(
        default=None,
        description="Whether sources were generated automatically"
    )
    source_count: Optional[int] = Field(
        default=None,
        description="Number of sources being used"
    )


class BiographyStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    character: str = Field(..., description="Character name")
    progress: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Progress details (chapters completed, words generated, etc.)"
    )
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(
        default=None,
        description="Job start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Job completion timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if job failed"
    )
    download_url: Optional[str] = Field(
        default=None,
        description="Download URL if job completed successfully"
    )
