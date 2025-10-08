"""
Scientific Figure Strategy - Specialized search for scientists and researchers
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class ScientificFigureStrategy(SourceStrategy):
    """Estrategia especializada para científicos"""
    
    def __init__(self, character_analysis: Optional[CharacterAnalysis] = None):
        """
        Initialize scientific figure strategy
        
        Args:
            character_analysis: Analysis of the scientific figure
        """
        self.analysis = character_analysis or CharacterAnalysis(name="", field="science")
    
    def get_priority_domains(self) -> List[str]:
        """Get priority domains for scientific sources"""
        return [
            'arxiv.org',                  # Preprints científicos
            'pubmed.ncbi.nlm.nih.gov',   # Literatura médica
            'ieeexplore.ieee.org',       # Ingeniería y tecnología
            'aps.org',                    # Física
            'acs.org',                    # Química
            'nature.com',                 # Revista Nature
            'science.org',                # Revista Science
            'nobelprize.org',             # Premio Nobel
            'nsf.gov',                    # National Science Foundation
            'cern.ch',                    # CERN (si es físico)
        ]
    
    def get_specialized_search_terms(self, character: str) -> List[str]:
        """
        Términos de búsqueda específicos para científicos
        
        Args:
            character: Character name
            
        Returns:
            List of specialized search terms
        """
        base_terms = [
            f'"{character}"',
            f'"{character}" scientist',
            f'"{character}" research'
        ]
        
        # Añadir términos específicos por disciplina
        if self.analysis.specialty:
            base_terms.extend([
                f'"{character}" {self.analysis.specialty}',
                f'"{character}" discovery',
                f'"{character}" theory',
                f'"{character}" experiment',
                f'"{character}" publication'
            ])
        
        return base_terms
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for scientific sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis (overrides init)
            
        Returns:
            List of source candidates from scientific databases
        """
        if context:
            self.analysis = context
        
        candidates = []
        
        # Nobel Prize if applicable
        candidates.extend(self._search_nobel_prize(character))
        
        # ArXiv for scientific papers
        candidates.extend(self._search_arxiv(character))
        
        # Nature and Science journals
        candidates.extend(self._search_scientific_journals(character))
        
        # National Science Foundation
        candidates.extend(self._search_nsf(character))
        
        return candidates
    
    def _search_nobel_prize(self, character: str) -> List[SourceCandidate]:
        """Search Nobel Prize website"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Nobel Prize",
            url=f"https://www.nobelprize.org/search/?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Nobel Prize Organization"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('nobelprize.org'),
            completeness=0.90,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('nobelprize.org'),
            metadata={
                'domain': 'nobelprize.org',
                'category': 'scientific',
                'specialty': 'nobel_laureate'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_arxiv(self, character: str) -> List[SourceCandidate]:
        """Search ArXiv for scientific papers"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - ArXiv Scientific Papers",
            url=f"https://arxiv.org/search/?query={character.replace(' ', '+')}&searchtype=author",
            source_type=SourceType.ARTICLE,
            author="ArXiv Contributors"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.88,
            credibility=95.0,  # ArXiv is highly credible
            completeness=0.85,
            uniqueness=0.80
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.88,
            credibility_score=95.0,
            metadata={
                'domain': 'arxiv.org',
                'category': 'scientific',
                'specialty': 'research_papers'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_scientific_journals(self, character: str) -> List[SourceCandidate]:
        """Search major scientific journals"""
        candidates = []
        
        journals = [
            ('nature.com', 'Nature Journal'),
            ('science.org', 'Science Journal'),
        ]
        
        for domain, journal_name in journals:
            source = SourceItem(
                title=f"{character} - {journal_name}",
                url=f"https://www.{domain}/search?q={character.replace(' ', '+')}",
                source_type=SourceType.ARTICLE,
                author=journal_name
            )
            
            quality_score = self._calculate_quality_score(
                relevance=0.90,
                credibility=PremiumDomainRegistry.get_authority_score(domain),
                completeness=0.87,
                uniqueness=0.82
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.90,
                credibility_score=PremiumDomainRegistry.get_authority_score(domain),
                metadata={
                    'domain': domain,
                    'category': 'scientific',
                    'specialty': 'journal'
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def _search_nsf(self, character: str) -> List[SourceCandidate]:
        """Search National Science Foundation"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - National Science Foundation",
            url=f"https://www.nsf.gov/awardsearch/simpleSearchResult?queryText={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="National Science Foundation"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.85,
            credibility=PremiumDomainRegistry.get_authority_score('nsf.gov'),
            completeness=0.83,
            uniqueness=0.78
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.85,
            credibility_score=PremiumDomainRegistry.get_authority_score('nsf.gov'),
            metadata={
                'domain': 'nsf.gov',
                'category': 'scientific',
                'specialty': 'government_research'
            }
        )
        candidates.append(candidate)
        
        return candidates
