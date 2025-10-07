"""
Tests for source validation endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestSourceValidation:
    """Tests for source validation endpoints"""
    
    def test_validate_sources_valid(self):
        """Test validating a list of valid sources"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Test Book",
                        "author": "Test Author",
                        "publication_date": "2020",
                        "source_type": "book"
                    },
                    {
                        "title": "Wikipedia Article",
                        "url": "https://en.wikipedia.org/wiki/Test",
                        "source_type": "url"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_sources"] == 2
        assert data["valid_sources"] == 2
        assert data["invalid_sources"] == 0
        assert len(data["results"]) == 2
        assert "summary" in data
    
    def test_validate_sources_invalid_url(self):
        """Test validating source with invalid URL"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Invalid URL",
                        "url": "not-a-url",
                        "source_type": "url"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        # Should get validation error from Pydantic
        assert response.status_code == 422
    
    def test_validate_sources_empty_title(self):
        """Test validating source with empty title"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "",
                        "source_type": "book"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        # Pydantic validates min_length=1, so this should fail at validation
        assert response.status_code == 422
    
    def test_validate_sources_invalid_date_format(self):
        """Test validating source with invalid date format"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Test Article",
                        "publication_date": "invalid-date",
                        "source_type": "article"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        result = data["results"][0]
        assert not result["is_valid"]
        assert any("date" in issue.lower() for issue in result["issues"])
    
    def test_validate_sources_valid_dates(self):
        """Test validating sources with various valid date formats"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {
                        "title": "Year only",
                        "publication_date": "2020",
                        "source_type": "book"
                    },
                    {
                        "title": "Year-Month",
                        "publication_date": "2020-05",
                        "source_type": "book"
                    },
                    {
                        "title": "Full date",
                        "publication_date": "2020-05-15",
                        "source_type": "book"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid_sources"] == 3
        assert data["invalid_sources"] == 0
    
    def test_validate_sources_empty_list(self):
        """Test validating empty sources list"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [],
                "check_accessibility": False
            }
        )
        
        # Should get validation error (min 1 source required)
        assert response.status_code == 422
    
    def test_validate_sources_source_types(self):
        """Test validating sources with different types"""
        response = client.post(
            "/api/v1/sources/validate",
            json={
                "sources": [
                    {"title": "URL Source", "url": "https://example.com", "source_type": "url"},
                    {"title": "Book Source", "source_type": "book"},
                    {"title": "Article Source", "source_type": "article"},
                    {"title": "Document Source", "source_type": "document"},
                    {"title": "Other Source", "source_type": "other"}
                ],
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_sources"] == 5
        assert "source_types" in data["summary"]
        assert data["summary"]["source_types"]["url"] == 1
        assert data["summary"]["source_types"]["book"] == 1
        assert data["summary"]["source_types"]["article"] == 1
        assert data["summary"]["source_types"]["document"] == 1
        assert data["summary"]["source_types"]["other"] == 1


class TestAdvancedSourceValidation:
    """Tests for advanced source validation endpoint"""
    
    def test_validate_sources_advanced_basic(self):
        """Test advanced validation with basic sources"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Einstein Biography",
                        "author": "Walter Isaacson",
                        "publication_date": "2007",
                        "source_type": "book"
                    }
                ],
                "biography_topic": "Albert Einstein",
                "check_accessibility": False,
                "min_relevance": 0.5,
                "min_credibility": 60.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_sources"] == 1
        assert "average_relevance" in data
        assert "average_credibility" in data
        assert "rejected_sources" in data
        assert "recommendations" in data
        assert len(data["results"]) == 1
        
        # Check result structure
        result = data["results"][0]
        assert "credibility_score" in result
        assert "domain_category" in result
        assert "is_trusted" in result
    
    def test_validate_sources_advanced_academic(self):
        """Test advanced validation with academic sources"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Physics Research Paper",
                        "author": "Dr. Smith",
                        "publication_date": "2023",
                        "url": "https://stanford.edu/research",
                        "source_type": "article"
                    }
                ],
                "biography_topic": "Albert Einstein",
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Academic sources should have high credibility
        assert data["average_credibility"] >= 80.0
        
        result = data["results"][0]
        assert result["is_trusted"] == True
        assert result["domain_category"] == "academic"
    
    def test_validate_sources_advanced_multiple(self):
        """Test advanced validation with multiple sources"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Einstein's Life",
                        "author": "Biographer",
                        "publication_date": "2020",
                        "url": "https://wikipedia.org/wiki/Einstein",
                        "source_type": "url"
                    },
                    {
                        "title": "Physics History",
                        "author": "Historian", 
                        "publication_date": "2019",
                        "source_type": "book"
                    },
                    {
                        "title": "Academic Article",
                        "author": "Professor",
                        "publication_date": "2022",
                        "url": "https://harvard.edu/einstein",
                        "source_type": "article"
                    }
                ],
                "biography_topic": "Albert Einstein",
                "check_accessibility": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_sources"] == 3
        assert len(data["results"]) == 3
        assert len(data["recommendations"]) > 0
        
        # Check summary statistics
        assert "summary" in data
        assert "trusted_sources" in data["summary"]
        assert "untrusted_sources" in data["summary"]
        assert "domain_categories" in data["summary"]
    
    def test_validate_sources_advanced_thresholds(self):
        """Test advanced validation with custom thresholds"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Test Source",
                        "source_type": "other"
                    }
                ],
                "biography_topic": "Test Topic",
                "check_accessibility": False,
                "min_relevance": 0.9,
                "min_credibility": 95.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # With high thresholds, likely to have rejections
        assert "rejected_sources" in data
    
    def test_validate_sources_advanced_missing_topic(self):
        """Test advanced validation without biography topic"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [
                    {
                        "title": "Test Source",
                        "source_type": "book"
                    }
                ],
                "check_accessibility": False
            }
        )
        
        # Should fail validation - biography_topic is required
        assert response.status_code == 422
    
    def test_validate_sources_advanced_empty_list(self):
        """Test advanced validation with empty sources list"""
        response = client.post(
            "/api/v1/sources/validate-advanced",
            json={
                "sources": [],
                "biography_topic": "Test Topic",
                "check_accessibility": False
            }
        )
        
        # Should fail validation - at least 1 source required
        assert response.status_code == 422
