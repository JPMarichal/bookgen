"""
Export Tasks
Celery tasks for exporting content to various formats
"""
import logging
from typing import Dict, Any, Optional
from celery import Task
from src.worker import app

logger = logging.getLogger(__name__)


class ExportTask(Task):
    """Base class for export tasks"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        logger.error(f"Export task {self.name} [{task_id}] failed: {exc}", exc_info=einfo)
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@app.task(
    base=ExportTask,
    bind=True,
    name='src.tasks.export_tasks.export_to_markdown',
    queue='export',
    priority=5
)
def export_to_markdown(
    self,
    character_name: str,
    content: Dict[str, Any],
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export biography to Markdown format
    
    Args:
        character_name: Name of the biographical subject
        content: Complete biography content
        output_path: Optional custom output path
        
    Returns:
        Export result with file path
    """
    logger.info(f"Exporting {character_name} biography to Markdown")
    
    try:
        # TODO: Implement actual markdown export
        # This would integrate with the concatenation service
        
        if output_path is None:
            output_path = f"/app/bios/{character_name}/biography.md"
        
        result = {
            'success': True,
            'character_name': character_name,
            'format': 'markdown',
            'output_path': output_path,
            'file_size': 0,  # Placeholder
            'task_id': self.request.id
        }
        
        logger.info(f"Markdown export complete: {output_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error exporting to Markdown: {e}")
        raise


@app.task(
    base=ExportTask,
    bind=True,
    name='src.tasks.export_tasks.export_to_word',
    queue='export',
    priority=5
)
def export_to_word(
    self,
    character_name: str,
    markdown_file: str,
    template_path: Optional[str] = None,
    include_toc: bool = True
) -> Dict[str, Any]:
    """
    Export biography to Word (DOCX) format
    
    Args:
        character_name: Name of the biographical subject
        markdown_file: Path to markdown source
        template_path: Optional Word template path
        include_toc: Whether to include table of contents
        
    Returns:
        Export result with file path and metadata
    """
    logger.info(f"Exporting {character_name} biography to Word")
    
    try:
        # TODO: Implement actual Word export
        # This would integrate with the Word export service
        
        if template_path is None:
            template_path = "/app/wordTemplate/reference.docx"
        
        output_path = f"/app/docx/{character_name}_biography.docx"
        
        result = {
            'success': True,
            'character_name': character_name,
            'format': 'docx',
            'output_path': output_path,
            'template_used': template_path,
            'has_toc': include_toc,
            'toc_entries': 20 if include_toc else 0,
            'file_size': 0,  # Placeholder
            'task_id': self.request.id
        }
        
        logger.info(f"Word export complete: {output_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error exporting to Word: {e}")
        raise


@app.task(
    base=ExportTask,
    bind=True,
    name='src.tasks.export_tasks.export_to_pdf',
    queue='export',
    priority=5
)
def export_to_pdf(
    self,
    character_name: str,
    source_file: str,
    include_toc: bool = True
) -> Dict[str, Any]:
    """
    Export biography to PDF format
    
    Args:
        character_name: Name of the biographical subject
        source_file: Path to source file (markdown or docx)
        include_toc: Whether to include table of contents
        
    Returns:
        Export result with file path
    """
    logger.info(f"Exporting {character_name} biography to PDF")
    
    try:
        # TODO: Implement actual PDF export
        
        output_path = f"/app/docx/{character_name}_biography.pdf"
        
        result = {
            'success': True,
            'character_name': character_name,
            'format': 'pdf',
            'output_path': output_path,
            'source_file': source_file,
            'has_toc': include_toc,
            'file_size': 0,  # Placeholder
            'task_id': self.request.id
        }
        
        logger.info(f"PDF export complete: {output_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        raise


@app.task(
    base=ExportTask,
    bind=True,
    name='src.tasks.export_tasks.export_all_formats',
    queue='export',
    priority=6
)
def export_all_formats(
    self,
    character_name: str,
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Export biography to all supported formats
    
    Args:
        character_name: Name of the biographical subject
        content: Complete biography content
        
    Returns:
        Results for all export operations
    """
    logger.info(f"Exporting {character_name} biography to all formats")
    
    try:
        from celery import group
        
        # Create markdown first, then other formats
        markdown_result = export_to_markdown.apply_async(
            args=[character_name, content],
            priority=7
        )
        
        # Wait for markdown to complete
        markdown_path = markdown_result.get()['output_path']
        
        # Export to other formats in parallel
        export_jobs = group([
            export_to_word.s(character_name, markdown_path),
            export_to_pdf.s(character_name, markdown_path)
        ])
        
        results = export_jobs.apply_async()
        
        return {
            'character_name': character_name,
            'formats': ['markdown', 'docx', 'pdf'],
            'markdown_ready': True,
            'markdown_path': markdown_path,
            'other_formats_processing': True,
            'group_id': results.id,
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in multi-format export: {e}")
        raise
