"""
Pydantic models for API request/response validation
"""
from .biographies import (
    BiographyGenerateRequest,
    BiographyGenerateResponse,
    BiographyStatusResponse,
    JobStatus
)
from .sources import SourceValidationRequest, SourceValidationResponse
from .content_analysis import (
    BiographicalDepthAnalysis,
    FactualAccuracyAnalysis,
    BiasAnalysis,
    ContentQualityScore,
    ContentAnalysisRequest,
    ContentAnalysisResponse
)

__all__ = [
    "BiographyGenerateRequest",
    "BiographyGenerateResponse",
    "BiographyStatusResponse",
    "JobStatus",
    "SourceValidationRequest",
    "SourceValidationResponse",
    "BiographicalDepthAnalysis",
    "FactualAccuracyAnalysis",
    "BiasAnalysis",
    "ContentQualityScore",
    "ContentAnalysisRequest",
    "ContentAnalysisResponse",
]
