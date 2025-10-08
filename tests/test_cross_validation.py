"""
Tests for Cross-Validation System
Tests for fact checking, source triangulation, and cross-validation
"""
import pytest
from unittest.mock import Mock, patch

from src.services.cross_validator import CrossValidationSystem
from src.utils.fact_checker import FactualConsistencyChecker
from src.utils.source_triangulator import SourceTriangulator
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType
from src.api.models.cross_validation import (
    ValidationResult,
    RedundancyAnalysis,
    AcademicStandards,
    KeyFact
)


class TestFactualConsistencyChecker:
    """Test FactualConsistencyChecker"""
    
    def test_initialization(self):
        """Test fact checker initialization"""
        checker = FactualConsistencyChecker()
        assert checker is not None
        assert checker.openrouter_client is not None
    
    def test_extract_key_facts_empty_content(self):
        """Test fact extraction with empty content"""
        checker = FactualConsistencyChecker()
        facts = checker.extract_key_facts("", "Einstein")
        assert facts == []
    
    def test_extract_key_facts_short_content(self):
        """Test fact extraction with short content"""
        checker = FactualConsistencyChecker()
        facts = checker.extract_key_facts("Short", "Einstein")
        assert facts == []
    
    @patch('src.services.openrouter_client.OpenRouterClient.generate_text')
    def test_extract_key_facts_with_ai(self, mock_generate):
        """Test fact extraction with AI response"""
        mock_generate.return_value = '''[
            {"fact": "Born in 1879", "confidence": 0.95, "category": "date"},
            {"fact": "Developed relativity", "confidence": 0.9, "category": "achievement"}
        ]'''
        
        checker = FactualConsistencyChecker()
        content = "Albert Einstein was born in 1879 and developed the theory of relativity"
        facts = checker.extract_key_facts(content, "Einstein")
        
        assert len(facts) == 2
        assert facts[0].fact == "Born in 1879"
        assert facts[0].confidence == 0.95
        assert facts[1].category == "achievement"
    
    def test_fallback_fact_extraction(self):
        """Test fallback fact extraction"""
        checker = FactualConsistencyChecker()
        content = "Einstein was born in Germany. Einstein studied physics. Einstein won Nobel Prize."
        facts = checker._fallback_fact_extraction(content, "Einstein")
        
        assert len(facts) > 0
        assert all(f.confidence == 0.5 for f in facts)
    
    def test_compare_facts_empty(self):
        """Test fact comparison with empty sets"""
        checker = FactualConsistencyChecker()
        score = checker.compare_facts([], [])
        assert score == 0.5  # Neutral score
    
    @patch('src.services.openrouter_client.OpenRouterClient.generate_text')
    def test_compare_facts_with_ai(self, mock_generate):
        """Test fact comparison with AI"""
        mock_generate.return_value = '''{
            "consistency_score": 0.9,
            "contradictions": 0,
            "agreements": 5,
            "explanation": "Facts are consistent"
        }'''
        
        checker = FactualConsistencyChecker()
        facts1 = [
            KeyFact(fact="Born 1879", source_index=0, confidence=0.9),
            KeyFact(fact="Physicist", source_index=0, confidence=0.9)
        ]
        facts2 = [
            KeyFact(fact="Born 1879", source_index=1, confidence=0.9),
            KeyFact(fact="Scientist", source_index=1, confidence=0.9)
        ]
        
        score = checker.compare_facts(facts1, facts2)
        assert score == 0.9
    
    def test_fallback_fact_comparison(self):
        """Test fallback fact comparison"""
        checker = FactualConsistencyChecker()
        facts1 = [
            KeyFact(fact="Einstein born 1879", source_index=0),
            KeyFact(fact="Developed relativity theory", source_index=0)
        ]
        facts2 = [
            KeyFact(fact="Einstein physicist", source_index=1),
            KeyFact(fact="Theory of relativity", source_index=1)
        ]
        
        score = checker._fallback_fact_comparison(facts1, facts2)
        assert 0.0 <= score <= 1.0


class TestSourceTriangulator:
    """Test SourceTriangulator"""
    
    def test_initialization(self):
        """Test triangulator initialization"""
        triangulator = SourceTriangulator()
        assert triangulator is not None
    
    def test_triangulate_facts_insufficient(self):
        """Test triangulation with insufficient fact sets"""
        triangulator = SourceTriangulator()
        result = triangulator.triangulate_facts([])
        
        assert result['verified_facts'] == []
        assert result['conflicting_facts'] == []
        assert result['confidence_score'] == 0.0
    
    def test_triangulate_facts_basic(self):
        """Test basic fact triangulation"""
        triangulator = SourceTriangulator()
        
        fact_sets = [
            [
                KeyFact(fact="Born in 1879", source_index=0, confidence=0.9),
                KeyFact(fact="German physicist", source_index=0, confidence=0.9)
            ],
            [
                KeyFact(fact="Born in 1879", source_index=1, confidence=0.95),
                KeyFact(fact="Nobel Prize winner", source_index=1, confidence=0.85)
            ],
            [
                KeyFact(fact="Born in 1879", source_index=2, confidence=0.9),
                KeyFact(fact="Theory of relativity", source_index=2, confidence=0.9)
            ]
        ]
        
        result = triangulator.triangulate_facts(fact_sets)
        
        assert len(result['verified_facts']) > 0
        assert result['confidence_score'] > 0
        assert 'total_facts' in result
    
    def test_normalize_fact(self):
        """Test fact normalization"""
        triangulator = SourceTriangulator()
        
        fact1 = "Born in 1879."
        fact2 = "BORN IN 1879"
        
        norm1 = triangulator._normalize_fact(fact1)
        norm2 = triangulator._normalize_fact(fact2)
        
        assert norm1 == norm2
    
    def test_calculate_source_overlap_single(self):
        """Test overlap calculation with single source"""
        triangulator = SourceTriangulator()
        
        source = SourceCandidate(
            source_item=SourceItem(
                title="Test",
                url="https://example.com/test",
                source_type=SourceType.URL
            )
        )
        
        result = triangulator.calculate_source_overlap([source])
        assert result['overlap_score'] == 0.0
        assert result['unique_sources'] == 1
    
    def test_calculate_source_overlap_multiple(self):
        """Test overlap calculation with multiple sources"""
        triangulator = SourceTriangulator()
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Test 1",
                    url="https://example.com/test1",
                    source_type=SourceType.URL
                )
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Test 2",
                    url="https://example.com/test2",
                    source_type=SourceType.URL
                )
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Test 3",
                    url="https://other.com/test",
                    source_type=SourceType.URL
                )
            )
        ]
        
        result = triangulator.calculate_source_overlap(sources)
        assert 'overlap_score' in result
        assert 'diversity_score' in result
        assert result['total_sources'] == 3
    
    def test_extract_domain(self):
        """Test domain extraction"""
        triangulator = SourceTriangulator()
        
        assert triangulator._extract_domain("https://www.example.com/path") == "example.com"
        assert triangulator._extract_domain("http://example.org/test") == "example.org"
        assert triangulator._extract_domain("https://sub.domain.com") == "sub.domain.com"
    
    def test_detect_source_diversity(self):
        """Test source diversity detection"""
        triangulator = SourceTriangulator()
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Book",
                    author="Author 1",
                    source_type=SourceType.BOOK
                )
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Article",
                    author="Author 2",
                    url="https://example.com",
                    source_type=SourceType.ARTICLE
                )
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Document",
                    author="Author 3",
                    url="https://other.org",
                    source_type=SourceType.DOCUMENT
                )
            )
        ]
        
        diversity = triangulator.detect_source_diversity(sources)
        assert 0.0 <= diversity <= 1.0
        assert diversity > 0.3  # Should have decent diversity


class TestCrossValidationSystem:
    """Test CrossValidationSystem"""
    
    def test_initialization(self):
        """Test system initialization"""
        system = CrossValidationSystem()
        assert system is not None
        assert system.fact_checker is not None
        assert system.source_triangulator is not None
    
    def test_validate_empty_sources(self):
        """Test validation with empty sources"""
        system = CrossValidationSystem()
        result = system.validate_source_set_quality([], "Einstein")
        
        assert isinstance(result, ValidationResult)
        assert result.consistency_score == 0.0
        assert result.overall_quality == 0.0
        assert len(result.recommendations) > 0
    
    def test_validate_single_source(self):
        """Test validation with single source"""
        system = CrossValidationSystem()
        
        source = SourceCandidate(
            source_item=SourceItem(
                title="Einstein Biography",
                author="Walter Isaacson",
                publication_date="2007",
                url="https://archive.org/einstein",
                source_type=SourceType.BOOK
            ),
            quality_score=85.0,
            credibility_score=90.0,
            relevance_score=0.9
        )
        
        result = system.validate_source_set_quality([source], "Einstein")
        
        assert isinstance(result, ValidationResult)
        assert 0.0 <= result.consistency_score <= 1.0
        assert 0.0 <= result.temporal_coverage <= 1.0
        assert 0.0 <= result.overall_quality <= 1.0
    
    def test_validate_multiple_sources(self):
        """Test validation with multiple sources"""
        system = CrossValidationSystem()
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein: His Life and Universe",
                    author="Walter Isaacson",
                    publication_date="2007",
                    url="https://stanford.edu/einstein",
                    source_type=SourceType.BOOK
                ),
                quality_score=90.0,
                credibility_score=95.0,
                relevance_score=0.95
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein Biography",
                    author="Alice Calaprice",
                    publication_date="2005",
                    url="https://archive.org/einstein-bio",
                    source_type=SourceType.BOOK
                ),
                quality_score=88.0,
                credibility_score=92.0,
                relevance_score=0.9
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Albert Einstein - Nobel Prize",
                    author="Nobel Foundation",
                    publication_date="1921",
                    url="https://nobelprize.org/einstein",
                    source_type=SourceType.ARTICLE
                ),
                quality_score=95.0,
                credibility_score=98.0,
                relevance_score=0.85
            )
        ]
        
        result = system.validate_source_set_quality(sources, "Einstein")
        
        assert isinstance(result, ValidationResult)
        assert result.consistency_score > 0.0
        assert result.diversity_score > 0.0
        assert result.overall_quality > 0.0
        assert len(result.recommendations) > 0
    
    def test_get_source_content(self):
        """Test content extraction from source"""
        system = CrossValidationSystem()
        
        source = SourceCandidate(
            source_item=SourceItem(
                title="Test Title",
                author="Test Author",
                source_type=SourceType.BOOK
            )
        )
        
        content = system._get_source_content(source)
        assert "Test Title" in content
        assert "Test Author" in content
    
    def test_analyze_temporal_coverage(self):
        """Test temporal coverage analysis"""
        system = CrossValidationSystem()
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein's Early Life and Education",
                    source_type=SourceType.ARTICLE
                ),
                metadata={'content': 'Born in 1879, childhood in Munich, early education'}
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein's Career and Achievements",
                    source_type=SourceType.ARTICLE
                ),
                metadata={'content': 'Professional work on relativity, career achievements'}
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Einstein's Later Years",
                    source_type=SourceType.ARTICLE
                ),
                metadata={'content': 'Later work, death in 1955, legacy and impact'}
            )
        ]
        
        coverage = system._analyze_temporal_coverage(sources, "Einstein")
        assert coverage > 0.5  # Should detect multiple periods
    
    def test_detect_information_redundancy(self):
        """Test redundancy detection"""
        system = CrossValidationSystem()
        
        # Same domain sources (high redundancy)
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Article 1",
                    url="https://example.com/article1",
                    source_type=SourceType.URL
                )
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Article 2",
                    url="https://example.com/article2",
                    source_type=SourceType.URL
                )
            )
        ]
        
        result = system._detect_information_redundancy(sources)
        
        assert isinstance(result, RedundancyAnalysis)
        assert 0.0 <= result.redundancy_percentage <= 1.0
    
    def test_verify_academic_standards(self):
        """Test academic standards verification"""
        system = CrossValidationSystem()
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title="Academic Paper",
                    url="https://stanford.edu/paper",
                    source_type=SourceType.ARTICLE
                ),
                credibility_score=95.0
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Journal Article",
                    url="https://jstor.org/article",
                    source_type=SourceType.ARTICLE
                ),
                credibility_score=92.0
            ),
            SourceCandidate(
                source_item=SourceItem(
                    title="Blog Post",
                    url="https://blog.com/post",
                    source_type=SourceType.URL
                ),
                credibility_score=60.0
            )
        ]
        
        result = system._verify_academic_standards(sources)
        
        assert isinstance(result, AcademicStandards)
        assert result.peer_reviewed_sources >= 2
        assert result.academic_credibility > 0
    
    def test_calculate_overall_quality(self):
        """Test overall quality calculation"""
        system = CrossValidationSystem()
        
        quality = system._calculate_overall_quality(
            consistency=0.9,
            temporal=0.8,
            diversity=0.7,
            redundancy=0.2,
            academic=0.85
        )
        
        assert 0.0 <= quality <= 1.0
        assert quality > 0.7  # Should be good with these scores
    
    def test_generate_recommendations_good_quality(self):
        """Test recommendations for good quality sources"""
        system = CrossValidationSystem()
        
        sources = [SourceCandidate(
            source_item=SourceItem(title=f"Source {i}", source_type=SourceType.BOOK)
        ) for i in range(15)]
        
        redundancy = RedundancyAnalysis(
            redundancy_percentage=0.2,
            unique_information_ratio=0.8,
            overlapping_facts=2,
            unique_facts=8
        )
        
        recommendations = system._generate_improvement_recommendations(
            sources=sources,
            character="Einstein",
            consistency=0.85,
            temporal=0.8,
            diversity=0.7,
            redundancy=redundancy
        )
        
        assert len(recommendations) > 0
        assert any("excellent" in r.lower() or "met" in r.lower() for r in recommendations)
    
    def test_generate_recommendations_low_quality(self):
        """Test recommendations for low quality sources"""
        system = CrossValidationSystem()
        
        sources = [SourceCandidate(
            source_item=SourceItem(title="Source", source_type=SourceType.OTHER)
        )]
        
        redundancy = RedundancyAnalysis(
            redundancy_percentage=0.5,
            unique_information_ratio=0.5,
            overlapping_facts=5,
            unique_facts=5
        )
        
        recommendations = system._generate_improvement_recommendations(
            sources=sources,
            character="Einstein",
            consistency=0.6,
            temporal=0.5,
            diversity=0.3,
            redundancy=redundancy
        )
        
        assert len(recommendations) > 1
        assert any("consistency" in r.lower() for r in recommendations)
        assert any("temporal" in r.lower() or "coverage" in r.lower() for r in recommendations)


class TestAcceptanceCriteria:
    """Test acceptance criteria from the issue"""
    
    @patch('src.services.openrouter_client.OpenRouterClient.generate_text')
    def test_acceptance_criteria(self, mock_generate):
        """Test all acceptance criteria"""
        # Mock AI responses to avoid API calls
        mock_generate.return_value = '''[
            {"fact": "Born in 1879", "confidence": 0.95, "category": "date"},
            {"fact": "Developed relativity", "confidence": 0.9, "category": "achievement"},
            {"fact": "Won Nobel Prize", "confidence": 0.9, "category": "achievement"}
        ]'''
        
        validator = CrossValidationSystem()
        
        # Create a good set of sources
        sources = []
        for i in range(12):
            source = SourceCandidate(
                source_item=SourceItem(
                    title=f"Einstein Biography Volume {i+1}",
                    author=f"Author {i+1}",
                    publication_date=f"20{10+i}",
                    url=f"https://university{i}.edu/einstein-{i}",
                    source_type=SourceType.BOOK if i % 2 == 0 else SourceType.ARTICLE
                ),
                quality_score=85.0 + i,
                credibility_score=88.0 + i,
                relevance_score=0.85 + (i * 0.01),
                metadata={
                    'content': f"Einstein was born in 1879. Career work on physics. "
                              f"Later years and legacy. Died in 1955. {' '.join(['detail'] * (i+1))}"
                }
            )
            sources.append(source)
        
        result = validator.validate_source_set_quality(sources, "Einstein")
        
        # Check acceptance criteria
        assert result.consistency_score >= 0.8, \
            f"consistency_score {result.consistency_score} should be >= 0.8"
        assert result.temporal_coverage >= 0.7, \
            f"temporal_coverage {result.temporal_coverage} should be >= 0.7"
        assert result.redundancy_level <= 0.3, \
            f"redundancy_level {result.redundancy_level} should be <= 0.3"
        assert len(result.recommendations) > 0, \
            "should have recommendations"
        
        # Additional checks
        assert isinstance(result, ValidationResult)
        assert 0.0 <= result.overall_quality <= 1.0
        assert 0.0 <= result.diversity_score <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
