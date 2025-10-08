# Legacy Scripts

This directory contains legacy utility scripts that have been replaced by newer services but are preserved for reference.

## Files

### check_lengths.py

**Status**: Deprecated - Replaced by `LengthValidationService`

**Original Purpose**: Validates chapter lengths against expected word counts in CSV format.

**Modern Alternative**: Use the `LengthValidationService` in `src/services/length_validator.py`

**Migration Guide**: See `docs/technical/components/LENGTH_VALIDATION_README.md`

```python
# Old way
# python check_lengths.py albert_einstein

# New way
from src.services.length_validator import LengthValidationService
service = LengthValidationService()
result = service.validate_character_content("albert_einstein")
```

### concat.py

**Status**: Deprecated - Replaced by `ConcatenationService`

**Original Purpose**: Concatenates biography sections into a complete document.

**Modern Alternative**: Use the `ConcatenationService` in `src/services/concatenation.py`

**Migration Guide**: See `docs/technical/components/CONCATENATION_SERVICE_README.md`

```python
# Old way
# python concat.py -personaje "Winston Churchill"

# New way
from src.services.concatenation import ConcatenationService
service = ConcatenationService()
result = service.concatenate_character("winston_churchill")
```

## Why These Are Deprecated

These scripts have been replaced with modern, feature-rich services that provide:

- **Better error handling**: Comprehensive exception handling and recovery
- **AI integration**: Advanced content analysis and quality checks
- **API access**: RESTful API endpoints for programmatic access
- **Asynchronous processing**: Task queue integration for better performance
- **Monitoring**: Built-in metrics and logging
- **Testing**: Comprehensive unit and integration tests

## Preservation Rationale

These files are kept for:
- Historical reference
- Understanding the evolution of the codebase
- Emergency fallback (if needed)
- Migration assistance for users of legacy scripts

**Note**: These scripts may not be maintained and may not work with the current system architecture.
