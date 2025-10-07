"""
Error Handler for BookGen Engine
Handles errors, recovery strategies, and rollback operations
"""
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone
from enum import Enum

from .state_machine import GenerationState

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Recoverable, retry same phase
    MEDIUM = "medium"     # Recoverable, may need to go back one phase
    HIGH = "high"         # Requires manual intervention or full restart
    CRITICAL = "critical" # Unrecoverable, job must fail


class ErrorType(Enum):
    """Types of errors that can occur"""
    VALIDATION_ERROR = "validation_error"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    FILE_ERROR = "file_error"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    GENERATION_ERROR = "generation_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY_CURRENT = "retry_current"         # Retry current phase
    RETRY_PREVIOUS = "retry_previous"       # Go back to previous phase
    RESTART = "restart"                     # Restart from beginning
    MANUAL = "manual"                       # Requires manual intervention
    FAIL = "fail"                           # Fail the job


class ErrorContext:
    """Context information for an error"""
    
    def __init__(
        self,
        error: Exception,
        error_type: ErrorType,
        severity: ErrorSeverity,
        state: GenerationState,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.error = error
        self.error_type = error_type
        self.severity = severity
        self.state = state
        self.timestamp = datetime.now(timezone.utc)
        self.metadata = metadata or {}
        self.retry_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary"""
        return {
            'error_message': str(self.error),
            'error_type': self.error_type.value,
            'severity': self.severity.value,
            'state': self.state.value,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count,
            'metadata': self.metadata
        }


class ErrorHandler:
    """
    Handles errors during biography generation workflow
    
    Provides error classification, recovery strategies, and rollback operations
    """
    
    # Define error type to severity mapping
    ERROR_SEVERITY_MAP = {
        ErrorType.VALIDATION_ERROR: ErrorSeverity.MEDIUM,
        ErrorType.API_ERROR: ErrorSeverity.MEDIUM,
        ErrorType.DATABASE_ERROR: ErrorSeverity.HIGH,
        ErrorType.FILE_ERROR: ErrorSeverity.MEDIUM,
        ErrorType.TIMEOUT_ERROR: ErrorSeverity.LOW,
        ErrorType.NETWORK_ERROR: ErrorSeverity.LOW,
        ErrorType.GENERATION_ERROR: ErrorSeverity.MEDIUM,
        ErrorType.UNKNOWN_ERROR: ErrorSeverity.HIGH,
    }
    
    # Define recovery strategies by error type and severity
    RECOVERY_STRATEGIES = {
        (ErrorType.VALIDATION_ERROR, ErrorSeverity.MEDIUM): RecoveryStrategy.RETRY_PREVIOUS,
        (ErrorType.API_ERROR, ErrorSeverity.MEDIUM): RecoveryStrategy.RETRY_CURRENT,
        (ErrorType.DATABASE_ERROR, ErrorSeverity.HIGH): RecoveryStrategy.MANUAL,
        (ErrorType.FILE_ERROR, ErrorSeverity.MEDIUM): RecoveryStrategy.RETRY_CURRENT,
        (ErrorType.TIMEOUT_ERROR, ErrorSeverity.LOW): RecoveryStrategy.RETRY_CURRENT,
        (ErrorType.NETWORK_ERROR, ErrorSeverity.LOW): RecoveryStrategy.RETRY_CURRENT,
        (ErrorType.GENERATION_ERROR, ErrorSeverity.MEDIUM): RecoveryStrategy.RETRY_CURRENT,
    }
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize error handler
        
        Args:
            max_retries: Maximum number of retries before failing
        """
        self.max_retries = max_retries
        self.error_history = []
        self.rollback_handlers: Dict[GenerationState, Callable] = {}
        
        logger.info(f"Error handler initialized with max_retries={max_retries}")
    
    def classify_error(
        self,
        error: Exception,
        state: GenerationState,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """
        Classify an error and create error context
        
        Args:
            error: The exception that occurred
            state: Current state when error occurred
            metadata: Additional metadata about the error
            
        Returns:
            ErrorContext with classification information
        """
        # Determine error type
        error_type = self._determine_error_type(error)
        
        # Get severity
        severity = self.ERROR_SEVERITY_MAP.get(error_type, ErrorSeverity.HIGH)
        
        # Create error context
        context = ErrorContext(
            error=error,
            error_type=error_type,
            severity=severity,
            state=state,
            metadata=metadata
        )
        
        self.error_history.append(context)
        
        logger.error(
            f"Error classified: {error_type.value} (severity: {severity.value}) "
            f"in state {state.value}: {str(error)}",
            exc_info=True
        )
        
        return context
    
    def _determine_error_type(self, error: Exception) -> ErrorType:
        """
        Determine error type from exception
        
        Args:
            error: The exception
            
        Returns:
            ErrorType classification
        """
        error_name = error.__class__.__name__.lower()
        error_msg = str(error).lower()
        
        # Check for specific error types
        if 'validation' in error_msg or 'invalid' in error_msg:
            return ErrorType.VALIDATION_ERROR
        elif 'api' in error_msg or 'request' in error_msg or 'response' in error_msg:
            return ErrorType.API_ERROR
        elif 'database' in error_msg or 'sql' in error_msg:
            return ErrorType.DATABASE_ERROR
        elif 'file' in error_msg or 'io' in error_msg:
            return ErrorType.FILE_ERROR
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            return ErrorType.TIMEOUT_ERROR
        elif 'network' in error_msg or 'connection' in error_msg:
            return ErrorType.NETWORK_ERROR
        elif 'generation' in error_msg or 'content' in error_msg:
            return ErrorType.GENERATION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def get_recovery_strategy(
        self,
        error_context: ErrorContext
    ) -> RecoveryStrategy:
        """
        Determine recovery strategy for an error
        
        Args:
            error_context: Error context
            
        Returns:
            Recommended recovery strategy
        """
        # Check if max retries exceeded
        if error_context.retry_count >= self.max_retries:
            logger.warning(
                f"Max retries ({self.max_retries}) exceeded for {error_context.error_type.value}"
            )
            return RecoveryStrategy.FAIL
        
        # Get strategy from map
        key = (error_context.error_type, error_context.severity)
        strategy = self.RECOVERY_STRATEGIES.get(key, RecoveryStrategy.FAIL)
        
        # For critical severity, always fail
        if error_context.severity == ErrorSeverity.CRITICAL:
            strategy = RecoveryStrategy.FAIL
        
        logger.info(
            f"Recovery strategy for {error_context.error_type.value}: {strategy.value}"
        )
        
        return strategy
    
    def register_rollback_handler(
        self,
        state: GenerationState,
        handler: Callable
    ):
        """
        Register a rollback handler for a specific state
        
        Args:
            state: State to register handler for
            handler: Callable that performs rollback operations
        """
        self.rollback_handlers[state] = handler
        logger.debug(f"Registered rollback handler for state: {state.value}")
    
    def rollback(
        self,
        state: GenerationState,
        job_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute rollback for a specific state
        
        Args:
            state: State to rollback from
            job_id: Job ID
            metadata: Additional metadata
            
        Returns:
            True if rollback was successful
        """
        logger.info(f"Executing rollback for state: {state.value}, job_id: {job_id}")
        
        handler = self.rollback_handlers.get(state)
        if handler:
            try:
                handler(job_id, metadata or {})
                logger.info(f"Rollback successful for state: {state.value}")
                return True
            except Exception as e:
                logger.error(f"Rollback failed for state {state.value}: {e}", exc_info=True)
                return False
        else:
            logger.warning(f"No rollback handler registered for state: {state.value}")
            return False
    
    def handle_error(
        self,
        error: Exception,
        state: GenerationState,
        job_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and determine next action
        
        Args:
            error: The exception that occurred
            state: Current state when error occurred
            job_id: Job ID
            metadata: Additional metadata
            
        Returns:
            Dictionary with error handling result and next action
        """
        # Classify error
        error_context = self.classify_error(error, state, metadata)
        
        # Get recovery strategy
        strategy = self.get_recovery_strategy(error_context)
        
        # Execute rollback if needed
        rollback_success = True
        if strategy in [RecoveryStrategy.RETRY_PREVIOUS, RecoveryStrategy.RESTART]:
            rollback_success = self.rollback(state, job_id, metadata)
        
        result = {
            'error_context': error_context.to_dict(),
            'recovery_strategy': strategy.value,
            'rollback_success': rollback_success,
            'next_state': self._get_next_state(state, strategy),
            'should_retry': strategy in [
                RecoveryStrategy.RETRY_CURRENT,
                RecoveryStrategy.RETRY_PREVIOUS
            ],
            'should_fail': strategy == RecoveryStrategy.FAIL
        }
        
        logger.info(
            f"Error handling result: strategy={strategy.value}, "
            f"next_state={result['next_state']}"
        )
        
        return result
    
    def _get_next_state(
        self,
        current_state: GenerationState,
        strategy: RecoveryStrategy
    ) -> Optional[str]:
        """
        Determine next state based on recovery strategy
        
        Args:
            current_state: Current state
            strategy: Recovery strategy
            
        Returns:
            Next state value or None
        """
        if strategy == RecoveryStrategy.RETRY_CURRENT:
            return current_state.value
        elif strategy == RecoveryStrategy.RETRY_PREVIOUS:
            # Map to previous state
            previous_states = {
                GenerationState.SOURCES_VALIDATING: GenerationState.INITIALIZED,
                GenerationState.CONTENT_GENERATING: GenerationState.SOURCES_VALIDATING,
                GenerationState.CHAPTERS_VALIDATING: GenerationState.CONTENT_GENERATING,
                GenerationState.CONCATENATING: GenerationState.CHAPTERS_VALIDATING,
                GenerationState.EXPORTING: GenerationState.CONCATENATING,
            }
            prev_state = previous_states.get(current_state)
            return prev_state.value if prev_state else None
        elif strategy == RecoveryStrategy.RESTART:
            return GenerationState.INITIALIZED.value
        elif strategy == RecoveryStrategy.FAIL:
            return GenerationState.FAILED.value
        else:
            return None
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all errors
        
        Returns:
            Dictionary with error statistics
        """
        total_errors = len(self.error_history)
        errors_by_type = {}
        errors_by_severity = {}
        
        for context in self.error_history:
            # Count by type
            type_key = context.error_type.value
            errors_by_type[type_key] = errors_by_type.get(type_key, 0) + 1
            
            # Count by severity
            severity_key = context.severity.value
            errors_by_severity[severity_key] = errors_by_severity.get(severity_key, 0) + 1
        
        return {
            'total_errors': total_errors,
            'errors_by_type': errors_by_type,
            'errors_by_severity': errors_by_severity,
            'recent_errors': [e.to_dict() for e in self.error_history[-5:]]
        }
