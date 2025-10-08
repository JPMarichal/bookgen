"""
Artistic Figure Strategy - Specialized search for artists, musicians, and composers
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class ArtisticFigureStrategy(SourceStrategy):
    """Estrategia especializada para figuras artísticas"""
    
    def __init__(self, character_analysis: Optional[CharacterAnalysis] = None):
        """
        Initialize artistic figure strategy
        
        Args:
            character_analysis: Analysis of the artistic figure
        """
        self.analysis = character_analysis or CharacterAnalysis(name="", field="arts")
    
    def get_priority_domains(self) -> List[str]:
        """Get priority domains for artistic sources"""
        return [
            'metmuseum.org',          # Metropolitan Museum of Art
            'moma.org',               # Museum of Modern Art
            'louvre.fr',              # Louvre Museum
            'nga.gov',                # National Gallery of Art
            'britishmuseum.org',      # British Museum
            'getty.edu',              # Getty Museum
            'smithsonianmag.com',     # Smithsonian Magazine
            'artic.edu',              # Art Institute of Chicago
        ]
    
    def get_specialized_search_terms(self, character: str) -> List[str]:
        """
        Términos de búsqueda específicos para artistas
        
        Args:
            character: Character name
            
        Returns:
            List of specialized search terms
        """
        base_terms = [
            f'"{character}"',
            f'"{character}" artist',
            f'"{character}" artwork',
            f'"{character}" painting'
        ]
        
        # Añadir términos específicos por especialidad
        if self.analysis.specialty:
            base_terms.extend([
                f'"{character}" {self.analysis.specialty}',
                f'"{character}" exhibition',
                f'"{character}" gallery',
                f'"{character}" collection'
            ])
        
        return base_terms
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for artistic sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis (overrides init)
            
        Returns:
            List of source candidates from art museums and galleries
        """
        if context:
            self.analysis = context
        
        candidates = []
        
        # Metropolitan Museum
        candidates.extend(self._search_met_museum(character))
        
        # Museum of Modern Art
        candidates.extend(self._search_moma(character))
        
        # National Gallery
        candidates.extend(self._search_national_gallery(character))
        
        # Getty Museum
        candidates.extend(self._search_getty(character))
        
        return candidates
    
    def _search_met_museum(self, character: str) -> List[SourceCandidate]:
        """Search Metropolitan Museum of Art"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Metropolitan Museum of Art",
            url=f"https://www.metmuseum.org/art/collection/search#{character.replace(' ', '%20')}",
            source_type=SourceType.ARTICLE,
            author="Metropolitan Museum of Art"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('metmuseum.org'),
            completeness=0.90,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('metmuseum.org'),
            metadata={
                'domain': 'metmuseum.org',
                'category': 'artistic',
                'specialty': 'museum'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_moma(self, character: str) -> List[SourceCandidate]:
        """Search Museum of Modern Art"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Museum of Modern Art",
            url=f"https://www.moma.org/search/?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Museum of Modern Art"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('moma.org'),
            completeness=0.88,
            uniqueness=0.83
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('moma.org'),
            metadata={
                'domain': 'moma.org',
                'category': 'artistic',
                'specialty': 'museum'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_national_gallery(self, character: str) -> List[SourceCandidate]:
        """Search National Gallery of Art"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - National Gallery of Art",
            url=f"https://www.nga.gov/collection-search-result.html?artobj_artisttext={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="National Gallery of Art"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.91,
            credibility=PremiumDomainRegistry.get_authority_score('nga.gov'),
            completeness=0.89,
            uniqueness=0.84
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.91,
            credibility_score=PremiumDomainRegistry.get_authority_score('nga.gov'),
            metadata={
                'domain': 'nga.gov',
                'category': 'artistic',
                'specialty': 'museum'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_getty(self, character: str) -> List[SourceCandidate]:
        """Search Getty Museum"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Getty Museum",
            url=f"https://www.getty.edu/art/collection/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Getty Museum"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.89,
            credibility=PremiumDomainRegistry.get_authority_score('getty.edu'),
            completeness=0.87,
            uniqueness=0.82
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.89,
            credibility_score=PremiumDomainRegistry.get_authority_score('getty.edu'),
            metadata={
                'domain': 'getty.edu',
                'category': 'artistic',
                'specialty': 'museum'
            }
        )
        candidates.append(candidate)
        
        return candidates
