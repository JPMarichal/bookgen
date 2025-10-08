"""
Tests for Personalized Search Strategies (Issue #63)
"""
import pytest
from src.strategies import (
    CharacterAnalysis,
    PersonalizedSearchStrategies,
    get_personalized_strategy,
    ScientificFigureStrategy,
    PoliticalFigureStrategy,
    ArtisticFigureStrategy,
    LiteraryFigureStrategy,
    MilitaryFigureStrategy,
    AcademicDatabaseStrategy
)


class TestPersonalizedSearchStrategies:
    """Tests for PersonalizedSearchStrategies dispatcher"""
    
    def test_get_strategy_for_scientist(self):
        """Test strategy selection for scientists"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Albert Einstein", field="science")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, ScientificFigureStrategy)
    
    def test_get_strategy_for_physicist(self):
        """Test strategy selection for physics field"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Marie Curie", field="physics")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, ScientificFigureStrategy)
    
    def test_get_strategy_for_politician(self):
        """Test strategy selection for politicians"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Abraham Lincoln", field="politics")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, PoliticalFigureStrategy)
    
    def test_get_strategy_for_artist(self):
        """Test strategy selection for artists"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Pablo Picasso", field="arts")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, ArtisticFigureStrategy)
    
    def test_get_strategy_for_writer(self):
        """Test strategy selection for writers"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="William Shakespeare", field="literature")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, LiteraryFigureStrategy)
    
    def test_get_strategy_for_military(self):
        """Test strategy selection for military figures"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Napoleon Bonaparte", field="military")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, MilitaryFigureStrategy)
    
    def test_get_strategy_for_unknown_field(self):
        """Test strategy selection for unknown field defaults to academic"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Unknown Person", field="unknown")
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, AcademicDatabaseStrategy)
    
    def test_get_strategy_no_field(self):
        """Test strategy selection when no field is specified"""
        dispatcher = PersonalizedSearchStrategies()
        analysis = CharacterAnalysis(name="Someone", field=None)
        
        strategy = dispatcher.get_search_strategy(analysis)
        
        assert isinstance(strategy, AcademicDatabaseStrategy)


class TestGetPersonalizedStrategy:
    """Tests for get_personalized_strategy helper function"""
    
    def test_einstein_returns_scientific_strategy(self):
        """Test that Einstein returns ScientificFigureStrategy"""
        strategy = get_personalized_strategy("Albert Einstein")
        
        assert isinstance(strategy, ScientificFigureStrategy)
    
    def test_curie_returns_scientific_strategy(self):
        """Test that Curie returns ScientificFigureStrategy"""
        strategy = get_personalized_strategy("Marie Curie")
        
        assert isinstance(strategy, ScientificFigureStrategy)
    
    def test_washington_returns_political_strategy(self):
        """Test that Washington returns PoliticalFigureStrategy"""
        strategy = get_personalized_strategy("George Washington")
        
        assert isinstance(strategy, PoliticalFigureStrategy)
    
    def test_picasso_returns_artistic_strategy(self):
        """Test that Picasso returns ArtisticFigureStrategy"""
        strategy = get_personalized_strategy("Pablo Picasso")
        
        assert isinstance(strategy, ArtisticFigureStrategy)
    
    def test_shakespeare_returns_literary_strategy(self):
        """Test that Shakespeare returns LiteraryFigureStrategy"""
        strategy = get_personalized_strategy("William Shakespeare")
        
        assert isinstance(strategy, LiteraryFigureStrategy)
    
    def test_napoleon_returns_military_strategy(self):
        """Test that Napoleon returns MilitaryFigureStrategy"""
        strategy = get_personalized_strategy("Napoleon Bonaparte")
        
        assert isinstance(strategy, MilitaryFigureStrategy)
    
    def test_unknown_person_returns_academic_strategy(self):
        """Test that unknown person returns default AcademicDatabaseStrategy"""
        strategy = get_personalized_strategy("Unknown Historical Figure")
        
        assert isinstance(strategy, AcademicDatabaseStrategy)


class TestScientificFigureStrategy:
    """Tests for ScientificFigureStrategy"""
    
    def test_search_returns_sources(self):
        """Test that search returns scientific sources"""
        analysis = CharacterAnalysis(name="Albert Einstein", field="science")
        strategy = ScientificFigureStrategy(analysis)
        
        sources = strategy.search("Albert Einstein")
        
        assert len(sources) > 0
        assert all(s.quality_score > 0 for s in sources)
    
    def test_priority_domains_include_scientific(self):
        """Test that priority domains include scientific sources"""
        strategy = ScientificFigureStrategy()
        domains = strategy.get_priority_domains()
        
        assert 'arxiv.org' in domains
        assert 'nobelprize.org' in domains
        assert 'nature.com' in domains
    
    def test_specialized_search_terms(self):
        """Test specialized search terms for scientists"""
        analysis = CharacterAnalysis(name="Einstein", field="science", specialty="physics")
        strategy = ScientificFigureStrategy(analysis)
        
        terms = strategy.get_specialized_search_terms("Einstein")
        
        assert any('scientist' in term for term in terms)
        assert any('research' in term for term in terms)
    
    def test_sources_include_nobelprize_org(self):
        """Test that sources include nobelprize.org"""
        strategy = ScientificFigureStrategy()
        sources = strategy.search("Einstein")
        
        assert any('nobelprize.org' in s.source_item.url for s in sources)
    
    def test_sources_include_arxiv(self):
        """Test that sources include arxiv.org"""
        strategy = ScientificFigureStrategy()
        sources = strategy.search("Einstein")
        
        assert any('arxiv.org' in s.source_item.url for s in sources)
    
    def test_quality_scores_high(self):
        """Test that quality scores are high for scientific sources"""
        strategy = ScientificFigureStrategy()
        sources = strategy.search("Marie Curie")
        
        # All scientific sources should have quality >= 85
        assert all(s.quality_score >= 85 for s in sources)


class TestPoliticalFigureStrategy:
    """Tests for PoliticalFigureStrategy"""
    
    def test_search_returns_sources(self):
        """Test that search returns political sources"""
        analysis = CharacterAnalysis(name="Lincoln", field="politics")
        strategy = PoliticalFigureStrategy(analysis)
        
        sources = strategy.search("Abraham Lincoln")
        
        assert len(sources) > 0
        assert all(s.quality_score > 0 for s in sources)
    
    def test_priority_domains_include_government(self):
        """Test that priority domains include government sources"""
        strategy = PoliticalFigureStrategy()
        domains = strategy.get_priority_domains()
        
        assert 'loc.gov' in domains
        assert 'archives.gov' in domains
    
    def test_sources_include_loc_gov(self):
        """Test that sources include Library of Congress"""
        strategy = PoliticalFigureStrategy()
        sources = strategy.search("George Washington")
        
        assert any('loc.gov' in s.source_item.url for s in sources)
    
    def test_american_president_includes_presidential_library(self):
        """Test that American presidents include presidential library sources"""
        analysis = CharacterAnalysis(
            name="Abraham Lincoln",
            field="politics",
            nationality="American"
        )
        strategy = PoliticalFigureStrategy(analysis)
        
        sources = strategy.search("Abraham Lincoln")
        
        # Should include presidential sources
        assert any('presidency.ucsb.edu' in s.source_item.url for s in sources)
    
    def test_quality_scores_high(self):
        """Test that quality scores are high for political sources"""
        strategy = PoliticalFigureStrategy()
        sources = strategy.search("Winston Churchill")
        
        # All political sources should have quality >= 85
        assert all(s.quality_score >= 85 for s in sources)


class TestArtisticFigureStrategy:
    """Tests for ArtisticFigureStrategy"""
    
    def test_search_returns_sources(self):
        """Test that search returns artistic sources"""
        analysis = CharacterAnalysis(name="Picasso", field="arts")
        strategy = ArtisticFigureStrategy(analysis)
        
        sources = strategy.search("Pablo Picasso")
        
        assert len(sources) > 0
        assert all(s.quality_score > 0 for s in sources)
    
    def test_priority_domains_include_museums(self):
        """Test that priority domains include art museums"""
        strategy = ArtisticFigureStrategy()
        domains = strategy.get_priority_domains()
        
        assert 'metmuseum.org' in domains
        assert 'moma.org' in domains
        assert 'nga.gov' in domains
    
    def test_sources_include_museums(self):
        """Test that sources include museum sources"""
        strategy = ArtisticFigureStrategy()
        sources = strategy.search("Leonardo da Vinci")
        
        museum_domains = ['metmuseum.org', 'moma.org', 'nga.gov', 'getty.edu']
        assert any(any(domain in s.source_item.url for domain in museum_domains) for s in sources)
    
    def test_quality_scores_high(self):
        """Test that quality scores are high for artistic sources"""
        strategy = ArtisticFigureStrategy()
        sources = strategy.search("Vincent van Gogh")
        
        # All artistic sources should have quality >= 85
        assert all(s.quality_score >= 85 for s in sources)


class TestLiteraryFigureStrategy:
    """Tests for LiteraryFigureStrategy"""
    
    def test_search_returns_sources(self):
        """Test that search returns literary sources"""
        analysis = CharacterAnalysis(name="Shakespeare", field="literature")
        strategy = LiteraryFigureStrategy(analysis)
        
        sources = strategy.search("William Shakespeare")
        
        assert len(sources) > 0
        assert all(s.quality_score > 0 for s in sources)
    
    def test_priority_domains_include_libraries(self):
        """Test that priority domains include literary libraries"""
        strategy = LiteraryFigureStrategy()
        domains = strategy.get_priority_domains()
        
        assert 'gutenberg.org' in domains
        assert 'bl.uk' in domains
        assert 'loc.gov' in domains
    
    def test_sources_include_gutenberg(self):
        """Test that sources include Project Gutenberg"""
        strategy = LiteraryFigureStrategy()
        sources = strategy.search("Charles Dickens")
        
        assert any('gutenberg.org' in s.source_item.url for s in sources)
    
    def test_quality_scores_high(self):
        """Test that quality scores are high for literary sources"""
        strategy = LiteraryFigureStrategy()
        sources = strategy.search("Mark Twain")
        
        # All literary sources should have quality >= 85
        assert all(s.quality_score >= 85 for s in sources)


class TestMilitaryFigureStrategy:
    """Tests for MilitaryFigureStrategy"""
    
    def test_search_returns_sources(self):
        """Test that search returns military sources"""
        analysis = CharacterAnalysis(name="Napoleon", field="military")
        strategy = MilitaryFigureStrategy(analysis)
        
        sources = strategy.search("Napoleon Bonaparte")
        
        assert len(sources) > 0
        assert all(s.quality_score > 0 for s in sources)
    
    def test_priority_domains_include_military(self):
        """Test that priority domains include military archives"""
        strategy = MilitaryFigureStrategy()
        domains = strategy.get_priority_domains()
        
        assert 'history.army.mil' in domains
        assert 'archives.gov' in domains
    
    def test_sources_include_military_archives(self):
        """Test that sources include military archives"""
        strategy = MilitaryFigureStrategy()
        sources = strategy.search("Douglas MacArthur")
        
        assert any('history.army.mil' in s.source_item.url or 'archives.gov' in s.source_item.url for s in sources)
    
    def test_quality_scores_high(self):
        """Test that quality scores are high for military sources"""
        strategy = MilitaryFigureStrategy()
        sources = strategy.search("Dwight Eisenhower")
        
        # All military sources should have quality >= 85
        assert all(s.quality_score >= 85 for s in sources)


class TestAcceptanceCriteria:
    """Tests for Issue #63 acceptance criteria"""
    
    def test_einstein_scientific_strategy(self):
        """Test acceptance criteria: Einstein returns ScientificFigureStrategy"""
        strategy = get_personalized_strategy("Albert Einstein")
        
        assert isinstance(strategy, ScientificFigureStrategy)
    
    def test_einstein_scientific_domains(self):
        """Test acceptance criteria: Scientific sources prioritize scientific domains"""
        strategy = get_personalized_strategy("Albert Einstein")
        sources = strategy.search("Einstein")
        
        # Should include scientific domains
        scientific_domains = ["arxiv.org", "nobelprize.org", "nature.com"]
        assert any(any(domain in s.source_item.url for domain in scientific_domains) for s in sources), \
            f"No scientific domains found in sources: {[s.source_item.url for s in sources]}"
    
    def test_all_strategies_return_high_quality(self):
        """Test that all strategies return high-quality sources"""
        test_cases = [
            ("Albert Einstein", ScientificFigureStrategy),
            ("George Washington", PoliticalFigureStrategy),
            ("Pablo Picasso", ArtisticFigureStrategy),
            ("William Shakespeare", LiteraryFigureStrategy),
            ("Napoleon Bonaparte", MilitaryFigureStrategy),
        ]
        
        for character_name, expected_strategy_type in test_cases:
            strategy = get_personalized_strategy(character_name)
            assert isinstance(strategy, expected_strategy_type), \
                f"Expected {expected_strategy_type.__name__} for {character_name}, got {type(strategy).__name__}"
            
            sources = strategy.search(character_name)
            assert len(sources) >= 3, \
                f"Expected at least 3 sources for {character_name}, got {len(sources)}"
            assert all(s.quality_score >= 85 for s in sources), \
                f"Some sources for {character_name} have quality < 85"
