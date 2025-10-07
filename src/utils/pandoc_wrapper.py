"""
Pandoc wrapper utility for document conversion
"""
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class PandocWrapper:
    """Wrapper for Pandoc command-line tool"""
    
    def __init__(self, pandoc_executable: str = "pandoc"):
        """
        Initialize Pandoc wrapper
        
        Args:
            pandoc_executable: Path to pandoc executable
        """
        self.pandoc_executable = pandoc_executable
        self._version = None
    
    def get_version(self) -> Optional[str]:
        """
        Get Pandoc version
        
        Returns:
            Version string or None if not available
        """
        if self._version:
            return self._version
        
        try:
            result = subprocess.run(
                [self.pandoc_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self._version = version_line
                return version_line
        except Exception as e:
            logger.error(f"Error getting Pandoc version: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """
        Check if Pandoc is available
        
        Returns:
            True if Pandoc is installed and accessible
        """
        return self.get_version() is not None
    
    def convert(
        self,
        input_file: str,
        output_file: str,
        from_format: str = "markdown",
        to_format: str = "docx",
        options: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> tuple[bool, str]:
        """
        Convert document using Pandoc
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            from_format: Input format (default: markdown)
            to_format: Output format (default: docx)
            options: Additional Pandoc options
            metadata: Metadata to include in document
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, message_or_error)
        """
        # Build command
        command = [
            self.pandoc_executable,
            input_file,
            "-f", from_format,
            "-o", output_file,
        ]
        
        # Add additional options
        if options:
            command.extend(options)
        
        # Add metadata
        if metadata:
            for key, value in metadata.items():
                command.extend(["--metadata", f"{key}={value}"])
        
        logger.info(f"Running Pandoc command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Pandoc conversion successful: {output_file}")
                return True, f"Successfully converted to {output_file}"
            else:
                error_msg = result.stderr or result.stdout or f"Exit code {result.returncode}"
                logger.error(f"Pandoc conversion failed: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Pandoc command timed out after {timeout} seconds"
            logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = f"Pandoc executable not found: {self.pandoc_executable}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running Pandoc: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def convert_to_word(
        self,
        markdown_file: str,
        output_file: str,
        reference_doc: Optional[str] = None,
        include_toc: bool = True,
        toc_depth: int = 1,
        toc_title: str = "Contenido",
        metadata: Optional[Dict[str, Any]] = None,
        standalone: bool = True,
        timeout: int = 300
    ) -> tuple[bool, str]:
        """
        Convert Markdown to Word document
        
        Args:
            markdown_file: Path to markdown input file
            output_file: Path to Word output file
            reference_doc: Path to Word template/reference document
            include_toc: Whether to include table of contents
            toc_depth: Depth of TOC (1-6)
            toc_title: Title for table of contents
            metadata: Document metadata
            standalone: Whether to create standalone document
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, message_or_error)
        """
        # Build options
        options = []
        
        if reference_doc:
            options.extend(["--reference-doc", reference_doc])
        
        if include_toc:
            options.extend([
                "--table-of-contents",
                f"--toc-depth={toc_depth}",
            ])
        
        if standalone:
            options.append("--standalone")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add TOC title to metadata if TOC is enabled
        if include_toc and 'toc-title' not in metadata:
            metadata['toc-title'] = toc_title
        
        return self.convert(
            input_file=markdown_file,
            output_file=output_file,
            from_format="markdown",
            to_format="docx",
            options=options,
            metadata=metadata,
            timeout=timeout
        )
    
    def count_headings(self, markdown_file: str) -> int:
        """
        Count number of headings in markdown file for TOC estimation
        
        Args:
            markdown_file: Path to markdown file
            
        Returns:
            Number of level 1 headings
        """
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count level 1 headings (# Heading)
            import re
            headings = re.findall(r'^# [^\n]+', content, re.MULTILINE)
            return len(headings)
        except Exception as e:
            logger.warning(f"Error counting headings: {e}")
            return 0
