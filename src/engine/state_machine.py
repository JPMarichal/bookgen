"""
State Machine for Biography Generation Workflow
Defines states and manages state transitions for the generation process
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GenerationState(Enum):
    """States for the biography generation workflow"""
    INITIALIZED = "initialized"
    SOURCES_VALIDATING = "sources_validating"
    CONTENT_GENERATING = "content_generating"
    CHAPTERS_VALIDATING = "chapters_validating"
    CONCATENATING = "concatenating"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    
    def __str__(self):
        return self.value


class StateTransition:
    """Represents a state transition"""
    
    def __init__(
        self,
        from_state: GenerationState,
        to_state: GenerationState,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary"""
        return {
            'from_state': self.from_state.value,
            'to_state': self.to_state.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class StateMachine:
    """
    State machine for managing biography generation workflow states
    
    Manages state transitions, validates allowed transitions, and tracks history
    """
    
    # Define allowed state transitions
    TRANSITIONS = {
        GenerationState.INITIALIZED: [
            GenerationState.SOURCES_VALIDATING,
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.SOURCES_VALIDATING: [
            GenerationState.CONTENT_GENERATING,
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.CONTENT_GENERATING: [
            GenerationState.CHAPTERS_VALIDATING,
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.CHAPTERS_VALIDATING: [
            GenerationState.CONCATENATING,
            GenerationState.CONTENT_GENERATING,  # Allow retry
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.CONCATENATING: [
            GenerationState.EXPORTING,
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.EXPORTING: [
            GenerationState.COMPLETED,
            GenerationState.FAILED,
            GenerationState.PAUSED
        ],
        GenerationState.COMPLETED: [],  # Terminal state
        GenerationState.FAILED: [
            GenerationState.INITIALIZED  # Allow retry from beginning
        ],
        GenerationState.PAUSED: [
            GenerationState.SOURCES_VALIDATING,
            GenerationState.CONTENT_GENERATING,
            GenerationState.CHAPTERS_VALIDATING,
            GenerationState.CONCATENATING,
            GenerationState.EXPORTING,
            GenerationState.FAILED
        ]
    }
    
    def __init__(self, initial_state: GenerationState = GenerationState.INITIALIZED):
        """
        Initialize state machine
        
        Args:
            initial_state: Starting state for the workflow
        """
        self.current_state = initial_state
        self.history: List[StateTransition] = []
        self.metadata: Dict[str, Any] = {}
        
        logger.info(f"State machine initialized with state: {initial_state.value}")
    
    def can_transition(self, to_state: GenerationState) -> bool:
        """
        Check if transition to a state is allowed
        
        Args:
            to_state: Target state
            
        Returns:
            True if transition is allowed
        """
        allowed_states = self.TRANSITIONS.get(self.current_state, [])
        return to_state in allowed_states
    
    def transition(
        self,
        to_state: GenerationState,
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> bool:
        """
        Transition to a new state
        
        Args:
            to_state: Target state
            metadata: Additional metadata for the transition
            force: Force transition even if not in allowed transitions
            
        Returns:
            True if transition was successful
            
        Raises:
            ValueError: If transition is not allowed and force=False
        """
        if not force and not self.can_transition(to_state):
            allowed = [s.value for s in self.TRANSITIONS.get(self.current_state, [])]
            raise ValueError(
                f"Invalid transition from {self.current_state.value} to {to_state.value}. "
                f"Allowed transitions: {allowed}"
            )
        
        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            metadata=metadata
        )
        self.history.append(transition)
        
        # Update current state
        old_state = self.current_state
        self.current_state = to_state
        
        logger.info(
            f"State transition: {old_state.value} -> {to_state.value}",
            extra={'metadata': metadata}
        )
        
        return True
    
    def get_state(self) -> GenerationState:
        """Get current state"""
        return self.current_state
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get state transition history
        
        Returns:
            List of transition dictionaries
        """
        return [t.to_dict() for t in self.history]
    
    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (completed or failed)"""
        return self.current_state in [GenerationState.COMPLETED, GenerationState.FAILED]
    
    def is_paused(self) -> bool:
        """Check if workflow is paused"""
        return self.current_state == GenerationState.PAUSED
    
    def get_progress_percentage(self) -> float:
        """
        Calculate progress percentage based on current state
        
        Returns:
            Progress as percentage (0-100)
        """
        state_progress = {
            GenerationState.INITIALIZED: 0.0,
            GenerationState.SOURCES_VALIDATING: 10.0,
            GenerationState.CONTENT_GENERATING: 30.0,
            GenerationState.CHAPTERS_VALIDATING: 70.0,
            GenerationState.CONCATENATING: 85.0,
            GenerationState.EXPORTING: 95.0,
            GenerationState.COMPLETED: 100.0,
            GenerationState.FAILED: 0.0,
            GenerationState.PAUSED: 0.0  # Use last known progress
        }
        
        return state_progress.get(self.current_state, 0.0)
    
    def reset(self):
        """Reset state machine to initial state"""
        self.current_state = GenerationState.INITIALIZED
        self.history = []
        self.metadata = {}
        logger.info("State machine reset to INITIALIZED")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state machine to dictionary
        
        Returns:
            Dictionary representation of state machine
        """
        return {
            'current_state': self.current_state.value,
            'progress': self.get_progress_percentage(),
            'is_terminal': self.is_terminal_state(),
            'is_paused': self.is_paused(),
            'history': self.get_history(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateMachine':
        """
        Create state machine from dictionary
        
        Args:
            data: Dictionary representation
            
        Returns:
            StateMachine instance
        """
        state = GenerationState(data['current_state'])
        machine = cls(initial_state=state)
        machine.metadata = data.get('metadata', {})
        
        # Reconstruct history
        for transition_data in data.get('history', []):
            transition = StateTransition(
                from_state=GenerationState(transition_data['from_state']),
                to_state=GenerationState(transition_data['to_state']),
                timestamp=datetime.fromisoformat(transition_data['timestamp']),
                metadata=transition_data.get('metadata', {})
            )
            machine.history.append(transition)
        
        return machine
