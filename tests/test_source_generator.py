"""
Tests for automatic source generator service
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json

from src.services.source_generator import AutomaticSourceGenerator
from src.api.models.sources import SourceItem, SourceType
from src.api.models.source_generation import (
    AutomaticSourceGenerationRequest,
    CharacterAnalysis
)
from src.strategies.wikipedia_strategy import WikipediaStrategy


class TestCharacterAnalysis:
    """Test CharacterAnalysis model"""
    
    def test_character_analysis_creation(self):
        """Test creating CharacterAnalysis object"""
        analysis = CharacterAnalysis(
            character_name="Albert Einstein",
            historical_period="20th century",
            nationality="German-American",
            professional_field="Physics",
            key_events=["Theory of Relativity", "Nobel Prize"],
            related_entities=["Niels Bohr", "Princeton"],
            search_terms=["Einstein biography", "relativity theory"]
        )
        
        assert analysis.character_name == "Albert Einstein"
        assert analysis.historical_period == "20th century"
        assert len(analysis.key_events) == 2
        assert len(analysis.search_terms) == 2
    
    def test_character_analysis_minimal(self):
        """Test CharacterAnalysis with minimal fields"""
        analysis = CharacterAnalysis(character_name="Test Person")
        
        assert analysis.character_name == "Test Person"
        assert analysis.key_events == []
        assert analysis.search_terms == []


class TestAutomaticSourceGenerationRequest:
    """Test AutomaticSourceGenerationRequest model"""
    
    def test_request_creation_defaults(self):
        """Test request with default values"""
        request = AutomaticSourceGenerationRequest(
            character_name="Albert Einstein"
        )
        
        assert request.character_name == "Albert Einstein"
        assert request.min_sources == 40
        assert request.max_sources == 60
        assert request.check_accessibility is True
        assert request.min_relevance == 0.7
        assert request.min_credibility == 80.0
    
    def test_request_creation_custom(self):
        """Test request with custom values"""
        request = AutomaticSourceGenerationRequest(
            character_name="Marie Curie",
            min_sources=30,
            max_sources=50,
            check_accessibility=False,
            min_relevance=0.6,
            min_credibility=70.0
        )
        
        assert request.character_name == "Marie Curie"
        assert request.min_sources == 30
        assert request.max_sources == 50
        assert request.check_accessibility is False
        assert request.min_relevance == 0.6
        assert request.min_credibility == 70.0


class TestWikipediaStrategy:
    """Test WikipediaStrategy"""
    
    def test_strategy_initialization(self):
        """Test WikipediaStrategy initializes correctly"""
        strategy = WikipediaStrategy()
        
        assert strategy.name == "WikipediaStrategy"
        assert strategy.api_base == "https://en.wikipedia.org/w/api.php"
    
    def test_strategy_name(self):
        """Test get_strategy_name returns correct name"""
        strategy = WikipediaStrategy()
        
        assert strategy.get_strategy_name() == "WikipediaStrategy"
    
    @patch('src.strategies.wikipedia_strategy.requests.Session')
    def test_find_main_article_success(self, mock_session_class):
        """Test finding main Wikipedia article"""
        # Mock the session and responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock search response
        search_response = Mock()
        search_response.json.return_value = {
            'query': {
                'search': [
                    {'title': 'Albert Einstein'}
                ]
            }
        }
        search_response.raise_for_status = Mock()
        
        # Mock page info response
        info_response = Mock()
        info_response.json.return_value = {
            'query': {
                'pages': {
                    '123': {
                        'title': 'Albert Einstein',
                        'pageid': 123
                    }
                }
            }
        }
        info_response.raise_for_status = Mock()
        
        # Configure session to return different responses
        mock_session.get.side_effect = [search_response, info_response]
        
        strategy = WikipediaStrategy()
        result = strategy._find_main_article("Albert Einstein")
        
        assert result is not None
        assert result.title == "Wikipedia: Albert Einstein"
        assert "wikipedia.org" in result.url
        assert result.source_type == SourceType.URL
    
    def test_extract_title_from_url(self):
        """Test extracting title from URL"""
        strategy = WikipediaStrategy()
        
        url = "https://archive.org/details/einstein-biography"
        title = strategy._extract_title_from_url(url)
        
        assert "archive.org" in title
        assert len(title) <= 200
    
    def test_is_quality_external_link(self):
        """Test quality external link detection"""
        strategy = WikipediaStrategy()
        
        assert strategy._is_quality_external_link("https://archive.org/details/test")
        assert strategy._is_quality_external_link("https://nobelprize.org/prizes")
        assert strategy._is_quality_external_link("https://harvard.edu/about")
        assert not strategy._is_quality_external_link("https://random-blog.com/post")


class TestAutomaticSourceGenerator:
    """Test AutomaticSourceGenerator service"""
    
    def test_generator_initialization(self):
        """Test generator initializes with strategies"""
        generator = AutomaticSourceGenerator()
        
        assert generator.openrouter_client is not None
        assert generator.source_validator is not None
        assert len(generator.search_strategies) >= 1
        assert any(isinstance(s, WikipediaStrategy) for s in generator.search_strategies)
    
    def test_create_fallback_analysis(self):
        """Test fallback analysis creation"""
        generator = AutomaticSourceGenerator()
        
        analysis = generator._create_fallback_analysis("Test Person")
        
        assert analysis.character_name == "Test Person"
        assert len(analysis.search_terms) > 0
        assert "Test Person biography" in analysis.search_terms
    
    @patch('src.services.source_generator.OpenRouterClient')
    def test_analyze_character_with_ai_success(self, mock_openrouter_class):
        """Test successful character analysis with AI"""
        # Mock OpenRouter client
        mock_client = Mock()
        mock_openrouter_class.return_value = mock_client
        
        # Mock AI response
        ai_response = json.dumps({
            "historical_period": "20th century, 1879-1955",
            "nationality": "German-American",
            "professional_field": "Theoretical Physics",
            "key_events": ["Theory of Relativity", "Nobel Prize 1921"],
            "related_entities": ["Niels Bohr", "Princeton University"],
            "search_terms": ["Einstein biography", "relativity theory"]
        })
        mock_client.generate_text.return_value = ai_response
        
        generator = AutomaticSourceGenerator(openrouter_client=mock_client)
        analysis = generator._analyze_character_with_ai("Albert Einstein")
        
        assert analysis.character_name == "Albert Einstein"
        assert analysis.historical_period == "20th century, 1879-1955"
        assert analysis.professional_field == "Theoretical Physics"
        assert len(analysis.key_events) == 2
        assert len(analysis.search_terms) == 2
    
    @patch('src.services.source_generator.OpenRouterClient')
    def test_analyze_character_with_ai_failure(self, mock_openrouter_class):
        """Test character analysis falls back on AI failure"""
        # Mock OpenRouter client that raises exception
        mock_client = Mock()
        mock_openrouter_class.return_value = mock_client
        mock_client.generate_text.side_effect = Exception("API Error")
        
        generator = AutomaticSourceGenerator(openrouter_client=mock_client)
        analysis = generator._analyze_character_with_ai("Albert Einstein")
        
        # Should return fallback analysis
        assert analysis.character_name == "Albert Einstein"
        assert len(analysis.search_terms) > 0
    
    def test_ensure_minimum_sources(self):
        """Test ensuring minimum source count"""
        generator = AutomaticSourceGenerator()
        
        sources = [
            SourceItem(title=f"Source {i}", url=f"http://example.com/{i}")
            for i in range(5)
        ]
        
        result = generator._ensure_minimum_sources(sources, min_sources=10)
        
        # Should return all sources even if below minimum
        assert len(result) == 5
    
    @patch('src.services.source_generator.OpenRouterClient')
    @patch('src.services.source_generator.SourceValidationService')
    def test_generate_sources_integration(self, mock_validator_class, mock_openrouter_class):
        """Test full source generation flow"""
        # Mock OpenRouter
        mock_client = Mock()
        mock_openrouter_class.return_value = mock_client
        ai_response = json.dumps({
            "historical_period": "20th century",
            "nationality": "German",
            "professional_field": "Physics",
            "key_events": ["Relativity"],
            "related_entities": ["Bohr"],
            "search_terms": ["Einstein biography", "physics"]
        })
        mock_client.generate_text.return_value = ai_response
        
        # Mock validator
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_sources.return_value = {
            'total_sources': 10,
            'valid_sources': 8,
            'invalid_sources': 2,
            'rejected_sources': 0,
            'average_relevance': 0.85,
            'average_credibility': 90.0,
            'results': [
                Mock(
                    is_valid=True,
                    relevance_score=0.85,
                    credibility_score=90.0,
                    source=SourceItem(title=f"Test Source {i}", url=f"http://test.com/{i}")
                )
                for i in range(8)
            ],
            'recommendations': []
        }
        
        generator = AutomaticSourceGenerator(
            openrouter_client=mock_client,
            source_validator=mock_validator
        )
        
        request = AutomaticSourceGenerationRequest(
            character_name="Albert Einstein",
            min_sources=10
        )
        
        # Mock the strategy search
        with patch.object(WikipediaStrategy, 'search') as mock_search:
            mock_search.return_value = [
                SourceItem(title=f"Test Source {i}", url=f"http://test.com/{i}")
                for i in range(10)
            ]
            
            result = generator.generate_sources_for_character(request)
        
        assert result['character_name'] == "Albert Einstein"
        assert 'sources' in result
        assert 'character_analysis' in result
        assert 'validation_summary' in result
        assert len(result['strategies_used']) >= 1


class TestSourceGeneratorEndpoint:
    """Test the API endpoint (integration test)"""
    
    @pytest.mark.api
    def test_endpoint_structure(self):
        """Test that endpoint models are properly structured"""
        request = AutomaticSourceGenerationRequest(
            character_name="Test Person"
        )
        
        assert request.character_name == "Test Person"
        assert request.min_sources >= 10
        assert request.max_sources <= 150
