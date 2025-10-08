"""
Hybrid source generator service - combines automatic generation with manual sources
"""
import logging
from typing import List, Dict, Any
from collections import defaultdict

from ..services.source_generator import AutomaticSourceGenerator
from ..services.source_validator import SourceValidationService
from ..api.models.sources import SourceItem, SourceType
from ..api.models.source_generation import AutomaticSourceGenerationRequest
from ..api.models.hybrid_generation import (
    HybridSourceGenerationRequest,
    SuggestionItem
)

logger = logging.getLogger(__name__)


class HybridSourceGenerator:
    """
    Hybrid source generator combining automatic generation with manual user sources
    
    This service implements the hybrid mode that:
    - Accepts user-provided sources
    - Auto-completes with AI-generated sources
    - Validates all sources (user + auto)
    - Provides intelligent suggestions
    - Maintains quality standards
    """
    
    def __init__(
        self,
        automatic_generator: AutomaticSourceGenerator = None,
        source_validator: SourceValidationService = None
    ):
        """
        Initialize the hybrid source generator
        
        Args:
            automatic_generator: Automatic source generator (creates default if None)
            source_validator: Source validation service (creates default if None)
        """
        self.automatic_generator = automatic_generator or AutomaticSourceGenerator()
        self.source_validator = source_validator or SourceValidationService()
        
        logger.info("HybridSourceGenerator initialized")
    
    def generate_hybrid_sources(
        self,
        request: HybridSourceGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate sources in hybrid mode (user + automatic)
        
        Args:
            request: Hybrid generation request with user sources and parameters
            
        Returns:
            Dictionary with combined sources and metadata
        """
        character_name = request.character_name
        logger.info(
            f"Starting hybrid source generation for '{character_name}' "
            f"with {len(request.user_sources)} user sources, target={request.target_count}"
        )
        
        # Step 1: Process user-provided sources
        user_sources = self._process_user_sources(
            request.user_sources,
            character_name,
            request.check_accessibility
        )
        logger.info(f"Processed {len(user_sources)} user sources")
        
        # Step 2: Auto-complete if requested
        auto_sources = []
        auto_generated_count = 0
        
        if request.auto_complete:
            needed_count = max(0, request.target_count - len(user_sources))
            
            if needed_count > 0:
                logger.info(f"Auto-completing with {needed_count} additional sources")
                
                # Ensure min_sources is at least 10 for AutomaticSourceGenerationRequest
                min_sources_for_request = max(10, needed_count)
                
                # Create automatic generation request
                auto_request = AutomaticSourceGenerationRequest(
                    character_name=character_name,
                    min_sources=min_sources_for_request,
                    max_sources=min_sources_for_request + 10,  # Generate extra to filter
                    check_accessibility=request.check_accessibility,
                    min_relevance=request.min_relevance,
                    min_credibility=request.min_credibility
                )
                
                # Generate automatic sources
                auto_result = self.automatic_generator.generate_sources_for_character(auto_request)
                auto_sources = auto_result['sources']
                
                # Filter out duplicates with user sources
                auto_sources = self._remove_duplicates(auto_sources, user_sources)
                
                # Limit to needed count
                auto_sources = auto_sources[:needed_count]
                auto_generated_count = len(auto_sources)
                
                logger.info(f"Auto-generated {auto_generated_count} sources")
        
        # Step 3: Combine sources
        combined_sources = user_sources + auto_sources
        logger.info(f"Combined total: {len(combined_sources)} sources")
        
        # Step 4: Validate combined sources
        validation_result = self._validate_combined_sources(
            combined_sources,
            character_name,
            request
        )
        
        # Step 5: Generate intelligent suggestions if requested
        suggestions = []
        if request.provide_suggestions:
            suggestions = self._generate_suggestions(
                combined_sources,
                user_sources,
                character_name,
                request
            )
            logger.info(f"Generated {len(suggestions)} suggestions")
        
        # Step 6: Build response
        return {
            'character_name': character_name,
            'sources': combined_sources,
            'user_source_count': len(user_sources),
            'auto_generated_count': auto_generated_count,
            'suggestions': suggestions,
            'validation_summary': validation_result,
            'configuration': {
                'auto_complete': request.auto_complete,
                'target_count': request.target_count,
                'min_relevance': request.min_relevance,
                'min_credibility': request.min_credibility,
                'check_accessibility': request.check_accessibility
            },
            'metadata': {
                'total_sources': len(combined_sources),
                'target_met': len(combined_sources) >= request.target_count,
                'suggestions_provided': len(suggestions)
            }
        }
    
    def _process_user_sources(
        self,
        user_urls: List[str],
        character_name: str,
        check_accessibility: bool
    ) -> List[SourceItem]:
        """
        Process and validate user-provided sources
        
        Args:
            user_urls: List of user-provided URLs
            character_name: Character name for context
            check_accessibility: Whether to check URL accessibility
            
        Returns:
            List of validated SourceItem objects
        """
        sources = []
        
        for url in user_urls:
            # Create basic source item from URL
            source = SourceItem(
                url=url,
                title=self._extract_title_from_url(url),
                source_type=SourceType.URL,
                author=None,
                publication_date=None
            )
            
            # Validate the source
            validation = self.source_validator.validate_single_source(
                source,
                character_name,
                check_accessibility=check_accessibility
            )
            
            # Include source even if validation has issues (user explicitly added it)
            # But log warnings for awareness
            if not validation.is_valid:
                logger.warning(
                    f"User source has validation issues: {url} - {validation.issues}"
                )
            
            sources.append(source)
        
        return sources
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract a basic title from URL
        
        Args:
            url: The URL to extract title from
            
        Returns:
            Basic title string
        """
        # Remove protocol
        title = url.replace('https://', '').replace('http://', '')
        
        # Remove www.
        title = title.replace('www.', '')
        
        # Take domain + path
        if '/' in title:
            parts = title.split('/')
            domain = parts[0]
            path = parts[-1] if len(parts) > 1 and parts[-1] else domain
            
            # Clean up path
            path = path.replace('-', ' ').replace('_', ' ')
            path = path.split('?')[0]  # Remove query params
            path = path.split('#')[0]  # Remove anchors
            
            if path != domain:
                title = f"{domain}: {path}"
            else:
                title = domain
        
        return title[:200]  # Limit length
    
    def _remove_duplicates(
        self,
        auto_sources: List[SourceItem],
        user_sources: List[SourceItem]
    ) -> List[SourceItem]:
        """
        Remove auto-generated sources that duplicate user sources
        
        Args:
            auto_sources: Auto-generated sources
            user_sources: User-provided sources
            
        Returns:
            Filtered auto sources without duplicates
        """
        user_urls = {source.url.lower() for source in user_sources if source.url}
        
        filtered = []
        for source in auto_sources:
            if source.url and source.url.lower() not in user_urls:
                filtered.append(source)
        
        return filtered
    
    def _validate_combined_sources(
        self,
        sources: List[SourceItem],
        character_name: str,
        request: HybridSourceGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate combined sources
        
        Args:
            sources: Combined list of sources
            character_name: Character name for context
            request: Original request with validation parameters
            
        Returns:
            Validation summary dictionary
        """
        if not sources:
            return {
                'total_sources': 0,
                'valid_sources': 0,
                'average_relevance': 0.0,
                'average_credibility': 0.0,
                'recommendations': ['No sources provided']
            }
        
        # Validate using advanced validation
        result = self.source_validator.validate_sources(
            biography_topic=character_name,
            sources_list=sources,
            check_accessibility=request.check_accessibility
        )
        
        return result
    
    def _generate_suggestions(
        self,
        combined_sources: List[SourceItem],
        user_sources: List[SourceItem],
        character_name: str,
        request: HybridSourceGenerationRequest
    ) -> List[SuggestionItem]:
        """
        Generate intelligent suggestions for additional sources
        
        Args:
            combined_sources: All combined sources
            user_sources: User-provided sources
            character_name: Character name for context
            request: Original request
            
        Returns:
            List of suggestion items
        """
        suggestions = []
        
        # Analyze source diversity
        domains = defaultdict(int)
        source_types = defaultdict(int)
        
        for source in combined_sources:
            if source.url:
                domain = self._extract_domain(source.url)
                domains[domain] += 1
            source_types[source.source_type.value] += 1
        
        # Suggestion 1: If missing academic sources
        has_academic = any(
            'scholar' in s.url.lower() or 'jstor' in s.url.lower() or 'edu' in s.url.lower()
            for s in combined_sources if s.url
        )
        
        if not has_academic:
            suggestions.append(SuggestionItem(
                suggested_source=SourceItem(
                    url=f"https://scholar.google.com/scholar?q={character_name.replace(' ', '+')}",
                    title=f"Google Scholar: {character_name}",
                    source_type=SourceType.ARTICLE,
                    author="Various"
                ),
                reason="No academic sources found. Consider adding scholarly articles.",
                relevance_score=0.9,
                category="fills_gap"
            ))
        
        # Suggestion 2: If missing government archives
        gov_domains = ['loc.gov', 'nationalarchives.gov.uk', 'nara.gov']
        has_gov = any(
            any(gov_domain in source.url.lower() for gov_domain in gov_domains)
            for source in combined_sources if source.url
        )
        
        if not has_gov:
            suggestions.append(SuggestionItem(
                suggested_source=SourceItem(
                    url=f"https://www.loc.gov/search/?q={character_name.replace(' ', '+')}",
                    title=f"Library of Congress: {character_name}",
                    source_type=SourceType.DOCUMENT,
                    author="Library of Congress"
                ),
                reason="No government archive sources. LOC often has historical documents.",
                relevance_score=0.85,
                category="fills_gap"
            ))
        
        # Suggestion 3: If too many sources from same domain
        for domain, count in domains.items():
            if count > 5:  # More than 5 from same domain
                suggestions.append(SuggestionItem(
                    suggested_source=SourceItem(
                        url=f"https://en.wikipedia.org/wiki/{character_name.replace(' ', '_')}",
                        title="Consider diversifying sources",
                        source_type=SourceType.URL,
                        author="Suggestion"
                    ),
                    reason=f"You have {count} sources from {domain}. Consider diversifying.",
                    relevance_score=0.7,
                    category="diversity"
                ))
                break  # Only suggest once
        
        # Suggestion 4: If target not met and auto_complete is disabled
        if len(combined_sources) < request.target_count and not request.auto_complete:
            needed = request.target_count - len(combined_sources)
            suggestions.append(SuggestionItem(
                suggested_source=SourceItem(
                    url="",
                    title=f"Enable auto_complete to reach target count",
                    source_type=SourceType.URL,
                    author="System"
                ),
                reason=f"You need {needed} more sources to reach target of {request.target_count}. "
                       f"Consider enabling auto_complete.",
                relevance_score=0.95,
                category="configuration"
            ))
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to top 5 suggestions
        return suggestions[:5]
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: The URL
            
        Returns:
            Domain string
        """
        domain = url.replace('https://', '').replace('http://', '')
        domain = domain.split('/')[0]
        domain = domain.replace('www.', '')
        return domain
