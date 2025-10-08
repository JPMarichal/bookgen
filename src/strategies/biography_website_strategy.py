"""
Biography Website Strategy - Search specialized biography websites
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class BiographyWebsiteStrategy(SourceStrategy):
    """Strategy for searching biography-focused websites like Britannica, Biography.com, etc."""
    
    def __init__(self):
        """Initialize biography website strategy"""
        self.biographical_domains = PremiumDomainRegistry.get_all_domains_by_category('biographical')
        self.encyclopedic_domains = PremiumDomainRegistry.get_all_domains_by_category('encyclopedic')
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search biography websites for sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis for informed searching
            
        Returns:
            List of source candidates from biography websites
        """
        candidates = []
        
        # Britannica - Encyclopedia Britannica
        candidates.extend(self._search_britannica(character, context))
        
        # Biography.com
        candidates.extend(self._search_biography_com(character, context))
        
        # History.com
        candidates.extend(self._search_history_com(character, context))
        
        # Nobel Prize (if applicable)
        if self._is_nobel_relevant(context):
            candidates.extend(self._search_nobel_prize(character, context))
        
        return candidates
    
    def _search_britannica(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Encyclopedia Britannica"""
        candidates = []
        
        # Main biography page
        source = SourceItem(
            title=f"{character} - Encyclopedia Britannica",
            url=f"https://www.britannica.com/biography/{character.replace(' ', '-')}",
            source_type=SourceType.ARTICLE,
            author="Encyclopedia Britannica Editors"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.92,
            credibility=PremiumDomainRegistry.get_authority_score('britannica.com'),
            completeness=0.90,
            uniqueness=0.80
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.92,
            credibility_score=PremiumDomainRegistry.get_authority_score('britannica.com'),
            metadata={
                'domain': 'britannica.com',
                'category': 'encyclopedic',
                'content_type': 'biography'
            }
        )
        candidates.append(candidate)
        
        # Topic page if field is known
        if context and context.field:
            source = SourceItem(
                title=f"{character} - {context.field} - Britannica",
                url=f"https://www.britannica.com/search?query={character.replace(' ', '+')}+{context.field}",
                source_type=SourceType.ARTICLE,
                author="Encyclopedia Britannica"
            )
            
            quality_score = self._calculate_quality_score(
                relevance=0.88,
                credibility=PremiumDomainRegistry.get_authority_score('britannica.com'),
                completeness=0.85,
                uniqueness=0.75
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.88,
                credibility_score=PremiumDomainRegistry.get_authority_score('britannica.com'),
                metadata={
                    'domain': 'britannica.com',
                    'category': 'encyclopedic',
                    'content_type': 'topic'
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def _search_biography_com(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Biography.com"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Biography",
            url=f"https://www.biography.com/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Biography.com Editors"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('biography.com'),
            completeness=0.88,
            uniqueness=0.78
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('biography.com'),
            metadata={
                'domain': 'biography.com',
                'category': 'biographical',
                'content_type': 'biography'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_history_com(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search History.com"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - History.com",
            url=f"https://www.history.com/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="History.com Editors"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.85,
            credibility=PremiumDomainRegistry.get_authority_score('history.com'),
            completeness=0.82,
            uniqueness=0.73
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.85,
            credibility_score=PremiumDomainRegistry.get_authority_score('history.com'),
            metadata={
                'domain': 'history.com',
                'category': 'biographical',
                'content_type': 'history'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_nobel_prize(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Nobel Prize website"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Nobel Prize",
            url=f"https://www.nobelprize.org/search/?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Nobel Prize Organization"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.95,
            credibility=PremiumDomainRegistry.get_authority_score('nobelprize.org'),
            completeness=0.93,
            uniqueness=0.90
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.95,
            credibility_score=PremiumDomainRegistry.get_authority_score('nobelprize.org'),
            metadata={
                'domain': 'nobelprize.org',
                'category': 'biographical',
                'content_type': 'official_biography',
                'nobel_related': True
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _is_nobel_relevant(self, context: Optional[CharacterAnalysis]) -> bool:
        """Check if Nobel Prize search is relevant"""
        if not context:
            return False
        
        # Check if character is in science, literature, peace, or economics
        nobel_fields = ['science', 'physics', 'chemistry', 'medicine', 
                       'literature', 'peace', 'economics']
        
        if context.field and any(field in context.field.lower() for field in nobel_fields):
            return True
        
        if context.specialty and any(field in context.specialty.lower() for field in nobel_fields):
            return True
        
        return False
