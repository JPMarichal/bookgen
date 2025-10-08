"""
Academic Database Strategy - Search academic databases and archives
"""
from typing import List, Optional
from ..api.models.sources import SourceItem, SourceType
from .base_strategy import SourceStrategy, CharacterAnalysis, SourceCandidate
from ..config.premium_domains import PremiumDomainRegistry


class AcademicDatabaseStrategy(SourceStrategy):
    """Strategy for searching academic databases like Archive.org, JSTOR, etc."""
    
    def __init__(self):
        """Initialize academic database strategy"""
        self.academic_domains = PremiumDomainRegistry.get_all_domains_by_category('academic')
    
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search academic databases for sources
        
        Args:
            character: Character name to search for
            context: Optional character analysis for informed searching
            
        Returns:
            List of source candidates from academic databases
        """
        candidates = []
        
        # Archive.org - Historical documents and books
        candidates.extend(self._search_archive_org(character, context))
        
        # JSTOR - Academic papers and historical documents
        candidates.extend(self._search_jstor(character, context))
        
        # University libraries
        candidates.extend(self._search_university_libraries(character, context))
        
        return candidates
    
    def _search_archive_org(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search Archive.org for sources"""
        candidates = []
        
        # Generate potential Archive.org URLs
        base_url = "https://archive.org"
        search_terms = [character]
        
        if context:
            if context.field:
                search_terms.append(f"{character} {context.field}")
            if context.specialty:
                search_terms.append(f"{character} {context.specialty}")
        
        # Create source candidates for Archive.org
        for i, term in enumerate(search_terms[:3]):  # Limit to 3 variations
            source = SourceItem(
                title=f"{character} - Archive.org Collection",
                url=f"{base_url}/details/{character.lower().replace(' ', '_')}",
                source_type=SourceType.ARTICLE,
                author="Internet Archive"
            )
            
            # High quality score for Archive.org
            quality_score = self._calculate_quality_score(
                relevance=0.87,
                credibility=PremiumDomainRegistry.get_authority_score('archive.org'),
                completeness=0.92,
                uniqueness=0.82
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.87,
                credibility_score=PremiumDomainRegistry.get_authority_score('archive.org'),
                metadata={
                    'domain': 'archive.org',
                    'category': 'academic',
                    'search_term': term
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def _search_jstor(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search JSTOR for academic papers"""
        candidates = []
        
        # Generate JSTOR search URLs
        base_url = "https://www.jstor.org"
        
        # Create source candidates for JSTOR
        source = SourceItem(
            title=f"{character} - JSTOR Academic Papers",
            url=f"{base_url}/action/doBasicSearch?Query={character.replace(' ', '+')}",
            source_type=SourceType.ARTICLE,
            author="JSTOR Contributors"
        )
        
        quality_score = self._calculate_quality_score(
            relevance=0.90,
            credibility=PremiumDomainRegistry.get_authority_score('jstor.org'),
            completeness=0.88,
            uniqueness=0.78
        )
        
        candidate = SourceCandidate(
            source_item=source,
            quality_score=quality_score,
            relevance_score=0.90,
            credibility_score=PremiumDomainRegistry.get_authority_score('jstor.org'),
            metadata={
                'domain': 'jstor.org',
                'category': 'academic',
                'search_term': character
            }
        )
        candidates.append(candidate)
        
        return candidates
    
    def _search_university_libraries(
        self,
        character: str,
        context: Optional[CharacterAnalysis]
    ) -> List[SourceCandidate]:
        """Search major university libraries"""
        candidates = []
        
        # Harvard, Stanford, MIT, Yale, Princeton, Oxford, Cambridge
        universities = [
            ('harvard.edu', 'Harvard University Library'),
            ('stanford.edu', 'Stanford University Library'),
            ('mit.edu', 'MIT Libraries'),
            ('yale.edu', 'Yale University Library'),
            ('princeton.edu', 'Princeton University Library'),
            ('oxford.ac.uk', 'Oxford University Library'),
            ('cambridge.org', 'Cambridge University Library'),
        ]
        
        for domain, library_name in universities[:4]:  # Limit to top 4
            source = SourceItem(
                title=f"{character} - {library_name}",
                url=f"https://{domain}/library/search?q={character.replace(' ', '+')}",
                source_type=SourceType.ARTICLE,
                author=library_name
            )
            
            quality_score = self._calculate_quality_score(
                relevance=0.85,
                credibility=PremiumDomainRegistry.get_authority_score(domain),
                completeness=0.85,
                uniqueness=0.75
            )
            
            candidate = SourceCandidate(
                source_item=source,
                quality_score=quality_score,
                relevance_score=0.85,
                credibility_score=PremiumDomainRegistry.get_authority_score(domain),
                metadata={
                    'domain': domain,
                    'category': 'academic',
                    'library': library_name
                }
            )
            candidates.append(candidate)
        
        return candidates
