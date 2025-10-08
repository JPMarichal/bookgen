# BookGen Engine - Quick Reference

## Overview
The BookGen Engine (Issue #12) provides the main orchestration system for biography generation with comprehensive state management, error handling, and progress tracking.

## Installation & Setup

```bash
# Initialize database
from src.database.config import init_db
init_db()
```

## Basic Usage

```python
from src.engine.bookgen_engine import BookGenEngine

# Create engine
engine = BookGenEngine()

# Start biography generation
job_id = engine.generate_biography("winston_churchill")

# Check status
status = engine.get_status(job_id)
print(f"State: {status.state}, Progress: {status.progress}%")

# Execute job (in production, use Celery)
result = engine.execute_job(job_id)

# Clean up
engine.db.close()
```

## State Machine

### States
| State | Progress | Description |
|-------|----------|-------------|
| `INITIALIZED` | 0% | Job initialized |
| `SOURCES_VALIDATING` | 10% | Validating sources |
| `CONTENT_GENERATING` | 30% | Generating content |
| `CHAPTERS_VALIDATING` | 70% | Validating chapters |
| `CONCATENATING` | 85% | Concatenating sections |
| `EXPORTING` | 95% | Exporting to format |
| `COMPLETED` | 100% | Generation complete |
| `FAILED` | 0% | Generation failed |

### State Transitions

```python
from src.engine.state_machine import StateMachine, GenerationState

# Create state machine
machine = StateMachine()

# Valid transition
machine.transition(GenerationState.SOURCES_VALIDATING)

# Check if transition is allowed
if machine.can_transition(GenerationState.CONTENT_GENERATING):
    machine.transition(GenerationState.CONTENT_GENERATING)

# Get current state
current = machine.get_state()  # Returns GenerationState enum

# Get progress
progress = machine.get_progress_percentage()  # Returns 0-100

# View history
history = machine.get_history()

# Serialize/deserialize
data = machine.to_dict()
restored = StateMachine.from_dict(data)
```

## Error Handling

```python
from src.engine.error_handler import ErrorHandler, RecoveryStrategy

# Create error handler
handler = ErrorHandler(max_retries=3)

# Classify error
error_context = handler.classify_error(
    error=ValueError("Validation failed"),
    state=GenerationState.SOURCES_VALIDATING,
    metadata={'source_id': 123}
)

# Get recovery strategy
strategy = handler.get_recovery_strategy(error_context)

# Handle error
result = handler.handle_error(
    error=error,
    state=current_state,
    job_id=job_id,
    metadata={'attempt': 1}
)

# Register rollback handler
def rollback_sources(job_id, metadata):
    # Cleanup logic here
    pass

handler.register_rollback_handler(
    GenerationState.SOURCES_VALIDATING,
    rollback_sources
)

# Get error summary
summary = handler.get_error_summary()
```

## Workflow Management

```python
from src.engine.workflow_manager import WorkflowManager

# Create components
state_machine = StateMachine()
error_handler = ErrorHandler()
workflow_manager = WorkflowManager(state_machine, error_handler)

# Register custom phase
def my_phase_executor(context):
    job_id = context['job_id']
    character = context['character']
    # Phase logic here
    return {'status': 'success', 'data': {...}}

workflow_manager.register_phase(
    state=GenerationState.SOURCES_VALIDATING,
    executor=my_phase_executor,
    description="Custom source validation",
    estimated_duration=60  # seconds
)

# Execute single phase
result = workflow_manager.execute_phase(
    GenerationState.SOURCES_VALIDATING,
    context={'job_id': 1, 'character': 'churchill'}
)

# Execute complete workflow
workflow_result = workflow_manager.execute_workflow(
    context={'job_id': 1, 'character': 'churchill'}
)

# Pause/resume
workflow_manager.pause_workflow()
workflow_manager.resume_workflow(context)

# Get progress
progress_info = workflow_manager.get_progress_info()
```

## Complete Example

```python
from src.database.config import init_db
from src.engine.bookgen_engine import BookGenEngine
from src.engine.state_machine import GenerationState

# Initialize
init_db()

# Create engine with context manager
with BookGenEngine() as engine:
    # Start job
    job_id = engine.generate_biography("marie_curie")
    print(f"Job {job_id} created")
    
    # Monitor status
    status = engine.get_status(job_id)
    print(f"State: {status.state}")
    print(f"Progress: {status.progress}%")
    
    # View logs
    for log in status.logs:
        print(f"[{log['level']}] {log['message']}")
    
    # Get state machine components
    state_machine, error_handler, workflow_manager = \
        engine._get_or_create_components(job_id)
    
    # Check current state
    print(f"Current state: {state_machine.get_state()}")
    print(f"Is terminal: {state_machine.is_terminal_state()}")
    
    # Execute workflow phases
    # (In production, this would be triggered by Celery)
    result = engine.execute_job(job_id)
    
    if result['success']:
        print(f"Job completed in {result['end_time']}")
    else:
        print(f"Job failed: {result['error']}")
```

## Testing

```bash
# Run engine tests
python -m pytest tests/test_engine.py -v

# Run all tests
python -m pytest tests/ -v

# Run demonstration
python demo_engine.py
```

## Database Schema

The engine uses existing database tables:

- **`biographies`** - Biography records
  - `character_name`: Subject name
  - `status`: Current status
  - `completed_at`: Completion timestamp
  
- **`generation_jobs`** - Job tracking
  - `biography_id`: FK to biography
  - `status`: Job status
  - `progress`: Progress percentage (0-100)
  - `current_phase`: Current workflow phase
  - `logs`: JSON array of log entries
  - `job_metadata`: JSON with state machine state
  - `error_message`: Error details if failed

## Integration with Celery

For production use, integrate with Celery for async execution:

```python
from celery import shared_task
from src.engine.bookgen_engine import BookGenEngine

@shared_task
def execute_biography_generation(job_id: int):
    """Celery task to execute biography generation"""
    with BookGenEngine() as engine:
        return engine.execute_job(job_id)

# Queue the task
job_id = engine.generate_biography("character_name")
execute_biography_generation.delay(job_id)
```

## Monitoring and Logging

All engine operations are logged:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Engine logs to 'src.engine.bookgen_engine'
logger = logging.getLogger('src.engine')
```

## Error Recovery Strategies

| Error Type | Severity | Recovery Strategy |
|------------|----------|-------------------|
| Validation Error | Medium | Retry previous phase |
| API Error | Medium | Retry current phase |
| Database Error | High | Manual intervention |
| File Error | Medium | Retry current phase |
| Timeout Error | Low | Retry current phase |
| Network Error | Low | Retry current phase |

## Performance Considerations

- State machine operations are in-memory (fast)
- Database writes only on state changes and logs
- Use `flag_modified()` for JSON column updates
- Context manager ensures proper cleanup
- Transactions for atomic operations

## Troubleshooting

### Job stuck in pending
```python
status = engine.get_status(job_id)
if status.state == 'pending':
    # Manually trigger execution
    engine.execute_job(job_id)
```

### State machine out of sync
```python
# Force state transition
state_machine.transition(target_state, force=True)
engine._save_state(job_id)
```

### Logs not updating
```python
# Ensure flag_modified is called
from sqlalchemy.orm.attributes import flag_modified
job.logs = new_logs
flag_modified(job, "logs")
db.commit()
```

## Next Steps

To complete the production system:

1. **Integrate with actual services**
   - Connect phase executors to real services
   - Implement source validation integration
   - Add content generation service calls
   
2. **Add Celery integration**
   - Create Celery tasks for each phase
   - Implement async workflow execution
   - Add task monitoring
   
3. **Add API endpoints**
   - POST `/api/v1/jobs` - Create job
   - GET `/api/v1/jobs/{id}` - Get status
   - POST `/api/v1/jobs/{id}/pause` - Pause job
   - POST `/api/v1/jobs/{id}/resume` - Resume job
   
4. **Add webhooks/notifications**
   - Job completion notifications
   - Error alerts
   - Progress updates

## API Reference

See `IMPLEMENTATION_SUMMARY_ISSUE_12.md` for complete API documentation.

## License

Part of the BookGen project.
