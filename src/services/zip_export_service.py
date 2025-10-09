"""
Service for creating ZIP archives of publication output files
"""
import os
import logging
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
from ..api.models.export import ZipExportResult

logger = logging.getLogger(__name__)


class ZipExportService:
    """Service for exporting publication files as ZIP archives"""
    
    def __init__(self, base_bios_dir: str = "bios"):
        """
        Initialize ZIP export service
        
        Args:
            base_bios_dir: Base directory containing biography files
        """
        self.base_bios_dir = base_bios_dir
    
    def validate_output_directory(self, character: str) -> bool:
        """
        Validate that the output directory exists and contains files
        
        Args:
            character: Normalized character name
            
        Returns:
            True if output directory exists and has files
        """
        output_dir = os.path.join(self.base_bios_dir, character, "output")
        
        if not os.path.exists(output_dir):
            logger.warning(f"Output directory not found: {output_dir}")
            return False
        
        if not os.path.isdir(output_dir):
            logger.warning(f"Output path is not a directory: {output_dir}")
            return False
        
        # Check if directory has any files (recursively)
        has_files = any(
            os.path.isfile(os.path.join(root, file))
            for root, _, files in os.walk(output_dir)
            for file in files
        )
        
        if not has_files:
            logger.warning(f"Output directory is empty: {output_dir}")
            return False
        
        return True
    
    def get_zip_filename(self, character: str) -> str:
        """
        Generate filename for the ZIP archive
        
        Args:
            character: Normalized character name
            
        Returns:
            ZIP filename: {character}_publicacion.zip
        """
        return f"{character}_publicacion.zip"
    
    def create_publication_zip(self, character: str) -> ZipExportResult:
        """
        Create a ZIP archive with all publication files
        
        Args:
            character: Normalized character name
            
        Returns:
            ZipExportResult with success status and file information
        """
        logger.info(f"ZIP export started for character: {character}")
        
        # Validate output directory exists
        if not self.validate_output_directory(character):
            error_msg = f"No publication files found for character: {character}"
            logger.error(f"ZIP creation failed: {error_msg}")
            return ZipExportResult(
                success=False,
                error_message=error_msg
            )
        
        output_dir = os.path.join(self.base_bios_dir, character, "output")
        
        try:
            # Create temporary ZIP file
            temp_fd, temp_zip_path = tempfile.mkstemp(
                suffix='.zip',
                prefix=f'{character}_publicacion_'
            )
            os.close(temp_fd)  # Close the file descriptor
            
            included_files = []
            
            # Create ZIP archive
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the output directory
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate the archive name (relative to output directory)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)
                        included_files.append(arcname)
                        logger.debug(f"Added to ZIP: {arcname}")
            
            # Get final file size
            zip_size = os.path.getsize(temp_zip_path)
            
            logger.info(
                f"ZIP created successfully: {temp_zip_path}, "
                f"size: {zip_size} bytes, files: {len(included_files)}"
            )
            
            return ZipExportResult(
                success=True,
                zip_path=temp_zip_path,
                zip_size=zip_size,
                included_files=included_files
            )
            
        except PermissionError as e:
            error_msg = f"Permission denied accessing files for character: {character}"
            logger.error(f"ZIP creation failed: {error_msg} - {e}")
            return ZipExportResult(
                success=False,
                error_message=error_msg
            )
        
        except OSError as e:
            # This catches disk full and other OS errors
            error_msg = f"System error creating ZIP: {str(e)}"
            logger.error(f"ZIP creation failed: {error_msg}")
            return ZipExportResult(
                success=False,
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error creating ZIP: {str(e)}"
            logger.error(f"ZIP creation failed: {error_msg}", exc_info=True)
            return ZipExportResult(
                success=False,
                error_message=error_msg
            )
