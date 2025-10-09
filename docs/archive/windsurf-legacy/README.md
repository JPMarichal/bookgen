# Legacy Windsurf Rules - Archived

This directory contains the original Windsurf rules that were used when book generation was a manual, AI-assisted process through the Windsurf IDE.

## Context

These rules were created when the workflow was:
1. User requests book generation in Windsurf Cascade chat
2. AI generates content based on these rules
3. Manual iteration and refinement with AI
4. Manual execution of scripts (concat.py, check_lengths.py, etc.)

## Why Archived?

The project has evolved into a fully automated FastAPI application that:
- Automates the entire book generation process
- Has business rules codified in the application itself
- Uses services like ConcatenationService, LengthValidator, etc.
- No longer requires manual AI prompting for book generation

## Archived Files

- **automation.md** - Manual concatenation and Pandoc workflow (now automated in services)
- **workflow.md** - Manual generation pipeline (now in state machine engine)
- **structure.md** - Manual chapter structure rules (now in content generation logic)
- **quality.md** - Manual validation steps (now in validation services)
- **length.md** - Manual length checking (now in LengthValidator service)
- **research.md** - Manual research workflow (now in source generation services)
- **fuentes-rules.md** - Manual source rules (now in SourceValidator)
- **style.md** - Technical writing style (now in content strategies)
- **literaryStyle.md** - Literary style rules (now in generation prompts)
- **kdp.md** - KDP guidelines (now in export services)
- **kdpData-rules.md** - KDP metadata rules (now in API models)

## Historical Reference

These files remain available for:
- Understanding the original manual workflow
- Reference when updating automated services
- Historical context of project evolution
- Potential rollback scenarios

## Current Rules

See `.windsurf/rules/` for the new development-focused rules that support the automated application.
