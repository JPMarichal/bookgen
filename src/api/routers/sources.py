"""
Source validation endpoints
"""
import logging
import re
from typing import List
from fastapi import APIRouter, status
import requests
from requests.exceptions import RequestException, Timeout

from ..models.sources import (
    SourceValidationRequest,
    SourceValidationResponse,
    SourceValidationResult,
    SourceItem,
    SourceType,
    AdvancedSourceValidationRequest,
    AdvancedSourceValidationResponse
)
from ..models.source_generation import (
    AutomaticSourceGenerationRequest,
    AutomaticSourceGenerationResponse
)
from ..models.hybrid_generation import (
    HybridSourceGenerationRequest,
    HybridSourceGenerationResponse
)
from ...services.source_validator import SourceValidationService
from ...services.source_generator import AutomaticSourceGenerator
from ...services.hybrid_generator import HybridSourceGenerator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/sources",
    tags=["sources"]
)


def validate_source_item(
    source: SourceItem,
    check_accessibility: bool = True
) -> SourceValidationResult:
    """
    Validate a single source item
    
    Args:
        source: Source item to validate
        check_accessibility: Whether to check URL accessibility
        
    Returns:
        Validation result
    """
    issues = []
    is_accessible = None
    metadata = {}
    
    # Validate title
    if not source.title or len(source.title.strip()) == 0:
        issues.append("Title is empty or missing")
    
    # Validate URL if present
    if source.url:
        # Check URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(source.url):
            issues.append("Invalid URL format")
        elif check_accessibility and source.source_type == SourceType.URL:
            # Check if URL is accessible
            try:
                response = requests.head(
                    source.url,
                    timeout=5,
                    allow_redirects=True,
                    headers={'User-Agent': 'BookGen/1.0 SourceValidator'}
                )
                is_accessible = response.status_code < 400
                
                if not is_accessible:
                    issues.append(f"URL not accessible (status code: {response.status_code})")
                else:
                    # Extract metadata from headers
                    metadata["content_type"] = response.headers.get("content-type", "unknown")
                    metadata["last_modified"] = response.headers.get("last-modified")
                    
            except Timeout:
                is_accessible = False
                issues.append("URL request timed out")
            except RequestException as e:
                is_accessible = False
                issues.append(f"URL not accessible: {str(e)}")
    
    # Validate author
    if source.author and len(source.author.strip()) == 0:
        issues.append("Author field is empty")
    
    # Validate publication date format if provided
    if source.publication_date:
        # Basic date format validation (YYYY, YYYY-MM, YYYY-MM-DD)
        date_pattern = re.compile(r'^\d{4}(-\d{2}(-\d{2})?)?$')
        if not date_pattern.match(source.publication_date):
            issues.append("Invalid publication date format (expected YYYY, YYYY-MM, or YYYY-MM-DD)")
    
    # Determine if source is valid
    is_valid = len(issues) == 0
    
    return SourceValidationResult(
        source=source,
        is_valid=is_valid,
        is_accessible=is_accessible,
        issues=issues,
        metadata=metadata if metadata else None
    )


@router.post(
    "/validate",
    response_model=SourceValidationResponse,
    status_code=status.HTTP_200_OK
)
async def validate_sources(request: SourceValidationRequest):
    """
    Validate a list of sources
    
    Checks source format, required fields, URL accessibility (if enabled),
    and returns detailed validation results for each source.
    """
    logger.info(f"Validating {len(request.sources)} sources")
    
    results: List[SourceValidationResult] = []
    valid_count = 0
    invalid_count = 0
    accessible_urls = 0
    inaccessible_urls = 0
    
    for source in request.sources:
        result = validate_source_item(source, request.check_accessibility)
        results.append(result)
        
        if result.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
        
        if result.is_accessible is True:
            accessible_urls += 1
        elif result.is_accessible is False:
            inaccessible_urls += 1
    
    # Build summary statistics
    summary = {
        "validation_rate": round((valid_count / len(request.sources)) * 100, 2),
        "source_types": {},
        "accessibility_checked": request.check_accessibility
    }
    
    # Count source types
    for source in request.sources:
        source_type = source.source_type.value
        summary["source_types"][source_type] = summary["source_types"].get(source_type, 0) + 1
    
    if request.check_accessibility:
        summary["accessible_urls"] = accessible_urls
        summary["inaccessible_urls"] = inaccessible_urls
        summary["unchecked_urls"] = len(request.sources) - accessible_urls - inaccessible_urls
    
    logger.info(
        f"Source validation complete: {valid_count} valid, {invalid_count} invalid"
    )
    
    return SourceValidationResponse(
        total_sources=len(request.sources),
        valid_sources=valid_count,
        invalid_sources=invalid_count,
        results=results,
        summary=summary
    )


@router.post(
    "/validate-advanced",
    response_model=AdvancedSourceValidationResponse,
    status_code=status.HTTP_200_OK
)
async def validate_sources_advanced(request: AdvancedSourceValidationRequest):
    """
    Validate sources with advanced AI analysis
    
    Performs comprehensive validation including:
    - TF-IDF relevance analysis
    - Domain credibility checking
    - Recency and completeness scoring
    - Automatic source filtering
    - Quality recommendations
    """
    logger.info(
        f"Advanced validation: {len(request.sources)} sources for topic '{request.biography_topic}'"
    )
    
    # Create validation service with configured thresholds
    validator = SourceValidationService(
        min_relevance=request.min_relevance,
        min_credibility=request.min_credibility,
        timeout=10
    )
    
    # Perform validation
    result = validator.validate_sources(
        biography_topic=request.biography_topic,
        sources_list=request.sources,
        check_accessibility=request.check_accessibility
    )
    
    # Build summary
    summary = {
        "validation_rate": round((result["valid_sources"] / result["total_sources"]) * 100, 2)
            if result["total_sources"] > 0 else 0,
        "rejection_rate": round((result["rejected_sources"] / result["total_sources"]) * 100, 2)
            if result["total_sources"] > 0 else 0,
        "source_types": {},
        "trusted_sources": 0,
        "untrusted_sources": 0,
        "domain_categories": {}
    }
    
    # Count source types and domain info
    for res in result["results"]:
        source_type = res.source.source_type.value
        summary["source_types"][source_type] = summary["source_types"].get(source_type, 0) + 1
        
        if res.is_trusted:
            summary["trusted_sources"] += 1
        else:
            summary["untrusted_sources"] += 1
        
        if res.domain_category:
            category = res.domain_category
            summary["domain_categories"][category] = summary["domain_categories"].get(category, 0) + 1
    
    logger.info(
        f"Advanced validation complete: avg_relevance={result['average_relevance']:.2f}, "
        f"avg_credibility={result['average_credibility']:.1f}, "
        f"rejected={result['rejected_sources']}"
    )
    
    return AdvancedSourceValidationResponse(
        total_sources=result["total_sources"],
        valid_sources=result["valid_sources"],
        invalid_sources=result["invalid_sources"],
        rejected_sources=result["rejected_sources"],
        average_relevance=result["average_relevance"],
        average_credibility=result["average_credibility"],
        results=result["results"],
        recommendations=result["recommendations"],
        summary=summary
    )


@router.post(
    "/generate-automatic",
    response_model=AutomaticSourceGenerationResponse,
    status_code=status.HTTP_200_OK
)
async def generate_sources_automatically(request: AutomaticSourceGenerationRequest):
    """
    Generate sources automatically for a character using AI
    
    This endpoint implements the original functionality from .windsurf rules:
    - Automatically generates high-quality sources (40-60 by default)
    - Uses AI to analyze the character and context
    - Applies multiple search strategies (Wikipedia, academic databases, etc.)
    - Validates sources for quality and relevance
    - Guarantees diversity and accessibility
    
    The system uses:
    - OpenRouter AI for character analysis
    - Wikipedia API for biographical sources
    - Advanced validation with TF-IDF relevance scoring
    - Domain credibility checking
    
    Example:
        POST /api/v1/sources/generate-automatic
        {
            "character_name": "Albert Einstein",
            "min_sources": 40,
            "max_sources": 60,
            "check_accessibility": true,
            "min_relevance": 0.7,
            "min_credibility": 80.0
        }
    """
    logger.info(
        f"Automatic source generation request for '{request.character_name}' "
        f"(min={request.min_sources}, max={request.max_sources})"
    )
    
    # Create generator
    generator = AutomaticSourceGenerator()
    
    # Generate sources
    result = generator.generate_sources_for_character(request)
    
    # Build response
    response = AutomaticSourceGenerationResponse(
        character_name=result['character_name'],
        sources=result['sources'],
        character_analysis=result['character_analysis'],
        validation_summary=result['validation_summary'],
        strategies_used=result['strategies_used'],
        generation_metadata=result['generation_metadata']
    )
    
    logger.info(
        f"Generation complete: {len(response.sources)} sources generated "
        f"(avg_relevance={result['validation_summary'].get('average_relevance', 0):.2f})"
    )
    
    return response


@router.post(
    "/generate-hybrid",
    response_model=HybridSourceGenerationResponse,
    status_code=status.HTTP_200_OK
)
async def generate_sources_hybrid(request: HybridSourceGenerationRequest):
    """
    Generate sources in hybrid mode (automatic + manual)
    
    This endpoint combines user-provided sources with automatic generation:
    - Accepts user-provided source URLs
    - Validates user sources
    - Auto-completes with AI-generated sources (if enabled)
    - Ensures target count is met
    - Provides intelligent suggestions for improvement
    - Validates all sources (user + auto) for quality
    
    The system offers maximum flexibility:
    - Full control: Provide all sources manually (auto_complete=false)
    - Full automation: Provide no sources (auto_complete=true)
    - Hybrid: Start with some sources, auto-complete the rest
    
    Example:
        POST /api/v1/sources/generate-hybrid
        {
            "character_name": "Albert Einstein",
            "user_sources": ["https://example.com/manual-source"],
            "auto_complete": true,
            "target_count": 50,
            "min_relevance": 0.7,
            "min_credibility": 80.0,
            "provide_suggestions": true
        }
    """
    logger.info(
        f"Hybrid source generation request for '{request.character_name}' "
        f"with {len(request.user_sources)} user sources, target={request.target_count}, "
        f"auto_complete={request.auto_complete}"
    )
    
    # Create hybrid generator
    generator = HybridSourceGenerator()
    
    # Generate sources in hybrid mode
    result = generator.generate_hybrid_sources(request)
    
    # Build response
    response = HybridSourceGenerationResponse(
        character_name=result['character_name'],
        sources=result['sources'],
        user_source_count=result['user_source_count'],
        auto_generated_count=result['auto_generated_count'],
        suggestions=result['suggestions'],
        validation_summary=result['validation_summary'],
        configuration=result['configuration'],
        metadata=result['metadata']
    )
    
    logger.info(
        f"Hybrid generation complete: {len(response.sources)} total sources "
        f"({response.user_source_count} user + {response.auto_generated_count} auto), "
        f"{len(response.suggestions)} suggestions"
    )
    
    return response
