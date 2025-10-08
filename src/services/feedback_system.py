"""
Quality Feedback System for continuous improvement
System that learns from successful generations to improve future searches
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..strategies.base_strategy import SourceCandidate
from ..models.quality_metrics import (
    BiographyQualityScore,
    SuccessCase,
    SuccessPattern,
    ImprovementMetrics,
    QualityWeights
)
from ..utils.pattern_analyzer import SuccessPatternAnalyzer

logger = logging.getLogger(__name__)


class QualityTracker:
    """Tracks quality data and success cases"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize quality tracker
        
        Args:
            storage_path: Path to store success cases (defaults to data/quality_tracking.json)
        """
        if storage_path is None:
            storage_path = "data/quality_tracking.json"
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.success_cases: List[SuccessCase] = []
        self._load_cases()
        logger.info(f"Initialized QualityTracker with {len(self.success_cases)} existing cases")
    
    def _load_cases(self):
        """Load success cases from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.success_cases = [
                        SuccessCase(**case) for case in data.get('cases', [])
                    ]
                logger.info(f"Loaded {len(self.success_cases)} cases from storage")
            except Exception as e:
                logger.error(f"Failed to load cases: {e}")
                self.success_cases = []
    
    def _save_cases(self):
        """Save success cases to storage"""
        try:
            data = {
                'cases': [case.model_dump(mode='json') for case in self.success_cases],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.success_cases)} cases to storage")
        except Exception as e:
            logger.error(f"Failed to save cases: {e}")
    
    def store_success_case(
        self,
        character: str,
        sources: List[SourceCandidate],
        patterns: List[SuccessPattern],
        quality_score: float
    ):
        """
        Store a successful generation case
        
        Args:
            character: Character name
            sources: Source candidates used
            patterns: Patterns identified
            quality_score: Quality score achieved
        """
        case = SuccessCase(
            character=character,
            quality_score=quality_score,
            source_count=len(sources),
            patterns=patterns,
            timestamp=datetime.now()
        )
        self.success_cases.append(case)
        self._save_cases()
        logger.info(f"Stored success case for {character} with score {quality_score}")
    
    def get_recent_cases(self, days: int = 30) -> List[SuccessCase]:
        """
        Get recent success cases
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent success cases
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            case for case in self.success_cases
            if case.timestamp >= cutoff
        ]
        logger.debug(f"Found {len(recent)} cases in last {days} days")
        return recent
    
    def get_all_cases(self) -> List[SuccessCase]:
        """Get all success cases"""
        return self.success_cases


class QualityFeedbackSystem:
    """System for continuous quality improvement based on feedback"""
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        min_pattern_frequency: int = 2
    ):
        """
        Initialize feedback system
        
        Args:
            storage_path: Path to store quality tracking data
            min_pattern_frequency: Minimum frequency for pattern detection
        """
        self.quality_tracker = QualityTracker(storage_path)
        self.success_patterns = SuccessPatternAnalyzer(min_pattern_frequency)
        self.quality_weights = QualityWeights()
        self._strategy_adjustments: Dict[str, Any] = {}
        logger.info("Initialized QualityFeedbackSystem")
    
    def learn_from_generation_success(
        self,
        character: str,
        sources: List[SourceCandidate],
        quality_score: BiographyQualityScore
    ):
        """
        Learn from a successful generation to improve future searches
        
        Args:
            character: Character name
            sources: Generated source candidates
            quality_score: Quality score of the biography
        """
        logger.info(f"Learning from generation of {character} (score: {quality_score.overall_score})")
        
        # Identify high-quality sources (>= 85)
        high_quality_sources = [s for s in sources if s.quality_score >= 85]
        logger.debug(f"Found {len(high_quality_sources)} high-quality sources")
        
        # Analyze patterns in successful sources
        common_patterns = self.success_patterns.identify_patterns(
            high_quality_sources if high_quality_sources else sources,
            character,
            quality_score
        )
        
        # Update search strategies and quality weights
        self._update_search_strategies(common_patterns)
        self._update_quality_weights(common_patterns)
        
        # Store for future analysis
        self.quality_tracker.store_success_case(
            character=character,
            sources=sources,
            patterns=common_patterns,
            quality_score=quality_score.overall_score
        )
        
        logger.info(f"Successfully learned from generation, identified {len(common_patterns)} patterns")
    
    def _update_search_strategies(self, patterns: List[SuccessPattern]):
        """
        Update search strategies based on identified patterns
        
        Args:
            patterns: Identified success patterns
        """
        logger.debug("Updating search strategies")
        
        # Group patterns by type
        domain_patterns = [p for p in patterns if p.pattern_type == "domain"]
        type_patterns = [p for p in patterns if p.pattern_type == "source_type"]
        
        # Store strategy adjustments
        if domain_patterns:
            # Prioritize domains that appear in successful patterns
            priority_domains = [
                p.pattern_value for p in domain_patterns
                if p.confidence >= 0.5
            ]
            self._strategy_adjustments['priority_domains'] = priority_domains
            logger.debug(f"Updated priority domains: {priority_domains}")
        
        if type_patterns:
            # Prioritize source types that appear in successful patterns
            priority_types = [
                p.pattern_value for p in type_patterns
                if p.confidence >= 0.5
            ]
            self._strategy_adjustments['priority_source_types'] = priority_types
            logger.debug(f"Updated priority source types: {priority_types}")
    
    def _update_quality_weights(self, patterns: List[SuccessPattern]):
        """
        Update quality scoring weights based on patterns
        
        Args:
            patterns: Identified success patterns
        """
        logger.debug("Updating quality weights")
        
        # Analyze which factors contribute most to success
        quality_patterns = [p for p in patterns if p.pattern_type == "quality_threshold"]
        metadata_patterns = [p for p in patterns if p.pattern_type == "metadata_feature"]
        
        # Adjust weights based on pattern significance
        if quality_patterns:
            # If high-quality sources are significant, increase content quality weight
            avg_confidence = sum(p.confidence for p in quality_patterns) / len(quality_patterns)
            if avg_confidence > 0.7:
                self.quality_weights.content_quality = min(0.35, self.quality_weights.content_quality + 0.05)
                logger.debug("Increased content quality weight")
        
        if metadata_patterns:
            # If metadata features are significant, adjust related weights
            has_citations = any(p.pattern_value == "has_publisher" for p in metadata_patterns)
            if has_citations:
                self.quality_weights.citations = min(0.20, self.quality_weights.citations + 0.03)
                logger.debug("Increased citations weight")
        
        # Normalize weights to sum to 1.0
        self.quality_weights.normalize()
    
    def get_improvement_metrics(self, lookback_days: int = 30) -> ImprovementMetrics:
        """
        Get metrics showing system improvement over time
        
        Args:
            lookback_days: Number of days to analyze
            
        Returns:
            Improvement metrics
        """
        logger.debug(f"Calculating improvement metrics for last {lookback_days} days")
        
        recent_cases = self.quality_tracker.get_recent_cases(lookback_days)
        all_cases = self.quality_tracker.get_all_cases()
        
        if not all_cases:
            logger.warning("No cases available for metrics calculation")
            return ImprovementMetrics(
                total_generations=0,
                avg_quality_score=0.0,
                quality_trend=0.0,
                success_rate=0.0,
                patterns_identified=0
            )
        
        # Calculate basic metrics
        total_generations = len(all_cases)
        avg_quality = sum(c.quality_score for c in all_cases) / len(all_cases)
        success_rate = sum(1 for c in all_cases if c.quality_score >= 85) / len(all_cases)
        
        # Calculate quality trend (compare recent vs older)
        if len(all_cases) >= 10:
            recent_avg = sum(c.quality_score for c in recent_cases) / max(1, len(recent_cases))
            older_cases = [c for c in all_cases if c not in recent_cases]
            older_avg = sum(c.quality_score for c in older_cases) / max(1, len(older_cases))
            quality_trend = recent_avg - older_avg
        else:
            quality_trend = 0.0
        
        # Aggregate patterns from all cases
        all_patterns = [case.patterns for case in all_cases]
        aggregated_patterns = self.success_patterns.aggregate_patterns(all_patterns)
        
        # Get most effective patterns (top 5)
        most_effective = sorted(
            aggregated_patterns,
            key=lambda p: p.avg_quality_impact * p.confidence,
            reverse=True
        )[:5]
        
        metrics = ImprovementMetrics(
            total_generations=total_generations,
            avg_quality_score=avg_quality,
            quality_trend=quality_trend,
            success_rate=success_rate,
            patterns_identified=len(aggregated_patterns),
            most_effective_patterns=most_effective,
            timestamp=datetime.now()
        )
        
        logger.info(f"Calculated metrics: {total_generations} generations, "
                   f"avg quality {avg_quality:.1f}, trend {quality_trend:+.1f}")
        
        return metrics
    
    def get_strategy_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for search strategy adjustments
        
        Returns:
            Dictionary of strategy recommendations
        """
        logger.debug("Generating strategy recommendations")
        
        metrics = self.get_improvement_metrics()
        
        recommendations = {
            'priority_domains': self._strategy_adjustments.get('priority_domains', []),
            'priority_source_types': self._strategy_adjustments.get('priority_source_types', []),
            'quality_weights': self.quality_weights.model_dump(),
            'top_patterns': [p.model_dump() for p in metrics.most_effective_patterns],
            'success_rate': metrics.success_rate,
            'quality_trend': metrics.quality_trend
        }
        
        return recommendations
    
    def export_dashboard_data(self) -> Dict[str, Any]:
        """
        Export data for quality dashboard visualization
        
        Returns:
            Dashboard data including metrics and trends
        """
        logger.debug("Exporting dashboard data")
        
        metrics = self.get_improvement_metrics()
        all_cases = self.quality_tracker.get_all_cases()
        
        # Prepare time series data
        time_series = []
        for case in sorted(all_cases, key=lambda c: c.timestamp):
            time_series.append({
                'timestamp': case.timestamp.isoformat(),
                'character': case.character,
                'quality_score': case.quality_score,
                'source_count': case.source_count
            })
        
        dashboard_data = {
            'metrics': metrics.model_dump(mode='json'),
            'time_series': time_series,
            'recommendations': self.get_strategy_recommendations(),
            'total_cases': len(all_cases),
            'generated_at': datetime.now().isoformat()
        }
        
        return dashboard_data
