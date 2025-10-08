"""
Literary Figure Strategy - Specialized search for authors, poets, and writers
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class LiteraryFigureStrategy(SourceStrategy):
    """Estrategia especializada para figuras literarias"""
    
    def __init__(self, character_analysis: Optional[CharacterAnalysis] = None):
        """
        Initialize literary figure strategy
        
        Args:
            character_analysis: Analysis of the literary figure
        """
        self.analysis = character_analysis or CharacterAnalysis(name="", field="literature")
    
    def get_priority_domains(self) -> List[str]:
        """Get priority domains for literary sources"""
        return [
            'gutenberg.org',              # Project Gutenberg
            'archive.org',                # Internet Archive
            'britannica.com',             # Encyclopedia Britannica
            'poetryfoundation.org',       # Poetry Foundation
            'folger.edu',                 # Folger Shakespeare Library
            'bl.uk',                      # British Library
            'loc.gov',                    # Library of Congress
        ]
    
    def get_specialized_search_terms(self, character: str) -> List[str]:
        """
        Términos de búsqueda específicos para escritores
        
        Args:
            character: Character name
            
        Returns:
            List of specialized search terms
        """
        base_terms = [
            f'"{character}"',
            f'"{character}" author',
            f'"{character}" writer',
            f'"{character}" works'
        ]
        
        # Añadir términos específicos por especialidad
        if self.analysis.specialty:
            base_terms.extend([
                f'"{character}" {self.analysis.specialty}',
                f'"{character}" bibliography',
                f'"{character}" manuscripts',
                f'"{character}" letters'
            ])
        
        return base_terms
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for literary sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis (overrides init)
            
        Returns:
            List of source candidates from literary archives
        """
        if context:
            self.analysis = context
        
        candidates = []
        
        # Project Gutenberg
        candidates.extend(self._search_gutenberg(character))
        
        # Poetry Foundation
        candidates.extend(self._search_poetry_foundation(character))
        
        # British Library
        candidates.extend(self._search_british_library(character))
        
        # Library of Congress
        candidates.extend(self._search_library_of_congress(character))
        
        return candidates
    
    def _search_gutenberg(self, character: str) -> List[SourceCandidate]:
        """Search Project Gutenberg"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Project Gutenberg",
            url=f"https://www.gutenberg.org/ebooks/search/?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Project Gutenberg"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('gutenberg.org'),
            completeness=0.90,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('gutenberg.org'),
            metadata={
                'domain': 'gutenberg.org',
                'category': 'literary',
                'specialty': 'digital_library'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_poetry_foundation(self, character: str) -> List[SourceCandidate]:
        """Search Poetry Foundation"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Poetry Foundation",
            url=f"https://www.poetryfoundation.org/search?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Poetry Foundation"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.88,
            credibility=92.0,
            completeness=0.86,
            uniqueness=0.81
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.88,
            credibility_score=92.0,
            metadata={
                'domain': 'poetryfoundation.org',
                'category': 'literary',
                'specialty': 'poetry'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_british_library(self, character: str) -> List[SourceCandidate]:
        """Search British Library"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - British Library",
            url=f"https://www.bl.uk/search?search_query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="British Library"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.91,
            credibility=PremiumDomainRegistry.get_authority_score('bl.uk'),
            completeness=0.89,
            uniqueness=0.84
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.91,
            credibility_score=PremiumDomainRegistry.get_authority_score('bl.uk'),
            metadata={
                'domain': 'bl.uk',
                'category': 'literary',
                'specialty': 'library_archive'
            }
        )
        candidates.append(candidate)
        
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
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('loc.gov'),
            completeness=0.88,
            uniqueness=0.83
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('loc.gov'),
            metadata={
                'domain': 'loc.gov',
                'category': 'literary',
                'specialty': 'library_archive'
            }
        )
        candidates.append(candidate)
        
        return candidates
