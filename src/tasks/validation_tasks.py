"""
Validation Tasks
Celery tasks for content validation and quality checks
"""
import logging
from typing import Dict, Any, List, Optional
from celery import Task
from src.worker import app

logger = logging.getLogger(__name__)


class ValidationTask(Task):
    """Base class for validation tasks"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        logger.error(f"Validation task {self.name} [{task_id}] failed: {exc}", exc_info=einfo)
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@app.task(
    base=ValidationTask,
    bind=True,
    name='src.tasks.validation_tasks.validate_chapter_length',
    queue='validation',
    priority=6
)
def validate_chapter_length(
    self,
    chapter_content: str,
    target_length: int = 2550,
    tolerance: float = 0.05
) -> Dict[str, Any]:
    """
    Validate chapter length meets requirements
    
    Args:
        chapter_content: Content to validate
        target_length: Target word count
        tolerance: Acceptable deviation (default 5%)
        
    Returns:
        Validation result with status and metrics
    """
    logger.info(f"Validating chapter length (target: {target_length} words)")
    
    try:
        # Simple word count
        words = chapter_content.split()
        actual_length = len(words)
        
        min_length = int(target_length * (1 - tolerance))
        max_length = int(target_length * (1 + tolerance))
        
        is_valid = min_length <= actual_length <= max_length
        deviation = ((actual_length - target_length) / target_length) * 100
        
        result = {
            'is_valid': is_valid,
            'actual_length': actual_length,
            'target_length': target_length,
            'min_length': min_length,
            'max_length': max_length,
            'deviation_percent': round(deviation, 2),
            'quality_score': max(0, 100 - abs(deviation)),
            'task_id': self.request.id
        }
        
        logger.info(f"Validation complete: {actual_length} words (valid: {is_valid})")
        return result
        
    except Exception as e:
        logger.error(f"Error validating chapter length: {e}")
        raise


@app.task(
    base=ValidationTask,
    bind=True,
    name='src.tasks.validation_tasks.validate_sources',
    queue='validation',
    priority=7
)
def validate_sources(
    self,
    character_name: str,
    sources: List[Dict[str, Any]],
    min_sources: int = 40,
    relevance_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Validate biographical sources
    
    Args:
        character_name: Name of the biographical subject
        sources: List of sources to validate
        min_sources: Minimum number of required sources
        relevance_threshold: Minimum relevance score
        
    Returns:
        Validation result with source analysis
    """
    logger.info(f"Validating {len(sources)} sources for {character_name}")
    
    try:
        # TODO: Implement actual source validation logic
        # This would integrate with the source validation service
        
        valid_sources = []
        rejected_sources = []
        
        for source in sources:
            # Placeholder validation
            relevance = source.get('relevance_score', 0.8)
            if relevance >= relevance_threshold:
                valid_sources.append(source)
            else:
                rejected_sources.append(source)
        
        is_valid = len(valid_sources) >= min_sources
        
        result = {
            'is_valid': is_valid,
            'total_sources': len(sources),
            'valid_sources': len(valid_sources),
            'rejected_sources': len(rejected_sources),
            'min_required': min_sources,
            'average_relevance': sum(s.get('relevance_score', 0) for s in valid_sources) / len(valid_sources) if valid_sources else 0,
            'validation_details': {
                'valid': [s.get('url', '') for s in valid_sources[:5]],  # First 5
                'rejected': [s.get('url', '') for s in rejected_sources[:5]]  # First 5
            },
            'task_id': self.request.id
        }
        
        logger.info(f"Source validation complete: {len(valid_sources)}/{len(sources)} valid")
        return result
        
    except Exception as e:
        logger.error(f"Error validating sources: {e}")
        raise


@app.task(
    base=ValidationTask,
    bind=True,
    name='src.tasks.validation_tasks.validate_content_quality',
    queue='validation',
    priority=6
)
def validate_content_quality(
    self,
    content: str,
    checks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate content quality (formatting, coherence, etc.)
    
    Args:
        content: Content to validate
        checks: List of quality checks to perform
        
    Returns:
        Quality validation results
    """
    logger.info("Validating content quality")
    
    try:
        if checks is None:
            checks = ['markdown_format', 'coherence', 'structure']
        
        results = {}
        overall_score = 0
        
        # Check markdown formatting
        if 'markdown_format' in checks:
            has_headers = '#' in content
            has_paragraphs = '\n\n' in content
            format_score = (has_headers + has_paragraphs) * 50
            results['markdown_format'] = {
                'score': format_score,
                'has_headers': has_headers,
                'has_paragraphs': has_paragraphs
            }
            overall_score += format_score
        
        # Check structure
        if 'structure' in checks:
            lines = content.split('\n')
            header_count = sum(1 for line in lines if line.startswith('#'))
            structure_score = min(100, header_count * 20)
            results['structure'] = {
                'score': structure_score,
                'header_count': header_count
            }
            overall_score += structure_score
        
        # Placeholder for coherence check
        if 'coherence' in checks:
            # TODO: Implement actual coherence checking
            results['coherence'] = {'score': 80}
            overall_score += 80
        
        num_checks = len(checks)
        average_score = overall_score / num_checks if num_checks > 0 else 0
        
        result = {
            'is_valid': average_score >= 70,
            'overall_score': round(average_score, 2),
            'checks_performed': checks,
            'detailed_results': results,
            'task_id': self.request.id
        }
        
        logger.info(f"Quality validation complete: score {average_score:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error validating content quality: {e}")
        raise


@app.task(
    base=ValidationTask,
    bind=True,
    name='src.tasks.validation_tasks.validate_complete_biography',
    queue='validation',
    priority=8
)
def validate_complete_biography(
    self,
    character_name: str,
    chapters: List[Dict[str, Any]],
    total_word_target: int = 51000
) -> Dict[str, Any]:
    """
    Validate complete biography against all requirements
    
    Args:
        character_name: Name of the biographical subject
        chapters: List of all chapter content
        total_word_target: Total word count target
        
    Returns:
        Complete validation report
    """
    logger.info(f"Validating complete biography for {character_name}")
    
    try:
        total_words = sum(len(ch.get('content', '').split()) for ch in chapters)
        num_chapters = len(chapters)
        
        validation_results = {
            'character_name': character_name,
            'is_valid': True,
            'total_chapters': num_chapters,
            'expected_chapters': 20,
            'total_words': total_words,
            'target_words': total_word_target,
            'word_deviation_percent': ((total_words - total_word_target) / total_word_target) * 100,
            'checks': {}
        }
        
        # Check chapter count
        validation_results['checks']['chapter_count'] = {
            'passed': num_chapters == 20,
            'actual': num_chapters,
            'expected': 20
        }
        
        # Check total word count
        word_tolerance = 0.05
        min_words = int(total_word_target * (1 - word_tolerance))
        max_words = int(total_word_target * (1 + word_tolerance))
        validation_results['checks']['total_words'] = {
            'passed': min_words <= total_words <= max_words,
            'actual': total_words,
            'min': min_words,
            'max': max_words
        }
        
        # Overall validation
        validation_results['is_valid'] = all(
            check['passed'] for check in validation_results['checks'].values()
        )
        
        validation_results['task_id'] = self.request.id
        
        logger.info(f"Complete validation: {validation_results['is_valid']}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validating complete biography: {e}")
        raise
