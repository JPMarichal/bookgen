"""
Collection-based biography generation endpoints
Implements automated generation from collection files
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from ..models.collections import (
    CollectionGenerateRequest,
    CollectionGenerateResponse,
    CollectionStatsResponse,
    CollectionListResponse
)
from ..models.biographies import BiographyGenerateRequest
from ...services.collection_service import CollectionService
from .biographies import generate_biography, jobs

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/collections",
    tags=["collections"]
)

# Initialize collection service
collection_service = CollectionService()


@router.post(
    "/generate-next",
    response_model=CollectionGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate next biography from collection",
    description="""
    Automatically detect the next uncompleted character in a collection file
    and initiate biography generation for that character.
    
    This endpoint:
    1. Inspects the specified collection file
    2. Finds the first character without a completion mark (✅)
    3. Initiates biography generation using existing infrastructure
    4. Optionally marks the character as completed in the collection file
    
    The generation runs in the background and can be monitored via the
    standard biography status endpoint.
    """
)
async def generate_next_from_collection(
    request: CollectionGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate biography for the next uncompleted character in a collection
    
    Args:
        request: Collection generation request parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        CollectionGenerateResponse with job details
        
    Raises:
        HTTPException: If collection file not found or no uncompleted characters
    """
    logger.info(f"Collection generation request for: {request.collection_file}")
    
    try:
        # Find first uncompleted character in collection
        line_idx, line_number, character_name = collection_service.find_first_uncompleted(
            request.collection_file
        )
        
        if character_name is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No uncompleted characters found in collection: {request.collection_file}"
            )
        
        logger.info(f"Found uncompleted character: {character_name} (line {line_idx})")
        
        # Normalize character name for use as identifier
        character_normalized = CollectionService.normalize_character_name(character_name)
        
        # Create biography generation request
        biography_request = BiographyGenerateRequest(
            character=character_name,
            mode=request.mode,
            chapters=request.chapters,
            total_words=request.total_words,
            min_sources=request.min_sources,
            quality_threshold=request.quality_threshold,
            sources=request.sources  # Pass through user-provided sources
        )
        
        # Call existing biography generation endpoint
        biography_response = await generate_biography(
            request=biography_request,
            background_tasks=background_tasks
        )
        
        # Optionally mark character as completed in collection file
        if request.mark_completed:
            try:
                collection_service.mark_as_completed(
                    request.collection_file,
                    character_name
                )
                logger.info(f"Marked character '{character_name}' as completed in collection")
            except Exception as e:
                logger.warning(f"Failed to mark character as completed: {e}")
                # Don't fail the request if marking fails
        
        # Return response with collection-specific information
        return CollectionGenerateResponse(
            job_id=biography_response.job_id,
            character=character_name,
            character_normalized=character_normalized,
            collection_file=request.collection_file,
            line_number=line_number.strip() if line_number else str(line_idx + 1),
            status=biography_response.status,
            mode=biography_response.mode,
            chapters=biography_response.chapters,
            created_at=biography_response.created_at,
            estimated_completion_time=biography_response.estimated_completion_time,
            message=f"Biography generation started for '{character_name}' from collection '{request.collection_file}'"
        )
        
    except FileNotFoundError as e:
        logger.error(f"Collection file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in collection generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate biography from collection: {str(e)}"
        )


@router.get(
    "/{collection_file}/stats",
    response_model=CollectionStatsResponse,
    summary="Get collection statistics",
    description="Get statistics about a collection file including total, completed, and remaining characters"
)
async def get_collection_stats(collection_file: str):
    """
    Get statistics for a collection file
    
    Args:
        collection_file: Collection file name
        
    Returns:
        CollectionStatsResponse with statistics
        
    Raises:
        HTTPException: If collection file not found
    """
    try:
        stats = collection_service.get_collection_stats(collection_file)
        return CollectionStatsResponse(**stats)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection statistics: {str(e)}"
        )


@router.get(
    "/",
    response_model=CollectionListResponse,
    summary="List all collections",
    description="Get a list of all available collection files"
)
async def list_collections():
    """
    List all available collection files
    
    Returns:
        CollectionListResponse with list of collections
    """
    try:
        collections = collection_service.list_collections()
        return CollectionListResponse(
            collections=collections,
            count=len(collections)
        )
    except Exception as e:
        logger.error(f"Error listing collections: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list collections: {str(e)}"
        )
