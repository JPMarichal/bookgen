"""
Tests for Quality Feedback System
Tests for feedback learning, pattern analysis, and continuous improvement
"""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.services.feedback_system import QualityFeedbackSystem, QualityTracker
from src.utils.pattern_analyzer import SuccessPatternAnalyzer
from src.models.quality_metrics import (
    BiographyQualityScore,
    SuccessPattern,
    SuccessCase,
    ImprovementMetrics,
    QualityWeights
)
from src.strategies.base_strategy import SourceCandidate
from src.api.models.sources import SourceItem, SourceType


class TestQualityMetricsModels:
    """Test quality metrics data models"""
    
    def test_biography_quality_score_creation(self):
        """Test BiographyQualityScore model creation"""
        score = BiographyQualityScore(
            overall_score=85.5,
            content_quality=90.0,
            factual_accuracy=88.0,
            source_quality=82.0
        )
        assert score.overall_score == 85.5
        assert score.content_quality == 90.0
        assert score.factual_accuracy == 88.0
    
    def test_success_pattern_creation(self):
        """Test SuccessPattern model creation"""
        pattern = SuccessPattern(
            pattern_type="domain",
            pattern_value="stanford.edu",
            frequency=5,
            avg_quality_impact=90.0,
            confidence=0.8
        )
        assert pattern.pattern_type == "domain"
        assert pattern.pattern_value == "stanford.edu"
        assert pattern.frequency == 5
    
    def test_quality_weights_validation(self):
        """Test QualityWeights validation"""
        weights = QualityWeights()
        assert weights.validate_weights()
        
        # Test normalization
        weights.domain_authority = 0.5
        weights.content_quality = 0.3
        weights.source_type = 0.1
        weights.recency = 0.05
        weights.citations = 0.05
        weights.normalize()
        assert weights.validate_weights()


class TestSuccessPatternAnalyzer:
    """Test SuccessPatternAnalyzer"""
    
    def test_initialization(self):
        """Test analyzer initialization"""
        analyzer = SuccessPatternAnalyzer()
        assert analyzer is not None
        assert analyzer.min_pattern_frequency == 2
    
    def test_identify_patterns_empty_sources(self):
        """Test pattern identification with empty sources"""
        analyzer = SuccessPatternAnalyzer()
        quality_score = BiographyQualityScore(overall_score=85.0)
        
        patterns = analyzer.identify_patterns([], "Einstein", quality_score)
        assert patterns == []
    
    def test_identify_domain_patterns(self):
        """Test domain pattern identification"""
        analyzer = SuccessPatternAnalyzer(min_pattern_frequency=2)
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title=f"Source {i}",
                    url=f"https://stanford.edu/einstein-{i}",
                    source_type=SourceType.ARTICLE
                ),
                quality_score=90.0
            )
            for i in range(3)
        ]
        
        quality_score = BiographyQualityScore(overall_score=88.0)
        patterns = analyzer.identify_patterns(sources, "Einstein", quality_score)
        
        # Should find stanford.edu as a pattern
        domain_patterns = [p for p in patterns if p.pattern_type == "domain"]
        assert len(domain_patterns) >= 1
        assert any(p.pattern_value == "stanford.edu" for p in domain_patterns)
    
    def test_identify_source_type_patterns(self):
        """Test source type pattern identification"""
        analyzer = SuccessPatternAnalyzer(min_pattern_frequency=2)
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title=f"Article Source {i}",
                    source_type=SourceType.ARTICLE
                ),
                quality_score=88.0
            )
            for i in range(3)
        ]
        
        quality_score = BiographyQualityScore(overall_score=90.0)
        patterns = analyzer.identify_patterns(sources, "Einstein", quality_score)
        
        # Should find ARTICLE as a pattern
        type_patterns = [p for p in patterns if p.pattern_type == "source_type"]
        assert len(type_patterns) >= 1
    
    def test_identify_quality_patterns(self):
        """Test quality threshold pattern identification"""
        analyzer = SuccessPatternAnalyzer(min_pattern_frequency=2)
        
        sources = [
            SourceCandidate(
                source_item=SourceItem(
                    title=f"High Quality Source {i}",
                    source_type=SourceType.ARTICLE
                ),
                quality_score=90.0
            )
            for i in range(3)
        ]
        
        quality_score = BiographyQualityScore(overall_score=92.0)
        patterns = analyzer.identify_patterns(sources, "Einstein", quality_score)
        
        # Should find high quality threshold pattern
        quality_patterns = [p for p in patterns if p.pattern_type == "quality_threshold"]
        assert len(quality_patterns) >= 1
    
    def test_aggregate_patterns(self):
        """Test pattern aggregation"""
        analyzer = SuccessPatternAnalyzer()
        
        # Create multiple pattern sets
        pattern_sets = [
            [
                SuccessPattern(
                    pattern_type="domain",
                    pattern_value="stanford.edu",
                    frequency=3,
                    avg_quality_impact=90.0,
                    confidence=0.8
                )
            ],
            [
                SuccessPattern(
                    pattern_type="domain",
                    pattern_value="stanford.edu",
                    frequency=2,
                    avg_quality_impact=92.0,
                    confidence=0.7
                )
            ]
        ]
        
        aggregated = analyzer.aggregate_patterns(pattern_sets)
        
        assert len(aggregated) == 1
        assert aggregated[0].pattern_value == "stanford.edu"
        assert aggregated[0].frequency == 5  # 3 + 2


class TestQualityTracker:
    """Test QualityTracker"""
    
    def test_initialization_with_temp_storage(self):
        """Test tracker initialization with temporary storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            tracker = QualityTracker(storage_path=str(storage_path))
            assert tracker is not None
            assert len(tracker.success_cases) == 0
    
    def test_store_and_load_success_case(self):
        """Test storing and loading success cases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            tracker = QualityTracker(storage_path=str(storage_path))
            
            # Store a success case
            sources = [
                SourceCandidate(
                    source_item=SourceItem(
                        title="Test Source",
                        source_type=SourceType.ARTICLE
                    ),
                    quality_score=90.0
                )
            ]
            patterns = [
                SuccessPattern(
                    pattern_type="domain",
                    pattern_value="test.edu",
                    frequency=1,
                    avg_quality_impact=90.0,
                    confidence=0.9
                )
            ]
            
            tracker.store_success_case(
                character="Einstein",
                sources=sources,
                patterns=patterns,
                quality_score=88.0
            )
            
            assert len(tracker.success_cases) == 1
            assert tracker.success_cases[0].character == "Einstein"
            
            # Create new tracker and verify data persists
            tracker2 = QualityTracker(storage_path=str(storage_path))
            assert len(tracker2.success_cases) == 1
            assert tracker2.success_cases[0].character == "Einstein"
    
    def test_get_recent_cases(self):
        """Test getting recent cases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            tracker = QualityTracker(storage_path=str(storage_path))
            
            # Add an old case
            old_case = SuccessCase(
                character="Old Person",
                quality_score=85.0,
                source_count=5,
                patterns=[],
                timestamp=datetime.now() - timedelta(days=40)
            )
            tracker.success_cases.append(old_case)
            
            # Add a recent case
            recent_case = SuccessCase(
                character="Recent Person",
                quality_score=90.0,
                source_count=6,
                patterns=[],
                timestamp=datetime.now()
            )
            tracker.success_cases.append(recent_case)
            
            # Get recent cases (last 30 days)
            recent = tracker.get_recent_cases(days=30)
            assert len(recent) == 1
            assert recent[0].character == "Recent Person"


class TestQualityFeedbackSystem:
    """Test QualityFeedbackSystem"""
    
    def test_initialization(self):
        """Test feedback system initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            assert system is not None
            assert system.quality_tracker is not None
            assert system.success_patterns is not None
    
    def test_learn_from_generation_success(self):
        """Test learning from successful generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            # Create test sources
            sources = [
                SourceCandidate(
                    source_item=SourceItem(
                        title="Stanford Einstein Biography",
                        url="https://stanford.edu/einstein",
                        source_type=SourceType.ARTICLE,
                        author="Dr. Smith"
                    ),
                    quality_score=90.0
                ),
                SourceCandidate(
                    source_item=SourceItem(
                        title="MIT Einstein Research",
                        url="https://mit.edu/einstein",
                        source_type=SourceType.ARTICLE,
                        author="Dr. Jones"
                    ),
                    quality_score=88.0
                ),
                SourceCandidate(
                    source_item=SourceItem(
                        title="Nobel Prize Einstein",
                        url="https://nobelprize.org/einstein",
                        source_type=SourceType.DOCUMENT,
                        author="Nobel Committee"
                    ),
                    quality_score=92.0
                )
            ]
            
            quality_score = BiographyQualityScore(
                overall_score=89.5,
                content_quality=90.0,
                factual_accuracy=92.0,
                source_quality=88.0
            )
            
            # Learn from this generation
            system.learn_from_generation_success(
                character="Einstein",
                sources=sources,
                quality_score=quality_score
            )
            
            # Verify a case was stored
            assert len(system.quality_tracker.success_cases) == 1
            case = system.quality_tracker.success_cases[0]
            assert case.character == "Einstein"
            assert case.quality_score == 89.5
            assert len(case.patterns) > 0
    
    def test_get_improvement_metrics_no_data(self):
        """Test getting metrics with no data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            metrics = system.get_improvement_metrics()
            assert isinstance(metrics, ImprovementMetrics)
            assert metrics.total_generations == 0
            assert metrics.avg_quality_score == 0.0
    
    def test_get_improvement_metrics_with_data(self):
        """Test getting metrics with data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            # Add some test cases
            for i in range(5):
                case = SuccessCase(
                    character=f"Person {i}",
                    quality_score=85.0 + i,
                    source_count=10,
                    patterns=[],
                    timestamp=datetime.now() - timedelta(days=i)
                )
                system.quality_tracker.success_cases.append(case)
            
            metrics = system.get_improvement_metrics()
            assert metrics.total_generations == 5
            assert metrics.avg_quality_score > 0
            assert 0.0 <= metrics.success_rate <= 1.0
    
    def test_get_strategy_recommendations(self):
        """Test getting strategy recommendations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            recommendations = system.get_strategy_recommendations()
            assert isinstance(recommendations, dict)
            assert 'quality_weights' in recommendations
            assert 'success_rate' in recommendations
            assert 'quality_trend' in recommendations
    
    def test_export_dashboard_data(self):
        """Test exporting dashboard data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            # Add a test case
            case = SuccessCase(
                character="Test Person",
                quality_score=88.0,
                source_count=8,
                patterns=[],
                timestamp=datetime.now()
            )
            system.quality_tracker.success_cases.append(case)
            
            dashboard = system.export_dashboard_data()
            assert isinstance(dashboard, dict)
            assert 'metrics' in dashboard
            assert 'time_series' in dashboard
            assert 'recommendations' in dashboard
            assert dashboard['total_cases'] == 1


class TestAcceptanceCriteria:
    """Test acceptance criteria from the issue"""
    
    def test_acceptance_criteria(self):
        """Test all acceptance criteria from the issue"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_tracking.json"
            feedback_system = QualityFeedbackSystem(storage_path=str(storage_path))
            
            # First, add some older generations with lower quality
            for j in range(6):
                older_sources = [
                    SourceCandidate(
                        source_item=SourceItem(
                            title=f"Older Source {i}",
                            url=f"https://old{i}.edu/person",
                            source_type=SourceType.ARTICLE
                        ),
                        quality_score=75.0 + i
                    )
                    for i in range(8)
                ]
                
                older_quality = BiographyQualityScore(
                    overall_score=75.0 + j,  # Lower quality initially
                    content_quality=76.0,
                    factual_accuracy=77.0
                )
                
                # Make these older by setting timestamp manually
                case = SuccessCase(
                    character=f"OldPerson {j}",
                    quality_score=older_quality.overall_score,
                    source_count=len(older_sources),
                    patterns=[],
                    timestamp=datetime.now() - timedelta(days=45)
                )
                feedback_system.quality_tracker.success_cases.append(case)
            
            # Then add recent generations with improving quality
            # Create high-quality sources for Einstein
            sources = [
                SourceCandidate(
                    source_item=SourceItem(
                        title=f"High Quality Einstein Source {i}",
                        url=f"https://university{i}.edu/einstein",
                        source_type=SourceType.ARTICLE,
                        author=f"Dr. Author {i}",
                        publication_date="2020"
                    ),
                    quality_score=90.0 + i,
                    relevance_score=0.95,
                    credibility_score=0.92
                )
                for i in range(12)
            ]
            
            biography_quality = BiographyQualityScore(
                overall_score=91.5,
                content_quality=92.0,
                factual_accuracy=93.0,
                source_quality=90.0,
                coherence_score=91.0,
                completeness_score=90.5
            )
            
            # Test the learning function
            feedback_system.learn_from_generation_success(
                character="Einstein",
                sources=sources,
                quality_score=biography_quality
            )
            
            # Add more recent generations with increasing quality
            for j in range(5):
                more_sources = [
                    SourceCandidate(
                        source_item=SourceItem(
                            title=f"Source {i}",
                            url=f"https://edu{i}.edu/person",
                            source_type=SourceType.ARTICLE
                        ),
                        quality_score=88.0 + j + i
                    )
                    for i in range(8)
                ]
                
                quality = BiographyQualityScore(
                    overall_score=88.0 + j * 2,  # Increasing quality
                    content_quality=89.0 + j * 2,
                    factual_accuracy=90.0 + j * 2
                )
                
                feedback_system.learn_from_generation_success(
                    character=f"Person {j}",
                    sources=more_sources,
                    quality_score=quality
                )
            
            # Test acceptance criteria: quality trend should be positive
            metrics = feedback_system.get_improvement_metrics()
            
            # The system must show improvement (recent vs older)
            assert metrics.quality_trend > 0, f"Quality trend must be positive (improving), got {metrics.quality_trend}"
            assert metrics.total_generations == 12  # 6 old + 1 Einstein + 5 new
            assert metrics.avg_quality_score > 0
            
            # Verify patterns were identified
            assert metrics.patterns_identified > 0
            
            # Verify recommendations are generated
            recommendations = feedback_system.get_strategy_recommendations()
            assert 'quality_weights' in recommendations
            assert 'top_patterns' in recommendations
            
            print(f"\n✅ Acceptance Criteria Met:")
            print(f"  - Quality trend: {metrics.quality_trend:+.2f} (positive = improving)")
            print(f"  - Total generations: {metrics.total_generations}")
            print(f"  - Average quality: {metrics.avg_quality_score:.2f}")
            print(f"  - Success rate: {metrics.success_rate:.2%}")
            print(f"  - Patterns identified: {metrics.patterns_identified}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
