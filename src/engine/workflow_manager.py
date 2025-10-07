"""
Workflow Manager for BookGen Engine
Manages the execution of different workflow phases
"""
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone

from .state_machine import GenerationState, StateMachine
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class WorkflowPhase:
    """Represents a single phase in the workflow"""
    
    def __init__(
        self,
        name: str,
        state: GenerationState,
        executor: Callable,
        description: str = "",
        estimated_duration: int = 60
    ):
        """
        Initialize workflow phase
        
        Args:
            name: Phase name
            state: Associated generation state
            executor: Callable that executes the phase
            description: Phase description
            estimated_duration: Estimated duration in seconds
        """
        self.name = name
        self.state = state
        self.executor = executor
        self.description = description
        self.estimated_duration = estimated_duration
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the phase
        
        Args:
            context: Execution context
            
        Returns:
            Phase execution result
        """
        logger.info(f"Executing phase: {self.name}")
        start_time = datetime.now(timezone.utc)
        
        try:
            result = self.executor(context)
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Phase {self.name} completed in {duration:.2f}s")
            
            return {
                'success': True,
                'phase': self.name,
                'state': self.state.value,
                'duration': duration,
                'result': result,
                'timestamp': end_time.isoformat()
            }
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Phase {self.name} failed after {duration:.2f}s: {e}", exc_info=True)
            
            return {
                'success': False,
                'phase': self.name,
                'state': self.state.value,
                'duration': duration,
                'error': str(e),
                'timestamp': end_time.isoformat()
            }


class WorkflowManager:
    """
    Manages the biography generation workflow
    
    Coordinates phase execution, state transitions, and progress tracking
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        error_handler: ErrorHandler
    ):
        """
        Initialize workflow manager
        
        Args:
            state_machine: State machine for tracking workflow state
            error_handler: Error handler for managing errors
        """
        self.state_machine = state_machine
        self.error_handler = error_handler
        self.phases: Dict[GenerationState, WorkflowPhase] = {}
        self.execution_log = []
        
        logger.info("Workflow manager initialized")
    
    def register_phase(
        self,
        state: GenerationState,
        executor: Callable,
        name: Optional[str] = None,
        description: str = "",
        estimated_duration: int = 60
    ):
        """
        Register a workflow phase
        
        Args:
            state: State associated with this phase
            executor: Callable that executes the phase
            name: Optional phase name (defaults to state name)
            description: Phase description
            estimated_duration: Estimated duration in seconds
        """
        phase_name = name or state.value
        phase = WorkflowPhase(
            name=phase_name,
            state=state,
            executor=executor,
            description=description,
            estimated_duration=estimated_duration
        )
        
        self.phases[state] = phase
        logger.debug(f"Registered phase: {phase_name} for state {state.value}")
    
    def execute_phase(
        self,
        state: GenerationState,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific workflow phase
        
        Args:
            state: State/phase to execute
            context: Execution context with job information
            
        Returns:
            Phase execution result
        """
        phase = self.phases.get(state)
        if not phase:
            raise ValueError(f"No phase registered for state: {state.value}")
        
        # Transition to the state
        try:
            self.state_machine.transition(state)
        except ValueError as e:
            logger.warning(f"State transition warning: {e}")
            # Force transition for retry scenarios
            self.state_machine.transition(state, force=True)
        
        # Execute the phase
        result = phase.execute(context)
        
        # Log execution
        self.execution_log.append({
            'phase': phase.name,
            'state': state.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': result['success'],
            'duration': result.get('duration', 0)
        })
        
        return result
    
    def execute_workflow(
        self,
        context: Dict[str, Any],
        start_state: Optional[GenerationState] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow
        
        Args:
            context: Execution context with job information
            start_state: Optional starting state (for resume)
            
        Returns:
            Workflow execution result
        """
        logger.info(f"Starting workflow execution for job {context.get('job_id')}")
        
        # Define workflow sequence
        workflow_sequence = [
            GenerationState.INITIALIZED,
            GenerationState.SOURCES_VALIDATING,
            GenerationState.CONTENT_GENERATING,
            GenerationState.CHAPTERS_VALIDATING,
            GenerationState.CONCATENATING,
            GenerationState.EXPORTING,
        ]
        
        # Determine starting point
        start_index = 0
        if start_state:
            try:
                start_index = workflow_sequence.index(start_state)
            except ValueError:
                logger.warning(f"Start state {start_state.value} not in sequence, starting from beginning")
        
        # Execute phases in sequence
        workflow_result = {
            'job_id': context.get('job_id'),
            'start_time': datetime.now(timezone.utc).isoformat(),
            'phases_executed': [],
            'success': False,
            'final_state': None,
            'error': None
        }
        
        for state in workflow_sequence[start_index:]:
            # Check if we should stop (e.g., paused)
            if self.state_machine.is_paused():
                logger.info("Workflow paused")
                workflow_result['final_state'] = GenerationState.PAUSED.value
                break
            
            # Execute phase
            try:
                phase_result = self.execute_phase(state, context)
                workflow_result['phases_executed'].append(phase_result)
                
                if not phase_result['success']:
                    # Handle error
                    error_info = self.error_handler.handle_error(
                        error=Exception(phase_result.get('error', 'Unknown error')),
                        state=state,
                        job_id=context.get('job_id'),
                        metadata={'phase': phase_result['phase']}
                    )
                    
                    workflow_result['error'] = error_info
                    
                    if error_info['should_fail']:
                        logger.error(f"Workflow failed in phase {state.value}")
                        self.state_machine.transition(GenerationState.FAILED, force=True)
                        workflow_result['final_state'] = GenerationState.FAILED.value
                        break
                    elif error_info['should_retry']:
                        logger.info(f"Retrying phase {state.value}")
                        # Retry logic would go here
                        continue
                    
            except Exception as e:
                logger.error(f"Unexpected error in phase {state.value}: {e}", exc_info=True)
                
                # Handle unexpected error
                error_info = self.error_handler.handle_error(
                    error=e,
                    state=state,
                    job_id=context.get('job_id'),
                    metadata={'phase': state.value}
                )
                
                workflow_result['error'] = error_info
                self.state_machine.transition(GenerationState.FAILED, force=True)
                workflow_result['final_state'] = GenerationState.FAILED.value
                break
        
        # Check if completed successfully
        if self.state_machine.get_state() == GenerationState.EXPORTING:
            self.state_machine.transition(GenerationState.COMPLETED)
            workflow_result['success'] = True
            workflow_result['final_state'] = GenerationState.COMPLETED.value
        
        workflow_result['end_time'] = datetime.now(timezone.utc).isoformat()
        
        logger.info(
            f"Workflow execution completed. "
            f"Final state: {workflow_result['final_state']}, "
            f"Success: {workflow_result['success']}"
        )
        
        return workflow_result
    
    def pause_workflow(self):
        """Pause the workflow execution"""
        self.state_machine.transition(GenerationState.PAUSED, force=True)
        logger.info("Workflow paused")
    
    def resume_workflow(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resume a paused workflow
        
        Args:
            context: Execution context
            
        Returns:
            Workflow execution result
        """
        if not self.state_machine.is_paused():
            raise ValueError("Workflow is not paused")
        
        logger.info("Resuming paused workflow")
        
        # Determine resume state from history
        history = self.state_machine.get_history()
        resume_state = GenerationState.INITIALIZED
        
        if history:
            # Find the last non-paused state
            for transition in reversed(history):
                from_state = GenerationState(transition['from_state'])
                if from_state != GenerationState.PAUSED:
                    resume_state = from_state
                    break
        
        return self.execute_workflow(context, start_state=resume_state)
    
    def get_execution_log(self) -> list:
        """
        Get execution log
        
        Returns:
            List of execution log entries
        """
        return self.execution_log
    
    def get_progress_info(self) -> Dict[str, Any]:
        """
        Get current progress information
        
        Returns:
            Dictionary with progress details
        """
        return {
            'current_state': self.state_machine.get_state().value,
            'progress_percentage': self.state_machine.get_progress_percentage(),
            'is_paused': self.state_machine.is_paused(),
            'is_complete': self.state_machine.is_terminal_state(),
            'phases_executed': len(self.execution_log),
            'state_history': self.state_machine.get_history()
        }
