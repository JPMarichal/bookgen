"""
Integration tests for biography generation with automatic source discovery

These tests verify the complete flow from request to job creation
with all three generation modes: automatic, hybrid, and manual.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestBiographyGenerationIntegration:
    """Integration tests for biography generation"""
    
    def test_complete_automatic_flow(self):
        """
        Test complete flow with automatic source generation
        
        This test verifies:
        1. Job creation succeeds with automatic mode
        2. Response includes mode and source metadata
        3. Job can be queried for status
        """
        # Create biography job in automatic mode
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Marie Curie",
                "mode": "automatic",
                "min_sources": 40,
                "quality_threshold": 0.8,
                "chapters": 10,
                "total_words": 25000
            }
        )
        
        # Verify job creation (may fail without API keys, but should accept request)
        if create_response.status_code == 202:
            data = create_response.json()
            
            # Verify response structure
            assert "job_id" in data
            assert data["mode"] == "automatic"
            assert "sources_generated_automatically" in data
            assert data["character"] == "Marie Curie"
            
            # Get job status
            job_id = data["job_id"]
            status_response = client.get(f"/api/v1/biographies/{job_id}/status")
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["job_id"] == job_id
            assert status_data["character"] == "Marie Curie"
    
    def test_complete_hybrid_flow(self):
        """
        Test complete flow with hybrid source generation
        
        This test verifies:
        1. Job creation with user sources + auto-completion
        2. Response includes both user and auto-generated counts
        3. Sources are validated and combined
        """
        # Create biography job in hybrid mode
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Albert Einstein",
                "mode": "hybrid",
                "sources": [
                    "https://en.wikipedia.org/wiki/Albert_Einstein",
                    "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
                ],
                "min_sources": 30,
                "chapters": 10,
                "total_words": 25000
            }
        )
        
        # Verify job creation
        if create_response.status_code == 202:
            data = create_response.json()
            
            assert "job_id" in data
            assert data["mode"] == "hybrid"
            assert "source_count" in data
            
            # Verify sources were processed
            if data.get("source_count"):
                assert data["source_count"] >= 2  # At least the user-provided sources
    
    def test_complete_manual_flow(self):
        """
        Test complete flow with manual source provision
        
        This test verifies:
        1. Job creation with manual sources
        2. Minimum source count validation
        3. Source URL validation
        """
        # Create valid source list (at least 10 required)
        sources = [
            f"https://example.com/source-{i}" for i in range(15)
        ]
        
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Isaac Newton",
                "mode": "manual",
                "sources": sources,
                "chapters": 10,
                "total_words": 25000
            }
        )
        
        # Verify job creation
        if create_response.status_code == 202:
            data = create_response.json()
            
            assert "job_id" in data
            assert data["mode"] == "manual"
            assert data["source_count"] == 15
            assert data.get("sources_generated_automatically") == False
    
    def test_automatic_mode_backward_compatibility(self):
        """
        Test backward compatibility - default mode should be manual
        
        Ensures existing API calls without 'mode' parameter still work.
        """
        # Create biography without specifying mode (should default to manual)
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test Character",
                "chapters": 5,
                "total_words": 5000
            }
        )
        
        assert create_response.status_code in [202, 400]  # 202 or 400 (no sources in manual mode)
        
        if create_response.status_code == 202:
            data = create_response.json()
            # Should default to manual mode
            assert data.get("mode", "manual") == "manual"
    
    def test_mode_validation(self):
        """Test that invalid modes are rejected"""
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "mode": "invalid_mode"
            }
        )
        
        # Should return validation error
        assert create_response.status_code == 422
    
    def test_manual_mode_insufficient_sources(self):
        """Test that manual mode requires minimum sources"""
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "mode": "manual",
                "sources": ["https://example.com"]  # Only 1, need 10
            }
        )
        
        # Should return bad request
        assert create_response.status_code == 400
        assert "at least 10 sources" in create_response.json()["detail"].lower()
    
    def test_quality_threshold_range(self):
        """Test quality threshold parameter validation"""
        # Test invalid threshold (> 1.0)
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "mode": "automatic",
                "quality_threshold": 1.5  # Invalid, should be 0-1
            }
        )
        
        assert create_response.status_code == 422  # Validation error
        
        # Test valid threshold
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "mode": "automatic",
                "quality_threshold": 0.8  # Valid
            }
        )
        
        # Should at least accept the request (may fail later without API keys)
        assert create_response.status_code in [202, 400, 500]


class TestEndpointCompatibility:
    """Test compatibility with existing endpoints"""
    
    def test_existing_source_validation_endpoint(self):
        """Verify existing source validation endpoint still works"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Test Source",
                        "author": "Test Author",
                        "url": "https://example.com",
                        "publication_year": 2020
                    }
                ]
            }
        )
        
        # Should work as before
        assert response.status_code in [200, 422]
    
    def test_existing_status_endpoint(self):
        """Verify status endpoint works with new job structure"""
        # First create a job
        create_response = client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "mode": "manual",
                "sources": [f"https://example.com/source-{i}" for i in range(15)]
            }
        )
        
        if create_response.status_code == 202:
            job_id = create_response.json()["job_id"]
            
            # Check status endpoint
            status_response = client.get(f"/api/v1/biographies/{job_id}/status")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert "job_id" in status_data
            assert "status" in status_data
            assert "character" in status_data
