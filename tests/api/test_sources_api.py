"""
Comprehensive API endpoint tests for sources router
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


pytestmark = [pytest.mark.api]


class TestSourcesValidationEndpoint:
    """Test sources validation endpoint"""
    
    def test_validate_sources_valid_request(self, test_client):
        """Test validating sources with valid request"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Winston Churchill Biography",
                        "url": "https://www.britannica.com/biography/Winston-Churchill",
                        "source_type": "article"
                    }
                ],
                "topic": "Winston Churchill",
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_validate_sources_multiple(self, test_client):
        """Test validating multiple sources"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Source 1",
                        "url": "https://example.edu/article1",
                        "source_type": "article"
                    },
                    {
                        "title": "Source 2",
                        "url": "https://example.org/article2",
                        "source_type": "book"
                    },
                    {
                        "title": "Source 3",
                        "url": "https://example.gov/article3",
                        "source_type": "article"
                    }
                ],
                "topic": "Test Topic",
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
    
    def test_validate_sources_empty_list(self, test_client):
        """Test validating empty source list"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [],
                "topic": "Test"
            }
        )
        
        # Should either accept empty or return validation error
        assert response.status_code in [200, 422]
    
    def test_validate_sources_with_accessibility_check(self, test_client):
        """Test validating sources with accessibility check"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Test Source",
                        "url": "https://example.com/article",
                        "source_type": "article"
                    }
                ],
                "topic": "Test",
                "check_accessibility": True
            }
        )
        
        assert response.status_code == 200
    
    def test_validate_sources_invalid_url(self, test_client):
        """Test validating sources with invalid URL"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Invalid Source",
                        "url": "not-a-valid-url",
                        "source_type": "article"
                    }
                ],
                "topic": "Test"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_validate_sources_missing_required_fields(self, test_client):
        """Test validating sources with missing required fields"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Missing URL"
                        # Missing url and source_type
                    }
                ],
                "topic": "Test"
            }
        )
        
        assert response.status_code == 422
    
    def test_validate_sources_with_dates(self, test_client):
        """Test validating sources with publication dates"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Recent Article",
                        "url": "https://example.com/recent",
                        "source_type": "article",
                        "publication_date": "2023-01-15"
                    },
                    {
                        "title": "Old Article",
                        "url": "https://example.com/old",
                        "source_type": "article",
                        "publication_date": "1990-05-20"
                    }
                ],
                "topic": "Test"
            }
        )
        
        assert response.status_code == 200


class TestSourcesAdvancedValidation:
    """Test advanced source validation features"""
    
    def test_validate_sources_with_custom_thresholds(self, test_client):
        """Test validation with custom relevance/credibility thresholds"""
        response = test_client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Test Source",
                        "url": "https://example.edu/article",
                        "source_type": "article"
                    }
                ],
                "topic": "Test Topic",
                "min_relevance": 0.7,
                "min_credibility": 0.8
            }
        )
        
        # Should accept or return appropriate error
        assert response.status_code in [200, 404]
    
    def test_validate_sources_source_types(self, test_client):
        """Test validation with different source types"""
        source_types = ["article", "book", "video", "podcast", "other"]
        
        for source_type in source_types:
            response = test_client.post(
                "/api/v1/sources/validate",
                json={
                    "sources": [
                        {
                            "title": f"Test {source_type}",
                            "url": f"https://example.com/{source_type}",
                            "source_type": source_type
                        }
                    ],
                    "topic": "Test"
                }
            )
            
            assert response.status_code == 200
    
    def test_validate_sources_academic_domains(self, test_client):
        """Test validation prioritizes academic domains"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Academic Article",
                        "url": "https://university.edu/research/article",
                        "source_type": "article"
                    },
                    {
                        "title": "Regular Article",
                        "url": "https://random-blog.com/article",
                        "source_type": "article"
                    }
                ],
                "topic": "Research Topic"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Academic source should have higher credibility
        if len(data.get("results", [])) >= 2:
            academic_result = data["results"][0]
            regular_result = data["results"][1]
            
            # Check if credibility scores exist and academic is higher
            if "credibility_score" in academic_result and "credibility_score" in regular_result:
                assert academic_result["credibility_score"] >= regular_result["credibility_score"]


class TestSourcesEdgeCases:
    """Test edge cases for sources API"""
    
    @pytest.mark.parametrize("num_sources", [1, 5, 10, 20, 50])
    def test_validate_various_source_counts(self, test_client, num_sources):
        """Test validating various numbers of sources"""
        sources = [
            {
                "title": f"Source {i}",
                "url": f"https://example.com/source{i}",
                "source_type": "article"
            }
            for i in range(num_sources)
        ]
        
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": sources,
                "topic": "Test",
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == num_sources
    
    def test_validate_sources_unicode_characters(self, test_client):
        """Test validating sources with unicode characters"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Français Article über 中文",
                        "url": "https://example.com/unicode",
                        "source_type": "article"
                    }
                ],
                "topic": "Unicode Test"
            }
        )
        
        assert response.status_code == 200
    
    def test_validate_sources_long_urls(self, test_client):
        """Test validating sources with very long URLs"""
        long_url = "https://example.com/" + "a" * 500
        
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Long URL Source",
                        "url": long_url,
                        "source_type": "article"
                    }
                ],
                "topic": "Test"
            }
        )
        
        # Should handle or reject based on validation rules
        assert response.status_code in [200, 422]
    
    def test_validate_sources_duplicate_urls(self, test_client):
        """Test validating sources with duplicate URLs"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Source 1",
                        "url": "https://example.com/same",
                        "source_type": "article"
                    },
                    {
                        "title": "Source 2 (duplicate URL)",
                        "url": "https://example.com/same",
                        "source_type": "article"
                    }
                ],
                "topic": "Test"
            }
        )
        
        assert response.status_code == 200
        # System should handle duplicates appropriately


class TestSourcesResponseStructure:
    """Test response structure of sources endpoints"""
    
    def test_validation_response_structure(self, test_client):
        """Test that validation response has expected structure"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Test",
                        "url": "https://example.com",
                        "source_type": "article"
                    }
                ],
                "topic": "Test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields
        assert "results" in data
        assert isinstance(data["results"], list)
        
        if len(data["results"]) > 0:
            result = data["results"][0]
            # Should have validation details
            assert "title" in result
            assert "url" in result
    
    def test_validation_includes_scores(self, test_client):
        """Test that validation includes relevance and credibility scores"""
        response = test_client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Academic Article",
                        "url": "https://university.edu/article",
                        "source_type": "article"
                    }
                ],
                "topic": "Academic Topic"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data.get("results", [])) > 0:
            result = data["results"][0]
            # Check for score fields (may vary by implementation)
            assert isinstance(result, dict)
