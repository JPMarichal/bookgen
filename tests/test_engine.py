"""
Tests for BookGen Engine
Integration tests for the orchestration engine
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.engine.bookgen_engine import BookGenEngine, JobStatus
from src.engine.state_machine import GenerationState, StateMachine, StateTransition
from src.engine.error_handler import ErrorHandler, ErrorSeverity, ErrorType, RecoveryStrategy
from src.engine.workflow_manager import WorkflowManager, WorkflowPhase
from src.database.base import Base
from src.models.generation_job import GenerationJob
from src.models.biography import Biography


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestGenerationState:
    """Test GenerationState enum"""
    
    def test_state_values(self):
        """Test that all required states exist"""
        assert GenerationState.INITIALIZED.value == "initialized"
        assert GenerationState.SOURCES_VALIDATING.value == "sources_validating"
        assert GenerationState.CONTENT_GENERATING.value == "content_generating"
        assert GenerationState.CHAPTERS_VALIDATING.value == "chapters_validating"
        assert GenerationState.CONCATENATING.value == "concatenating"
        assert GenerationState.EXPORTING.value == "exporting"
        assert GenerationState.COMPLETED.value == "completed"
        assert GenerationState.FAILED.value == "failed"
    
    def test_state_string_conversion(self):
        """Test state to string conversion"""
        state = GenerationState.INITIALIZED
        assert str(state) == "initialized"


class TestStateMachine:
    """Test StateMachine class"""
    
    def test_initialization(self):
        """Test state machine initialization"""
        machine = StateMachine()
        assert machine.get_state() == GenerationState.INITIALIZED
        assert len(machine.history) == 0
    
    def test_valid_transition(self):
        """Test valid state transition"""
        machine = StateMachine()
        result = machine.transition(GenerationState.SOURCES_VALIDATING)
        assert result is True
        assert machine.get_state() == GenerationState.SOURCES_VALIDATING
        assert len(machine.history) == 1
    
    def test_invalid_transition(self):
        """Test invalid state transition raises error"""
        machine = StateMachine()
        with pytest.raises(ValueError) as exc_info:
            machine.transition(GenerationState.COMPLETED)
        assert "Invalid transition" in str(exc_info.value)
    
    def test_forced_transition(self):
        """Test forced transition bypasses validation"""
        machine = StateMachine()
        result = machine.transition(GenerationState.COMPLETED, force=True)
        assert result is True
        assert machine.get_state() == GenerationState.COMPLETED
    
    def test_can_transition(self):
        """Test can_transition check"""
        machine = StateMachine()
        assert machine.can_transition(GenerationState.SOURCES_VALIDATING) is True
        assert machine.can_transition(GenerationState.COMPLETED) is False
    
    def test_transition_history(self):
        """Test transition history tracking"""
        machine = StateMachine()
        machine.transition(GenerationState.SOURCES_VALIDATING)
        machine.transition(GenerationState.CONTENT_GENERATING)
        
        history = machine.get_history()
        assert len(history) == 2
        assert history[0]['from_state'] == 'initialized'
        assert history[0]['to_state'] == 'sources_validating'
        assert history[1]['from_state'] == 'sources_validating'
        assert history[1]['to_state'] == 'content_generating'
    
    def test_is_terminal_state(self):
        """Test terminal state detection"""
        machine = StateMachine()
        assert machine.is_terminal_state() is False
        
        machine.transition(GenerationState.COMPLETED, force=True)
        assert machine.is_terminal_state() is True
    
    def test_is_paused(self):
        """Test paused state detection"""
        machine = StateMachine()
        assert machine.is_paused() is False
        
        machine.transition(GenerationState.PAUSED, force=True)
        assert machine.is_paused() is True
    
    def test_progress_percentage(self):
        """Test progress percentage calculation"""
        machine = StateMachine()
        assert machine.get_progress_percentage() == 0.0
        
        machine.transition(GenerationState.SOURCES_VALIDATING)
        assert machine.get_progress_percentage() == 10.0
        
        machine.transition(GenerationState.CONTENT_GENERATING)
        assert machine.get_progress_percentage() == 30.0
        
        machine.transition(GenerationState.COMPLETED, force=True)
        assert machine.get_progress_percentage() == 100.0
    
    def test_reset(self):
        """Test state machine reset"""
        machine = StateMachine()
        machine.transition(GenerationState.SOURCES_VALIDATING)
        machine.transition(GenerationState.CONTENT_GENERATING)
        
        machine.reset()
        assert machine.get_state() == GenerationState.INITIALIZED
        assert len(machine.history) == 0
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        machine = StateMachine()
        machine.transition(GenerationState.SOURCES_VALIDATING)
        machine.metadata = {'test': 'value'}
        
        # Serialize
        data = machine.to_dict()
        assert data['current_state'] == 'sources_validating'
        assert data['progress'] == 10.0
        assert len(data['history']) == 1
        
        # Deserialize
        machine2 = StateMachine.from_dict(data)
        assert machine2.get_state() == GenerationState.SOURCES_VALIDATING
        assert len(machine2.history) == 1
        assert machine2.metadata == {'test': 'value'}


class TestErrorHandler:
    """Test ErrorHandler class"""
    
    def test_initialization(self):
        """Test error handler initialization"""
        handler = ErrorHandler(max_retries=5)
        assert handler.max_retries == 5
        assert len(handler.error_history) == 0
    
    def test_classify_error(self):
        """Test error classification"""
        handler = ErrorHandler()
        
        error = ValueError("Validation failed")
        context = handler.classify_error(error, GenerationState.SOURCES_VALIDATING)
        
        assert context.error_type == ErrorType.VALIDATION_ERROR
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.state == GenerationState.SOURCES_VALIDATING
        assert len(handler.error_history) == 1
    
    def test_get_recovery_strategy(self):
        """Test recovery strategy determination"""
        handler = ErrorHandler(max_retries=3)
        
        # Test normal recovery
        error = TimeoutError("Request timed out")
        context = handler.classify_error(error, GenerationState.CONTENT_GENERATING)
        strategy = handler.get_recovery_strategy(context)
        assert strategy == RecoveryStrategy.RETRY_CURRENT
        
        # Test max retries exceeded
        context.retry_count = 5
        strategy = handler.get_recovery_strategy(context)
        assert strategy == RecoveryStrategy.FAIL
    
    def test_rollback_handler_registration(self):
        """Test rollback handler registration"""
        handler = ErrorHandler()
        
        def rollback_func(job_id, metadata):
            pass
        
        handler.register_rollback_handler(GenerationState.CONTENT_GENERATING, rollback_func)
        assert GenerationState.CONTENT_GENERATING in handler.rollback_handlers
    
    def test_handle_error(self):
        """Test error handling"""
        handler = ErrorHandler()
        
        error = TimeoutError("API timeout")
        result = handler.handle_error(
            error,
            GenerationState.CONTENT_GENERATING,
            job_id=1,
            metadata={'attempt': 1}
        )
        
        assert 'error_context' in result
        assert 'recovery_strategy' in result
        assert result['should_retry'] is True
        assert result['should_fail'] is False
    
    def test_error_summary(self):
        """Test error summary generation"""
        handler = ErrorHandler()
        
        # Add some errors
        handler.classify_error(ValueError("validation"), GenerationState.SOURCES_VALIDATING)
        handler.classify_error(TimeoutError("timeout"), GenerationState.CONTENT_GENERATING)
        
        summary = handler.get_error_summary()
        assert summary['total_errors'] == 2
        assert 'errors_by_type' in summary
        assert 'errors_by_severity' in summary


class TestWorkflowManager:
    """Test WorkflowManager class"""
    
    def test_initialization(self):
        """Test workflow manager initialization"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        assert manager.state_machine == state_machine
        assert manager.error_handler == error_handler
        assert len(manager.phases) == 0
    
    def test_register_phase(self):
        """Test phase registration"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        def test_executor(context):
            return {'status': 'success'}
        
        manager.register_phase(
            GenerationState.INITIALIZED,
            test_executor,
            description="Test phase"
        )
        
        assert GenerationState.INITIALIZED in manager.phases
        phase = manager.phases[GenerationState.INITIALIZED]
        assert phase.description == "Test phase"
    
    def test_execute_phase(self):
        """Test phase execution"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        def test_executor(context):
            return {'status': 'success', 'data': context.get('test_data')}
        
        manager.register_phase(GenerationState.INITIALIZED, test_executor)
        
        result = manager.execute_phase(
            GenerationState.INITIALIZED,
            {'job_id': 1, 'test_data': 'test'}
        )
        
        assert result['success'] is True
        assert result['result']['status'] == 'success'
        assert result['result']['data'] == 'test'
    
    def test_execute_phase_with_error(self):
        """Test phase execution with error"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        def failing_executor(context):
            raise ValueError("Test error")
        
        manager.register_phase(GenerationState.INITIALIZED, failing_executor)
        
        result = manager.execute_phase(
            GenerationState.INITIALIZED,
            {'job_id': 1}
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_pause_and_resume(self):
        """Test workflow pause and resume"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        manager.pause_workflow()
        assert state_machine.is_paused() is True
    
    def test_get_progress_info(self):
        """Test progress information retrieval"""
        state_machine = StateMachine()
        error_handler = ErrorHandler()
        manager = WorkflowManager(state_machine, error_handler)
        
        info = manager.get_progress_info()
        assert 'current_state' in info
        assert 'progress_percentage' in info
        assert info['current_state'] == 'initialized'


class TestBookGenEngine:
    """Test BookGenEngine class"""
    
    def test_initialization(self, test_db):
        """Test engine initialization"""
        engine = BookGenEngine(db_session=test_db)
        assert engine.db == test_db
        assert len(engine.state_machines) == 0
    
    def test_generate_biography(self, test_db):
        """Test biography generation initiation"""
        engine = BookGenEngine(db_session=test_db)
        
        job_id = engine.generate_biography("winston_churchill")
        
        assert job_id is not None
        assert isinstance(job_id, int)
        
        # Verify job was created in database
        job = test_db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        assert job is not None
        assert job.status == "pending"
        assert job.progress == 0.0
    
    def test_get_status(self, test_db):
        """Test getting job status"""
        engine = BookGenEngine(db_session=test_db)
        
        # Create a job
        job_id = engine.generate_biography("winston_churchill")
        
        # Get status
        status = engine.get_status(job_id)
        
        assert isinstance(status, JobStatus)
        assert status.job_id == job_id
        assert status.character_name == "winston_churchill"
        assert status.state in ["pending", "initialized"]
        assert status.progress >= 0
    
    def test_get_status_nonexistent_job(self, test_db):
        """Test getting status for nonexistent job"""
        engine = BookGenEngine(db_session=test_db)
        
        with pytest.raises(ValueError) as exc_info:
            engine.get_status(999)
        assert "not found" in str(exc_info.value)
    
    def test_context_manager(self, test_db):
        """Test engine as context manager"""
        with BookGenEngine(db_session=test_db) as engine:
            assert engine is not None
            job_id = engine.generate_biography("test_character")
            assert job_id is not None


class TestIntegration:
    """Integration tests for the complete engine"""
    
    def test_complete_workflow_structure(self, test_db):
        """Test that complete workflow can be set up"""
        engine = BookGenEngine(db_session=test_db)
        
        # Create a job
        job_id = engine.generate_biography("winston_churchill")
        
        # Get components
        state_machine, error_handler, workflow_manager = engine._get_or_create_components(job_id)
        
        # Verify all components exist
        assert state_machine is not None
        assert error_handler is not None
        assert workflow_manager is not None
        
        # Verify phases are registered
        assert len(workflow_manager.phases) > 0
        assert GenerationState.INITIALIZED in workflow_manager.phases
        assert GenerationState.SOURCES_VALIDATING in workflow_manager.phases
        assert GenerationState.CONTENT_GENERATING in workflow_manager.phases
    
    def test_state_persistence(self, test_db):
        """Test that state is persisted to database"""
        engine = BookGenEngine(db_session=test_db)
        
        # Create a job
        job_id = engine.generate_biography("winston_churchill")
        
        # Get state machine and make a transition
        state_machine, _, _ = engine._get_or_create_components(job_id)
        state_machine.transition(GenerationState.SOURCES_VALIDATING)
        
        # Save state
        engine._save_state(job_id)
        
        # Retrieve job and verify state was saved
        job = test_db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        assert job.job_metadata is not None
        assert 'state_machine' in job.job_metadata
        assert job.job_metadata['state_machine']['current_state'] == 'sources_validating'
    
    def test_log_addition(self, test_db):
        """Test adding logs to job"""
        engine = BookGenEngine(db_session=test_db)
        
        # Create a job
        job_id = engine.generate_biography("winston_churchill")
        
        # Add a log
        engine._add_log(job_id, "INFO", "Test log message", {"key": "value"})
        
        # Refresh the session to get updated data
        test_db.expire_all()
        
        # Retrieve and verify
        job = test_db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        assert len(job.logs) >= 1
        
        # Find the test log
        test_log = next((log for log in job.logs if log['message'] == 'Test log message'), None)
        assert test_log is not None
        assert test_log['level'] == 'INFO'
        assert test_log['metadata']['key'] == 'value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
