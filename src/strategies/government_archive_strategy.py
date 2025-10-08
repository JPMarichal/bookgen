"""
Government Archive Strategy - Search government archives and national libraries
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class GovernmentArchiveStrategy(SourceStrategy):
    """Strategy for searching government archives like LOC, National Archives, etc."""
    
    def __init__(self):
        """Initialize government archive strategy"""
        self.government_domains = PremiumDomainRegistry.get_all_domains_by_category('government')
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search government archives for sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis for informed searching
            
        Returns:
            List of source candidates from government archives
        """
        candidates = []
        
        # Library of Congress
        candidates.extend(self._search_library_of_congress(character, context))
        
        # National Archives (US)
        candidates.extend(self._search_national_archives_us(character, context))
        
        # British Library & National Archives UK
        if context and context.nationality in ['British', 'UK', 'English', 'Scottish', 'Welsh']:
            candidates.extend(self._search_british_archives(character, context))
        
        # International organizations
        candidates.extend(self._search_international_orgs(character, context))
        
        return candidates
    
    def _search_library_of_congress(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Library of Congress"""
        candidates = []
        
        base_url = "https://www.loc.gov"
        
        # Main search
        source = SourceItem(
            title=f"{character} - Library of Congress",
            url=f"{base_url}/search/?q={character.replace(' ', '+')}",
            source_type=SourceType.DOCUMENT,
            author="Library of Congress"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('loc.gov'),
            completeness=0.92,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('loc.gov'),
            metadata={
                'domain': 'loc.gov',
                'category': 'government',
                'archive_type': 'national_library'
            }
        )
        candidates.append(candidate)
        
        # Manuscripts division if applicable
        if context and context.era:
            source = SourceItem(
                title=f"{character} - LOC Manuscripts Division",
                url=f"{base_url}/manuscripts/search?q={character.replace(' ', '+')}",
                source_type=SourceType.DOCUMENT,
                author="Library of Congress - Manuscripts Division"
            )
            
            quality_score = self._calculate_quality_score(
                relevance=0.88,
                credibility=PremiumDomainRegistry.get_authority_score('loc.gov'),
                completeness=0.90,
                uniqueness=0.90
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.88,
                credibility_score=PremiumDomainRegistry.get_authority_score('loc.gov'),
                metadata={
                    'domain': 'loc.gov',
                    'category': 'government',
                    'archive_type': 'manuscripts'
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def _search_national_archives_us(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search National Archives (US)"""
        candidates = []
        
        source = SourceItem(
            title=f"{character} - National Archives",
            url=f"https://catalog.archives.gov/search?q={character.replace(' ', '+')}",
            source_type=SourceType.DOCUMENT,
            author="National Archives and Records Administration"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.87,
            credibility=PremiumDomainRegistry.get_authority_score('nara.gov'),
            completeness=0.88,
            uniqueness=0.82
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.87,
            credibility_score=PremiumDomainRegistry.get_authority_score('nara.gov'),
            metadata={
                'domain': 'nara.gov',
                'category': 'government',
                'archive_type': 'government_records'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_british_archives(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search British Library and National Archives UK"""
        candidates = []
        
        # British Library
        source = SourceItem(
            title=f"{character} - British Library",
            url=f"https://www.bl.uk/search?q={character.replace(' ', '+')}",
            source_type=SourceType.DOCUMENT,
            author="British Library"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.89,
            credibility=PremiumDomainRegistry.get_authority_score('bl.uk'),
            completeness=0.90,
            uniqueness=0.83
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.89,
            credibility_score=PremiumDomainRegistry.get_authority_score('bl.uk'),
            metadata={
                'domain': 'bl.uk',
                'category': 'government',
                'archive_type': 'national_library'
            }
        )
        candidates.append(candidate)
        
        # National Archives UK
        source = SourceItem(
            title=f"{character} - UK National Archives",
            url=f"https://www.nationalarchives.gov.uk/search/results/?query={character.replace(' ', '+')}",
            source_type=SourceType.DOCUMENT,
            author="The National Archives UK"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.87,
            credibility=PremiumDomainRegistry.get_authority_score('nationalarchives.gov.uk'),
            completeness=0.88,
            uniqueness=0.85
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.87,
            credibility_score=PremiumDomainRegistry.get_authority_score('nationalarchives.gov.uk'),
            metadata={
                'domain': 'nationalarchives.gov.uk',
                'category': 'government',
                'archive_type': 'government_records'
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_international_orgs(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search international organizations like UNESCO, UN"""
        candidates = []
        
        # Only include UNESCO if relevant to the character's field
        if context and context.field and any(
            field in context.field.lower() 
            for field in ['culture', 'education', 'science', 'peace']
        ):
            # UNESCO
            source = SourceItem(
                title=f"{character} - UNESCO Archives",
                url=f"https://www.unesco.org/en/search?q={character.replace(' ', '+')}",
                source_type=SourceType.DOCUMENT,
                author="UNESCO"
            )
            
            quality_score = self._calculate_quality_score(
                relevance=0.78,
                credibility=PremiumDomainRegistry.get_authority_score('unesco.org'),
                completeness=0.85,
                uniqueness=0.80
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.78,
                credibility_score=PremiumDomainRegistry.get_authority_score('unesco.org'),
                metadata={
                    'domain': 'unesco.org',
                    'category': 'government',
                    'archive_type': 'international_organization'
                }
            )
            candidates.append(candidate)
        
        return candidates
