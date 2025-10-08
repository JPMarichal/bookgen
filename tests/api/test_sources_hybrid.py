"""
Integration tests for hybrid source generation endpoint
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import app


@pytest.mark.api
class TestHybridSourceGenerationEndpoint:
    """Integration tests for /api/v1/sources/generate-hybrid endpoint"""
    
    def test_endpoint_exists(self):
        """Test that the endpoint is registered"""
        client = TestClient(app)
        
        # Test with invalid request to confirm endpoint exists
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={}
        )
        
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_endpoint_user_sources_only(self, mock_validator_class, mock_auto_gen_class):
        """Test hybrid endpoint with only user sources (no auto-complete)"""
        client = TestClient(app)
        
        # Mock validator
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        mock_validator.validate_sources.return_value = {
            'total_sources': 2,
            'valid_sources': 2,
            'average_relevance': 0.8,
            'average_credibility': 85.0,
            'recommendations': []
        }
        
        # Request with user sources only
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "character_name": "Einstein",
                "user_sources": [
                    "https://example.com/einstein1",
                    "https://example.com/einstein2"
                ],
                "auto_complete": False,
                "target_count": 2,
                "provide_suggestions": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['character_name'] == "Einstein"
        assert data['user_source_count'] == 2
        assert data['auto_generated_count'] == 0
        assert len(data['sources']) == 2
        assert data['configuration']['auto_complete'] is False
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_endpoint_hybrid_mode(self, mock_validator_class, mock_auto_gen_class):
        """Test hybrid endpoint with user sources + auto-complete"""
        client = TestClient(app)
        
        # Mock validator
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        mock_validator.validate_sources.return_value = {
            'total_sources': 50,
            'valid_sources': 50,
            'average_relevance': 0.8,
            'average_credibility': 85.0,
            'recommendations': []
        }
        
        # Mock auto generator
        mock_auto_gen = Mock()
        mock_auto_gen_class.return_value = mock_auto_gen
        
        # Create mock auto-generated sources
        from src.api.models.sources import SourceItem, SourceType
        auto_sources = [
            SourceItem(
                url=f"https://auto.com/{i}",
                title=f"Auto Source {i}",
                source_type=SourceType.URL
            )
            for i in range(48)
        ]
        
        mock_auto_gen.generate_sources_for_character.return_value = {
            'sources': auto_sources,
            'character_analysis': None,
            'validation_summary': {}
        }
        
        # Request with hybrid mode
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "character_name": "Einstein",
                "user_sources": [
                    "https://example.com/manual1",
                    "https://example.com/manual2"
                ],
                "auto_complete": True,
                "target_count": 50,
                "provide_suggestions": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['character_name'] == "Einstein"
        assert data['user_source_count'] == 2
        assert data['auto_generated_count'] == 48
        assert len(data['sources']) == 50
        assert data['configuration']['auto_complete'] is True
        assert data['metadata']['target_met'] is True
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_endpoint_with_suggestions(self, mock_validator_class, mock_auto_gen_class):
        """Test hybrid endpoint with suggestion generation"""
        client = TestClient(app)
        
        # Mock validator
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        mock_validator.validate_sources.return_value = {
            'total_sources': 2,
            'valid_sources': 2,
            'average_relevance': 0.8,
            'average_credibility': 85.0,
            'recommendations': []
        }
        
        # Request with suggestions enabled
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "character_name": "Einstein",
                "user_sources": [
                    "https://example.com/source1",
                    "https://example.com/source2"
                ],
                "auto_complete": False,
                "target_count": 50,
                "provide_suggestions": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have suggestions because target not met
        assert len(data['suggestions']) > 0
    
    def test_endpoint_validates_request(self):
        """Test that endpoint validates request parameters"""
        client = TestClient(app)
        
        # Missing required field
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "user_sources": ["https://example.com"]
            }
        )
        assert response.status_code == 422
        
        # Invalid URL format
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "character_name": "Test",
                "user_sources": ["not-a-url"]
            }
        )
        assert response.status_code == 422
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_acceptance_criteria_via_endpoint(self, mock_validator_class, mock_auto_gen_class):
        """
        Test acceptance criteria from issue via API endpoint
        
        User can combine automatic + manual
        """
        client = TestClient(app)
        
        # Mock validator
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        mock_validator.validate_sources.return_value = {
            'total_sources': 50,
            'valid_sources': 50,
            'average_relevance': 0.8,
            'average_credibility': 85.0,
            'recommendations': []
        }
        
        # Mock auto generator
        mock_auto_gen = Mock()
        mock_auto_gen_class.return_value = mock_auto_gen
        
        from src.api.models.sources import SourceItem, SourceType
        auto_sources = [
            SourceItem(
                url=f"https://auto.com/{i}",
                title=f"Auto {i}",
                source_type=SourceType.URL
            )
            for i in range(49)
        ]
        
        mock_auto_gen.generate_sources_for_character.return_value = {
            'sources': auto_sources,
            'character_analysis': None,
            'validation_summary': {}
        }
        
        # ACCEPTANCE CRITERIA REQUEST:
        response = client.post(
            "/api/v1/sources/generate-hybrid",
            json={
                "character_name": "Einstein",
                "user_sources": ["https://example.com/manual-source"],
                "auto_complete": True,
                "target_count": 50
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        sources = data["sources"]
        
        # ACCEPTANCE CRITERIA CHECKS:
        # 1. User's manual source should be in result
        assert "https://example.com/manual-source" in [s["url"] for s in sources]
        
        # 2. Should have 50 sources total
        assert len(sources) == 50
        
        print("✅ API acceptance criteria met!")
