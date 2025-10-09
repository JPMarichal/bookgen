# Directory Structure Migration - Completed

## Overview

This document describes the new consolidated directory structure for character biographies implemented on 2024-10-09.

## New Structure

All character information is now organized under a single directory: `bios/{character_name}/`

```
bios/
├── {character_name}/
│   ├── research/              # Research materials and planning
│   │   ├── fuentes.md         # Source materials
│   │   └── plan-de-trabajo.md # Work plan
│   │
│   ├── chapters/              # Chapter content files
│   │   ├── capitulo-01.md
│   │   ├── capitulo-02.md
│   │   └── ...
│   │
│   ├── sections/              # Special sections
│   │   ├── prologo.md
│   │   ├── introduccion.md
│   │   ├── cronologia.md
│   │   ├── epilogo.md
│   │   ├── glosario.md
│   │   ├── dramatis-personae.md
│   │   └── fuentes.md
│   │
│   ├── output/                # Generated files
│   │   ├── markdown/          # Concatenated markdown
│   │   │   └── La biografia de {Character}.md
│   │   ├── word/              # Word documents
│   │   │   └── La biografia de {Character}.docx
│   │   └── kdp/               # Amazon KDP assets
│   │       ├── metadata.md
│   │       └── descripcion.md
│   │
│   └── control/               # Quality control (optional)
│       └── longitudes.csv
```

## Migration Details

### What Changed

1. **Removed directories:**
   - `esquemas/` - Files moved to `bios/{character}/research/`
   - `docx/` - Files moved to `bios/{character}/output/word/`

2. **Reorganized files:**
   - Chapter files (`capitulo-*.md`) → `bios/{character}/chapters/`
   - Section files (prologo, epilogo, etc.) → `bios/{character}/sections/`
   - Concatenated markdown → `bios/{character}/output/markdown/`
   - Word documents → `bios/{character}/output/word/`
   - KDP assets → `bios/{character}/output/kdp/`
   - Research files → `bios/{character}/research/`

### Code Updates

The following files were updated to work with the new structure:

- `src/config/export_config.py` - Updated output directory configuration
- `src/services/concatenation.py` - Updated to read from subdirectories
- `src/services/word_exporter.py` - Updated character name extraction and output paths
- `development/scripts/legacy/concat.py` - Updated to use new subdirectory structure
- `src/tasks/export_tasks.py` - Updated PDF output path
- `tests/test_concatenation.py` - Updated test file creation
- `tests/test_word_export.py` - Updated path test
- `.windsurf/rules/kdpData-rules.md` - Updated KDP documentation

## Benefits

### 🎯 Organization
- All character information in one place
- Clear separation between research, content, and output
- Scalable for future characters

### 🔧 Maintenance
- Single directory per character for backup/restore
- Easy identification of missing files
- Simplified permission management

### 🚀 Development
- Intuitive navigation in IDE
- Consistent structure across all characters
- Fewer errors from incorrect paths

### 📊 Operations
- Per-character monitoring
- Storage metrics by biography
- Automated cleanup processes

## Tools

### Migration Script

```bash
python development/scripts/migrate_structure.py
```

Migrates all characters from the old structure to the new one.

### Validation Script

```bash
python development/scripts/validate_structure.py
```

Validates that all character directories follow the new structure.

### Concatenation

```bash
python development/scripts/legacy/concat.py -personaje "Character Name"
```

Concatenates files from the new structure into the output markdown file.

## Rollback

If you need to rollback, restore from the backup created during migration:

```bash
# Backup location: /tmp/backup-pre-migration-{timestamp}.tar.gz
tar -xzf /tmp/backup-pre-migration-{timestamp}.tar.gz
```

## Migration Statistics

### Characters Migrated
- ✅ harry_s_truman (20 chapters, 7 sections, 2 research files)
- ✅ joseph_stalin (15 chapters, 7 sections, 2 research files)
- ✅ winston_churchill (20 chapters, 7 sections, 2 research files)

### Files Reorganized
- 55 chapter files moved to `chapters/`
- 21 section files moved to `sections/`
- 6 research files moved to `research/`
- 3 output markdown files moved to `output/markdown/`
- 3 Word files moved to `output/word/`
- 6 KDP files moved to `output/kdp/`

### Directories Removed
- ❌ `esquemas/` - Consolidated into `research/`
- ❌ `docx/` - Consolidated into `output/word/`

## Future Additions

When adding a new character, create the following structure:

```bash
mkdir -p bios/{character_name}/{research,chapters,sections,output/{markdown,word,kdp},control}
```

Then populate with:
- Research files in `research/`
- Chapter files in `chapters/`
- Section files in `sections/`
- Generated files will automatically go to `output/`
