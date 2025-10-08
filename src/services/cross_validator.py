"""
Cross-Validation System
System for cross-validating sources and ensuring factual consistency
"""
import logging
from typing import List, Dict, Any, Optional

from ..strategies.base_strategy import SourceCandidate
from ..utils.fact_checker import FactualConsistencyChecker
from ..utils.source_triangulator import SourceTriangulator
from ..api.models.cross_validation import (
    ValidationResult,
    RedundancyAnalysis,
    AcademicStandards,
    TemporalCoverage,
    KeyFact
)
from ..services.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)


class CrossValidationSystem:
    """System for cross-validation of sources to ensure factual consistency"""
    
    def __init__(self, openrouter_client: Optional[OpenRouterClient] = None):
        """
        Initialize cross-validation system
        
        Args:
            openrouter_client: Optional OpenRouter client instance
        """
        self.fact_checker = FactualConsistencyChecker(openrouter_client)
        self.source_triangulator = SourceTriangulator()
        self.openrouter_client = openrouter_client or OpenRouterClient()
        logger.info("CrossValidationSystem initialized")
    
    def validate_source_set_quality(
        self,
        sources: List[SourceCandidate],
        character: str
    ) -> ValidationResult:
        """
        Perform cross-validation on a set of sources
        
        Args:
            sources: List of source candidates to validate
            character: Character name for context
            
        Returns:
            ValidationResult with comprehensive analysis
        """
        logger.info(f"Validating {len(sources)} sources for {character}")
        
        if not sources:
            logger.warning("No sources to validate")
            return self._create_default_result()
        
        # 1. Check factual consistency
        consistency_score = self._check_factual_consistency(sources, character)
        
        # 2. Analyze temporal coverage
        temporal_coverage = self._analyze_temporal_coverage(sources, character)
        
        # 3. Calculate source diversity
        diversity_score = self._calculate_source_diversity(sources)
        
        # 4. Detect information redundancy
        redundancy_analysis = self._detect_information_redundancy(sources)
        
        # 5. Verify academic standards
        academic_standards = self._verify_academic_standards(sources)
        
        # 6. Calculate overall quality
        overall_quality = self._calculate_overall_quality(
            consistency_score,
            temporal_coverage,
            diversity_score,
            redundancy_analysis.redundancy_percentage,
            academic_standards.compliance_score
        )
        
        # 7. Generate recommendations
        recommendations = self._generate_improvement_recommendations(
            sources,
            character,
            consistency_score,
            temporal_coverage,
            diversity_score,
            redundancy_analysis
        )
        
        result = ValidationResult(
            consistency_score=consistency_score,
            temporal_coverage=temporal_coverage,
            diversity_score=diversity_score,
            redundancy_level=redundancy_analysis.redundancy_percentage,
            academic_compliance=academic_standards.compliance_score,
            overall_quality=overall_quality,
            recommendations=recommendations,
            metadata={
                'source_count': len(sources),
                'temporal_analysis': {
                    'early_life': temporal_coverage >= 0.7,
                    'career': temporal_coverage >= 0.7,
                    'later_years': temporal_coverage >= 0.7,
                    'legacy': temporal_coverage >= 0.7
                }
            }
        )
        
        logger.info(f"Validation complete - Overall quality: {overall_quality:.2f}")
        return result
    
    def _check_factual_consistency(
        self,
        sources: List[SourceCandidate],
        character: str
    ) -> float:
        """
        Check factual consistency across sources
        
        Args:
            sources: List of sources
            character: Character name
            
        Returns:
            Consistency score (0-1)
        """
        logger.debug("Checking factual consistency")
        
        # Extract facts from each source (limit to first 10 for efficiency)
        fact_sets = []
        for idx, source in enumerate(sources[:10]):
            # Get content from metadata or use title/author info
            content = self._get_source_content(source)
            if content:
                facts = self.fact_checker.extract_key_facts(content, character)
                # Set source index for each fact
                for fact in facts:
                    fact.source_index = idx
                fact_sets.append(facts)
        
        if len(fact_sets) < 2:
            logger.warning("Not enough sources with content for consistency check")
            return 0.7  # Default decent score
        
        # Build consistency matrix
        consistency_matrix = self._build_consistency_matrix(fact_sets)
        
        # Calculate weighted consistency score
        score = self._calculate_weighted_consistency_score(consistency_matrix)
        
        return score
    
    def _get_source_content(self, source: SourceCandidate) -> str:
        """
        Extract content from source for analysis
        
        Args:
            source: Source candidate
            
        Returns:
            Content string
        """
        # Try to get content from metadata
        if source.metadata and 'content' in source.metadata:
            return source.metadata['content']
        
        # Fall back to combining title and author
        content_parts = []
        if hasattr(source.source_item, 'title'):
            content_parts.append(source.source_item.title)
        if hasattr(source.source_item, 'author') and source.source_item.author:
            content_parts.append(f"Author: {source.source_item.author}")
        
        return " ".join(content_parts)
    
    def _build_consistency_matrix(
        self,
        fact_sets: List[List[KeyFact]]
    ) -> List[List[float]]:
        """
        Build matrix of consistency scores between fact sets
        
        Args:
            fact_sets: List of fact sets from different sources
            
        Returns:
            Matrix of consistency scores
        """
        n = len(fact_sets)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                score = self.fact_checker.compare_facts(fact_sets[i], fact_sets[j])
                matrix[i][j] = score
                matrix[j][i] = score
            matrix[i][i] = 1.0
        
        return matrix
    
    def _calculate_weighted_consistency_score(
        self,
        consistency_matrix: List[List[float]]
    ) -> float:
        """
        Calculate weighted consistency score from matrix
        
        Args:
            consistency_matrix: Matrix of pairwise consistency scores
            
        Returns:
            Overall consistency score (0-1)
        """
        if not consistency_matrix:
            return 0.5
        
        n = len(consistency_matrix)
        if n == 0:
            return 0.5
        
        # Calculate average of all pairwise comparisons
        total = 0.0
        count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                total += consistency_matrix[i][j]
                count += 1
        
        if count == 0:
            return 0.5
        
        return total / count
    
    def _analyze_temporal_coverage(
        self,
        sources: List[SourceCandidate],
        character: str
    ) -> float:
        """
        Analyze temporal coverage across sources
        
        Args:
            sources: List of sources
            character: Character name
            
        Returns:
            Temporal coverage score (0-1)
        """
        logger.debug("Analyzing temporal coverage")
        
        # Look for indicators of different life periods
        early_life_keywords = ['birth', 'childhood', 'early', 'youth', 'education', 'born']
        career_keywords = ['career', 'work', 'achievement', 'professional', 'developed']
        later_keywords = ['later', 'retirement', 'death', 'died', 'legacy', 'final']
        
        coverage = {
            'early_life': False,
            'career': False,
            'later_years': False
        }
        
        for source in sources:
            content = self._get_source_content(source).lower()
            
            if any(kw in content for kw in early_life_keywords):
                coverage['early_life'] = True
            if any(kw in content for kw in career_keywords):
                coverage['career'] = True
            if any(kw in content for kw in later_keywords):
                coverage['later_years'] = True
        
        # Calculate coverage score
        covered = sum(1 for v in coverage.values() if v)
        total = len(coverage)
        score = covered / total if total > 0 else 0.0
        
        return score
    
    def _calculate_source_diversity(
        self,
        sources: List[SourceCandidate]
    ) -> float:
        """
        Calculate diversity of sources
        
        Args:
            sources: List of sources
            
        Returns:
            Diversity score (0-1)
        """
        return self.source_triangulator.detect_source_diversity(sources)
    
    def _detect_information_redundancy(
        self,
        sources: List[SourceCandidate]
    ) -> RedundancyAnalysis:
        """
        Detect redundancy in information across sources
        
        Args:
            sources: List of sources
            
        Returns:
            RedundancyAnalysis
        """
        logger.debug("Detecting information redundancy")
        
        overlap = self.source_triangulator.calculate_source_overlap(sources)
        
        # Extract and compare content
        unique_content_ratio = 1.0 - overlap['overlap_score']
        
        return RedundancyAnalysis(
            redundancy_percentage=overlap['overlap_score'],
            unique_information_ratio=unique_content_ratio,
            overlapping_facts=overlap.get('redundant_sources', 0),
            unique_facts=overlap.get('unique_sources', len(sources)),
            details=f"Found {overlap.get('unique_sources', 0)} unique source domains"
        )
    
    def _verify_academic_standards(
        self,
        sources: List[SourceCandidate]
    ) -> AcademicStandards:
        """
        Verify academic standards compliance
        
        Args:
            sources: List of sources
            
        Returns:
            AcademicStandards
        """
        logger.debug("Verifying academic standards")
        
        # Count academic sources
        academic_domains = [
            '.edu', '.ac.', 'jstor', 'scholar', 'academia',
            'ieee', 'acm', 'springer', 'oxford', 'cambridge'
        ]
        
        peer_reviewed = 0
        primary_sources = 0
        academic_credibility = 0.0
        issues = []
        
        for source in sources:
            url = getattr(source.source_item, 'url', '') or ''
            url_lower = url.lower()
            
            # Check if academic
            is_academic = any(domain in url_lower for domain in academic_domains)
            if is_academic:
                peer_reviewed += 1
            
            # Check credibility score
            if source.credibility_score >= 90:
                primary_sources += 1
            
            academic_credibility += source.credibility_score
        
        # Calculate compliance
        if not sources:
            compliance = 0.0
        else:
            academic_credibility /= len(sources)
            academic_ratio = peer_reviewed / len(sources)
            compliance = (academic_ratio * 0.6 + (academic_credibility / 100) * 0.4)
        
        # Generate issues
        if peer_reviewed < len(sources) * 0.3:
            issues.append("Low percentage of peer-reviewed academic sources")
        if academic_credibility < 75:
            issues.append("Average academic credibility below recommended threshold")
        
        return AcademicStandards(
            compliance_score=compliance,
            citation_quality=academic_credibility,
            peer_reviewed_sources=peer_reviewed,
            primary_sources=primary_sources,
            academic_credibility=academic_credibility,
            issues=issues
        )
    
    def _calculate_overall_quality(
        self,
        consistency: float,
        temporal: float,
        diversity: float,
        redundancy: float,
        academic: float
    ) -> float:
        """
        Calculate overall quality score
        
        Args:
            consistency: Consistency score
            temporal: Temporal coverage score
            diversity: Diversity score
            redundancy: Redundancy level
            academic: Academic compliance score
            
        Returns:
            Overall quality score (0-1)
        """
        # Weight factors
        weights = {
            'consistency': 0.30,
            'temporal': 0.20,
            'diversity': 0.20,
            'redundancy': 0.15,  # Lower redundancy is better
            'academic': 0.15
        }
        
        # Invert redundancy (lower is better)
        redundancy_score = 1.0 - redundancy
        
        overall = (
            consistency * weights['consistency'] +
            temporal * weights['temporal'] +
            diversity * weights['diversity'] +
            redundancy_score * weights['redundancy'] +
            academic * weights['academic']
        )
        
        return overall
    
    def _generate_improvement_recommendations(
        self,
        sources: List[SourceCandidate],
        character: str,
        consistency: float,
        temporal: float,
        diversity: float,
        redundancy: RedundancyAnalysis
    ) -> List[str]:
        """
        Generate recommendations for improvement
        
        Args:
            sources: List of sources
            character: Character name
            consistency: Consistency score
            temporal: Temporal coverage score
            diversity: Diversity score
            redundancy: Redundancy analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check consistency
        if consistency < 0.8:
            recommendations.append(
                f"Consistency score ({consistency:.2f}) is below recommended threshold (0.8). "
                "Review sources for potential factual conflicts and remove questionable sources."
            )
        
        # Check temporal coverage
        if temporal < 0.7:
            recommendations.append(
                f"Temporal coverage ({temporal:.2f}) is below recommended threshold (0.7). "
                "Add sources covering different periods of the subject's life."
            )
        
        # Check diversity
        if diversity < 0.5:
            recommendations.append(
                f"Source diversity ({diversity:.2f}) is low. "
                "Include sources from different types (books, articles, archives) and domains."
            )
        
        # Check redundancy
        if redundancy.redundancy_percentage > 0.3:
            recommendations.append(
                f"Redundancy level ({redundancy.redundancy_percentage:.2f}) is above threshold (0.3). "
                "Consider removing duplicate or highly similar sources."
            )
        
        # Source count
        if len(sources) < 10:
            recommendations.append(
                f"Only {len(sources)} sources provided. "
                "Consider adding more sources for better coverage and validation."
            )
        
        # If everything is good
        if not recommendations:
            recommendations.append(
                "Source set quality is excellent. All validation criteria met."
            )
        
        return recommendations
    
    def _create_default_result(self) -> ValidationResult:
        """
        Create default validation result for empty input
        
        Returns:
            Default ValidationResult
        """
        return ValidationResult(
            consistency_score=0.0,
            temporal_coverage=0.0,
            diversity_score=0.0,
            redundancy_level=0.0,
            academic_compliance=0.0,
            overall_quality=0.0,
            recommendations=["No sources provided for validation"]
        )
