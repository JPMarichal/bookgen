"""
Political Figure Strategy - Specialized search for political leaders and statesmen
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class PoliticalFigureStrategy(SourceStrategy):
    """Estrategia especializada para figuras políticas"""
    
    def __init__(self, character_analysis: Optional[CharacterAnalysis] = None):
        """
        Initialize political figure strategy
        
        Args:
            character_analysis: Analysis of the political figure
        """
        self.analysis = character_analysis or CharacterAnalysis(name="", field="politics")
    
    def get_priority_domains(self) -> List[str]:
        """Get priority domains for political sources"""
        return [
            'loc.gov',                    # Library of Congress
            'archives.gov',               # US National Archives
            'nationalarchives.gov.uk',    # UK National Archives
            'presidency.ucsb.edu',        # American Presidency Project
            'un.org',                     # United Nations
            'whitehouse.gov',             # White House
            'congress.gov',               # US Congress
            'parliament.uk',              # UK Parliament
        ]
    
    def get_specialized_search_terms(self, character: str) -> List[str]:
        """
        Términos de búsqueda específicos para políticos
        
        Args:
            character: Character name
            
        Returns:
            List of specialized search terms
        """
        base_terms = [
            f'"{character}"',
            f'"{character}" president',
            f'"{character}" political',
            f'"{character}" government'
        ]
        
        # Añadir términos específicos
        if self.analysis.specialty:
            base_terms.extend([
                f'"{character}" {self.analysis.specialty}',
                f'"{character}" policy',
                f'"{character}" speech',
                f'"{character}" administration'
            ])
        
        return base_terms
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for political sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis (overrides init)
            
        Returns:
            List of source candidates from political archives
        """
        if context:
            self.analysis = context
        
        candidates = []
        
        # Library of Congress
        candidates.extend(self._search_library_of_congress(character))
        
        # National Archives
        candidates.extend(self._search_national_archives(character))
        
        # Presidential libraries (if American)
        if self.analysis.nationality and 'american' in self.analysis.nationality.lower():
            candidates.extend(self._search_presidential_libraries(character))
        
        # UK archives (if British)
        if self.analysis.nationality and 'british' in self.analysis.nationality.lower():
            candidates.extend(self._search_uk_archives(character))
        
        # UN archives
        candidates.extend(self._search_un_archives(character))
        
        return candidates
    
    def _search_library_of_congress(self, character: str) -> List[SourceCandidate]:
        """Search Library of Congress"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Library of Congress",
            url=f"https://www.loc.gov/search/?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Library of Congress"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('loc.gov'),
            completeness=0.90,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('loc.gov'),
            metadata={
                'domain': 'loc.gov',
                'category': 'political',
                'specialty': 'government_archive'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_national_archives(self, character: str) -> List[SourceCandidate]:
        """Search US National Archives"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - National Archives",
            url=f"https://catalog.archives.gov/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="US National Archives"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('archives.gov'),
            completeness=0.88,
            uniqueness=0.83
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('archives.gov'),
            metadata={
                'domain': 'archives.gov',
                'category': 'political',
                'specialty': 'government_archive'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_presidential_libraries(self, character: str) -> List[SourceCandidate]:
        """Search American Presidency Project"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - American Presidency Project",
            url=f"https://www.presidency.ucsb.edu/advanced-search?field-keywords={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="American Presidency Project"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.93,
            credibility=95.0,
            completeness=0.91,
            uniqueness=0.86
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.93,
            credibility_score=95.0,
            metadata={
                'domain': 'presidency.ucsb.edu',
                'category': 'political',
                'specialty': 'presidential'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_uk_archives(self, character: str) -> List[SourceCandidate]:
        """Search UK National Archives"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - UK National Archives",
            url=f"https://discovery.nationalarchives.gov.uk/results/r?_q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="UK National Archives"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.91,
            credibility=PremiumDomainRegistry.get_authority_score('nationalarchives.gov.uk'),
            completeness=0.89,
            uniqueness=0.84
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.91,
            credibility_score=PremiumDomainRegistry.get_authority_score('nationalarchives.gov.uk'),
            metadata={
                'domain': 'nationalarchives.gov.uk',
                'category': 'political',
                'specialty': 'government_archive'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_un_archives(self, character: str) -> List[SourceCandidate]:
        """Search United Nations archives"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - United Nations",
            url=f"https://search.un.org/results.php?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="United Nations"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.85,
            credibility=93.0,
            completeness=0.83,
            uniqueness=0.80
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.85,
            credibility_score=93.0,
            metadata={
                'domain': 'un.org',
                'category': 'political',
                'specialty': 'international'
            }
        )
        candidates.append(candidate)
        
        return candidates
