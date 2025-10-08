"""
Source Triangulator
Cross-reference and triangulate information from multiple sources
"""
import logging
from typing import List, Dict, Any, Set
from collections import defaultdict

from ..strategies.base_strategy import SourceCandidate
from ..api.models.cross_validation import KeyFact

logger = logging.getLogger(__name__)


class SourceTriangulator:
    """Triangulator for cross-referencing multiple sources"""
    
    def __init__(self):
        """Initialize the source triangulator"""
        logger.info("SourceTriangulator initialized")
    
    def triangulate_facts(
        self,
        fact_sets: List[List[KeyFact]]
    ) -> Dict[str, Any]:
        """
        Triangulate facts across multiple sources
        
        Args:
            fact_sets: List of fact sets from different sources
            
        Returns:
            Dictionary with triangulation results
        """
        if not fact_sets or len(fact_sets) < 2:
            logger.warning("Need at least 2 fact sets for triangulation")
            return {
                'verified_facts': [],
                'conflicting_facts': [],
                'confidence_score': 0.0
            }
        
        # Count fact occurrences across sources
        fact_occurrence = defaultdict(int)
        fact_details = {}
        
        for source_idx, facts in enumerate(fact_sets):
            for fact in facts:
                # Normalize fact text for comparison
                normalized = self._normalize_fact(fact.fact)
                fact_occurrence[normalized] += 1
                
                if normalized not in fact_details:
                    fact_details[normalized] = {
                        'original': fact.fact,
                        'sources': [],
                        'confidence': fact.confidence
                    }
                fact_details[normalized]['sources'].append(source_idx)
        
        # Categorize facts based on occurrence
        verified_facts = []
        conflicting_facts = []
        
        for normalized, count in fact_occurrence.items():
            details = fact_details[normalized]
            
            # Facts appearing in 2+ sources are verified
            if count >= 2:
                verified_facts.append({
                    'fact': details['original'],
                    'source_count': count,
                    'sources': details['sources'],
                    'confidence': details['confidence']
                })
            # Facts in only 1 source might conflict with others
            elif count == 1:
                conflicting_facts.append({
                    'fact': details['original'],
                    'sources': details['sources']
                })
        
        # Calculate confidence score
        total_facts = len(fact_occurrence)
        confidence = len(verified_facts) / total_facts if total_facts > 0 else 0.0
        
        return {
            'verified_facts': verified_facts,
            'conflicting_facts': conflicting_facts,
            'confidence_score': confidence,
            'total_facts': total_facts,
            'verification_rate': confidence
        }
    
    def _normalize_fact(self, fact: str) -> str:
        """
        Normalize fact text for comparison
        
        Args:
            fact: Fact text
            
        Returns:
            Normalized fact text
        """
        # Convert to lowercase
        normalized = fact.lower().strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common punctuation
        normalized = normalized.rstrip('.,;:!?')
        
        return normalized
    
    def calculate_source_overlap(
        self,
        sources: List[SourceCandidate]
    ) -> Dict[str, Any]:
        """
        Calculate information overlap between sources
        
        Args:
            sources: List of source candidates
            
        Returns:
            Overlap analysis
        """
        if len(sources) < 2:
            return {
                'overlap_score': 0.0,
                'unique_sources': len(sources),
                'redundant_sources': 0
            }
        
        # Extract domains
        domains = []
        for source in sources:
            if hasattr(source.source_item, 'url') and source.source_item.url:
                domain = self._extract_domain(source.source_item.url)
                domains.append(domain)
        
        # Count unique domains
        unique_domains = len(set(domains))
        total_sources = len(sources)
        
        # Calculate diversity
        diversity = unique_domains / total_sources if total_sources > 0 else 0.0
        
        return {
            'overlap_score': 1.0 - diversity,
            'unique_sources': unique_domains,
            'redundant_sources': total_sources - unique_domains,
            'total_sources': total_sources,
            'diversity_score': diversity
        }
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: URL string
            
        Returns:
            Domain name
        """
        import re
        
        # Remove protocol
        domain = re.sub(r'https?://', '', url)
        
        # Remove www.
        domain = re.sub(r'^www\.', '', domain)
        
        # Get first part (domain)
        domain = domain.split('/')[0]
        
        return domain
    
    def detect_source_diversity(
        self,
        sources: List[SourceCandidate]
    ) -> float:
        """
        Detect diversity of source types and origins
        
        Args:
            sources: List of source candidates
            
        Returns:
            Diversity score (0-1)
        """
        if not sources:
            return 0.0
        
        # Collect different aspects
        source_types: Set[str] = set()
        domains: Set[str] = set()
        authors: Set[str] = set()
        
        for source in sources:
            # Source type
            if hasattr(source.source_item, 'source_type'):
                source_types.add(str(source.source_item.source_type))
            
            # Domain
            if hasattr(source.source_item, 'url') and source.source_item.url:
                domain = self._extract_domain(source.source_item.url)
                domains.add(domain)
            
            # Author
            if hasattr(source.source_item, 'author') and source.source_item.author:
                authors.add(source.source_item.author)
        
        # Calculate diversity based on multiple factors
        type_diversity = len(source_types) / min(5, len(sources))
        domain_diversity = len(domains) / len(sources)
        author_diversity = len(authors) / len(sources) if authors else 0.3
        
        # Weighted average
        diversity = (
            type_diversity * 0.3 +
            domain_diversity * 0.5 +
            author_diversity * 0.2
        )
        
        return min(1.0, diversity)
