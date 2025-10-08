"""
Pydantic models for content analysis with AI
Data models for advanced content quality analysis
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class BiographicalDepthAnalysis(BaseModel):
    """Analysis of biographical depth in content"""
    depth_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall biographical depth score (0-1)"
    )
    early_life_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Coverage of early life and formation (0-100)"
    )
    professional_development: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Professional development and achievements (0-100)"
    )
    historical_context: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Historical and social context (0-100)"
    )
    personal_relationships: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Personal relationships and influences (0-100)"
    )
    legacy_impact: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Legacy and historical impact (0-100)"
    )
    specificity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Use of specific details vs generalities (0-100)"
    )
    concrete_details: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Use of dates, places, and concrete names (0-100)"
    )
    justification: Optional[str] = Field(
        default=None,
        description="AI justification for the scores"
    )


class FactualAccuracyAnalysis(BaseModel):
    """Analysis of factual accuracy in content"""
    accuracy_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall factual accuracy score (0-1)"
    )
    citation_count: int = Field(
        default=0,
        ge=0,
        description="Number of citations or references found"
    )
    verifiable_facts: int = Field(
        default=0,
        ge=0,
        description="Number of verifiable factual statements"
    )
    questionable_claims: int = Field(
        default=0,
        ge=0,
        description="Number of questionable or unverified claims"
    )
    date_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Accuracy of dates mentioned (0-100)"
    )
    consistency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Internal consistency of facts (0-100)"
    )
    justification: Optional[str] = Field(
        default=None,
        description="AI justification for the scores"
    )


class BiasAnalysis(BaseModel):
    """Analysis of bias and neutrality in content"""
    neutrality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall neutrality score (0-1)"
    )
    political_bias: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Detected political bias (0=neutral, 100=extreme bias)"
    )
    emotional_language: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Use of emotional vs neutral language (0-100)"
    )
    perspective_balance: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Balance of different perspectives (0-100)"
    )
    objectivity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall objectivity (0-100)"
    )
    detected_biases: List[str] = Field(
        default_factory=list,
        description="List of detected bias types"
    )
    justification: Optional[str] = Field(
        default=None,
        description="AI justification for the scores"
    )


class ContentQualityScore(BaseModel):
    """Comprehensive content quality score"""
    biographical_depth: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Biographical depth score (0-1)"
    )
    factual_accuracy: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Factual accuracy score (0-1)"
    )
    information_density: float = Field(
        ...,
        ge=0.0,
        description="Information density (words per meaningful fact)"
    )
    neutrality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Neutrality/objectivity score (0-1)"
    )
    source_citations: int = Field(
        default=0,
        ge=0,
        description="Number of source citations"
    )
    content_uniqueness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Content uniqueness score (0-1)"
    )
    overall_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall weighted quality score (0-1)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional analysis metadata"
    )
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        weights = {
            'biographical_depth': 0.30,
            'factual_accuracy': 0.30,
            'information_density': 0.15,
            'neutrality_score': 0.15,
            'content_uniqueness': 0.10
        }
        
        # Normalize information_density to 0-1 scale (assuming good density is around 20-50 words per fact)
        normalized_density = min(1.0, max(0.0, 1.0 - (self.information_density - 30) / 50))
        
        overall = (
            self.biographical_depth * weights['biographical_depth'] +
            self.factual_accuracy * weights['factual_accuracy'] +
            normalized_density * weights['information_density'] +
            self.neutrality_score * weights['neutrality_score'] +
            self.content_uniqueness * weights['content_uniqueness']
        )
        
        return round(overall, 3)


class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis"""
    source_url: str = Field(
        ...,
        min_length=1,
        description="URL of the source to analyze"
    )
    character: str = Field(
        ...,
        min_length=1,
        description="Character/person name for biographical analysis"
    )
    max_content_length: int = Field(
        default=10000,
        ge=100,
        le=50000,
        description="Maximum content length to analyze (in characters)"
    )


class ContentAnalysisResponse(BaseModel):
    """Response model for content analysis"""
    source_url: str = Field(..., description="Analyzed source URL")
    character: str = Field(..., description="Character analyzed")
    quality_score: ContentQualityScore = Field(
        ...,
        description="Comprehensive quality score"
    )
    depth_analysis: Optional[BiographicalDepthAnalysis] = Field(
        default=None,
        description="Detailed biographical depth analysis"
    )
    factual_analysis: Optional[FactualAccuracyAnalysis] = Field(
        default=None,
        description="Detailed factual accuracy analysis"
    )
    bias_analysis: Optional[BiasAnalysis] = Field(
        default=None,
        description="Detailed bias analysis"
    )
    content_length: int = Field(
        default=0,
        ge=0,
        description="Length of analyzed content in characters"
    )
    analysis_timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp of the analysis"
    )
