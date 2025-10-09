"""
Configuration for Word export service
"""
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ExportConfig:
    """Configuration for Word document export"""
    
    # Pandoc configuration
    pandoc_executable: str = field(default_factory=lambda: os.getenv('PANDOC_PATH', 'pandoc'))
    
    # Template configuration
    word_template_path: str = field(default_factory=lambda: os.getenv(
        'WORD_TEMPLATE_PATH', 
        '/app/wordTemplate/reference.docx'
    ))
    
    # Output configuration
    # Note: This is now a template - actual output goes to bios/{character}/output/word/
    output_directory: str = field(default_factory=lambda: os.getenv(
        'EXPORT_OUTPUT_DIR',
        '/app/bios/{character}/output/word'
    ))
    
    # TOC configuration
    toc_title: str = "Contenido"
    toc_depth: int = 1  # Only level 1 headings
    include_toc: bool = True
    
    # Metadata configuration
    include_metadata: bool = True
    
    # Export options
    standalone: bool = True
    number_sections: bool = False
    
    # Pandoc filters and extensions
    use_crossref: bool = False
    
    @classmethod
    def from_env(cls) -> "ExportConfig":
        """
        Create configuration from environment variables
        
        Returns:
            ExportConfig instance with values from .env
        """
        return cls()
    
    def get_pandoc_command(
        self,
        input_file: str,
        output_file: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Build Pandoc command with all options
        
        Args:
            input_file: Path to input markdown file
            output_file: Path to output Word file
            metadata: Optional metadata dictionary
            
        Returns:
            List of command arguments for subprocess
        """
        command = [
            self.pandoc_executable,
            input_file,
            "-o", output_file,
            "--reference-doc", self.word_template_path,
        ]
        
        if self.include_toc:
            command.extend([
                "--table-of-contents",
                f"--toc-depth={self.toc_depth}",
            ])
        
        if self.standalone:
            command.append("--standalone")
        
        if self.number_sections:
            command.append("--number-sections")
        
        # Add metadata
        if metadata:
            if self.include_toc and 'toc-title' not in metadata:
                metadata['toc-title'] = self.toc_title
            
            for key, value in metadata.items():
                command.extend(["--metadata", f"{key}={value}"])
        elif self.include_toc:
            command.extend(["--metadata", f"toc-title={self.toc_title}"])
        
        # Add crossref filter if enabled
        if self.use_crossref:
            command.extend(["--filter", "pandoc-crossref"])
        
        return command
    
    def validate_pandoc_installation(self) -> tuple[bool, str]:
        """
        Validate that Pandoc is installed and accessible
        
        Returns:
            Tuple of (is_installed, version_or_error)
        """
        import subprocess
        
        try:
            result = subprocess.run(
                [self.pandoc_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return True, version_line
            else:
                return False, f"Pandoc returned error code {result.returncode}"
        except FileNotFoundError:
            return False, f"Pandoc not found at: {self.pandoc_executable}"
        except subprocess.TimeoutExpired:
            return False, "Pandoc command timed out"
        except Exception as e:
            return False, f"Error checking Pandoc: {str(e)}"
    
    def validate_template(self) -> tuple[bool, str]:
        """
        Validate that Word template exists
        
        Returns:
            Tuple of (exists, path_or_error)
        """
        if os.path.exists(self.word_template_path):
            return True, self.word_template_path
        else:
            return False, f"Template not found: {self.word_template_path}"


# Export default configuration instance
export_config = ExportConfig()
