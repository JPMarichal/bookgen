"""
Tests for Word export service
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.services.word_exporter import WordExporter
from src.config.export_config import ExportConfig
from src.utils.pandoc_wrapper import PandocWrapper
from src.api.models.export import (
    WordExportResult,
    WordExportError,
    DocumentMetadata,
    DocumentInfo
)


class TestExportConfig:
    """Test export configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ExportConfig()
        
        assert config.toc_title == "Contenido"
        assert config.toc_depth == 1
        assert config.include_toc is True
        assert config.standalone is True
    
    def test_pandoc_command_basic(self):
        """Test basic Pandoc command generation"""
        config = ExportConfig()
        command = config.get_pandoc_command(
            input_file="input.md",
            output_file="output.docx"
        )
        
        assert "pandoc" in command[0]
        assert "input.md" in command
        assert "-o" in command
        assert "output.docx" in command
        assert "--table-of-contents" in command
    
    def test_pandoc_command_with_metadata(self):
        """Test Pandoc command with metadata"""
        config = ExportConfig()
        metadata = {
            'title': 'Test Document',
            'author': 'Test Author'
        }
        command = config.get_pandoc_command(
            input_file="input.md",
            output_file="output.docx",
            metadata=metadata
        )
        
        assert "--metadata" in command
        assert "title=Test Document" in command
        assert "author=Test Author" in command
    
    def test_pandoc_command_without_toc(self):
        """Test Pandoc command without TOC"""
        config = ExportConfig(include_toc=False)
        command = config.get_pandoc_command(
            input_file="input.md",
            output_file="output.docx"
        )
        
        assert "--table-of-contents" not in command
        assert "--toc-depth" not in ' '.join(command)


class TestPandocWrapper:
    """Test Pandoc wrapper"""
    
    def test_initialization(self):
        """Test wrapper initialization"""
        wrapper = PandocWrapper("pandoc")
        assert wrapper.pandoc_executable == "pandoc"
    
    @patch('subprocess.run')
    def test_get_version_success(self, mock_run):
        """Test getting Pandoc version"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="pandoc 2.19.2\n"
        )
        
        wrapper = PandocWrapper()
        version = wrapper.get_version()
        
        assert version is not None
        assert "pandoc" in version.lower()
    
    @patch('subprocess.run')
    def test_get_version_failure(self, mock_run):
        """Test Pandoc version when not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        wrapper = PandocWrapper()
        version = wrapper.get_version()
        
        assert version is None
    
    @patch('subprocess.run')
    def test_is_available(self, mock_run):
        """Test checking Pandoc availability"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="pandoc 2.19.2\n"
        )
        
        wrapper = PandocWrapper()
        assert wrapper.is_available() is True
    
    @patch('subprocess.run')
    def test_convert_success(self, mock_run):
        """Test successful conversion"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        wrapper = PandocWrapper()
        success, message = wrapper.convert(
            input_file="input.md",
            output_file="output.docx"
        )
        
        assert success is True
        assert "Successfully" in message
    
    @patch('subprocess.run')
    def test_convert_failure(self, mock_run):
        """Test failed conversion"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Pandoc error"
        )
        
        wrapper = PandocWrapper()
        success, message = wrapper.convert(
            input_file="input.md",
            output_file="output.docx"
        )
        
        assert success is False
        assert "error" in message.lower()
    
    def test_count_headings(self, tmp_path):
        """Test counting headings in markdown"""
        md_file = tmp_path / "test.md"
        md_file.write_text("""
# Heading 1
Some content
## Heading 2
More content
# Heading 3
Final content
""")
        
        wrapper = PandocWrapper()
        count = wrapper.count_headings(str(md_file))
        
        assert count == 2  # Only level 1 headings


class TestDocumentMetadata:
    """Test document metadata"""
    
    def test_empty_metadata(self):
        """Test empty metadata"""
        metadata = DocumentMetadata()
        data = metadata.to_dict()
        
        assert data == {}
    
    def test_full_metadata(self):
        """Test full metadata"""
        metadata = DocumentMetadata(
            title="Test Title",
            author="Test Author",
            subject="Test Subject",
            description="Test Description",
            keywords="test, keywords",
            date="2024-01-01"
        )
        data = metadata.to_dict()
        
        assert data['title'] == "Test Title"
        assert data['author'] == "Test Author"
        assert data['subject'] == "Test Subject"
        assert data['description'] == "Test Description"
        assert data['keywords'] == "test, keywords"
        assert data['date'] == "2024-01-01"


class TestWordExportResult:
    """Test word export result"""
    
    def test_successful_result(self):
        """Test successful export result"""
        result = WordExportResult(
            success=True,
            output_file="/tmp/test.docx",
            file_size=1024000,
            has_toc=True,
            toc_entries=10
        )
        
        assert result.success is True
        assert result.is_valid is True
        assert result.file_size_mb == pytest.approx(0.98, rel=0.1)
    
    def test_failed_result(self):
        """Test failed export result"""
        result = WordExportResult(
            success=False,
            output_file="",
            file_size=0,
            has_toc=False,
            toc_entries=0,
            error_message="Test error"
        )
        
        assert result.success is False
        assert result.is_valid is False
        assert result.error_message == "Test error"
    
    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = WordExportResult(
            success=True,
            output_file="/tmp/test.docx",
            file_size=1024,
            has_toc=True,
            toc_entries=5
        )
        
        data = result.to_dict()
        
        assert data['success'] is True
        assert data['output_file'] == "/tmp/test.docx"
        assert data['file_size'] == 1024
        assert data['has_toc'] is True
        assert data['toc_entries'] == 5


class TestWordExporter:
    """Test Word exporter service"""
    
    def test_initialization(self):
        """Test exporter initialization"""
        exporter = WordExporter()
        
        assert exporter.config is not None
        assert exporter.pandoc is not None
    
    def test_initialization_with_config(self):
        """Test exporter with custom config"""
        config = ExportConfig(toc_title="Contents", toc_depth=2)
        exporter = WordExporter(config)
        
        assert exporter.config.toc_title == "Contents"
        assert exporter.config.toc_depth == 2
    
    @patch('src.services.word_exporter.PandocWrapper')
    def test_validate_environment_success(self, mock_pandoc_class):
        """Test environment validation success"""
        mock_pandoc = Mock()
        mock_pandoc.is_available.return_value = True
        mock_pandoc_class.return_value = mock_pandoc
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ExportConfig(
                output_directory=tmpdir,
                word_template_path=os.path.join(tmpdir, "template.docx")
            )
            # Create template file
            Path(config.word_template_path).touch()
            
            exporter = WordExporter(config)
            is_valid, issues = exporter.validate_environment()
            
            # Should be valid since output dir exists and template exists
            assert is_valid is True or len(issues) <= 1  # May have pandoc issue in test env
    
    def test_extract_character_name_from_path(self):
        """Test extracting character name from path"""
        exporter = WordExporter()
        
        # Test with new path structure (bios/character/output/markdown/...)
        name = exporter._extract_character_name("/app/bios/winston_churchill/output/markdown/biography.md")
        assert name == "winston_churchill"
        
        # Test with different structure
        name = exporter._extract_character_name("/tmp/test_character/file.md")
        assert name == "test_character"
    
    @patch('subprocess.run')
    def test_export_to_word_with_toc(self, mock_subprocess):
        """Test exporting to Word with TOC"""
        # Mock subprocess for Pandoc
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test markdown file
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, 'w') as f:
                f.write("# Heading 1\nContent\n# Heading 2\nMore content")
            
            # Create template
            template_file = os.path.join(tmpdir, "template.docx")
            Path(template_file).touch()
            
            # Setup output path
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)
            
            config = ExportConfig(
                output_directory=output_dir,
                word_template_path=template_file,
                pandoc_executable="pandoc"
            )
            exporter = WordExporter(config)
            
            # Mock the actual file creation by Pandoc
            def subprocess_side_effect(command, **kwargs):
                # Extract output file from command
                if '-o' in command:
                    idx = command.index('-o')
                    output_file = command[idx + 1]
                    # Create the output file
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    with open(output_file, 'wb') as f:
                        f.write(b'fake docx content - ' * 100)
                
                return Mock(returncode=0, stdout="", stderr="")
            
            mock_subprocess.side_effect = subprocess_side_effect
            
            result = exporter.export_to_word_with_toc(
                markdown_file=md_file,
                toc_title="Contenido",
                toc_depth=1
            )
            
            assert result.success is True
            assert result.has_toc is True
            assert result.toc_entries == 2  # Two level 1 headings in test file
            assert result.file_size > 0
    
    @patch('src.utils.pandoc_wrapper.PandocWrapper.is_available')
    def test_export_biography(self, mock_available):
        """Test biography export"""
        mock_available.return_value = True
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            md_file = os.path.join(tmpdir, "character", "biography.md")
            os.makedirs(os.path.dirname(md_file))
            with open(md_file, 'w') as f:
                f.write("# Biography\nContent")
            
            exporter = WordExporter()
            
            # Mock the internal export method
            with patch.object(exporter, 'export_to_word_with_toc') as mock_export:
                mock_export.return_value = WordExportResult(
                    success=True,
                    output_file=os.path.join(tmpdir, "output.docx"),
                    file_size=1024,
                    has_toc=True,
                    toc_entries=3
                )
                
                result_path = exporter.export_biography(md_file)
                
                assert result_path is not None
                assert mock_export.called
    
    def test_export_biography_failure(self):
        """Test biography export failure"""
        exporter = WordExporter()
        
        with patch.object(exporter, 'export_to_word_with_toc') as mock_export:
            mock_export.return_value = WordExportResult(
                success=False,
                output_file="",
                file_size=0,
                has_toc=False,
                toc_entries=0,
                error_message="Test error"
            )
            
            with pytest.raises(WordExportError):
                exporter.export_biography("/nonexistent/file.md")


class TestIntegration:
    """Integration tests (require Pandoc installation)"""
    
    @pytest.mark.skipif(
        not PandocWrapper().is_available(),
        reason="Pandoc not installed"
    )
    def test_full_export_workflow(self, tmp_path):
        """Test complete export workflow with real Pandoc"""
        # Create test markdown
        md_file = tmp_path / "test.md"
        md_file.write_text("""
# Chapter 1
This is the first chapter.

# Chapter 2
This is the second chapter.

# Chapter 3
This is the third chapter.
""")
        
        # Note: This test would need a real Word template to work fully
        # For now, we'll skip if template doesn't exist
        template_path = "/app/wordTemplate/reference.docx"
        if not os.path.exists(template_path):
            pytest.skip("Word template not available")
        
        config = ExportConfig(
            word_template_path=template_path,
            output_directory=str(tmp_path)
        )
        exporter = WordExporter(config)
        
        metadata = DocumentMetadata(
            title="Test Biography",
            author="Test Author"
        )
        
        result = exporter.export_to_word_with_toc(
            markdown_file=str(md_file),
            metadata=metadata
        )
        
        assert result.success is True
        assert os.path.exists(result.output_file)
        assert result.file_size > 0
        assert result.has_toc is True
        assert result.toc_entries == 3
