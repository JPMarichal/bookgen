#!/usr/bin/env python
"""
Demonstration of BookGen Engine
Shows the orchestration engine in action with state management and error handling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import init_db
from src.engine.bookgen_engine import BookGenEngine
from src.engine.state_machine import GenerationState


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_status(status):
    """Print job status in a formatted way"""
    print(f"\nJob ID: {status.job_id}")
    print(f"Character: {status.character_name}")
    print(f"State: {status.state}")
    print(f"Progress: {status.progress:.1f}%")
    print(f"Created: {status.created_at}")
    print(f"Updated: {status.updated_at}")
    if status.error_message:
        print(f"Error: {status.error_message}")
    if status.logs:
        print(f"\nLogs ({len(status.logs)} entries):")
        for log in status.logs[-3:]:  # Show last 3 logs
            print(f"  [{log['level']}] {log['message']}")


def demo_basic_usage():
    """Demonstrate basic engine usage"""
    print_header("1. Basic Engine Usage")
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    
    # Create engine
    print("Creating BookGen engine...")
    engine = BookGenEngine()
    
    # Start biography generation
    print("\nStarting biography generation for Winston Churchill...")
    job_id = engine.generate_biography("winston_churchill")
    print(f"✓ Job created with ID: {job_id}")
    
    # Get status
    print("\nChecking job status...")
    status = engine.get_status(job_id)
    print_status(status)
    
    # Verify states match issue requirements
    print("\n\nVerifying state machine states:")
    required_states = [
        'INITIALIZED', 'SOURCES_VALIDATING', 'CONTENT_GENERATING',
        'CHAPTERS_VALIDATING', 'CONCATENATING', 'EXPORTING',
        'COMPLETED', 'FAILED'
    ]
    for state_name in required_states:
        state = getattr(GenerationState, state_name, None)
        if state:
            print(f"  ✓ {state_name}: {state.value}")
    
    engine.db.close()
    print("\n✓ Basic usage demonstration complete!")


def demo_state_machine():
    """Demonstrate state machine functionality"""
    print_header("2. State Machine Demonstration")
    
    from src.engine.state_machine import StateMachine
    
    print("\nCreating state machine...")
    machine = StateMachine()
    print(f"Initial state: {machine.get_state().value}")
    print(f"Progress: {machine.get_progress_percentage()}%")
    
    # Valid transition
    print("\n\nTransitioning through workflow states:")
    states_sequence = [
        GenerationState.SOURCES_VALIDATING,
        GenerationState.CONTENT_GENERATING,
        GenerationState.CHAPTERS_VALIDATING,
        GenerationState.CONCATENATING,
        GenerationState.EXPORTING,
    ]
    
    for state in states_sequence:
        machine.transition(state)
        print(f"  → {state.value}: {machine.get_progress_percentage()}% complete")
    
    # Show transition history
    print("\n\nTransition history:")
    history = machine.get_history()
    for i, transition in enumerate(history[-3:], 1):  # Show last 3
        print(f"  {i}. {transition['from_state']} → {transition['to_state']}")
    
    # Test invalid transition
    print("\n\nTesting invalid transition (should fail):")
    try:
        machine.reset()
        machine.transition(GenerationState.COMPLETED)
        print("  ✗ Invalid transition was allowed (should have failed)")
    except ValueError as e:
        print(f"  ✓ Invalid transition blocked: {str(e)[:50]}...")
    
    # Test forced transition
    print("\nTesting forced transition:")
    machine.transition(GenerationState.COMPLETED, force=True)
    print(f"  ✓ Forced to {machine.get_state().value}")
    
    print("\n✓ State machine demonstration complete!")


def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print_header("3. Error Handling Demonstration")
    
    from src.engine.error_handler import ErrorHandler
    
    print("\nCreating error handler...")
    handler = ErrorHandler(max_retries=3)
    
    # Classify different types of errors
    print("\n\nClassifying different error types:")
    
    errors_to_test = [
        (ValueError("Validation failed"), "Validation error"),
        (TimeoutError("Request timed out"), "Timeout error"),
        (ConnectionError("Network error"), "Network error"),
    ]
    
    for error, description in errors_to_test:
        context = handler.classify_error(error, GenerationState.CONTENT_GENERATING)
        strategy = handler.get_recovery_strategy(context)
        print(f"\n  {description}:")
        print(f"    Type: {context.error_type.value}")
        print(f"    Severity: {context.severity.value}")
        print(f"    Recovery: {strategy.value}")
    
    # Show error summary
    print("\n\nError summary:")
    summary = handler.get_error_summary()
    print(f"  Total errors: {summary['total_errors']}")
    print(f"  By type: {summary['errors_by_type']}")
    print(f"  By severity: {summary['errors_by_severity']}")
    
    print("\n✓ Error handling demonstration complete!")


def demo_workflow_execution():
    """Demonstrate workflow execution"""
    print_header("4. Workflow Execution Demonstration")
    
    from src.engine.state_machine import StateMachine
    from src.engine.error_handler import ErrorHandler
    from src.engine.workflow_manager import WorkflowManager
    
    print("\nSetting up workflow components...")
    state_machine = StateMachine()
    error_handler = ErrorHandler()
    workflow_manager = WorkflowManager(state_machine, error_handler)
    
    # Register a test phase
    print("Registering workflow phases...")
    
    def test_phase(context):
        print(f"    Executing phase for job {context.get('job_id')}...")
        return {'status': 'success', 'message': 'Phase completed'}
    
    workflow_manager.register_phase(
        GenerationState.INITIALIZED,
        test_phase,
        description="Test initialization phase"
    )
    
    # Execute the phase
    print("\nExecuting workflow phase:")
    result = workflow_manager.execute_phase(
        GenerationState.INITIALIZED,
        {'job_id': 123, 'character': 'test'}
    )
    
    print(f"  Success: {result['success']}")
    print(f"  Duration: {result['duration']:.3f}s")
    print(f"  Result: {result['result']}")
    
    # Get progress info
    print("\n\nProgress information:")
    progress = workflow_manager.get_progress_info()
    print(f"  Current state: {progress['current_state']}")
    print(f"  Progress: {progress['progress_percentage']}%")
    print(f"  Phases executed: {progress['phases_executed']}")
    
    print("\n✓ Workflow execution demonstration complete!")


def demo_persistence():
    """Demonstrate state persistence"""
    print_header("5. State Persistence Demonstration")
    
    # Initialize database
    init_db()
    
    print("\nCreating job and saving state...")
    engine = BookGenEngine()
    job_id = engine.generate_biography("albert_einstein")
    
    # Get components and make state transitions
    state_machine, _, _ = engine._get_or_create_components(job_id)
    
    print(f"Initial state: {state_machine.get_state().value}")
    
    # Make some transitions
    state_machine.transition(GenerationState.SOURCES_VALIDATING)
    state_machine.transition(GenerationState.CONTENT_GENERATING)
    
    print(f"After transitions: {state_machine.get_state().value}")
    
    # Save state to database
    print("\nSaving state to database...")
    engine._save_state(job_id)
    
    # Add some logs
    engine._add_log(job_id, "INFO", "State saved successfully")
    engine._add_log(job_id, "INFO", "Ready to continue generation")
    
    # Verify persistence
    print("\nVerifying state was persisted...")
    status = engine.get_status(job_id)
    print(f"  Persisted state: {status.state}")
    print(f"  Persisted progress: {status.progress}%")
    print(f"  Log entries: {len(status.logs)}")
    
    # Simulate loading state in new engine instance
    print("\n\nSimulating state restoration in new engine...")
    engine2 = BookGenEngine()
    restored_machine, _, _ = engine2._get_or_create_components(job_id)
    print(f"  Restored state: {restored_machine.get_state().value}")
    print(f"  Restored progress: {restored_machine.get_progress_percentage()}%")
    
    engine.db.close()
    engine2.db.close()
    
    print("\n✓ State persistence demonstration complete!")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  BookGen Engine Demonstration")
    print("  Issue #12: Main Orchestration Engine")
    print("=" * 70)
    
    try:
        demo_basic_usage()
        demo_state_machine()
        demo_error_handling()
        demo_workflow_execution()
        demo_persistence()
        
        print("\n" + "=" * 70)
        print("  ✓ All demonstrations completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
