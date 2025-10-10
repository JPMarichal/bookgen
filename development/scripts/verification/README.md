# Verification Scripts

This directory contains scripts for verifying acceptance criteria and implementation of various features.

## Verification Scripts (Python)

- `verify_api_implementation.py` - API implementation verification
- `verify_cross_validation.py` - Cross-validation system verification
- `verify_database_implementation.py` - Database implementation checks
- `verify_feedback_system.py` - Feedback system acceptance criteria
- `verify_issue_16.py` - Issue #16 implementation verification
- `verify_issue_62.py` - Issue #62 implementation verification
- `verify_issue_63.py` - Issue #63 implementation verification
- `verify_notifications.py` - Notification system verification
- `verify_openrouter_integration.py` - OpenRouter API integration verification
- `verify_personalized_strategies.py` - Personalized source strategies verification
- `verify_source_strategies.py` - Source search strategies verification
- `verify_word_export.py` - Word export functionality verification

## Verification Scripts (Shell)

- `verify_celery_setup.sh` - Celery setup and configuration checks
- `verify_concatenation.sh` - Concatenation service verification
- `verify_issue_11.sh` - Issue #11 implementation verification
- `verify_performance_tests.sh` - Performance testing verification

## Usage

### Python Scripts

```bash
cd scripts/verification
python verify_openrouter_integration.py
```

### Shell Scripts

```bash
cd scripts/verification
./verify_celery_setup.sh
```

Or from the project root:

```bash
bash scripts/verification/verify_celery_setup.sh
```

## Purpose

These scripts verify that:
- All acceptance criteria are met
- Features work as expected
- Integrations are functioning correctly
- Performance requirements are satisfied

They are typically run after implementing a feature to ensure everything works correctly.

## See Also

- **Examples**: See `examples/` for usage demonstrations
- **Tests**: See `tests/` for automated unit and integration tests
