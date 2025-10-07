"""
Biography generation endpoints
"""
import uuid
import logging
import os
from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse

from ..models.biographies import (
    BiographyGenerateRequest,
    BiographyGenerateResponse,
    BiographyStatusResponse,
    JobStatus
)
from ...services.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/biographies",
    tags=["biographies"]
)

# In-memory job storage (in production, use a database)
jobs: Dict[str, Dict] = {}


def run_biography_generation(job_id: str, request: BiographyGenerateRequest):
    """
    Background task to generate biography
    
    Args:
        job_id: Unique job identifier
        request: Generation request parameters
    """
    try:
        # Update job status
        jobs[job_id]["status"] = JobStatus.IN_PROGRESS
        jobs[job_id]["started_at"] = datetime.now(timezone.utc)
        
        logger.info(f"Starting biography generation for job {job_id}")
        
        # Initialize OpenRouter client
        client = OpenRouterClient()
        
        # Calculate words per chapter
        words_per_chapter = request.total_words // request.chapters
        
        # Generate a simple test biography (in production, this would be more complex)
        chapters_generated = []
        for i in range(1, request.chapters + 1):
            chapter_prompt = (
                f"Write chapter {i} of {request.chapters} about {request.character}. "
                f"The chapter should be approximately {words_per_chapter} words long. "
                f"Focus on their life story, achievements, and impact."
            )
            
            try:
                chapter_content = client.generate_text(
                    prompt=chapter_prompt,
                    system_prompt="You are an expert biographer writing a comprehensive biography.",
                    temperature=request.temperature,
                    max_tokens=min(words_per_chapter * 2, 8192)  # Rough token estimate
                )
                
                chapters_generated.append({
                    "chapter": i,
                    "content": chapter_content,
                    "word_count": len(chapter_content.split())
                })
                
                # Update progress
                jobs[job_id]["progress"] = {
                    "chapters_completed": i,
                    "total_chapters": request.chapters,
                    "percentage": round((i / request.chapters) * 100, 2)
                }
                
                logger.info(f"Job {job_id}: Completed chapter {i}/{request.chapters}")
                
            except Exception as e:
                logger.error(f"Error generating chapter {i} for job {job_id}: {e}")
                raise
        
        # Mark job as completed
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc)
        jobs[job_id]["chapters"] = chapters_generated
        jobs[job_id]["download_url"] = f"/api/v1/biographies/{job_id}/download"
        
        logger.info(f"Successfully completed biography generation for job {job_id}")
        
    except Exception as e:
        logger.error(f"Failed to generate biography for job {job_id}: {e}", exc_info=True)
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc)


@router.post(
    "/generate",
    response_model=BiographyGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def generate_biography(
    request: BiographyGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate biography generation
    
    Creates a new job to generate a biography based on the provided parameters.
    The generation runs in the background and can be monitored via the status endpoint.
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "character": request.character,
        "chapters": request.chapters,
        "total_words": request.total_words,
        "model": request.model or os.getenv("OPENROUTER_MODEL", "qwen/qwen2.5-vl-72b-instruct:free"),
        "temperature": request.temperature,
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None,
        "progress": None,
        "error": None,
        "chapters": [],
        "download_url": None
    }
    
    # Add background task for generation
    background_tasks.add_task(run_biography_generation, job_id, request)
    
    logger.info(
        f"Created biography generation job {job_id} for character '{request.character}'"
    )
    
    return BiographyGenerateResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Biography generation job created successfully",
        character=request.character,
        chapters=request.chapters,
        created_at=jobs[job_id]["created_at"],
        estimated_completion_time=f"{request.chapters * 30} seconds"  # Rough estimate
    )


@router.get(
    "/{job_id}/status",
    response_model=BiographyStatusResponse
)
async def get_biography_status(job_id: str):
    """
    Get the status of a biography generation job
    
    Returns current status, progress information, and error details if applicable.
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs[job_id]
    
    return BiographyStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        character=job["character"],
        progress=job.get("progress"),
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        error=job.get("error"),
        download_url=job.get("download_url")
    )


@router.get("/{job_id}/download")
async def download_biography(job_id: str):
    """
    Download the generated biography document
    
    Returns the completed biography as a downloadable file.
    Only available for completed jobs.
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )
    
    # In a real implementation, this would return the actual generated file
    # For now, we'll create a temporary text file with the biography content
    import tempfile
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.txt',
        delete=False,
        prefix=f"biography_{job['character']}_"
    ) as tmp_file:
        tmp_file.write(f"Biography of {job['character']}\n")
        tmp_file.write("=" * 50 + "\n\n")
        
        for chapter_data in job["chapters"]:
            tmp_file.write(f"Chapter {chapter_data['chapter']}\n")
            tmp_file.write("-" * 30 + "\n")
            tmp_file.write(chapter_data["content"] + "\n\n")
        
        tmp_file.write(f"\nGenerated on: {job['completed_at'].isoformat()}\n")
        tmp_file.write(f"Total chapters: {len(job['chapters'])}\n")
        
        tmp_path = tmp_file.name
    
    # Return file as download
    return FileResponse(
        path=tmp_path,
        filename=f"biography_{job['character'].replace(' ', '_')}.txt",
        media_type="text/plain",
        background=BackgroundTasks()  # Will clean up temp file after sending
    )
