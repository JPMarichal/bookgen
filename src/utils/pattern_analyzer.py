"""
Pattern analyzer for identifying success patterns in source generation
Analyzes successful generations to identify common patterns
"""
import logging
from typing import List, Dict, Any, Set
from collections import Counter, defaultdict
from urllib.parse import urlparse

from ..strategies.base_strategy import SourceCandidate
from ..models.quality_metrics import (
    SuccessPattern,
    BiographyQualityScore
)

logger = logging.getLogger(__name__)


class SuccessPatternAnalyzer:
    """Analyzer for identifying patterns in successful source generations"""
    
    def __init__(self, min_pattern_frequency: int = 2):
        """
        Initialize pattern analyzer
        
        Args:
            min_pattern_frequency: Minimum frequency for a pattern to be considered significant
        """
        self.min_pattern_frequency = min_pattern_frequency
        logger.info("Initialized SuccessPatternAnalyzer")
    
    def identify_patterns(
        self,
        sources: List[SourceCandidate],
        character: str,
        quality_score: BiographyQualityScore
    ) -> List[SuccessPattern]:
        """
        Identify common patterns in successful sources
        
        Args:
            sources: List of source candidates
            character: Character name
            quality_score: Quality score of the biography
            
        Returns:
            List of identified success patterns
        """
        logger.debug(f"Identifying patterns for {character} with quality {quality_score.overall_score}")
        
        if not sources:
            logger.warning("No sources provided for pattern analysis")
            return []
        
        patterns = []
        
        # Analyze domain patterns
        patterns.extend(self._analyze_domain_patterns(sources, quality_score))
        
        # Analyze source type patterns
        patterns.extend(self._analyze_source_type_patterns(sources, quality_score))
        
        # Analyze quality score patterns
        patterns.extend(self._analyze_quality_patterns(sources, quality_score))
        
        # Analyze metadata patterns
        patterns.extend(self._analyze_metadata_patterns(sources, quality_score))
        
        logger.info(f"Identified {len(patterns)} patterns")
        return patterns
    
    def _analyze_domain_patterns(
        self,
        sources: List[SourceCandidate],
        quality_score: BiographyQualityScore
    ) -> List[SuccessPattern]:
        """Analyze domain-based patterns"""
        patterns = []
        domain_counter = Counter()
        
        for source in sources:
            if hasattr(source.source_item, 'url') and source.source_item.url:
                try:
                    domain = urlparse(source.source_item.url).netloc
                    # Remove www. prefix
                    domain = domain.replace('www.', '')
                    if domain:
                        domain_counter[domain] += 1
                except Exception as e:
                    logger.debug(f"Failed to parse URL: {e}")
                    continue
        
        # Create patterns for frequent domains
        for domain, count in domain_counter.items():
            if count >= self.min_pattern_frequency:
                pattern = SuccessPattern(
                    pattern_type="domain",
                    pattern_value=domain,
                    frequency=count,
                    avg_quality_impact=quality_score.overall_score,
                    confidence=min(1.0, count / len(sources))
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_source_type_patterns(
        self,
        sources: List[SourceCandidate],
        quality_score: BiographyQualityScore
    ) -> List[SuccessPattern]:
        """Analyze source type patterns"""
        patterns = []
        type_counter = Counter()
        
        for source in sources:
            if hasattr(source.source_item, 'source_type') and source.source_item.source_type:
                source_type = str(source.source_item.source_type)
                type_counter[source_type] += 1
        
        # Create patterns for frequent source types
        for source_type, count in type_counter.items():
            if count >= self.min_pattern_frequency:
                pattern = SuccessPattern(
                    pattern_type="source_type",
                    pattern_value=source_type,
                    frequency=count,
                    avg_quality_impact=quality_score.overall_score,
                    confidence=min(1.0, count / len(sources))
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_quality_patterns(
        self,
        sources: List[SourceCandidate],
        quality_score: BiographyQualityScore
    ) -> List[SuccessPattern]:
        """Analyze quality score patterns"""
        patterns = []
        
        # Count high-quality sources
        high_quality_count = sum(1 for s in sources if s.quality_score >= 85)
        
        if high_quality_count >= self.min_pattern_frequency:
            pattern = SuccessPattern(
                pattern_type="quality_threshold",
                pattern_value="high_quality_sources",
                frequency=high_quality_count,
                avg_quality_impact=quality_score.overall_score,
                confidence=high_quality_count / len(sources),
                metadata={"threshold": 85}
            )
            patterns.append(pattern)
        
        # Analyze average quality score
        if sources:
            avg_quality = sum(s.quality_score for s in sources) / len(sources)
            pattern = SuccessPattern(
                pattern_type="avg_source_quality",
                pattern_value=f"avg_{int(avg_quality)}",
                frequency=len(sources),
                avg_quality_impact=quality_score.overall_score,
                confidence=1.0,
                metadata={"average_quality": avg_quality}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_metadata_patterns(
        self,
        sources: List[SourceCandidate],
        quality_score: BiographyQualityScore
    ) -> List[SuccessPattern]:
        """Analyze metadata patterns"""
        patterns = []
        
        # Track presence of various metadata features
        features = defaultdict(int)
        
        for source in sources:
            if hasattr(source.source_item, 'author') and source.source_item.author:
                features['has_author'] += 1
            
            if hasattr(source.source_item, 'publication_date') and source.source_item.publication_date:
                features['has_publication_date'] += 1
            
            if hasattr(source.source_item, 'publisher') and source.source_item.publisher:
                features['has_publisher'] += 1
            
            # Check for academic/scholarly indicators
            if source.metadata and isinstance(source.metadata, dict):
                if source.metadata.get('is_academic'):
                    features['is_academic'] += 1
                if source.metadata.get('is_peer_reviewed'):
                    features['is_peer_reviewed'] += 1
        
        # Create patterns for significant features
        for feature, count in features.items():
            if count >= self.min_pattern_frequency:
                pattern = SuccessPattern(
                    pattern_type="metadata_feature",
                    pattern_value=feature,
                    frequency=count,
                    avg_quality_impact=quality_score.overall_score,
                    confidence=min(1.0, count / len(sources))
                )
                patterns.append(pattern)
        
        return patterns
    
    def aggregate_patterns(
        self,
        pattern_sets: List[List[SuccessPattern]]
    ) -> List[SuccessPattern]:
        """
        Aggregate patterns from multiple success cases
        
        Args:
            pattern_sets: List of pattern lists from different success cases
            
        Returns:
            Aggregated and ranked patterns
        """
        logger.debug(f"Aggregating {len(pattern_sets)} pattern sets")
        
        # Group patterns by type and value
        pattern_groups: Dict[tuple, List[SuccessPattern]] = defaultdict(list)
        
        for patterns in pattern_sets:
            for pattern in patterns:
                key = (pattern.pattern_type, pattern.pattern_value)
                pattern_groups[key].append(pattern)
        
        # Aggregate each group
        aggregated = []
        for (pattern_type, pattern_value), patterns in pattern_groups.items():
            total_frequency = sum(p.frequency for p in patterns)
            avg_quality = sum(p.avg_quality_impact for p in patterns) / len(patterns)
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            
            aggregated_pattern = SuccessPattern(
                pattern_type=pattern_type,
                pattern_value=pattern_value,
                frequency=total_frequency,
                avg_quality_impact=avg_quality,
                confidence=avg_confidence,
                metadata={"aggregated_from": len(patterns)}
            )
            aggregated.append(aggregated_pattern)
        
        # Sort by quality impact and confidence
        aggregated.sort(
            key=lambda p: (p.avg_quality_impact * p.confidence),
            reverse=True
        )
        
        logger.info(f"Aggregated to {len(aggregated)} unique patterns")
        return aggregated
