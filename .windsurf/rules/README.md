# Windsurf Rules for BookGen

This directory contains AI agent rules for supporting the BookGen automated biography generation system.

## Overview

BookGen is now a **fully automated FastAPI application** that generates biographies through API calls. These rules help AI agents (like Windsurf Cascade) support development, maintenance, and bug fixes for the automated system.

## Current Rules

### [development.md](development.md) 
**Trigger:** `always_on`

Comprehensive development guide including:
- Project structure and file organization
- Quick code navigation (where to find components)
- Common development tasks (testing, migrations, running app)
- Business rules for directory organization
- Testing and documentation standards
- Bug fixing workflow
- File placement guidelines

**Use this for:**
- Finding code quickly for bug fixes
- Understanding project structure
- Knowing where to place new files
- Development workflow guidance

### [business-rules.md](business-rules.md)
**Trigger:** `always_on`

Core business rules and constraints including:
- Biography generation requirements (structure, content, sources)
- Directory structure rules (enforced by application)
- Generation strategies (automatic/hybrid/personalized)
- State machine phases
- Data management and storage rules
- API design patterns
- Quality assurance requirements
- Performance and monitoring rules
- Security constraints
- Deployment configuration

**Use this for:**
- Understanding how the system works
- Enforced business constraints
- Application logic and validation rules
- What the system requires/expects

## Historical Context

### What Changed?

**Before (Manual Process):**
- User requested book in Windsurf chat
- AI generated content following `.windsurf/rules`
- Manual execution of scripts (concat.py, etc.)
- Iterative refinement with AI assistance

**Now (Automated Application):**
- User calls REST API endpoints
- FastAPI application orchestrates entire workflow
- Business rules codified in Python services
- State machine manages generation phases
- No manual AI prompting needed for generation

### Legacy Rules (Archived)

The original manual workflow rules have been moved to:
`/docs/archive/windsurf-legacy/`

These included:
- automation.md (manual concat/pandoc)
- workflow.md (manual generation pipeline)
- structure.md (chapter structure)
- quality.md (manual validation)
- length.md (manual length checks)
- research.md (manual research)
- style.md/literaryStyle.md (writing style)
- kdp.md (KDP guidelines)
- And others...

See `/docs/archive/windsurf-legacy/README.md` for details.

## Using These Rules

### For Development Tasks

1. **Bug Fixes:**
   - Use `development.md` to locate relevant code
   - Check `business-rules.md` for constraints
   - Make minimal changes
   - Run tests before and after

2. **New Features:**
   - Follow project structure in `development.md`
   - Respect business rules in `business-rules.md`
   - Add tests in `/tests`
   - Update docs in `/docs`

3. **Refactoring:**
   - Understand current structure from `development.md`
   - Preserve business rules from `business-rules.md`
   - Update documentation
   - Maintain test coverage

### For Code Navigation

**Quick Lookup:**
- Biography API → `src/api/routers/biographies.py`
- Generation Logic → `src/engine/biography_engine.py`
- Content Services → `src/services/`
- Database Models → `src/models/`
- Async Tasks → `src/tasks/`

See `development.md` "Quick Code Navigation" section for full index.

### For Understanding the System

**Read in this order:**
1. `README.md` (this file) - Context
2. `development.md` - Project structure and navigation
3. `business-rules.md` - How the system works
4. `/docs/architecture/system-overview.md` - Detailed architecture

## Key Principles

### 1. Keep Root Clean
- No new .md files in root (use `/docs`)
- No test files in root (use `/tests`)
- No scripts in root (use `/development/scripts`)
- No data files (use `/bios` or gitignored dirs)

### 2. Minimal Changes
- Change only what's necessary
- Don't refactor unrelated code
- Preserve existing tests
- Keep changes focused

### 3. Test-Driven
- Run tests before changes: `pytest`
- Run tests after changes: `pytest`
- Add tests for new features
- Don't break existing tests

### 4. Documentation in Sync
- Update docs with code changes
- Keep technical docs in `/docs/technical`
- Keep user docs in `/docs/user-guide`
- Link related documentation

## Directory Philosophy

### Application Code (`/src`)
All Python application code organized by responsibility:
- API layer → `api/`
- Business logic → `services/`
- Database → `models/`, `repositories/`
- Background jobs → `tasks/`
- Configuration → `config/`

### Tests (`/tests`)
All test code mirroring src structure:
- Unit tests → `test_*.py`
- Integration tests → `integration/`
- Fixtures → `conftest.py`, `fixtures/`

### Documentation (`/docs`)
All documentation organized by audience:
- Users → `user-guide/`
- Developers → `api/`, `architecture/`
- Operators → `operations/`
- Technical → `technical/`

### Development Utilities (`/development`)
Scripts and tools for development:
- Deployment → `scripts/deploy-*.sh`
- Migrations → `scripts/migrate_*.py`
- Legacy → `scripts/legacy/` (archived)

### Infrastructure (`/infrastructure`)
Deployment and infrastructure:
- Docker → `Dockerfile`, `docker-compose*.yml`
- Nginx → `nginx/`
- CI/CD → (if added)

### Data (Gitignored)
Generated and working data:
- Biographies → `bios/{character}/`
- Database → `data/`
- Logs → `logs/`
- Temp → `tmp/`

## Common Scenarios

### Scenario: "Fix a bug in biography generation"

1. **Locate code:** Use `development.md` → Biography Generation Flow
2. **Understand flow:** `business-rules.md` → State Machine Phases
3. **Find bug:** Navigate to relevant service/task
4. **Fix:** Make minimal change
5. **Test:** `pytest tests/test_biography_tasks.py`
6. **Verify:** Run integration test or manual test
7. **Document:** Update docs if behavior changed

### Scenario: "Add new API endpoint"

1. **Location:** `src/api/routers/` (appropriate router)
2. **Models:** `src/api/models/` (request/response models)
3. **Business logic:** `src/services/` (new service if needed)
4. **Tests:** `tests/test_api/` (new test file)
5. **Docs:** `docs/api/` (update API docs)
6. **Follow:** API design patterns in `business-rules.md`

### Scenario: "Update directory structure"

1. **Check:** `business-rules.md` → Directory Structure Requirements
2. **Migration:** Create script in `development/scripts/`
3. **Update code:** All path references
4. **Update config:** `src/config/export_config.py`
5. **Update docs:** `docs/technical/components/DIRECTORY_MIGRATION.md`
6. **Test:** Ensure no broken paths

### Scenario: "Improve documentation"

1. **Location:** Identify audience (user/dev/ops)
2. **Place in:** Appropriate `/docs` subdirectory
3. **Format:** Use clear headings and examples
4. **Link:** Cross-reference related docs
5. **Update:** `DOCUMENTATION_MAP.md` if major addition
6. **Don't:** Add loose .md files to root

## Integration with Windsurf

### Cascade Chat Usage

When working with Windsurf Cascade:

**For bug fixes:**
> "There's a bug in chapter concatenation - chapters are in wrong order"

Cascade will:
1. Read `development.md` to locate `ConcatenationService`
2. Check `business-rules.md` for section order requirements
3. Navigate to `src/services/concatenation.py`
4. Identify the issue in FILE_ORDER constant
5. Make minimal fix
6. Run tests to verify

**For feature requests:**
> "Add ability to export biographies as PDF"

Cascade will:
1. Check `development.md` for export service patterns
2. Review existing `WordExporter` in `src/services/`
3. Create new `PDFExporter` following same pattern
4. Add endpoint in `src/api/routers/biographies.py`
5. Add task in `src/tasks/export_tasks.py`
6. Add tests in `tests/test_pdf_export.py`
7. Update docs in `docs/api/`

**For understanding:**
> "How does biography generation work?"

Cascade will:
1. Direct you to `business-rules.md` → State Machine Phases
2. Show flow in `development.md` → Biography Generation Flow
3. Explain each phase and responsible components
4. Reference `/docs/architecture/system-overview.md` for details

## Maintenance

### Updating These Rules

**When to update:**
- Major architecture changes
- New important components
- Changed directory structure
- New business rules/constraints
- Deprecated features

**How to update:**
- Keep rules concise and focused
- Update cross-references
- Test that AI can follow them
- Keep examples current
- Archive obsolete rules

### Archive Policy

Rules become obsolete when:
- Feature is removed from system
- Workflow fundamentally changes
- Business rules change
- No longer relevant to development

**Process:**
1. Move to `/docs/archive/windsurf-legacy/`
2. Update legacy README with context
3. Remove from active rules directory
4. Update cross-references

## Related Documentation

- [System Architecture](../../docs/architecture/system-overview.md)
- [API Documentation](../../docs/api/overview.md)
- [Documentation Map](../../DOCUMENTATION_MAP.md)
- [Directory Migration](../../docs/technical/components/DIRECTORY_MIGRATION.md)
- [Legacy Rules Archive](../../docs/archive/windsurf-legacy/README.md)
- [Main README](../../README.md)

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ BookGen Windsurf Rules Quick Reference                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Find Code:        development.md → Quick Code Navigation    │
│ Business Rules:   business-rules.md → All constraints       │
│ File Placement:   development.md → File Placement Guide     │
│ Testing:          development.md → Running Tests            │
│ API Patterns:     business-rules.md → API Design Rules     │
│                                                              │
│ Keep Root Clean:  No new .md, .py, or data files           │
│ Minimal Changes:  Only change what's necessary              │
│ Test Everything:  pytest before and after changes           │
│ Document Changes: Update /docs when behavior changes        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
