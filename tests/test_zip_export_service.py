"""
Tests for ZIP export service
"""
import os
import pytest
import tempfile
import zipfile
from pathlib import Path
from src.services.zip_export_service import ZipExportService
from src.api.models.export import ZipExportResult


class TestZipExportService:
    """Test suite for ZipExportService"""
    
    @pytest.fixture
    def temp_bios_dir(self, tmp_path):
        """Create a temporary bios directory structure"""
        bios_dir = tmp_path / "bios"
        bios_dir.mkdir()
        return str(bios_dir)
    
    @pytest.fixture
    def character_with_output(self, temp_bios_dir):
        """Create a test character with output files"""
        character = "test_character"
        output_dir = Path(temp_bios_dir) / character / "output"
        
        # Create markdown directory with files
        markdown_dir = output_dir / "markdown"
        markdown_dir.mkdir(parents=True)
        (markdown_dir / "biography.md").write_text("# Test Biography\n\nContent here.")
        (markdown_dir / "quality-metrics.json").write_text('{"quality": 0.9}')
        
        # Create word directory with files
        word_dir = output_dir / "word"
        word_dir.mkdir(parents=True)
        (word_dir / "biography.docx").write_text("Mock Word document")
        (word_dir / "export-metadata.json").write_text('{"exported": "2024-01-01"}')
        
        # Create kdp directory with files
        kdp_dir = output_dir / "kdp"
        kdp_dir.mkdir(parents=True)
        (kdp_dir / "cover.jpg").write_text("Mock cover image")
        (kdp_dir / "metadata.json").write_text('{"title": "Test"}')
        
        return character
    
    @pytest.fixture
    def character_without_output(self, temp_bios_dir):
        """Create a test character without output directory"""
        character = "no_output_character"
        char_dir = Path(temp_bios_dir) / character
        char_dir.mkdir()
        return character
    
    @pytest.fixture
    def character_empty_output(self, temp_bios_dir):
        """Create a test character with empty output directory"""
        character = "empty_output_character"
        output_dir = Path(temp_bios_dir) / character / "output"
        output_dir.mkdir(parents=True)
        return character
    
    def test_init(self, temp_bios_dir):
        """Test service initialization"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        assert service.base_bios_dir == temp_bios_dir
    
    def test_init_default(self):
        """Test service initialization with default base directory"""
        service = ZipExportService()
        assert service.base_bios_dir == "bios"
    
    def test_get_zip_filename(self, temp_bios_dir):
        """Test ZIP filename generation"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        
        filename = service.get_zip_filename("harry_s_truman")
        assert filename == "harry_s_truman_publicacion.zip"
        
        filename = service.get_zip_filename("albert_einstein")
        assert filename == "albert_einstein_publicacion.zip"
    
    def test_validate_output_directory_exists(self, temp_bios_dir, character_with_output):
        """Test validation succeeds when output directory exists with files"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        assert service.validate_output_directory(character_with_output) is True
    
    def test_validate_output_directory_not_exists(self, temp_bios_dir):
        """Test validation fails when output directory doesn't exist"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        assert service.validate_output_directory("nonexistent_character") is False
    
    def test_validate_output_directory_empty(self, temp_bios_dir, character_empty_output):
        """Test validation fails when output directory is empty"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        assert service.validate_output_directory(character_empty_output) is False
    
    def test_validate_output_directory_character_without_output(
        self, temp_bios_dir, character_without_output
    ):
        """Test validation fails when character exists but has no output directory"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        assert service.validate_output_directory(character_without_output) is False
    
    def test_create_publication_zip_success(self, temp_bios_dir, character_with_output):
        """Test successful ZIP creation"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip(character_with_output)
        
        assert result.success is True
        assert result.zip_path is not None
        assert result.zip_size is not None
        assert result.zip_size > 0
        assert result.error_message is None
        assert len(result.included_files) == 6  # 2 markdown + 2 word + 2 kdp
        
        # Verify ZIP file exists
        assert os.path.exists(result.zip_path)
        
        # Verify ZIP file is valid
        with zipfile.ZipFile(result.zip_path, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) == 6
            assert "markdown/biography.md" in files
            assert "markdown/quality-metrics.json" in files
            assert "word/biography.docx" in files
            assert "word/export-metadata.json" in files
            assert "kdp/cover.jpg" in files
            assert "kdp/metadata.json" in files
        
        # Cleanup
        os.remove(result.zip_path)
    
    def test_create_publication_zip_character_not_found(self, temp_bios_dir):
        """Test ZIP creation fails for nonexistent character"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip("nonexistent_character")
        
        assert result.success is False
        assert result.zip_path is None
        assert result.zip_size is None
        assert result.error_message is not None
        assert "No publication files found" in result.error_message
        assert len(result.included_files) == 0
    
    def test_create_publication_zip_empty_output(self, temp_bios_dir, character_empty_output):
        """Test ZIP creation fails for empty output directory"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip(character_empty_output)
        
        assert result.success is False
        assert result.zip_path is None
        assert result.error_message is not None
        assert "No publication files found" in result.error_message
    
    def test_create_publication_zip_file_structure(self, temp_bios_dir, character_with_output):
        """Test ZIP file maintains correct directory structure"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip(character_with_output)
        
        assert result.success is True
        
        # Verify directory structure in ZIP
        with zipfile.ZipFile(result.zip_path, 'r') as zipf:
            for file_path in result.included_files:
                # Check file is in correct subdirectory
                assert file_path.startswith(("markdown/", "word/", "kdp/"))
                
                # Verify file can be extracted
                info = zipf.getinfo(file_path)
                assert info.file_size > 0
        
        # Cleanup
        os.remove(result.zip_path)
    
    def test_create_publication_zip_result_properties(self, temp_bios_dir, character_with_output):
        """Test ZipExportResult properties"""
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip(character_with_output)
        
        # Test zip_size_mb property
        assert result.zip_size_mb > 0
        assert result.zip_size_mb == result.zip_size / (1024 * 1024)
        
        # Test to_dict method
        result_dict = result.to_dict()
        assert result_dict['success'] is True
        assert result_dict['zip_path'] == result.zip_path
        assert result_dict['zip_size'] == result.zip_size
        assert 'zip_size_mb' in result_dict
        assert result_dict['file_count'] == len(result.included_files)
        assert 'timestamp' in result_dict
        
        # Cleanup
        os.remove(result.zip_path)
    
    def test_zip_export_result_failed_properties(self):
        """Test ZipExportResult properties for failed export"""
        result = ZipExportResult(
            success=False,
            error_message="Test error"
        )
        
        assert result.zip_size_mb == 0.0
        assert result.zip_path is None
        assert result.zip_size is None
        
        result_dict = result.to_dict()
        assert result_dict['success'] is False
        assert result_dict['error_message'] == "Test error"
        assert result_dict['file_count'] == 0
    
    def test_create_publication_zip_with_subdirectories(self, temp_bios_dir):
        """Test ZIP creation with nested subdirectories"""
        character = "nested_character"
        output_dir = Path(temp_bios_dir) / character / "output"
        
        # Create nested structure
        markdown_dir = output_dir / "markdown" / "chapters"
        markdown_dir.mkdir(parents=True)
        (markdown_dir / "chapter1.md").write_text("Chapter 1")
        (markdown_dir / "chapter2.md").write_text("Chapter 2")
        
        service = ZipExportService(base_bios_dir=temp_bios_dir)
        result = service.create_publication_zip(character)
        
        assert result.success is True
        assert len(result.included_files) == 2
        
        # Verify nested paths
        with zipfile.ZipFile(result.zip_path, 'r') as zipf:
            files = zipf.namelist()
            assert "markdown/chapters/chapter1.md" in files
            assert "markdown/chapters/chapter2.md" in files
        
        # Cleanup
        os.remove(result.zip_path)
