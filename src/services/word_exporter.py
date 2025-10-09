"""
Word document export service with automatic TOC
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from src.config.export_config import ExportConfig
from src.utils.pandoc_wrapper import PandocWrapper
from src.api.models.export import (
    WordExportResult,
    WordExportError,
    DocumentMetadata,
    DocumentInfo
)

logger = logging.getLogger(__name__)


class WordExporter:
    """Service for exporting Markdown to Word with table of contents"""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize Word exporter
        
        Args:
            config: Export configuration (uses defaults if not provided)
        """
        self.config = config or ExportConfig.from_env()
        self.pandoc = PandocWrapper(self.config.pandoc_executable)
        
        # Validate Pandoc installation on initialization
        if not self.pandoc.is_available():
            logger.warning(
                f"Pandoc not available at {self.config.pandoc_executable}. "
                "Word export will fail until Pandoc is installed."
            )
    
    def validate_environment(self) -> tuple[bool, list]:
        """
        Validate that export environment is properly configured
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check Pandoc
        pandoc_ok, pandoc_msg = self.config.validate_pandoc_installation()
        if not pandoc_ok:
            issues.append(f"Pandoc issue: {pandoc_msg}")
        
        # Check template
        template_ok, template_msg = self.config.validate_template()
        if not template_ok:
            issues.append(f"Template issue: {template_msg}")
        
        # Check output directory
        if not os.path.exists(self.config.output_directory):
            try:
                os.makedirs(self.config.output_directory, exist_ok=True)
                logger.info(f"Created output directory: {self.config.output_directory}")
            except Exception as e:
                issues.append(f"Cannot create output directory: {e}")
        
        return len(issues) == 0, issues
    
    def export_to_word_with_toc(
        self,
        markdown_file: str,
        output_file: Optional[str] = None,
        toc_title: str = "Contenido",
        toc_depth: int = 1,
        metadata: Optional[DocumentMetadata] = None
    ) -> WordExportResult:
        """
        Export Markdown file to Word with table of contents
        
        Args:
            markdown_file: Path to input markdown file
            output_file: Optional path to output file (auto-generated if not provided)
            toc_title: Title for table of contents
            toc_depth: Depth of TOC (1-6, default 1 for level 1 headings only)
            metadata: Optional document metadata
            
        Returns:
            WordExportResult with export details
        """
        logger.info(f"Exporting {markdown_file} to Word with TOC")
        
        try:
            # Validate environment
            is_valid, issues = self.validate_environment()
            if not is_valid:
                raise WordExportError(
                    "Export environment validation failed",
                    details={'issues': issues}
                )
            
            # Validate input file
            if not os.path.exists(markdown_file):
                raise WordExportError(f"Input file not found: {markdown_file}")
            
            # Generate output file name if not provided
            if output_file is None:
                character_name = self._extract_character_name(markdown_file)
                # New structure: bios/{character}/output/word/
                # Extract character from path to avoid nesting issues
                path_parts = Path(markdown_file).parts
                if 'bios' in path_parts:
                    bios_idx = path_parts.index('bios')
                    if len(path_parts) > bios_idx + 1:
                        character_name = path_parts[bios_idx + 1]
                
                output_file = os.path.join(
                    '/app/bios',
                    character_name,
                    'output',
                    'word',
                    f"La biografia de {character_name}.docx"
                )
            
            # Create output directory
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Prepare metadata
            metadata_dict = {}
            if metadata:
                metadata_dict = metadata.to_dict()
            
            # Count TOC entries
            toc_entries = self.pandoc.count_headings(markdown_file)
            
            # Convert to Word
            success, message = self.pandoc.convert_to_word(
                markdown_file=markdown_file,
                output_file=output_file,
                reference_doc=self.config.word_template_path,
                include_toc=self.config.include_toc,
                toc_depth=toc_depth,
                toc_title=toc_title,
                metadata=metadata_dict,
                standalone=self.config.standalone
            )
            
            if not success:
                raise WordExportError(f"Pandoc conversion failed: {message}")
            
            # Validate output file
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise WordExportError(
                    "Output file not generated correctly",
                    details={'output_file': output_file}
                )
            
            file_size = os.path.getsize(output_file)
            pandoc_version = self.pandoc.get_version()
            
            logger.info(
                f"Word export successful: {output_file} "
                f"({file_size} bytes, {toc_entries} TOC entries)"
            )
            
            return WordExportResult(
                success=True,
                output_file=output_file,
                file_size=file_size,
                has_toc=self.config.include_toc,
                toc_entries=toc_entries,
                metadata=metadata_dict,
                pandoc_version=pandoc_version,
                template_used=self.config.word_template_path
            )
            
        except WordExportError as e:
            logger.error(f"Word export error: {e}")
            return WordExportResult(
                success=False,
                output_file=output_file or "",
                file_size=0,
                has_toc=False,
                toc_entries=0,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error during Word export: {e}", exc_info=True)
            return WordExportResult(
                success=False,
                output_file=output_file or "",
                file_size=0,
                has_toc=False,
                toc_entries=0,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def export_biography(
        self,
        biography_path: str,
        character_name: Optional[str] = None,
        metadata: Optional[DocumentMetadata] = None
    ) -> str:
        """
        Export a biography to Word document
        
        Args:
            biography_path: Path to biography markdown file
            character_name: Optional character name (extracted from path if not provided)
            metadata: Optional document metadata
            
        Returns:
            Path to exported Word document
            
        Raises:
            WordExportError: If export fails
        """
        if character_name is None:
            character_name = self._extract_character_name(biography_path)
        
        # Prepare metadata if not provided
        if metadata is None:
            metadata = DocumentMetadata(
                title=f"La biografía de {character_name}",
                author="BookGen Sistema Automatizado",
                subject=f"Biografía de {character_name}",
                date=datetime.now().strftime("%Y-%m-%d")
            )
        
        result = self.export_to_word_with_toc(
            markdown_file=biography_path,
            metadata=metadata
        )
        
        if not result.success:
            raise WordExportError(
                f"Failed to export biography: {result.error_message}"
            )
        
        return result.output_file
    
    def get_document_info(self, doc_path: str, source_markdown: Optional[str] = None) -> DocumentInfo:
        """
        Get information about a Word document
        
        Args:
            doc_path: Path to Word document
            source_markdown: Optional path to source markdown for TOC counting
            
        Returns:
            DocumentInfo with document details
        """
        # Try to determine if document has TOC by checking if it was created with TOC enabled
        has_toc = self.config.include_toc
        toc_entries = 0
        
        # Try to count TOC entries from source markdown if provided
        if source_markdown and os.path.exists(source_markdown):
            toc_entries = self.pandoc.count_headings(source_markdown)
        
        return DocumentInfo.from_file(
            doc_path,
            has_toc=has_toc,
            toc_entries=toc_entries
        )
    
    def _extract_character_name(self, file_path: str) -> str:
        """
        Extract character name from file path
        
        Args:
            file_path: Path to biography file
            
        Returns:
            Character name
        """
        # Try to extract from directory structure (bios/character_name/...)
        path_parts = Path(file_path).parts
        
        # Look for bios directory and get the next part as character name
        if 'bios' in path_parts:
            bios_idx = path_parts.index('bios')
            if len(path_parts) > bios_idx + 1:
                character_dir = path_parts[bios_idx + 1]
                # Clean up the name
                if character_dir not in ['bios', 'docx', 'app', 'output', 'markdown', 'word', 'kdp']:
                    return character_dir
        
        # Look for the parent directory of the markdown file
        if len(path_parts) >= 2:
            # Get the directory containing the file
            character_dir = path_parts[-2]
            
            # Clean up the name
            if character_dir not in ['bios', 'docx', 'app', 'output', 'markdown', 'word', 'kdp']:
                return character_dir
        
        # Fallback: use filename without extension
        return Path(file_path).stem.replace('La biografia de ', '').replace('biography', '').strip()
    
    def _count_toc_entries(self, markdown_file: str) -> int:
        """
        Count the number of TOC entries in a markdown file
        
        Args:
            markdown_file: Path to markdown file
            
        Returns:
            Number of level 1 headings
        """
        return self.pandoc.count_headings(markdown_file)
