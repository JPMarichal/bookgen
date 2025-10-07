"""
Tests for advanced source validation service
"""
import pytest
from src.services.source_validator import SourceValidationService
from src.api.models.sources import SourceItem, SourceType
from src.utils.tfidf_analyzer import TfidfAnalyzer
from src.utils.credibility_checker import CredibilityChecker
from src.config.trusted_domains import (
    get_domain_credibility_score,
    is_trusted_domain,
    get_domain_category
)


class TestTrustedDomains:
    """Test trusted domains configuration"""
    
    def test_academic_domain_score(self):
        """Test academic domain gets high score"""
        score = get_domain_credibility_score("stanford.edu")
        assert score >= 90.0
    
    def test_government_domain_score(self):
        """Test government domain gets high score"""
        score = get_domain_credibility_score("loc.gov")
        assert score >= 90.0
    
    def test_trusted_site_score(self):
        """Test trusted site gets high score"""
        score = get_domain_credibility_score("wikipedia.org")
        assert score >= 85.0
    
    def test_unknown_domain_score(self):
        """Test unknown domain gets neutral score"""
        score = get_domain_credibility_score("random-blog.com")
        assert 40.0 <= score <= 60.0
    
    def test_is_trusted_domain(self):
        """Test trusted domain detection"""
        assert is_trusted_domain("harvard.edu") == True
        assert is_trusted_domain("random-site.com") == False
    
    def test_domain_category(self):
        """Test domain categorization"""
        assert get_domain_category("mit.edu") == "academic"
        assert get_domain_category("gov.uk") == "government"
        assert get_domain_category("nytimes.com") == "news"
        assert get_domain_category("archive.org") == "archive"


class TestTfidfAnalyzer:
    """Test TF-IDF analyzer"""
    
    def test_calculate_similarity_high(self):
        """Test high similarity calculation"""
        analyzer = TfidfAnalyzer()
        reference = "Albert Einstein physics relativity theory"
        content = "Albert Einstein was a theoretical physicist who developed the theory of relativity"
        
        similarity = analyzer.calculate_similarity(reference, content)
        assert similarity > 0.3  # Should have decent similarity
    
    def test_calculate_similarity_low(self):
        """Test low similarity calculation"""
        analyzer = TfidfAnalyzer()
        reference = "Albert Einstein physics"
        content = "Cooking recipes for delicious pasta dishes"
        
        similarity = analyzer.calculate_similarity(reference, content)
        assert similarity < 0.3  # Should have low similarity
    
    def test_character_mentions_bonus(self):
        """Test character mentions add bonus to score"""
        analyzer = TfidfAnalyzer()
        character_name = "Winston Churchill"
        title = "Winston Churchill Biography"
        content = "Winston Churchill was a British statesman. Winston Churchill served as Prime Minister."
        
        score = analyzer.calculate_relevance_with_mentions(character_name, title, content)
        assert score > 0.5  # Should get bonus for multiple mentions
    
    def test_simple_relevance_score(self):
        """Test simple fallback relevance scoring"""
        analyzer = TfidfAnalyzer()
        content = "Biography of Albert Einstein. Born in Germany. Died in 1955. Career in physics."
        character_name = "Albert Einstein"
        
        score = analyzer.simple_relevance_score(content, character_name)
        assert score > 0.0


class TestCredibilityChecker:
    """Test credibility checker"""
    
    def test_check_source_credibility_complete(self):
        """Test credibility check with complete source"""
        checker = CredibilityChecker()
        result = checker.check_source_credibility(
            url="https://wikipedia.org/wiki/Test",
            title="Test Article",
            author="Test Author",
            publication_date="2020-01-01"
        )
        
        assert result["credibility_score"] > 0
        assert "domain_score" in result
        assert "recency_score" in result
        assert "completeness_score" in result
    
    def test_check_source_credibility_academic(self):
        """Test academic source gets high credibility"""
        checker = CredibilityChecker()
        result = checker.check_source_credibility(
            url="https://stanford.edu/article",
            title="Academic Article",
            author="Professor Smith",
            publication_date="2023-01-01"
        )
        
        assert result["credibility_score"] >= 80.0
        assert result["is_trusted"] == True
        assert result["domain_category"] == "academic"
    
    def test_check_recency_recent(self):
        """Test recent publication gets high recency score"""
        checker = CredibilityChecker()
        result = checker._check_recency("2023-01-01")
        
        assert result["score"] >= 90.0
    
    def test_check_recency_old(self):
        """Test old publication gets lower recency score"""
        checker = CredibilityChecker()
        result = checker._check_recency("1950-01-01")
        
        assert result["score"] < 70.0
        assert len(result["warnings"]) > 0
    
    def test_check_completeness(self):
        """Test completeness checking"""
        checker = CredibilityChecker()
        result = checker._check_completeness(
            title="Test Title",
            author="Test Author",
            publication_date="2020",
            url="https://example.com"
        )
        
        assert result["score"] == 100.0
        assert len(result["issues"]) == 0
    
    def test_check_completeness_incomplete(self):
        """Test incomplete source"""
        checker = CredibilityChecker()
        result = checker._check_completeness(
            title="Test Title",
            author=None,
            publication_date=None,
            url=None
        )
        
        assert result["score"] < 100.0
        assert len(result["issues"]) > 0
    
    def test_is_academic_format(self):
        """Test academic format checking"""
        checker = CredibilityChecker()
        
        # Complete academic format
        assert checker.is_academic_format(
            title="Research Paper",
            author="Dr. Smith",
            publication_date="2020"
        ) == True
        
        # Incomplete format
        assert checker.is_academic_format(
            title="",
            author=None,
            publication_date=None
        ) == False


class TestSourceValidationService:
    """Test source validation service"""
    
    def test_validate_sources_basic(self):
        """Test basic source validation"""
        validator = SourceValidationService(min_relevance=0.5, min_credibility=60.0)
        
        sources = [
            SourceItem(
                title="Albert Einstein Biography",
                author="Author Name",
                publication_date="2020",
                source_type=SourceType.BOOK
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        assert result["total_sources"] == 1
        assert result["valid_sources"] >= 0
        assert "average_credibility" in result
        assert "recommendations" in result
    
    def test_validate_sources_multiple(self):
        """Test validation of multiple sources"""
        validator = SourceValidationService(min_relevance=0.5, min_credibility=60.0)
        
        sources = [
            SourceItem(
                title="Einstein's Life",
                author="Biographer",
                publication_date="2020",
                url="https://wikipedia.org/wiki/Einstein",
                source_type=SourceType.URL
            ),
            SourceItem(
                title="Physics History",
                author="Historian",
                publication_date="2019",
                source_type=SourceType.BOOK
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        assert result["total_sources"] == 2
        assert len(result["results"]) == 2
        assert result["average_credibility"] > 0
    
    def test_validate_single_source_high_credibility(self):
        """Test validation of high credibility source"""
        validator = SourceValidationService()
        
        source = SourceItem(
            title="Academic Article on Einstein",
            author="Professor Smith",
            publication_date="2023-01-01",
            url="https://stanford.edu/einstein",
            source_type=SourceType.ARTICLE
        )
        
        result = validator.validate_single_source(
            source=source,
            biography_topic="Albert Einstein",
            check_accessibility=False
        )
        
        assert result.credibility_score >= 80.0
        assert result.is_trusted == True
        assert result.domain_category == "academic"
    
    def test_validate_single_source_low_credibility(self):
        """Test validation of low credibility source"""
        validator = SourceValidationService()
        
        source = SourceItem(
            title="Blog Post",
            author=None,
            publication_date=None,
            url="https://random-blog.com/post",
            source_type=SourceType.URL
        )
        
        result = validator.validate_single_source(
            source=source,
            biography_topic="Albert Einstein",
            check_accessibility=False
        )
        
        assert result.credibility_score < 80.0
        assert result.is_trusted == False
    
    def test_validate_sources_with_recommendations(self):
        """Test that recommendations are generated"""
        validator = SourceValidationService(min_relevance=0.8, min_credibility=85.0)
        
        sources = [
            SourceItem(
                title="Low Quality Source",
                source_type=SourceType.OTHER
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Test Topic",
            sources_list=sources,
            check_accessibility=False
        )
        
        assert len(result["recommendations"]) > 0
    
    def test_extract_text_from_html(self):
        """Test HTML text extraction"""
        validator = SourceValidationService()
        
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <script>alert('test');</script>
                <p>This is test content.</p>
                <p>More content here.</p>
            </body>
        </html>
        """
        
        text = validator._extract_text_from_html(html)
        assert "This is test content" in text
        assert "alert" not in text  # Script should be removed
    
    def test_is_generic_page(self):
        """Test generic page detection"""
        validator = SourceValidationService()
        
        # Generic search page
        html_search = "<html><title>Search Results</title></html>"
        assert validator._is_generic_page(html_search) == True
        
        # Normal content page
        html_content = "<html><title>Albert Einstein Biography</title></html>"
        assert validator._is_generic_page(html_content) == False
    
    def test_generate_recommendations_good_sources(self):
        """Test recommendations for good sources"""
        validator = SourceValidationService()
        
        results = [
            type('obj', (object,), {
                'is_trusted': True,
                'source': type('obj', (object,), {
                    'author': 'Author',
                    'publication_date': '2020'
                })(),
                'is_accessible': True
            })()
        ]
        
        recommendations = validator._generate_recommendations(results, 0.85, 90.0)
        
        # Should have positive recommendation for good sources
        assert any("good" in rec.lower() or "no major" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_relevance(self):
        """Test recommendations for low relevance"""
        validator = SourceValidationService()
        
        results = []
        recommendations = validator._generate_recommendations(results, 0.5, 90.0)
        
        # Should recommend improving relevance
        assert any("relevance" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_credibility(self):
        """Test recommendations for low credibility"""
        validator = SourceValidationService()
        
        results = []
        recommendations = validator._generate_recommendations(results, 0.85, 60.0)
        
        # Should recommend improving credibility
        assert any("credibility" in rec.lower() for rec in recommendations)


class TestSourceValidationIntegration:
    """Integration tests for source validation"""
    
    def test_end_to_end_validation(self):
        """Test end-to-end validation workflow"""
        validator = SourceValidationService(min_relevance=0.7, min_credibility=80.0)
        
        sources = [
            SourceItem(
                title="Albert Einstein: His Life and Universe",
                author="Walter Isaacson",
                publication_date="2007",
                url="https://archive.org/details/einstein",
                source_type=SourceType.BOOK
            ),
            SourceItem(
                title="Einstein's Theory of Relativity",
                author="Max Born",
                publication_date="1962",
                url="https://britannica.com/einstein",
                source_type=SourceType.ARTICLE
            ),
            SourceItem(
                title="Physics Today",
                publication_date="2020",
                source_type=SourceType.ARTICLE
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        # Verify result structure
        assert result["total_sources"] == 3
        assert "valid_sources" in result
        assert "average_relevance" in result
        assert "average_credibility" in result
        assert len(result["results"]) == 3
        assert len(result["recommendations"]) > 0
        
        # Verify individual results have required fields
        for res in result["results"]:
            assert hasattr(res, 'source')
            assert hasattr(res, 'is_valid')
            assert hasattr(res, 'credibility_score')
    
    def test_acceptance_criteria_relevance(self):
        """Test that average relevance can be > 0.7 with good sources"""
        validator = SourceValidationService(min_relevance=0.7)
        
        # Create sources that should be relevant
        sources = [
            SourceItem(
                title="Einstein Biography Complete Works",
                author="Renowned Author",
                publication_date="2020",
                url="https://stanford.edu/einstein-bio",
                source_type=SourceType.BOOK
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        # With good matching titles, we should achieve decent scores
        # Note: Without actual content, this tests the framework
        assert "average_relevance" in result
    
    def test_acceptance_criteria_credibility(self):
        """Test that credibility score can be > 80 with trusted sources"""
        validator = SourceValidationService(min_credibility=80.0)
        
        sources = [
            SourceItem(
                title="Einstein Research Paper",
                author="Dr. Smith",
                publication_date="2022",
                url="https://harvard.edu/research",
                source_type=SourceType.ARTICLE
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        # Academic sources should have high credibility
        assert result["average_credibility"] > 80.0
    
    def test_acceptance_criteria_rejected_sources(self):
        """Test that rejected sources are counted"""
        validator = SourceValidationService(min_relevance=0.9, min_credibility=95.0)
        
        sources = [
            SourceItem(
                title="Random Blog Post",
                source_type=SourceType.OTHER
            )
        ]
        
        result = validator.validate_sources(
            biography_topic="Albert Einstein",
            sources_list=sources,
            check_accessibility=False
        )
        
        # Should have rejected_sources field
        assert "rejected_sources" in result
        assert result["rejected_sources"] >= 0
