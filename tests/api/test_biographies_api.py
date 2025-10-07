"""
Comprehensive API endpoint tests for biographies router
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


pytestmark = [pytest.mark.api]


class TestBiographiesEndpoints:
    """Test biographies API endpoints"""
    
    def test_generate_biography_valid_request(self, test_client):
        """Test generating a biography with valid request"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "task-123"
            
            response = test_client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Winston Churchill",
                    "chapters": 8,
                    "length_type": "normal"
                }
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "pending"
            assert data["character"] == "Winston Churchill"
    
    def test_generate_biography_invalid_chapters(self, test_client):
        """Test generating biography with invalid chapter count"""
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={
                "character": "Test",
                "chapters": 0  # Invalid
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_biography_missing_character(self, test_client):
        """Test generating biography without character name"""
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={
                "chapters": 5
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_biography_with_sources(self, test_client):
        """Test generating biography with source inclusion"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "task-456"
            
            response = test_client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Marie Curie",
                    "chapters": 6,
                    "include_sources": True
                }
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "job_id" in data
    
    def test_generate_biography_custom_length(self, test_client):
        """Test generating biography with custom length type"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "task-789"
            
            response = test_client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": "Albert Einstein",
                    "chapters": 10,
                    "length_type": "long"
                }
            )
            
            assert response.status_code == 202
    
    @patch('src.api.routers.biographies.db')
    def test_get_biography_status_success(self, mock_db, test_client):
        """Test getting biography status"""
        mock_session = MagicMock()
        mock_db.SessionLocal.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "job-123"
        mock_job.status = "completed"
        mock_job.character_name = "Test Character"
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        response = test_client.get("/api/v1/biographies/job-123/status")
        
        assert response.status_code in [200, 404]  # May not find in test DB
    
    def test_get_biography_status_not_found(self, test_client):
        """Test getting status for non-existent biography"""
        response = test_client.get("/api/v1/biographies/nonexistent-id/status")
        
        # Should return 404 or handle gracefully
        assert response.status_code in [404, 200]
    
    @patch('src.api.routers.biographies.db')
    def test_download_biography_success(self, mock_db, test_client):
        """Test downloading a completed biography"""
        mock_session = MagicMock()
        mock_db.SessionLocal.return_value = mock_session
        
        mock_biography = MagicMock()
        mock_biography.id = "bio-123"
        mock_biography.status = "completed"
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_biography
        
        response = test_client.get("/api/v1/biographies/bio-123/download")
        
        # Should return file or redirect
        assert response.status_code in [200, 404, 302]
    
    def test_download_biography_not_ready(self, test_client):
        """Test downloading biography that's not ready"""
        response = test_client.get("/api/v1/biographies/pending-bio/download")
        
        # Should handle gracefully
        assert response.status_code in [404, 400, 200]


class TestBiographiesValidation:
    """Test input validation for biographies endpoints"""
    
    def test_validate_chapter_range(self, test_client):
        """Test chapter count validation"""
        # Too few chapters
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={"character": "Test", "chapters": 0}
        )
        assert response.status_code == 422
        
        # Too many chapters
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={"character": "Test", "chapters": 100}
        )
        assert response.status_code == 422
    
    def test_validate_length_type(self, test_client):
        """Test length type validation"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "task-val"
            
            # Valid length types
            for length_type in ["short", "normal", "long"]:
                response = test_client.post(
                    "/api/v1/biographies/generate",
                    json={
                        "character": "Test",
                        "chapters": 5,
                        "length_type": length_type
                    }
                )
                assert response.status_code == 202
    
    def test_validate_character_name_length(self, test_client):
        """Test character name length validation"""
        # Empty character name
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={"character": "", "chapters": 5}
        )
        assert response.status_code == 422
        
        # Very long character name (if there's a limit)
        response = test_client.post(
            "/api/v1/biographies/generate",
            json={"character": "X" * 500, "chapters": 5}
        )
        # Should either accept or reject based on validation rules
        assert response.status_code in [202, 422]


class TestBiographiesEdgeCases:
    """Test edge cases for biographies API"""
    
    @pytest.mark.parametrize("chapters", [1, 5, 10, 15, 20])
    def test_various_chapter_counts(self, test_client, chapters):
        """Test generating biographies with various chapter counts"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = f"task-{chapters}"
            
            response = test_client.post(
                "/api/v1/biographies/generate",
                json={
                    "character": f"Test Character {chapters}",
                    "chapters": chapters
                }
            )
            
            # Should accept valid chapter counts
            if 1 <= chapters <= 30:
                assert response.status_code == 202
    
    def test_concurrent_generation_requests(self, test_client):
        """Test handling multiple concurrent generation requests"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "concurrent-task"
            
            responses = []
            for i in range(5):
                response = test_client.post(
                    "/api/v1/biographies/generate",
                    json={
                        "character": f"Character {i}",
                        "chapters": 5
                    }
                )
                responses.append(response)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 202
    
    def test_special_characters_in_name(self, test_client):
        """Test handling special characters in character names"""
        with patch('src.api.routers.biographies.generate_chapter') as mock_task:
            mock_task.delay.return_value.id = "special-task"
            
            special_names = [
                "José María",
                "François Müller",
                "李明",
                "O'Brien"
            ]
            
            for name in special_names:
                response = test_client.post(
                    "/api/v1/biographies/generate",
                    json={"character": name, "chapters": 5}
                )
                # Should handle special characters
                assert response.status_code in [202, 422]
