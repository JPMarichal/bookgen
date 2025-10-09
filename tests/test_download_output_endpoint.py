"""
Integration tests for the download-output endpoint
"""
import os
import pytest
import tempfile
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestDownloadOutputEndpoint:
    """Integration tests for GET /{character}/download-output endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, tmp_path, monkeypatch):
        """Setup test character data before each test"""
        # Create temporary bios directory
        bios_dir = tmp_path / "bios"
        bios_dir.mkdir()
        
        # Monkeypatch the bios directory
        monkeypatch.setattr("src.services.zip_export_service.ZipExportService.__init__",
                           lambda self, base_bios_dir="bios": setattr(self, 'base_bios_dir', str(bios_dir)))
        
        # Create test character with output files
        self.test_character = "test_character"
        output_dir = bios_dir / self.test_character / "output"
        
        # Create markdown files
        markdown_dir = output_dir / "markdown"
        markdown_dir.mkdir(parents=True)
        (markdown_dir / "La biografia de Test Character.md").write_text(
            "# Test Character\n\nThis is a test biography."
        )
        (markdown_dir / "concatenation-log.txt").write_text("Concatenation log")
        (markdown_dir / "quality-metrics.json").write_text('{"quality": 0.95}')
        
        # Create word files
        word_dir = output_dir / "word"
        word_dir.mkdir()
        (word_dir / "La biografia de Test Character.docx").write_text("Mock Word document")
        (word_dir / "export-metadata.json").write_text('{"exported_at": "2024-01-01"}')
        
        # Create kdp files
        kdp_dir = output_dir / "kdp"
        kdp_dir.mkdir()
        (kdp_dir / "cover-image.jpg").write_text("Mock cover image data")
        (kdp_dir / "formatted-manuscript.docx").write_text("Mock formatted manuscript")
        (kdp_dir / "kdp-metadata.json").write_text('{"title": "Test Character Biography"}')
        
        self.bios_dir = str(bios_dir)
        
        yield
    
    def test_download_output_success(self, monkeypatch):
        """Test successful download of output files"""
        response = client.get(f"/api/v1/biographies/{self.test_character}/download-output")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert f"{self.test_character}_publicacion.zip" in response.headers["content-disposition"]
        
        # Verify ZIP content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            with zipfile.ZipFile(tmp_path, 'r') as zipf:
                files = zipf.namelist()
                # Should have markdown, word, and kdp files
                assert any("markdown/" in f for f in files)
                assert any("word/" in f for f in files)
                assert any("kdp/" in f for f in files)
        finally:
            os.remove(tmp_path)
    
    def test_download_output_character_not_found(self):
        """Test 404 error when character doesn't exist"""
        response = client.get("/api/v1/biographies/nonexistent_character/download-output")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() or "no publication files" in data["detail"].lower()
    
    def test_download_output_empty_character_name(self):
        """Test 400 error for empty character name"""
        response = client.get("/api/v1/biographies/ /download-output")
        
        # This might be caught by routing or our validation
        assert response.status_code in [400, 404]
    
    def test_download_output_normalizes_character_name(self, monkeypatch):
        """Test that character name is normalized (spaces to underscores)"""
        # Create character with spaces in directory name (after normalization)
        bios_dir = Path(self.bios_dir)
        output_dir = bios_dir / "test_with_spaces" / "output"
        markdown_dir = output_dir / "markdown"
        markdown_dir.mkdir(parents=True)
        (markdown_dir / "test.md").write_text("Test")
        
        # Request with spaces should be normalized to underscores
        response = client.get("/api/v1/biographies/test with spaces/download-output")
        
        # Should succeed if normalization works
        assert response.status_code == 200
    
    def test_download_output_filename_format(self, monkeypatch):
        """Test that ZIP filename follows correct format"""
        response = client.get(f"/api/v1/biographies/{self.test_character}/download-output")
        
        assert response.status_code == 200
        
        # Check filename in Content-Disposition header
        content_disposition = response.headers.get("content-disposition", "")
        assert f"{self.test_character}_publicacion.zip" in content_disposition
    
    def test_download_output_zip_contains_all_directories(self, monkeypatch):
        """Test that ZIP contains all expected directories"""
        response = client.get(f"/api/v1/biographies/{self.test_character}/download-output")
        
        assert response.status_code == 200
        
        # Save and verify ZIP content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            with zipfile.ZipFile(tmp_path, 'r') as zipf:
                files = zipf.namelist()
                
                # Check for expected subdirectories
                markdown_files = [f for f in files if f.startswith("markdown/")]
                word_files = [f for f in files if f.startswith("word/")]
                kdp_files = [f for f in files if f.startswith("kdp/")]
                
                assert len(markdown_files) > 0, "Should contain markdown files"
                assert len(word_files) > 0, "Should contain word files"
                assert len(kdp_files) > 0, "Should contain kdp files"
        finally:
            os.remove(tmp_path)
    
    def test_download_output_valid_zip_file(self, monkeypatch):
        """Test that downloaded file is a valid ZIP archive"""
        response = client.get(f"/api/v1/biographies/{self.test_character}/download-output")
        
        assert response.status_code == 200
        
        # Verify it's a valid ZIP by opening it
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            # This should not raise an exception
            with zipfile.ZipFile(tmp_path, 'r') as zipf:
                # Verify ZIP integrity
                bad_file = zipf.testzip()
                assert bad_file is None, f"ZIP file is corrupted: {bad_file}"
        finally:
            os.remove(tmp_path)
