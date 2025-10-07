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
    SourceType
)

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
