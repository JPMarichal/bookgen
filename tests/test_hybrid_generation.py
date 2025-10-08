"""
Tests for hybrid source generation service
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json

from src.services.hybrid_generator import HybridSourceGenerator
from src.services.source_generator import AutomaticSourceGenerator
from src.services.source_validator import SourceValidationService
from src.api.models.sources import SourceItem, SourceType
from src.api.models.hybrid_generation import (
    HybridSourceGenerationRequest,
    HybridSourceGenerationResponse,
    SuggestionItem
)


class TestHybridSourceGenerationRequest:
    """Test HybridSourceGenerationRequest model"""
    
    def test_request_creation_defaults(self):
        """Test request with default values"""
        request = HybridSourceGenerationRequest(
            character_name="Albert Einstein"
        )
        
        assert request.character_name == "Albert Einstein"
        assert request.user_sources == []
        assert request.auto_complete is True
        assert request.target_count == 50
        assert request.check_accessibility is True
        assert request.min_relevance == 0.7
        assert request.min_credibility == 80.0
        assert request.provide_suggestions is True
    
    def test_request_creation_custom(self):
        """Test request with custom values"""
        request = HybridSourceGenerationRequest(
            character_name="Marie Curie",
            user_sources=["https://example.com/curie"],
            auto_complete=False,
            target_count=30,
            check_accessibility=False,
            min_relevance=0.6,
            min_credibility=70.0,
            provide_suggestions=False
        )
        
        assert request.character_name == "Marie Curie"
        assert len(request.user_sources) == 1
        assert request.user_sources[0] == "https://example.com/curie"
        assert request.auto_complete is False
        assert request.target_count == 30
        assert request.check_accessibility is False
        assert request.min_relevance == 0.6
        assert request.min_credibility == 70.0
        assert request.provide_suggestions is False
    
    def test_request_validates_urls(self):
        """Test request validates URL format"""
        with pytest.raises(ValueError, match="Invalid URL format"):
            HybridSourceGenerationRequest(
                character_name="Test",
                user_sources=["not-a-url"]
            )
    
    def test_request_accepts_valid_urls(self):
        """Test request accepts valid URLs"""
        request = HybridSourceGenerationRequest(
            character_name="Test",
            user_sources=[
                "https://example.com/page",
                "http://test.org/article"
            ]
        )
        assert len(request.user_sources) == 2


class TestSuggestionItem:
    """Test SuggestionItem model"""
    
    def test_suggestion_creation(self):
        """Test creating a suggestion"""
        source = SourceItem(
            url="https://example.com/suggestion",
            title="Suggested Source",
            source_type=SourceType.ARTICLE
        )
        
        suggestion = SuggestionItem(
            suggested_source=source,
            reason="This fills a gap in your sources",
            relevance_score=0.85,
            category="fills_gap"
        )
        
        assert suggestion.suggested_source.url == "https://example.com/suggestion"
        assert suggestion.reason == "This fills a gap in your sources"
        assert suggestion.relevance_score == 0.85
        assert suggestion.category == "fills_gap"


class TestHybridSourceGenerator:
    """Test HybridSourceGenerator service"""
    
    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        generator = HybridSourceGenerator()
        
        assert generator.automatic_generator is not None
        assert generator.source_validator is not None
    
    def test_extract_title_from_url(self):
        """Test extracting title from URL"""
        generator = HybridSourceGenerator()
        
        # Simple domain
        title = generator._extract_title_from_url("https://example.com")
        assert "example.com" in title
        
        # With path
        title = generator._extract_title_from_url("https://example.com/article-name")
        assert "example.com" in title
        assert "article name" in title.lower()
        
        # With query params
        title = generator._extract_title_from_url("https://example.com/page?id=123")
        assert "?" not in title
    
    def test_extract_domain(self):
        """Test extracting domain from URL"""
        generator = HybridSourceGenerator()
        
        assert generator._extract_domain("https://www.example.com/path") == "example.com"
        assert generator._extract_domain("http://example.com") == "example.com"
        assert generator._extract_domain("https://sub.example.com") == "sub.example.com"
    
    def test_remove_duplicates(self):
        """Test removing duplicate sources"""
        generator = HybridSourceGenerator()
        
        user_sources = [
            SourceItem(url="https://example.com/1", title="User 1", source_type=SourceType.URL),
            SourceItem(url="https://example.com/2", title="User 2", source_type=SourceType.URL)
        ]
        
        auto_sources = [
            SourceItem(url="https://example.com/1", title="Auto 1", source_type=SourceType.URL),  # Duplicate
            SourceItem(url="https://example.com/3", title="Auto 3", source_type=SourceType.URL),  # Unique
            SourceItem(url="https://EXAMPLE.com/2", title="Auto 2", source_type=SourceType.URL)   # Duplicate (case)
        ]
        
        result = generator._remove_duplicates(auto_sources, user_sources)
        
        assert len(result) == 1
        assert result[0].url == "https://example.com/3"
    
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_process_user_sources(self, mock_validator_class):
        """Test processing user-provided sources"""
        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        
        generator = HybridSourceGenerator(source_validator=mock_validator)
        
        user_urls = [
            "https://example.com/source1",
            "https://example.com/source2"
        ]
        
        result = generator._process_user_sources(
            user_urls,
            "Test Character",
            check_accessibility=True
        )
        
        assert len(result) == 2
        assert all(isinstance(s, SourceItem) for s in result)
        assert result[0].url == "https://example.com/source1"
        assert result[1].url == "https://example.com/source2"
    
    def test_generate_suggestions_fills_gaps(self):
        """Test suggestion generation identifies missing source types"""
        generator = HybridSourceGenerator()
        
        # Sources without academic sources
        sources = [
            SourceItem(url="https://example.com/1", title="URL Source", source_type=SourceType.URL)
        ]
        
        request = HybridSourceGenerationRequest(
            character_name="Einstein",
            target_count=50,
            provide_suggestions=True
        )
        
        suggestions = generator._generate_suggestions(
            sources, sources, "Einstein", request
        )
        
        # Should suggest academic sources or other missing types
        assert len(suggestions) > 0
    
    def test_generate_suggestions_warns_same_domain(self):
        """Test suggestion generation warns about too many from same domain"""
        generator = HybridSourceGenerator()
        
        # Many sources from same domain
        sources = [
            SourceItem(
                url=f"https://example.com/page{i}",
                title=f"Page {i}",
                source_type=SourceType.URL
            )
            for i in range(10)
        ]
        
        request = HybridSourceGenerationRequest(
            character_name="Test",
            target_count=50,
            provide_suggestions=True
        )
        
        suggestions = generator._generate_suggestions(
            sources, sources, "Test", request
        )
        
        # Should suggest diversification
        assert any("divers" in s.reason.lower() for s in suggestions)
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_generate_hybrid_sources_user_only(self, mock_validator_class, mock_auto_gen_class):
        """Test hybrid generation with only user sources (no auto-complete)"""
        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
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
        
        # Mock auto generator (shouldn't be called)
        mock_auto_gen = MagicMock()
        
        generator = HybridSourceGenerator(
            automatic_generator=mock_auto_gen,
            source_validator=mock_validator
        )
        
        request = HybridSourceGenerationRequest(
            character_name="Einstein",
            user_sources=["https://example.com/1", "https://example.com/2"],
            auto_complete=False,
            target_count=2,
            provide_suggestions=False
        )
        
        result = generator.generate_hybrid_sources(request)
        
        assert result['character_name'] == "Einstein"
        assert result['user_source_count'] == 2
        assert result['auto_generated_count'] == 0
        assert len(result['sources']) == 2
        assert result['configuration']['auto_complete'] is False
        
        # Auto generator should not have been called
        mock_auto_gen.generate_sources_for_character.assert_not_called()
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_generate_hybrid_sources_with_autocomplete(
        self, mock_validator_class, mock_auto_gen_class
    ):
        """Test hybrid generation with auto-complete"""
        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
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
        mock_auto_gen = MagicMock()
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
        
        generator = HybridSourceGenerator(
            automatic_generator=mock_auto_gen,
            source_validator=mock_validator
        )
        
        request = HybridSourceGenerationRequest(
            character_name="Einstein",
            user_sources=["https://example.com/1", "https://example.com/2"],
            auto_complete=True,
            target_count=50,
            provide_suggestions=False
        )
        
        result = generator.generate_hybrid_sources(request)
        
        assert result['character_name'] == "Einstein"
        assert result['user_source_count'] == 2
        assert result['auto_generated_count'] == 48
        assert len(result['sources']) == 50
        assert result['metadata']['target_met'] is True
        
        # Auto generator should have been called
        mock_auto_gen.generate_sources_for_character.assert_called_once()
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_generate_hybrid_sources_removes_duplicates(
        self, mock_validator_class, mock_auto_gen_class
    ):
        """Test that hybrid generation removes duplicate sources"""
        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = True
        mock_validation_result.issues = []
        mock_validator.validate_single_source.return_value = mock_validation_result
        mock_validator.validate_sources.return_value = {
            'total_sources': 5,
            'valid_sources': 5,
            'average_relevance': 0.8,
            'average_credibility': 85.0,
            'recommendations': []
        }
        
        # Mock auto generator with some duplicate URLs
        mock_auto_gen = MagicMock()
        auto_sources = [
            SourceItem(url="https://example.com/1", title="Dup", source_type=SourceType.URL),  # Duplicate
            SourceItem(url="https://auto.com/2", title="Unique 2", source_type=SourceType.URL),
            SourceItem(url="https://auto.com/3", title="Unique 3", source_type=SourceType.URL),
            SourceItem(url="https://auto.com/4", title="Unique 4", source_type=SourceType.URL),
        ]
        mock_auto_gen.generate_sources_for_character.return_value = {
            'sources': auto_sources,
            'character_analysis': None,
            'validation_summary': {}
        }
        
        generator = HybridSourceGenerator(
            automatic_generator=mock_auto_gen,
            source_validator=mock_validator
        )
        
        request = HybridSourceGenerationRequest(
            character_name="Test",
            user_sources=["https://example.com/1"],  # Will be duplicate
            auto_complete=True,
            target_count=5,
            provide_suggestions=False
        )
        
        result = generator.generate_hybrid_sources(request)
        
        # Should have removed the duplicate
        urls = [s.url for s in result['sources']]
        assert urls.count("https://example.com/1") == 1  # Only user's copy
        assert "https://auto.com/2" in urls
        assert "https://auto.com/3" in urls


class TestHybridSourceGenerationResponse:
    """Test HybridSourceGenerationResponse model"""
    
    def test_response_creation(self):
        """Test creating a response"""
        sources = [
            SourceItem(url="https://example.com/1", title="Source 1", source_type=SourceType.URL),
            SourceItem(url="https://example.com/2", title="Source 2", source_type=SourceType.URL)
        ]
        
        response = HybridSourceGenerationResponse(
            character_name="Einstein",
            sources=sources,
            user_source_count=1,
            auto_generated_count=1,
            suggestions=[],
            validation_summary={'total_sources': 2},
            configuration={'auto_complete': True},
            metadata={'target_met': True}
        )
        
        assert response.character_name == "Einstein"
        assert len(response.sources) == 2
        assert response.user_source_count == 1
        assert response.auto_generated_count == 1
        assert response.metadata['target_met'] is True


class TestAcceptanceCriteria:
    """Test acceptance criteria from the issue"""
    
    @patch('src.services.hybrid_generator.AutomaticSourceGenerator')
    @patch('src.services.hybrid_generator.SourceValidationService')
    def test_acceptance_criteria_hybrid_mode(
        self, mock_validator_class, mock_auto_gen_class
    ):
        """
        Test acceptance criteria:
        User can combine automatic + manual sources
        """
        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
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
        mock_auto_gen = MagicMock()
        auto_sources = [
            SourceItem(
                url=f"https://auto.com/{i}",
                title=f"Auto Source {i}",
                source_type=SourceType.URL
            )
            for i in range(49)
        ]
        mock_auto_gen.generate_sources_for_character.return_value = {
            'sources': auto_sources,
            'character_analysis': None,
            'validation_summary': {}
        }
        
        generator = HybridSourceGenerator(
            automatic_generator=mock_auto_gen,
            source_validator=mock_validator
        )
        
        # Simulate the acceptance criteria request
        request = HybridSourceGenerationRequest(
            character_name="Einstein",
            user_sources=["https://example.com/manual-source"],
            auto_complete=True,
            target_count=50
        )
        
        result = generator.generate_hybrid_sources(request)
        
        # Build response as the endpoint would
        sources = result['sources']
        
        # ACCEPTANCE CRITERIA CHECKS:
        # 1. User's manual source should be in the result
        assert "https://example.com/manual-source" in [s.url for s in sources]
        
        # 2. Total count should be 50 (target_count)
        assert len(sources) == 50
        
        # 3. Should have both user and auto-generated sources
        assert result['user_source_count'] >= 1
        assert result['auto_generated_count'] >= 1
        
        # 4. Target should be met
        assert result['metadata']['target_met'] is True
        
        print("✅ All acceptance criteria met!")
