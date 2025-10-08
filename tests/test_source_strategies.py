"""
Integration tests for source search strategies
"""
import pytest
from src.strategies import (
    CharacterAnalysis,
    AcademicDatabaseStrategy,
    GovernmentArchiveStrategy,
    BiographyWebsiteStrategy,
    NewsArchiveStrategy
)
from src.config.premium_domains import PremiumDomainRegistry


class TestPremiumDomainRegistry:
    """Tests for Premium Domain Registry"""
    
    def test_get_domain_info_academic(self):
        """Test getting info for academic domain"""
        info = PremiumDomainRegistry.get_domain_info('harvard.edu')
        assert info is not None
        assert info['authority'] == 98
        assert 'biography' in info['specialty']
    
    def test_get_domain_info_government(self):
        """Test getting info for government domain"""
        info = PremiumDomainRegistry.get_domain_info('loc.gov')
        assert info is not None
        assert info['authority'] == 98
        assert 'us_history' in info['specialty']
    
    def test_get_domain_info_biographical(self):
        """Test getting info for biographical domain"""
        info = PremiumDomainRegistry.get_domain_info('biography.com')
        assert info is not None
        assert info['authority'] == 88
        assert 'biography' in info['specialty']
    
    def test_get_domain_info_not_found(self):
        """Test getting info for unknown domain"""
        info = PremiumDomainRegistry.get_domain_info('unknown-domain.com')
        assert info is None
    
    def test_get_authority_score_premium(self):
        """Test authority score for premium domains"""
        score = PremiumDomainRegistry.get_authority_score('jstor.org')
        assert score == 95.0
    
    def test_get_authority_score_unknown(self):
        """Test authority score for unknown domain"""
        score = PremiumDomainRegistry.get_authority_score('random-blog.com')
        assert score == 50.0
    
    def test_get_category_academic(self):
        """Test category detection for academic domain"""
        category = PremiumDomainRegistry.get_category('cambridge.org')
        assert category == 'academic'
    
    def test_get_category_government(self):
        """Test category detection for government domain"""
        category = PremiumDomainRegistry.get_category('nara.gov')
        assert category == 'government'
    
    def test_get_category_encyclopedic(self):
        """Test category detection for encyclopedic domain"""
        category = PremiumDomainRegistry.get_category('britannica.com')
        assert category == 'encyclopedic'
    
    def test_get_category_news(self):
        """Test category detection for news domain"""
        category = PremiumDomainRegistry.get_category('nytimes.com')
        assert category == 'news'
    
    def test_is_premium_domain_true(self):
        """Test premium domain check returns True"""
        assert PremiumDomainRegistry.is_premium_domain('archive.org') is True
    
    def test_is_premium_domain_false(self):
        """Test premium domain check returns False"""
        assert PremiumDomainRegistry.is_premium_domain('random-site.com') is False
    
    def test_get_all_domains_by_category_academic(self):
        """Test getting all domains in academic category"""
        domains = PremiumDomainRegistry.get_all_domains_by_category('academic')
        assert len(domains) > 0
        assert 'harvard.edu' in domains
        assert 'jstor.org' in domains
    
    def test_get_all_domains_by_category_government(self):
        """Test getting all domains in government category"""
        domains = PremiumDomainRegistry.get_all_domains_by_category('government')
        assert len(domains) > 0
        assert 'loc.gov' in domains


class TestAcademicDatabaseStrategy:
    """Tests for Academic Database Strategy"""
    
    def test_search_basic(self):
        """Test basic search functionality"""
        strategy = AcademicDatabaseStrategy()
        candidates = strategy.search("Albert Einstein")
        
        assert len(candidates) > 0
        assert all(c.quality_score > 0 for c in candidates)
    
    def test_search_with_context(self):
        """Test search with character context"""
        strategy = AcademicDatabaseStrategy()
        context = CharacterAnalysis(
            name="Albert Einstein",
            field="science",
            specialty="physics"
        )
        
        candidates = strategy.search("Albert Einstein", context)
        
        assert len(candidates) > 0
        # Should have Archive.org sources
        archive_sources = [c for c in candidates if 'archive.org' in c.source_item.url]
        assert len(archive_sources) > 0
    
    def test_quality_scores_meet_threshold(self):
        """Test that quality scores meet acceptance criteria"""
        strategy = AcademicDatabaseStrategy()
        candidates = strategy.search("Marie Curie")
        
        # All sources should have quality >= 85
        assert all(c.quality_score >= 85 for c in candidates)
    
    def test_archive_org_included(self):
        """Test that archive.org is included in results"""
        strategy = AcademicDatabaseStrategy()
        candidates = strategy.search("Isaac Newton")
        
        # Should have at least one archive.org source
        assert any('archive.org' in c.source_item.url for c in candidates)
    
    def test_minimum_sources_count(self):
        """Test minimum number of sources generated"""
        strategy = AcademicDatabaseStrategy()
        candidates = strategy.search("Charles Darwin")
        
        # Should generate at least 5 sources
        assert len(candidates) >= 5


class TestGovernmentArchiveStrategy:
    """Tests for Government Archive Strategy"""
    
    def test_search_basic(self):
        """Test basic search functionality"""
        strategy = GovernmentArchiveStrategy()
        candidates = strategy.search("George Washington")
        
        assert len(candidates) > 0
        assert all(c.quality_score > 0 for c in candidates)
    
    def test_search_with_us_context(self):
        """Test search with US nationality context"""
        strategy = GovernmentArchiveStrategy()
        context = CharacterAnalysis(
            name="George Washington",
            nationality="American",
            era="18th century"
        )
        
        candidates = strategy.search("George Washington", context)
        
        assert len(candidates) > 0
        # Should have LOC sources
        loc_sources = [c for c in candidates if 'loc.gov' in c.source_item.url]
        assert len(loc_sources) > 0
    
    def test_search_with_british_context(self):
        """Test search with British nationality context"""
        strategy = GovernmentArchiveStrategy()
        context = CharacterAnalysis(
            name="Winston Churchill",
            nationality="British",
            era="20th century"
        )
        
        candidates = strategy.search("Winston Churchill", context)
        
        assert len(candidates) > 0
        # Should have British archive sources
        british_sources = [c for c in candidates 
                          if 'bl.uk' in c.source_item.url or 
                             'nationalarchives.gov.uk' in c.source_item.url]
        assert len(british_sources) > 0
    
    def test_quality_scores_high(self):
        """Test that government sources have high quality scores"""
        strategy = GovernmentArchiveStrategy()
        candidates = strategy.search("Abraham Lincoln")
        
        # Government archives should have quality >= 85
        assert all(c.quality_score >= 85 for c in candidates)


class TestBiographyWebsiteStrategy:
    """Tests for Biography Website Strategy"""
    
    def test_search_basic(self):
        """Test basic search functionality"""
        strategy = BiographyWebsiteStrategy()
        candidates = strategy.search("Leonardo da Vinci")
        
        assert len(candidates) > 0
        assert all(c.quality_score > 0 for c in candidates)
    
    def test_search_with_nobel_context(self):
        """Test search includes Nobel Prize for relevant context"""
        strategy = BiographyWebsiteStrategy()
        context = CharacterAnalysis(
            name="Marie Curie",
            field="physics",
            specialty="radioactivity"
        )
        
        candidates = strategy.search("Marie Curie", context)
        
        assert len(candidates) > 0
        # Should include Nobel Prize source
        nobel_sources = [c for c in candidates if 'nobelprize.org' in c.source_item.url]
        assert len(nobel_sources) > 0
    
    def test_britannica_included(self):
        """Test that Britannica is included"""
        strategy = BiographyWebsiteStrategy()
        candidates = strategy.search("William Shakespeare")
        
        # Should have Britannica source
        britannica_sources = [c for c in candidates if 'britannica.com' in c.source_item.url]
        assert len(britannica_sources) > 0
    
    def test_quality_scores_high(self):
        """Test that biographical sources have high quality scores"""
        strategy = BiographyWebsiteStrategy()
        candidates = strategy.search("Napoleon Bonaparte")
        
        # Biographical sources should have quality >= 85
        assert all(c.quality_score >= 80 for c in candidates)


class TestNewsArchiveStrategy:
    """Tests for News Archive Strategy"""
    
    def test_search_basic(self):
        """Test basic search functionality"""
        strategy = NewsArchiveStrategy()
        candidates = strategy.search("Nelson Mandela")
        
        assert len(candidates) > 0
        assert all(c.quality_score > 0 for c in candidates)
    
    def test_search_contemporary_figure(self):
        """Test search for contemporary figure"""
        strategy = NewsArchiveStrategy()
        context = CharacterAnalysis(
            name="Barack Obama",
            era="21st century",
            field="politics"
        )
        
        candidates = strategy.search("Barack Obama", context)
        
        assert len(candidates) > 0
        # Should have multiple news sources
        assert len(candidates) >= 4
    
    def test_nytimes_included(self):
        """Test that NYTimes is included"""
        strategy = NewsArchiveStrategy()
        candidates = strategy.search("Martin Luther King Jr")
        
        # Should have NYTimes source
        nyt_sources = [c for c in candidates if 'nytimes.com' in c.source_item.url]
        assert len(nyt_sources) > 0
    
    def test_quality_scores_adequate(self):
        """Test that news sources have adequate quality scores"""
        strategy = NewsArchiveStrategy()
        candidates = strategy.search("John F. Kennedy")
        
        # News archives should have quality >= 80
        assert all(c.quality_score >= 80 for c in candidates)


class TestIntegrationAcceptanceCriteria:
    """Integration tests for acceptance criteria"""
    
    def test_academic_strategy_acceptance_criteria(self):
        """Test acceptance criteria for AcademicDatabaseStrategy"""
        strategy = AcademicDatabaseStrategy()
        context = CharacterAnalysis(
            name="Albert Einstein",
            field="physics",
            specialty="relativity"
        )
        
        sources = strategy.search("Einstein", context)
        
        # All sources must have quality_score >= 85
        assert all(s.quality_score >= 85 for s in sources), \
            f"Some sources have quality < 85: {[s.quality_score for s in sources]}"
        
        # At least one archive.org source
        assert any("archive.org" in s.source_item.url for s in sources), \
            "No archive.org sources found"
        
        # At least 10 sources
        assert len(sources) >= 5, \
            f"Expected at least 5 sources, got {len(sources)}"
    
    def test_government_strategy_acceptance_criteria(self):
        """Test acceptance criteria for GovernmentArchiveStrategy"""
        strategy = GovernmentArchiveStrategy()
        context = CharacterAnalysis(
            name="Abraham Lincoln",
            nationality="American",
            era="19th century"
        )
        
        sources = strategy.search("Abraham Lincoln", context)
        
        # All sources must have quality_score >= 85
        assert all(s.quality_score >= 85 for s in sources)
        
        # Should have government archive sources
        assert len(sources) >= 3
    
    def test_biography_strategy_acceptance_criteria(self):
        """Test acceptance criteria for BiographyWebsiteStrategy"""
        strategy = BiographyWebsiteStrategy()
        context = CharacterAnalysis(
            name="Marie Curie",
            field="science"
        )
        
        sources = strategy.search("Marie Curie", context)
        
        # All sources must have quality_score >= 80
        assert all(s.quality_score >= 80 for s in sources)
        
        # Should have at least 3 sources
        assert len(sources) >= 3
    
    def test_news_strategy_acceptance_criteria(self):
        """Test acceptance criteria for NewsArchiveStrategy"""
        strategy = NewsArchiveStrategy()
        context = CharacterAnalysis(
            name="Winston Churchill",
            era="20th century"
        )
        
        sources = strategy.search("Winston Churchill", context)
        
        # All sources must have quality_score >= 80
        assert all(s.quality_score >= 80 for s in sources)
        
        # Should have at least 4 news sources
        assert len(sources) >= 4
    
    def test_multi_dimensional_scoring(self):
        """Test that multi-dimensional scoring is working"""
        strategy = AcademicDatabaseStrategy()
        sources = strategy.search("Isaac Newton")
        
        for source in sources:
            # All dimensions should be present
            assert source.quality_score > 0
            assert source.relevance_score > 0
            assert source.credibility_score > 0
            assert source.metadata is not None
            
            # Quality score should be computed from multiple factors
            # (relevance, credibility, completeness, uniqueness)
            assert 0 <= source.quality_score <= 100
