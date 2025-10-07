"""
Tests for biography generation endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestBiographyEndpoints:
    """Tests for biography generation endpoints"""
    
    def test_generate_biography_valid_request(self):
        """Test biography generation with valid request"""
        response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test Character",
                "chapters": 5,
                "total_words": 5000
            }
        )
        
        assert response.status_code == 202
        data = response.json()
        
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["character"] == "Test Character"
        assert data["chapters"] == 5
        assert "created_at" in data
        assert "estimated_completion_time" in data
    
    def test_generate_biography_minimal_request(self):
        """Test biography generation with minimal request (only character)"""
        response = client.post(
            "/api/v1/biographies/generate",
            json={"character": "Minimal Test"}
        )
        
        assert response.status_code == 202
        data = response.json()
        
        assert data["character"] == "Minimal Test"
        assert data["chapters"] == 20  # Default value
    
    def test_generate_biography_invalid_character(self):
        """Test biography generation with empty character name"""
        response = client.post(
            "/api/v1/biographies/generate",
            json={"character": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_biography_invalid_chapters(self):
        """Test biography generation with invalid chapter count"""
        response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "chapters": 0  # Must be >= 1
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_biography_too_many_chapters(self):
        """Test biography generation with too many chapters"""
        response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "chapters": 100  # Max is 50
            }
        )
        
        assert response.status_code == 422
    
    def test_get_job_status_valid(self):
        """Test getting status of a valid job"""
        # First create a job
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={"character": "Status Test"}
        )
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = client.get(f"/api/v1/biographies/{job_id}/status")
        
        assert status_response.status_code == 200
        data = status_response.json()
        
        assert data["job_id"] == job_id
        assert data["character"] == "Status Test"
        assert "status" in data
        assert "created_at" in data
    
    def test_get_job_status_not_found(self):
        """Test getting status of non-existent job"""
        response = client.get("/api/v1/biographies/fake-job-id/status")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_download_job_not_found(self):
        """Test downloading non-existent job"""
        response = client.get("/api/v1/biographies/fake-job-id/download")
        
        assert response.status_code == 404
    
    def test_download_job_not_completed(self):
        """Test downloading job that's not completed"""
        # Create a job
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={"character": "Download Test"}
        )
        job_id = create_response.json()["job_id"]
        
        # Try to download immediately (job is still pending)
        download_response = client.get(f"/api/v1/biographies/{job_id}/download")
        
        # Should fail because job is not completed
        assert download_response.status_code == 400
        assert "not completed" in download_response.json()["detail"].lower()
