"""
Tests for Advanced Content Analyzer
Unit tests for AI-powered content quality analysis
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.services.content_analyzer import (
    ContentAnalyzer,
    AdvancedContentAnalyzer
)
from src.api.models.content_analysis import (
    BiographicalDepthAnalysis,
    FactualAccuracyAnalysis,
    BiasAnalysis,
    ContentQualityScore
)
from src.services.openrouter_client import OpenRouterClient, OpenRouterException


class TestContentAnalysisModels:
    """Tests for content analysis data models"""
    
    def test_biographical_depth_analysis_creation(self):
        """Test creating BiographicalDepthAnalysis model"""
        analysis = BiographicalDepthAnalysis(
            depth_score=0.8,
            early_life_coverage=75.0,
            professional_development=85.0,
            historical_context=70.0,
            personal_relationships=60.0,
            legacy_impact=90.0,
            specificity_score=80.0,
            concrete_details=75.0,
            justification="Good biographical coverage"
        )
        
        assert analysis.depth_score == 0.8
        assert analysis.early_life_coverage == 75.0
        assert analysis.justification == "Good biographical coverage"
    
    def test_factual_accuracy_analysis_creation(self):
        """Test creating FactualAccuracyAnalysis model"""
        analysis = FactualAccuracyAnalysis(
            accuracy_score=0.85,
            citation_count=5,
            verifiable_facts=20,
            questionable_claims=2,
            date_accuracy=90.0,
            consistency_score=85.0,
            justification="High factual accuracy"
        )
        
        assert analysis.accuracy_score == 0.85
        assert analysis.citation_count == 5
        assert analysis.verifiable_facts == 20
    
    def test_bias_analysis_creation(self):
        """Test creating BiasAnalysis model"""
        analysis = BiasAnalysis(
            neutrality_score=0.75,
            political_bias=20.0,
            emotional_language=15.0,
            perspective_balance=80.0,
            objectivity_score=85.0,
            detected_biases=["temporal"],
            justification="Generally neutral content"
        )
        
        assert analysis.neutrality_score == 0.75
        assert len(analysis.detected_biases) == 1
    
    def test_content_quality_score_creation(self):
        """Test creating ContentQualityScore model"""
        score = ContentQualityScore(
            biographical_depth=0.8,
            factual_accuracy=0.85,
            information_density=25.0,
            neutrality_score=0.75,
            source_citations=5,
            content_uniqueness=0.7
        )
        
        assert score.biographical_depth == 0.8
        assert score.factual_accuracy == 0.85
        assert score.information_density == 25.0
    
    def test_content_quality_score_overall_calculation(self):
        """Test overall score calculation"""
        score = ContentQualityScore(
            biographical_depth=0.8,
            factual_accuracy=0.9,
            information_density=30.0,  # Good density
            neutrality_score=0.7,
            source_citations=5,
            content_uniqueness=0.6
        )
        
        overall = score.calculate_overall_score()
        
        assert 0.0 <= overall <= 1.0
        assert overall > 0.5  # Should be relatively high given good scores


class TestContentAnalyzer:
    """Tests for ContentAnalyzer"""
    
    @pytest.fixture
    def mock_openrouter_client(self):
        """Create mock OpenRouter client"""
        client = Mock(spec=OpenRouterClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_openrouter_client):
        """Create ContentAnalyzer instance with mock client"""
        return ContentAnalyzer(openrouter_client=mock_openrouter_client)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.openrouter_client is not None
        assert 'content_depth' in analyzer.quality_models
        assert 'factual_accuracy' in analyzer.quality_models
        assert 'biographical_relevance' in analyzer.quality_models
    
    def test_analyzer_alias(self):
        """Test that AdvancedContentAnalyzer is an alias"""
        assert AdvancedContentAnalyzer == ContentAnalyzer
    
    @patch('requests.get')
    def test_fetch_and_clean_content(self, mock_get, analyzer):
        """Test content fetching and cleaning"""
        # Mock HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <head><title>Test</title></head>
            <body>
                <script>alert('test');</script>
                <nav>Navigation</nav>
                <main>
                    <h1>Albert Einstein</h1>
                    <p>Born in 1879 in Germany. Famous physicist.</p>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        content = analyzer._fetch_and_clean_content(
            "https://example.com/einstein",
            max_length=5000
        )
        
        assert len(content) > 0
        assert 'Albert Einstein' in content
        assert 'Born in 1879' in content
        assert 'Navigation' not in content  # Should be removed
        assert 'Footer content' not in content  # Should be removed
        assert "alert('test')" not in content  # Scripts should be removed
    
    @patch('requests.get')
    def test_fetch_and_clean_content_truncation(self, mock_get, analyzer):
        """Test content truncation at max length"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>" + b"A" * 10000 + b"</body></html>"
        mock_get.return_value = mock_response
        
        content = analyzer._fetch_and_clean_content(
            "https://example.com/test",
            max_length=1000
        )
        
        assert len(content) <= 1000
    
    @patch('requests.get')
    def test_fetch_and_clean_content_error_handling(self, mock_get, analyzer):
        """Test error handling when fetching content"""
        mock_get.side_effect = Exception("Network error")
        
        content = analyzer._fetch_and_clean_content(
            "https://example.com/error",
            max_length=5000
        )
        
        assert content == ""
    
    def test_analyze_biographical_depth_success(self, analyzer, mock_openrouter_client):
        """Test biographical depth analysis with successful AI response"""
        # Mock AI response
        ai_response = json.dumps({
            "early_life_coverage": 80,
            "professional_development": 85,
            "historical_context": 75,
            "personal_relationships": 70,
            "legacy_impact": 90,
            "specificity_score": 85,
            "concrete_details": 80,
            "justification": "Excellent biographical coverage with specific details"
        })
        
        mock_openrouter_client.generate_text.return_value = ai_response
        
        content = "Albert Einstein was born on March 14, 1879, in Ulm, Germany..."
        result = analyzer._analyze_biographical_depth(content, "Einstein")
        
        assert isinstance(result, BiographicalDepthAnalysis)
        assert result.early_life_coverage == 80
        assert result.professional_development == 85
        assert 0.0 <= result.depth_score <= 1.0
        mock_openrouter_client.generate_text.assert_called_once()
    
    def test_analyze_biographical_depth_with_markdown_json(self, analyzer, mock_openrouter_client):
        """Test parsing JSON from markdown-formatted AI response"""
        # AI might return JSON wrapped in markdown
        ai_response = """Here's the analysis:
        
```json
{
    "early_life_coverage": 75,
    "professional_development": 80,
    "historical_context": 70,
    "personal_relationships": 65,
    "legacy_impact": 85,
    "specificity_score": 80,
    "concrete_details": 75,
    "justification": "Good coverage"
}
```
        """
        
        mock_openrouter_client.generate_text.return_value = ai_response
        
        result = analyzer._analyze_biographical_depth("Test content", "Einstein")
        
        assert isinstance(result, BiographicalDepthAnalysis)
        assert result.early_life_coverage == 75
    
    def test_analyze_biographical_depth_error_handling(self, analyzer, mock_openrouter_client):
        """Test error handling in biographical depth analysis"""
        mock_openrouter_client.generate_text.side_effect = OpenRouterException("API error")
        
        result = analyzer._analyze_biographical_depth("Test content", "Einstein")
        
        assert isinstance(result, BiographicalDepthAnalysis)
        assert result.depth_score == 0.5  # Default fallback
        assert "error" in result.justification.lower()
    
    def test_verify_factual_accuracy_success(self, analyzer, mock_openrouter_client):
        """Test factual accuracy verification"""
        ai_response = json.dumps({
            "citation_count": 5,
            "verifiable_facts": 20,
            "questionable_claims": 2,
            "date_accuracy": 90,
            "consistency_score": 85,
            "justification": "High factual accuracy with good citations"
        })
        
        mock_openrouter_client.generate_text.return_value = ai_response
        
        result = analyzer._verify_factual_accuracy("Test content", "Einstein")
        
        assert isinstance(result, FactualAccuracyAnalysis)
        assert result.citation_count == 5
        assert result.verifiable_facts == 20
        assert result.questionable_claims == 2
        assert 0.0 <= result.accuracy_score <= 1.0
    
    def test_verify_factual_accuracy_error_handling(self, analyzer, mock_openrouter_client):
        """Test error handling in factual accuracy verification"""
        mock_openrouter_client.generate_text.side_effect = OpenRouterException("API error")
        
        result = analyzer._verify_factual_accuracy("Test content", "Einstein")
        
        assert isinstance(result, FactualAccuracyAnalysis)
        assert result.accuracy_score == 0.6  # Default fallback
    
    def test_analyze_bias_and_neutrality_success(self, analyzer, mock_openrouter_client):
        """Test bias and neutrality analysis"""
        ai_response = json.dumps({
            "political_bias": 15,
            "emotional_language": 20,
            "perspective_balance": 80,
            "objectivity_score": 85,
            "detected_biases": ["temporal"],
            "justification": "Generally neutral with minor temporal bias"
        })
        
        mock_openrouter_client.generate_text.return_value = ai_response
        
        result = analyzer._analyze_bias_and_neutrality("Test content")
        
        assert isinstance(result, BiasAnalysis)
        assert result.political_bias == 15
        assert result.emotional_language == 20
        assert result.perspective_balance == 80
        assert result.objectivity_score == 85
        assert "temporal" in result.detected_biases
        assert 0.0 <= result.neutrality_score <= 1.0
    
    def test_analyze_bias_and_neutrality_error_handling(self, analyzer, mock_openrouter_client):
        """Test error handling in bias analysis"""
        mock_openrouter_client.generate_text.side_effect = OpenRouterException("API error")
        
        result = analyzer._analyze_bias_and_neutrality("Test content")
        
        assert isinstance(result, BiasAnalysis)
        assert result.neutrality_score == 0.7  # Default fallback
    
    def test_calculate_information_density(self, analyzer):
        """Test information density calculation"""
        # Content with good fact density
        content = """
        Albert Einstein was born on March 14, 1879, in Ulm, Germany.
        He studied at ETH Zurich and graduated in 1900.
        In 1905, he published four groundbreaking papers.
        He received the Nobel Prize in Physics in 1921.
        Einstein died on April 18, 1955, in Princeton, New Jersey.
        """
        
        density = analyzer._calculate_information_density(content, "Einstein")
        
        assert isinstance(density, float)
        assert density > 0
        # Should have relatively low density (many facts per word)
        assert density < 50
    
    def test_calculate_uniqueness_score(self, analyzer):
        """Test content uniqueness score calculation"""
        # Content with uniqueness indicators
        content = """
        "Einstein once said, 'Imagination is more important than knowledge.'"
        Born on 14 March 1879, he showed early genius.
        Furthermore, his work on relativity [1] changed physics.
        Subsequently, he received numerous awards (1921).
        """
        
        uniqueness = analyzer._calculate_uniqueness_score(content, "Einstein")
        
        assert isinstance(uniqueness, float)
        assert 0.0 <= uniqueness <= 1.0
        # Should have relatively high uniqueness due to quotes, dates, citations
        assert uniqueness > 0.5
    
    @patch('requests.get')
    def test_analyze_source_content_quality_full_integration(
        self,
        mock_get,
        analyzer,
        mock_openrouter_client
    ):
        """Test full content quality analysis integration"""
        # Mock HTML response with sufficient content
        html_content = """
        <html><body>
            <h1>Albert Einstein</h1>
            <p>Born March 14, 1879 in Ulm, Germany. Albert Einstein was a German-born 
            theoretical physicist who is widely held to be one of the greatest and most 
            influential scientists of all time. Best known for developing the theory of 
            relativity, he also made important contributions to quantum mechanics.</p>
            <p>Einstein's work is also known for its influence on the philosophy of science. 
            He received the 1921 Nobel Prize in Physics for his services to theoretical physics, 
            and especially for his discovery of the law of the photoelectric effect.</p>
            <p>During his career, Einstein published more than 300 scientific papers and 
            150 non-scientific works. His intellectual achievements and originality have 
            made the word "Einstein" synonymous with "genius".</p>
        </body></html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Mock AI responses for different analysis types
        depth_response = json.dumps({
            "early_life_coverage": 80,
            "professional_development": 85,
            "historical_context": 75,
            "personal_relationships": 70,
            "legacy_impact": 90,
            "specificity_score": 85,
            "concrete_details": 80,
            "justification": "Good coverage"
        })
        
        accuracy_response = json.dumps({
            "citation_count": 3,
            "verifiable_facts": 15,
            "questionable_claims": 1,
            "date_accuracy": 95,
            "consistency_score": 90,
            "justification": "High accuracy"
        })
        
        bias_response = json.dumps({
            "political_bias": 10,
            "emotional_language": 15,
            "perspective_balance": 85,
            "objectivity_score": 90,
            "detected_biases": [],
            "justification": "Neutral content"
        })
        
        # Mock generate_text to return different responses
        mock_openrouter_client.generate_text.side_effect = [
            depth_response,
            accuracy_response,
            bias_response
        ]
        
        # Analyze content
        result = analyzer.analyze_source_content_quality(
            "https://example.com/einstein",
            "Einstein"
        )
        
        assert isinstance(result, ContentQualityScore)
        assert 0.0 <= result.biographical_depth <= 1.0
        assert 0.0 <= result.factual_accuracy <= 1.0
        assert result.information_density > 0
        assert 0.0 <= result.neutrality_score <= 1.0
        assert 0.0 <= result.content_uniqueness <= 1.0
        assert 0.0 <= result.overall_score <= 1.0
        
        # Verify AI was called for each analysis type
        assert mock_openrouter_client.generate_text.call_count == 3
        
        # Verify metadata is populated
        assert result.metadata is not None
        assert 'content_length' in result.metadata
        assert 'analysis_timestamp' in result.metadata
    
    @patch('requests.get')
    def test_analyze_source_content_quality_with_empty_content(
        self,
        mock_get,
        analyzer,
        mock_openrouter_client
    ):
        """Test handling of empty or insufficient content"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body></body></html>"
        mock_get.return_value = mock_response
        
        result = analyzer.analyze_source_content_quality(
            "https://example.com/empty",
            "Einstein"
        )
        
        # Should return default scores
        assert isinstance(result, ContentQualityScore)
        assert result.overall_score == 0.3  # Default score
    
    def test_acceptance_criteria(self, analyzer, mock_openrouter_client):
        """Test acceptance criteria from issue"""
        # Mock successful AI responses
        depth_response = json.dumps({
            "early_life_coverage": 85,
            "professional_development": 90,
            "historical_context": 80,
            "personal_relationships": 75,
            "legacy_impact": 95,
            "specificity_score": 85,
            "concrete_details": 90,
            "justification": "Excellent coverage"
        })
        
        accuracy_response = json.dumps({
            "citation_count": 8,
            "verifiable_facts": 30,
            "questionable_claims": 2,
            "date_accuracy": 95,
            "consistency_score": 90,
            "justification": "High accuracy"
        })
        
        bias_response = json.dumps({
            "political_bias": 10,
            "emotional_language": 15,
            "perspective_balance": 85,
            "objectivity_score": 90,
            "detected_biases": [],
            "justification": "Neutral"
        })
        
        mock_openrouter_client.generate_text.side_effect = [
            depth_response,
            accuracy_response,
            bias_response
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            # Provide sufficient content for analysis
            html_content = """<html><body>
                <h1>Albert Einstein Biography</h1>
                <p>Albert Einstein was born on March 14, 1879, in Ulm, Kingdom of Wuerttemberg, 
                in the German Empire. He was a German-born theoretical physicist who is widely 
                held to be one of the greatest and most influential scientists of all time.</p>
                <p>Best known for developing the theory of relativity, Einstein also made 
                important contributions to quantum mechanics. His mass-energy equivalence 
                formula E = mc2, which arises from relativity theory, has been called 
                "the world's most famous equation".</p>
                <p>He received the 1921 Nobel Prize in Physics for his services to theoretical 
                physics, and especially for his discovery of the law of the photoelectric effect, 
                a pivotal step in the development of quantum theory. His work is also known 
                for its influence on the philosophy of science.</p>
                <p>Einstein published more than 300 scientific papers and 150 non-scientific 
                works during his career. He died on April 18, 1955, in Princeton, New Jersey.</p>
            </body></html>"""
            mock_response.content = html_content.encode('utf-8')
            mock_get.return_value = mock_response
            
            score = analyzer.analyze_source_content_quality(
                "https://example.com/einstein",
                "Einstein"
            )
            
            # Acceptance criteria from issue
            assert score.biographical_depth >= 0.7, f"Expected >= 0.7, got {score.biographical_depth}"
            assert score.factual_accuracy >= 0.8, f"Expected >= 0.8, got {score.factual_accuracy}"
            assert score.neutrality_score >= 0.6, f"Expected >= 0.6, got {score.neutrality_score}"
            assert score.information_density > 0, f"Expected > 0, got {score.information_density}"


class TestIntegration:
    """Integration tests (require actual OpenRouter API)"""
    
    @pytest.mark.skip(reason="Requires actual OpenRouter API key")
    def test_real_content_analysis(self):
        """Test with real content (skip in CI)"""
        analyzer = ContentAnalyzer()
        
        score = analyzer.analyze_source_content_quality(
            "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
            "Einstein"
        )
        
        assert score.biographical_depth > 0
        assert score.factual_accuracy > 0
        assert score.overall_score > 0
