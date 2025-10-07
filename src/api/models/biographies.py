"""
Pydantic models for biography generation endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Status of a biography generation job"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


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
    
    @field_validator("character")
    @classmethod
    def validate_character(cls, v: str) -> str:
        """Validate character name"""
        if not v.strip():
            raise ValueError("Character name cannot be empty")
        return v.strip()


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
