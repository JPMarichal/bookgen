"""
Integration test for automatic source generation endpoint
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import app


@pytest.mark.api
class TestAutomaticSourceGenerationEndpoint:
    """Integration tests for /api/v1/sources/generate-automatic endpoint"""
    
    def test_endpoint_exists(self):
        """Test that the endpoint is registered"""
        client = TestClient(app)
        
        # Test with invalid request to confirm endpoint exists
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={}
        )
        
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    @patch('src.services.source_generator.OpenRouterClient')
    @patch('src.strategies.wikipedia_strategy.requests.Session')
    def test_endpoint_successful_generation(self, mock_session_class, mock_openrouter_class):
        """Test successful source generation via endpoint"""
        # Mock OpenRouter AI response
        mock_client = Mock()
        mock_openrouter_class.return_value = mock_client
        mock_client.generate_text.return_value = '''{
            "historical_period": "20th century, 1879-1955",
            "nationality": "German-American",
            "professional_field": "Theoretical Physics",
            "key_events": ["Theory of Relativity", "Nobel Prize 1921"],
            "related_entities": ["Niels Bohr", "Princeton University"],
            "search_terms": ["Einstein biography", "relativity theory", "physics Nobel"]
        }'''
        
        # Mock Wikipedia API responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock Wikipedia search response
        search_response = Mock()
        search_response.json.return_value = {
            'query': {
                'search': [{'title': 'Albert Einstein'}]
            }
        }
        search_response.raise_for_status = Mock()
        
        # Mock Wikipedia page info response
        info_response = Mock()
        info_response.json.return_value = {
            'query': {
                'pages': {
                    '123': {'title': 'Albert Einstein', 'pageid': 123}
                }
            }
        }
        info_response.raise_for_status = Mock()
        
        # Mock external links response
        extlinks_response = Mock()
        extlinks_response.json.return_value = {
            'query': {
                'pages': {
                    '123': {
                        'extlinks': [
                            {'*': 'https://nobelprize.org/prizes/physics/1921/einstein'},
                            {'*': 'https://archive.org/details/einstein-papers'}
                        ]
                    }
                }
            }
        }
        extlinks_response.raise_for_status = Mock()
        
        mock_session.get.side_effect = [
            search_response,
            info_response,
            extlinks_response
        ]
        
        # Make request
        client = TestClient(app)
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={
                "character_name": "Albert Einstein",
                "min_sources": 10,
                "max_sources": 20,
                "check_accessibility": False
            }
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["character_name"] == "Albert Einstein"
        assert "sources" in data
        assert "character_analysis" in data
        assert "validation_summary" in data
        assert "strategies_used" in data
        assert "generation_metadata" in data
        
        # Verify character analysis
        analysis = data["character_analysis"]
        assert analysis["character_name"] == "Albert Einstein"
        assert analysis["professional_field"] == "Theoretical Physics"
        assert len(analysis["search_terms"]) > 0
        
        # Verify strategies used
        assert "WikipediaStrategy" in data["strategies_used"]
    
    def test_endpoint_validation_errors(self):
        """Test endpoint validation"""
        client = TestClient(app)
        
        # Test missing character_name
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={}
        )
        assert response.status_code == 422
        
        # Test empty character_name
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={"character_name": ""}
        )
        assert response.status_code == 422
        
        # Test invalid min_sources
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={
                "character_name": "Test Person",
                "min_sources": 5  # Below minimum of 10
            }
        )
        assert response.status_code == 422
        
        # Test invalid relevance threshold
        response = client.post(
            "/api/v1/sources/generate-automatic",
            json={
                "character_name": "Test Person",
                "min_relevance": 1.5  # Above maximum of 1.0
            }
        )
        assert response.status_code == 422
