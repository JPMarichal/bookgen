"""
News Archive Strategy - Search news archives from reputable sources
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class NewsArchiveStrategy(SourceStrategy):
    """Strategy for searching news archives like NYTimes, Reuters, etc."""
    
    def __init__(self):
        """Initialize news archive strategy"""
        self.news_domains = PremiumDomainRegistry.get_all_domains_by_category('news')
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search news archives for sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis for informed searching
            
        Returns:
            List of source candidates from news archives
        """
        candidates = []
        
        # New York Times Archive
        candidates.extend(self._search_nytimes(character, context))
        
        # Reuters Archive
        candidates.extend(self._search_reuters(character, context))
        
        # BBC Archive
        candidates.extend(self._search_bbc(character, context))
        
        # The Guardian
        candidates.extend(self._search_guardian(character, context))
        
        # AP News (for contemporary figures)
        if self._is_contemporary(context):
            candidates.extend(self._search_ap_news(character, context))
        
        return candidates
    
    def _search_nytimes(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search New York Times Archive"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - New York Times Archive",
            url=f"https://www.nytimes.com/search?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="New York Times"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.85,
            credibility=PremiumDomainRegistry.get_authority_score('nytimes.com'),
            completeness=0.83,
            uniqueness=0.77
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.85,
            credibility_score=PremiumDomainRegistry.get_authority_score('nytimes.com'),
            metadata={
                'domain': 'nytimes.com',
                'category': 'news',
                'archive_type': 'newspaper'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_reuters(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Reuters Archive"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - Reuters Archive",
            url=f"https://www.reuters.com/site-search/?query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Reuters"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.83,
            credibility=PremiumDomainRegistry.get_authority_score('reuters.com'),
            completeness=0.82,
            uniqueness=0.75
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.83,
            credibility_score=PremiumDomainRegistry.get_authority_score('reuters.com'),
            metadata={
                'domain': 'reuters.com',
                'category': 'news',
                'archive_type': 'news_agency'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_bbc(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search BBC Archive"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - BBC News",
            url=f"https://www.bbc.com/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="BBC"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.84,
            credibility=PremiumDomainRegistry.get_authority_score('bbc.com'),
            completeness=0.81,
            uniqueness=0.74
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.84,
            credibility_score=PremiumDomainRegistry.get_authority_score('bbc.com'),
            metadata={
                'domain': 'bbc.com',
                'category': 'news',
                'archive_type': 'broadcaster'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_guardian(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search The Guardian"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - The Guardian",
            url=f"https://www.theguardian.com/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="The Guardian"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.82,
            credibility=PremiumDomainRegistry.get_authority_score('theguardian.com'),
            completeness=0.80,
            uniqueness=0.73
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.82,
            credibility_score=PremiumDomainRegistry.get_authority_score('theguardian.com'),
            metadata={
                'domain': 'theguardian.com',
                'category': 'news',
                'archive_type': 'newspaper'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_ap_news(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search AP News"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - AP News",
            url=f"https://apnews.com/search?q={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="Associated Press"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.84,
            credibility=PremiumDomainRegistry.get_authority_score('apnews.com'),
            completeness=0.81,
            uniqueness=0.75
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.84,
            credibility_score=PremiumDomainRegistry.get_authority_score('apnews.com'),
            metadata={
                'domain': 'apnews.com',
                'category': 'news',
                'archive_type': 'news_agency'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _is_contemporary(self, context: Optional[CharacterAnalysis]) -> bool:
        """Check if character is contemporary (20th/21st century)"""
        if not context or not context.era:
            return True  # Default to True for news relevance
        
        contemporary_eras = [
            '20th century', '21st century', 'contemporary',
            'modern', '1900s', '2000s'
        ]
        
        return any(era in context.era.lower() for era in contemporary_eras)
