"""
BookGen Engine - Main Orchestration Engine
Coordinates all services for biography generation with state management and error handling
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from .state_machine import GenerationState, StateMachine
from .error_handler import ErrorHandler
from .workflow_manager import WorkflowManager
from ..database.config import SessionLocal, get_db
from ..models.generation_job import GenerationJob
from ..models.biography import Biography

logger = logging.getLogger(__name__)


class JobStatus:
    """Job status information"""
    
    def __init__(
        self,
        job_id: int,
        state: str,
        progress: float,
        character_name: str,
        created_at: datetime,
        updated_at: datetime,
        error_message: Optional[str] = None,
        logs: Optional[list] = None
    ):
        self.job_id = job_id
        self.state = state
        self.progress = progress
        self.character_name = character_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.error_message = error_message
        self.logs = logs or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'state': self.state,
            'progress': self.progress,
            'character_name': self.character_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'error_message': self.error_message,
            'logs': self.logs
        }


class BookGenEngine:
    """
    Main orchestration engine for biography generation
    
    Coordinates all services, manages state, handles errors, and tracks progress
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize BookGen engine
        
        Args:
            db_session: Optional database session (creates new if not provided)
        """
        self.db = db_session or SessionLocal()
        self._should_close_db = db_session is None
        
        # Initialize components
        self.state_machines: Dict[int, StateMachine] = {}
        self.error_handlers: Dict[int, ErrorHandler] = {}
        self.workflow_managers: Dict[int, WorkflowManager] = {}
        
        logger.info("BookGen Engine initialized")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._should_close_db:
            self.db.close()
    
    def _get_or_create_components(
        self,
        job_id: int
    ) -> tuple[StateMachine, ErrorHandler, WorkflowManager]:
        """
        Get or create engine components for a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Tuple of (state_machine, error_handler, workflow_manager)
        """
        if job_id not in self.state_machines:
            # Load state from database
            job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            
            if job and job.job_metadata and 'state_machine' in job.job_metadata:
                # Restore from saved state
                state_machine = StateMachine.from_dict(job.job_metadata['state_machine'])
            else:
                # Create new state machine
                state_machine = StateMachine()
            
            self.state_machines[job_id] = state_machine
            
            # Create error handler
            error_handler = ErrorHandler(max_retries=3)
            self.error_handlers[job_id] = error_handler
            
            # Create workflow manager
            workflow_manager = WorkflowManager(state_machine, error_handler)
            self.workflow_managers[job_id] = workflow_manager
            
            # Register workflow phases
            self._register_workflow_phases(workflow_manager, job_id)
        
        return (
            self.state_machines[job_id],
            self.error_handlers[job_id],
            self.workflow_managers[job_id]
        )
    
    def _register_workflow_phases(self, workflow_manager: WorkflowManager, job_id: int):
        """
        Register all workflow phases
        
        Args:
            workflow_manager: Workflow manager to register phases with
            job_id: Job ID
        """
        # Register each phase with its executor
        workflow_manager.register_phase(
            GenerationState.INITIALIZED,
            lambda ctx: self._phase_initialize(ctx),
            description="Initialize generation job",
            estimated_duration=10
        )
        
        workflow_manager.register_phase(
            GenerationState.SOURCES_VALIDATING,
            lambda ctx: self._phase_validate_sources(ctx),
            description="Validate biographical sources",
            estimated_duration=60
        )
        
        workflow_manager.register_phase(
            GenerationState.CONTENT_GENERATING,
            lambda ctx: self._phase_generate_content(ctx),
            description="Generate biography content",
            estimated_duration=600
        )
        
        workflow_manager.register_phase(
            GenerationState.CHAPTERS_VALIDATING,
            lambda ctx: self._phase_validate_chapters(ctx),
            description="Validate generated chapters",
            estimated_duration=120
        )
        
        workflow_manager.register_phase(
            GenerationState.CONCATENATING,
            lambda ctx: self._phase_concatenate(ctx),
            description="Concatenate biography sections",
            estimated_duration=30
        )
        
        workflow_manager.register_phase(
            GenerationState.EXPORTING,
            lambda ctx: self._phase_export(ctx),
            description="Export to final format",
            estimated_duration=60
        )
    
    def _phase_initialize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize phase - setup job and verify prerequisites"""
        logger.info(f"Initializing job {context['job_id']}")
        
        job_id = context['job_id']
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Update job status
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        job.current_phase = "initialized"
        self.db.commit()
        
        self._add_log(job_id, "INFO", "Job initialized successfully")
        
        return {'status': 'initialized', 'job_id': job_id}
    
    def _phase_validate_sources(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sources phase - verify biographical sources"""
        logger.info(f"Validating sources for job {context['job_id']}")
        
        job_id = context['job_id']
        self._update_job_phase(job_id, "sources_validating")
        self._add_log(job_id, "INFO", "Validating biographical sources")
        
        # TODO: Integrate with source validation service
        # For now, placeholder implementation
        
        return {'status': 'sources_validated', 'source_count': 0}
    
    def _phase_generate_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content phase - create biography chapters"""
        logger.info(f"Generating content for job {context['job_id']}")
        
        job_id = context['job_id']
        self._update_job_phase(job_id, "content_generating")
        self._add_log(job_id, "INFO", "Generating biography content")
        
        # TODO: Integrate with content generation tasks
        # For now, placeholder implementation
        
        return {'status': 'content_generated', 'chapters': 0}
    
    def _phase_validate_chapters(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate chapters phase - verify chapter quality"""
        logger.info(f"Validating chapters for job {context['job_id']}")
        
        job_id = context['job_id']
        self._update_job_phase(job_id, "chapters_validating")
        self._add_log(job_id, "INFO", "Validating generated chapters")
        
        # TODO: Integrate with chapter validation
        # For now, placeholder implementation
        
        return {'status': 'chapters_validated', 'valid_chapters': 0}
    
    def _phase_concatenate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Concatenate phase - combine all sections"""
        logger.info(f"Concatenating biography for job {context['job_id']}")
        
        job_id = context['job_id']
        self._update_job_phase(job_id, "concatenating")
        self._add_log(job_id, "INFO", "Concatenating biography sections")
        
        # TODO: Integrate with concatenation service
        # For now, placeholder implementation
        
        return {'status': 'concatenated', 'file_path': None}
    
    def _phase_export(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Export phase - export to final format"""
        logger.info(f"Exporting biography for job {context['job_id']}")
        
        job_id = context['job_id']
        self._update_job_phase(job_id, "exporting")
        self._add_log(job_id, "INFO", "Exporting to final format")
        
        # TODO: Integrate with export service
        # For now, placeholder implementation
        
        return {'status': 'exported', 'export_path': None}
    
    def _update_job_phase(self, job_id: int, phase: str):
        """Update job current phase"""
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            job.current_phase = phase
            job.updated_at = datetime.now(timezone.utc)
            self.db.commit()
    
    def _add_log(self, job_id: int, level: str, message: str, metadata: Optional[Dict] = None):
        """Add log entry to job"""
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            logs = job.logs or []
            logs.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': level,
                'message': message,
                'metadata': metadata or {}
            })
            job.logs = logs
            flag_modified(job, "logs")  # Tell SQLAlchemy that the JSON column changed
            self.db.commit()
    
    def _save_state(self, job_id: int):
        """Save state machine state to database"""
        state_machine = self.state_machines.get(job_id)
        if not state_machine:
            return
        
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            metadata = job.job_metadata or {}
            metadata['state_machine'] = state_machine.to_dict()
            job.job_metadata = metadata
            flag_modified(job, "job_metadata")  # Tell SQLAlchemy that the JSON column changed
            job.progress = state_machine.get_progress_percentage()
            job.updated_at = datetime.now(timezone.utc)
            self.db.commit()
    
    def generate_biography(self, character: str) -> int:
        """
        Start biography generation for a character
        
        Args:
            character: Name of the biographical subject
            
        Returns:
            Job ID
        """
        logger.info(f"Starting biography generation for: {character}")
        
        # Create biography record
        biography = Biography(
            character_name=character,
            status="pending"
        )
        self.db.add(biography)
        self.db.commit()
        self.db.refresh(biography)
        
        # Create generation job
        job = GenerationJob(
            biography_id=biography.id,
            status="pending",
            progress=0.0,
            current_phase="initialized",
            logs=[{
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': 'INFO',
                'message': f'Biography generation job created for {character}'
            }]
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Initialize components
        state_machine, error_handler, workflow_manager = self._get_or_create_components(job.id)
        
        # Execute workflow asynchronously (in production, use Celery)
        # For now, we'll just mark it as pending
        logger.info(f"Job {job.id} created for character: {character}")
        
        # TODO: Trigger async workflow execution via Celery
        # For now, return job ID
        
        return job.id
    
    def get_status(self, job_id: int) -> JobStatus:
        """
        Get status of a generation job
        
        Args:
            job_id: Job ID
            
        Returns:
            JobStatus object with current status
        """
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        biography = self.db.query(Biography).filter(Biography.id == job.biography_id).first()
        
        # Get state machine if available
        state_machine = self.state_machines.get(job_id)
        if state_machine:
            state = state_machine.get_state().value
            progress = state_machine.get_progress_percentage()
        else:
            # Try to restore from database
            if job.job_metadata and 'state_machine' in job.job_metadata:
                state_machine = StateMachine.from_dict(job.job_metadata['state_machine'])
                state = state_machine.get_state().value
                progress = state_machine.get_progress_percentage()
            else:
                state = job.status
                progress = job.progress
        
        return JobStatus(
            job_id=job.id,
            state=state,
            progress=progress,
            character_name=biography.character_name if biography else "Unknown",
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message,
            logs=job.logs
        )
    
    def execute_job(self, job_id: int) -> Dict[str, Any]:
        """
        Execute a generation job
        
        Args:
            job_id: Job ID to execute
            
        Returns:
            Execution result
        """
        logger.info(f"Executing job {job_id}")
        
        # Get components
        state_machine, error_handler, workflow_manager = self._get_or_create_components(job_id)
        
        # Create execution context
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        biography = self.db.query(Biography).filter(Biography.id == job.biography_id).first()
        
        context = {
            'job_id': job_id,
            'biography_id': job.biography_id,
            'character': biography.character_name if biography else "Unknown",
            'db': self.db
        }
        
        # Execute workflow
        try:
            result = workflow_manager.execute_workflow(context)
            
            # Update job based on result
            if result['success']:
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)
                job.progress = 100.0
                if biography:
                    biography.status = "completed"
                    biography.completed_at = datetime.now(timezone.utc)
            else:
                job.status = "failed"
                job.error_message = result.get('error', {}).get('error_context', {}).get('error_message', 'Unknown error')
                if biography:
                    biography.status = "failed"
                    biography.error_message = job.error_message
            
            # Save state
            self._save_state(job_id)
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Job {job_id} execution failed: {e}", exc_info=True)
            
            job.status = "failed"
            job.error_message = str(e)
            if biography:
                biography.status = "failed"
                biography.error_message = str(e)
            
            self._save_state(job_id)
            self.db.commit()
            
            raise
    
    def pause_job(self, job_id: int):
        """Pause a running job"""
        workflow_manager = self.workflow_managers.get(job_id)
        if not workflow_manager:
            raise ValueError(f"No active workflow for job {job_id}")
        
        workflow_manager.pause_workflow()
        
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            job.status = "paused"
            self._save_state(job_id)
            self.db.commit()
        
        logger.info(f"Job {job_id} paused")
    
    def resume_job(self, job_id: int) -> Dict[str, Any]:
        """Resume a paused job"""
        state_machine, error_handler, workflow_manager = self._get_or_create_components(job_id)
        
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        biography = self.db.query(Biography).filter(Biography.id == job.biography_id).first()
        
        context = {
            'job_id': job_id,
            'biography_id': job.biography_id,
            'character': biography.character_name if biography else "Unknown",
            'db': self.db
        }
        
        result = workflow_manager.resume_workflow(context)
        
        job.status = "running"
        self._save_state(job_id)
        self.db.commit()
        
        logger.info(f"Job {job_id} resumed")
        
        return result
