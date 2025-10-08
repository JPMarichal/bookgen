"""
Military Figure Strategy - Specialized search for military leaders and commanders
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class MilitaryFigureStrategy(SourceStrategy):
    """Estrategia especializada para figuras militares"""
    
    def __init__(self, character_analysis: Optional[CharacterAnalysis] = None):
        """
        Initialize military figure strategy
        
        Args:
            character_analysis: Analysis of the military figure
        """
        self.analysis = character_analysis or CharacterAnalysis(name="", field="military")
    
    def get_priority_domains(self) -> List[str]:
        """Get priority domains for military sources"""
        return [
            'army.mil',                   # US Army
            'history.army.mil',           # US Army History
            'navy.mil',                   # US Navy
            'archives.gov',               # National Archives
            'loc.gov',                    # Library of Congress
            'nationalarchives.gov.uk',    # UK National Archives
            'iwm.org.uk',                 # Imperial War Museum
            'usni.org',                   # US Naval Institute
        ]
    
    def get_specialized_search_terms(self, character: str) -> List[str]:
        """
        Términos de búsqueda específicos para militares
        
        Args:
            character: Character name
            
        Returns:
            List of specialized search terms
        """
        base_terms = [
            f'"{character}"',
            f'"{character}" general',
            f'"{character}" military',
            f'"{character}" commander'
        ]
        
        # Añadir términos específicos por especialidad
        if self.analysis.specialty:
            base_terms.extend([
                f'"{character}" {self.analysis.specialty}',
                f'"{character}" battle',
                f'"{character}" campaign',
                f'"{character}" war'
            ])
        
        return base_terms
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for military sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis (overrides init)
            
        Returns:
            List of source candidates from military archives
        """
        if context:
            self.analysis = context
        
        candidates = []
        
        # US Army History
        candidates.extend(self._search_army_history(character))
        
        # National Archives
        candidates.extend(self._search_national_archives(character))
        
        # US Naval Institute
        candidates.extend(self._search_naval_institute(character))
        
        # Imperial War Museum (if British or WWII-related)
        if self._is_british_or_wwii():
            candidates.extend(self._search_imperial_war_museum(character))
        
        return candidates
    
    def _is_british_or_wwii(self) -> bool:
        """Check if British nationality or WWII era"""
        if self.analysis.nationality and 'british' in self.analysis.nationality.lower():
            return True
        if self.analysis.era and ('20th century' in self.analysis.era.lower() or 'wwii' in self.analysis.era.lower()):
            return True
        return False
    
    def _search_army_history(self, character: str) -> List[SourceCandidate]:
        """Search US Army History"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - US Army History",
            url=f"https://history.army.mil/search.html?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="US Army Center of Military History"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.91,
            credibility=95.0,
            completeness=0.89,
            uniqueness=0.84
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.91,
            credibility_score=95.0,
            metadata={
                'domain': 'history.army.mil',
                'category': 'military',
                'specialty': 'army_history'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_national_archives(self, character: str) -> List[SourceCandidate]:
        """Search National Archives"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - National Archives Military Records",
            url=f"https://catalog.archives.gov/search?q={character.replace(' ', '+')}&f.level=item&f.materialsType=militaryrecords",
            source_type=SourceType.ARTICLE,
            author="US National Archives"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('archives.gov'),
            completeness=0.90,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('archives.gov'),
            metadata={
                'domain': 'archives.gov',
                'category': 'military',
                'specialty': 'government_archive'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_naval_institute(self, character: str) -> List[SourceCandidate]:
        """Search US Naval Institute"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - US Naval Institute",
            url=f"https://www.usni.org/search?keys={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="US Naval Institute"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.88,
            credibility=93.0,
            completeness=0.86,
            uniqueness=0.81
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.88,
            credibility_score=93.0,
            metadata={
                'domain': 'usni.org',
                'category': 'military',
                'specialty': 'naval_history'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_imperial_war_museum(self, character: str) -> List[SourceCandidate]:
        """Search Imperial War Museum"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Imperial War Museum",
            url=f"https://www.iwm.org.uk/search?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Imperial War Museum"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=94.0,
            completeness=0.88,
            uniqueness=0.83
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=94.0,
            metadata={
                'domain': 'iwm.org.uk',
                'category': 'military',
                'specialty': 'war_museum'
            }
        )
        candidates.append(candidate)
        
        return candidates
