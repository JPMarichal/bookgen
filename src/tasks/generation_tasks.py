"""
Content Generation Tasks
Celery tasks for generating book chapters and content
"""
import logging
from typing import Dict, Any, Optional
from celery import Task
from src.worker import app
from src.utils.retry_handler import RetryException

logger = logging.getLogger(__name__)


class GenerationTask(Task):
    """Base class for generation tasks with custom error handling"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        logger.error(f"Task {self.name} [{task_id}] failed: {exc}", exc_info=einfo)
        # Send to dead letter queue
        return super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f"Task {self.name} [{task_id}] retry due to: {exc}")
        return super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f"Task {self.name} [{task_id}] completed successfully")
        return super().on_success(retval, task_id, args, kwargs)


@app.task(
    base=GenerationTask,
    bind=True,
    name='src.tasks.generation_tasks.generate_chapter',
    queue='content_generation',
    priority=5
)
def generate_chapter(
    self,
    character_name: str,
    chapter_number: int,
    chapter_title: str,
    target_words: int = 2550,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a single chapter for a biography
    
    Args:
        character_name: Name of the biographical subject
        chapter_number: Chapter number (1-20)
        chapter_title: Title of the chapter
        target_words: Target word count for the chapter
        context: Additional context for generation
        
    Returns:
        Dict with chapter content and metadata
    """
    logger.info(f"Generating chapter {chapter_number} for {character_name}")
    
    try:
        # TODO: Implement actual chapter generation logic
        # This is a placeholder that will be integrated with the AI service
        
        result = {
            'character_name': character_name,
            'chapter_number': chapter_number,
            'chapter_title': chapter_title,
            'content': f"# Chapter {chapter_number}: {chapter_title}\n\nPlaceholder content...",
            'word_count': target_words,
            'status': 'generated',
            'task_id': self.request.id
        }
        
        logger.info(f"Chapter {chapter_number} generated successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error generating chapter {chapter_number}: {e}")
        raise


@app.task(
    base=GenerationTask,
    bind=True,
    name='src.tasks.generation_tasks.generate_introduction',
    queue='content_generation',
    priority=6
)
def generate_introduction(
    self,
    character_name: str,
    target_words: int = 1000,
    sources: Optional[list] = None
) -> Dict[str, Any]:
    """
    Generate introduction section
    
    Args:
        character_name: Name of the biographical subject
        target_words: Target word count
        sources: List of sources for the biography
        
    Returns:
        Dict with introduction content and metadata
    """
    logger.info(f"Generating introduction for {character_name}")
    
    try:
        # TODO: Implement actual introduction generation
        result = {
            'character_name': character_name,
            'content': f"# Introduction\n\nPlaceholder introduction...",
            'word_count': target_words,
            'status': 'generated',
            'task_id': self.request.id
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating introduction: {e}")
        raise


@app.task(
    base=GenerationTask,
    bind=True,
    name='src.tasks.generation_tasks.generate_conclusion',
    queue='content_generation',
    priority=6
)
def generate_conclusion(
    self,
    character_name: str,
    target_words: int = 1000,
    chapter_summaries: Optional[list] = None
) -> Dict[str, Any]:
    """
    Generate conclusion section
    
    Args:
        character_name: Name of the biographical subject
        target_words: Target word count
        chapter_summaries: Summaries of all chapters
        
    Returns:
        Dict with conclusion content and metadata
    """
    logger.info(f"Generating conclusion for {character_name}")
    
    try:
        # TODO: Implement actual conclusion generation
        result = {
            'character_name': character_name,
            'content': f"# Conclusion\n\nPlaceholder conclusion...",
            'word_count': target_words,
            'status': 'generated',
            'task_id': self.request.id
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating conclusion: {e}")
        raise


@app.task(
    base=GenerationTask,
    bind=True,
    name='src.tasks.generation_tasks.regenerate_chapter',
    queue='content_generation',
    priority=7
)
def regenerate_chapter(
    self,
    character_name: str,
    chapter_number: int,
    reason: str,
    previous_content: Optional[str] = None,
    feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Regenerate a chapter that failed validation
    
    Args:
        character_name: Name of the biographical subject
        chapter_number: Chapter number to regenerate
        reason: Reason for regeneration
        previous_content: Previous chapter content
        feedback: Validation feedback
        
    Returns:
        Dict with regenerated chapter content
    """
    logger.info(f"Regenerating chapter {chapter_number} for {character_name}. Reason: {reason}")
    
    try:
        # TODO: Implement regeneration with feedback
        result = {
            'character_name': character_name,
            'chapter_number': chapter_number,
            'content': f"# Chapter {chapter_number} (Regenerated)\n\nImproved content...",
            'word_count': 2550,
            'status': 'regenerated',
            'reason': reason,
            'task_id': self.request.id
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error regenerating chapter {chapter_number}: {e}")
        raise


@app.task(
    base=GenerationTask,
    bind=True,
    name='src.tasks.generation_tasks.batch_generate_chapters',
    queue='content_generation',
    priority=4
)
def batch_generate_chapters(
    self,
    character_name: str,
    chapter_specs: list,
    batch_size: int = 5
) -> Dict[str, Any]:
    """
    Generate multiple chapters in batch
    
    Args:
        character_name: Name of the biographical subject
        chapter_specs: List of chapter specifications
        batch_size: Number of chapters to process in parallel
        
    Returns:
        Dict with batch results
    """
    logger.info(f"Batch generating {len(chapter_specs)} chapters for {character_name}")
    
    try:
        from celery import group
        
        # Create a group of generation tasks
        job = group([
            generate_chapter.s(
                character_name,
                spec['number'],
                spec['title'],
                spec.get('target_words', 2550),
                spec.get('context')
            )
            for spec in chapter_specs
        ])
        
        result = job.apply_async()
        
        return {
            'character_name': character_name,
            'total_chapters': len(chapter_specs),
            'batch_size': batch_size,
            'group_id': result.id,
            'status': 'processing',
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in batch generation: {e}")
        raise
