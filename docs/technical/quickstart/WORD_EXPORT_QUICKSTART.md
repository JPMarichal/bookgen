# Word Document Exporter - Quick Start Guide

## Overview

The Word Document Exporter service provides automated conversion of Markdown biographies to professional Word documents (.docx) with automatic table of contents, metadata, and professional styling.

## Features

- ✅ **Automatic TOC**: Table of contents with configurable depth and title
- ✅ **Professional Styling**: Uses reference template for consistent formatting
- ✅ **Complete Metadata**: Title, author, subject, keywords, date
- ✅ **Pandoc Integration**: Leverages Pandoc for high-quality conversion
- ✅ **MS Word Compatible**: Generates .docx files compatible with Microsoft Word 2007+
- ✅ **Flexible Configuration**: Environment-based configuration

## Prerequisites

### Install Pandoc

Pandoc is required for document conversion. Install based on your platform:

```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS (using Homebrew)
brew install pandoc

# Windows (using Chocolatey)
choco install pandoc

# Windows (using winget)
winget install JohnMacFarlane.Pandoc

# Verify installation
pandoc --version
```

### Python Dependencies

```bash
pip install python-dotenv python-docx
```

## Quick Start

### Basic Usage

```python
from src.services.word_exporter import WordExporter
from src.api.models.export import DocumentMetadata
from datetime import datetime

# Initialize exporter
exporter = WordExporter()

# Prepare metadata
metadata = DocumentMetadata(
    title="La biografía de Winston Churchill",
    author="BookGen Sistema Automatizado",
    subject="Biografía de Winston Churchill",
    date=datetime.now().strftime("%Y-%m-%d")
)

# Export biography
doc_path = exporter.export_biography(
    biography_path="bios/churchill/biography.md",
    character_name="Churchill",
    metadata=metadata
)

print(f"Document created: {doc_path}")
```

### Custom Configuration

```python
from src.config.export_config import ExportConfig
from src.services.word_exporter import WordExporter

# Create custom configuration
config = ExportConfig(
    output_directory="/custom/output/path",
    word_template_path="/path/to/template.docx",
    toc_title="Tabla de Contenido",
    toc_depth=2,  # Include level 1 and 2 headings
    include_toc=True
)

# Initialize with config
exporter = WordExporter(config)

# Export with custom settings
result = exporter.export_to_word_with_toc(
    markdown_file="input.md",
    toc_title="Contents",
    toc_depth=1
)

if result.success:
    print(f"Success! File: {result.output_file}")
    print(f"Size: {result.file_size_mb:.2f} MB")
    print(f"TOC entries: {result.toc_entries}")
else:
    print(f"Error: {result.error_message}")
```

### Celery Task Integration

```python
from src.tasks.export_tasks import export_to_word

# Queue export task
result = export_to_word.delay(
    character_name="Churchill",
    markdown_file="/app/bios/churchill/biography.md",
    template_path="/app/wordTemplate/reference.docx",
    include_toc=True
)

# Wait for result
export_info = result.get()
print(f"Export complete: {export_info['output_path']}")
```

## Configuration

### Environment Variables

Configure via `.env` file:

```bash
# Pandoc Configuration
PANDOC_PATH=pandoc

# Template Configuration
WORD_TEMPLATE_PATH=/app/wordTemplate/reference.docx

# Output Configuration
EXPORT_OUTPUT_DIR=/app/docx
```

### Configuration Object

```python
from src.config.export_config import ExportConfig

config = ExportConfig(
    pandoc_executable="pandoc",          # Pandoc path
    word_template_path="template.docx",  # Word template
    output_directory="/app/docx",        # Output directory
    toc_title="Contenido",              # TOC title
    toc_depth=1,                        # TOC depth (1-6)
    include_toc=True,                   # Include TOC
    include_metadata=True,              # Include metadata
    standalone=True,                    # Standalone document
    number_sections=False               # Auto-number sections
)
```

## API Reference

### WordExporter

#### Methods

**`export_to_word_with_toc(markdown_file, output_file=None, toc_title="Contenido", toc_depth=1, metadata=None)`**

Export Markdown to Word with TOC.

- `markdown_file`: Path to input markdown file
- `output_file`: Optional output path (auto-generated if not provided)
- `toc_title`: Title for table of contents
- `toc_depth`: Depth of TOC (1-6)
- `metadata`: Optional DocumentMetadata object

Returns: `WordExportResult`

**`export_biography(biography_path, character_name=None, metadata=None)`**

Export a biography to Word document.

- `biography_path`: Path to biography markdown
- `character_name`: Optional character name
- `metadata`: Optional DocumentMetadata object

Returns: Path to exported document

**`get_document_info(doc_path, source_markdown=None)`**

Get information about a Word document.

- `doc_path`: Path to Word document
- `source_markdown`: Optional source markdown for TOC counting

Returns: `DocumentInfo`

**`validate_environment()`**

Validate export environment.

Returns: `(is_valid, list_of_issues)`

### DocumentMetadata

```python
metadata = DocumentMetadata(
    title="Document Title",
    author="Author Name",
    subject="Subject",
    description="Description",
    keywords="keyword1, keyword2",
    date="2024-01-01"
)
```

### WordExportResult

```python
result = WordExportResult(
    success=True,
    output_file="/path/to/output.docx",
    file_size=25000,
    has_toc=True,
    toc_entries=10,
    metadata={},
    error_message=None,
    pandoc_version="pandoc 3.1.3",
    template_used="/path/to/template.docx"
)

# Properties
result.file_size_mb  # File size in MB
result.is_valid      # True if successful with file
result.to_dict()     # Convert to dictionary
```

## Testing

### Run Tests

```bash
# Run all Word export tests
pytest tests/test_word_export.py -v

# Run specific test
pytest tests/test_word_export.py::TestWordExporter::test_export_to_word_with_toc -v

# Run with coverage
pytest tests/test_word_export.py --cov=src.services.word_exporter
```

### Demo Script

```bash
# Run interactive demo
python examples/demo_word_export.py
```

### Verify Implementation

```bash
# Verify all acceptance criteria
python development/scripts/verification/verify_word_export.py
```

## Troubleshooting

### Pandoc Not Found

**Error**: `Pandoc not available at: pandoc`

**Solution**: Install Pandoc (see Prerequisites) or set `PANDOC_PATH` environment variable:

```bash
export PANDOC_PATH=/usr/local/bin/pandoc
```

### Template Not Found

**Error**: `Template not found: /app/wordTemplate/reference.docx`

**Solution**: Ensure Word template exists or configure custom path:

```python
config = ExportConfig(
    word_template_path="/path/to/your/template.docx"
)
```

### Permission Denied

**Error**: `Cannot create output directory: Permission denied`

**Solution**: Ensure output directory is writable or configure alternative:

```python
config = ExportConfig(
    output_directory="/tmp/output"
)
```

### Empty TOC

**Issue**: TOC is empty in generated document

**Solution**: Ensure markdown has level 1 headings (`# Heading`). Pandoc uses these for TOC generation.

## Examples

### Example 1: Simple Export

```python
from src.services.word_exporter import WordExporter

exporter = WordExporter()
doc_path = exporter.export_biography("bios/churchill/biography.md")
print(f"Exported to: {doc_path}")
```

### Example 2: With Metadata

```python
from src.services.word_exporter import WordExporter
from src.api.models.export import DocumentMetadata
from datetime import datetime

metadata = DocumentMetadata(
    title="Winston Churchill Biography",
    author="BookGen",
    date=datetime.now().strftime("%Y-%m-%d")
)

exporter = WordExporter()
doc_path = exporter.export_biography(
    "bios/churchill/biography.md",
    metadata=metadata
)
```

### Example 3: Custom Configuration

```python
from src.config.export_config import ExportConfig
from src.services.word_exporter import WordExporter

config = ExportConfig(
    toc_depth=2,  # Include level 1 and 2 headings
    toc_title="Table of Contents"
)

exporter = WordExporter(config)
result = exporter.export_to_word_with_toc(
    markdown_file="input.md",
    toc_depth=2
)

print(f"Success: {result.success}")
print(f"TOC entries: {result.toc_entries}")
```

## Integration Examples

### With Concatenation Service

```python
from src.services.concatenation import ConcatenationService
from src.services.word_exporter import WordExporter

# Concatenate biography
concat_service = ConcatenationService()
concat_result = concat_service.concatenate_biography("Churchill")

# Export to Word
exporter = WordExporter()
doc_path = exporter.export_biography(concat_result.output_file)
```

### With Celery

```python
from celery import chain
from src.tasks.export_tasks import export_to_word

# Chain tasks
workflow = chain(
    # ... other tasks
    export_to_word.s(
        character_name="Churchill",
        markdown_file="/app/bios/churchill/biography.md"
    )
)

result = workflow.apply_async()
```

## License

Part of the BookGen Sistema Automatizado project.

## Support

For issues or questions, please refer to the main project documentation or create an issue on GitHub.
