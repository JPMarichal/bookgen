"""
Tests for performance profiler.
"""
import pytest
import time
from src.utils.profiler import (
    PerformanceProfiler,
    performance_profile,
    get_system_metrics,
    PerformanceMetrics,
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization with defaults"""
        metrics = PerformanceMetrics()
        assert metrics.memory_peak == 0.0
        assert metrics.db_queries == []
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
    
    def test_db_query_avg_empty(self):
        """Test average with no queries"""
        metrics = PerformanceMetrics()
        assert metrics.db_query_avg == 0.0
    
    def test_db_query_avg_with_queries(self):
        """Test average with queries"""
        metrics = PerformanceMetrics()
        metrics.db_queries = [0.1, 0.2, 0.3]
        assert abs(metrics.db_query_avg - 0.2) < 0.001
    
    def test_cache_hit_ratio_no_requests(self):
        """Test cache hit ratio with no requests"""
        metrics = PerformanceMetrics()
        assert metrics.cache_hit_ratio == 0.0
    
    def test_cache_hit_ratio_with_hits(self):
        """Test cache hit ratio calculation"""
        metrics = PerformanceMetrics()
        metrics.cache_hits = 80
        metrics.cache_misses = 20
        assert metrics.cache_hit_ratio == 0.8
    
    def test_memory_increase(self):
        """Test memory increase calculation"""
        metrics = PerformanceMetrics()
        metrics.memory_start = 100 * 1024 * 1024  # 100MB
        metrics.memory_end = 150 * 1024 * 1024    # 150MB
        assert metrics.memory_increase == 50 * 1024 * 1024  # 50MB


class TestPerformanceProfiler:
    """Test PerformanceProfiler class"""
    
    def test_profiler_context_manager(self):
        """Test profiler as context manager"""
        profiler = PerformanceProfiler()
        
        with profiler:
            # Simulate some work
            time.sleep(0.1)
        
        # Check that metrics were recorded
        assert profiler.metrics.duration >= 0.1
        assert profiler.metrics.memory_start > 0
        assert profiler.metrics.memory_end > 0
    
    def test_record_db_query(self):
        """Test recording database query times"""
        profiler = PerformanceProfiler()
        
        profiler.record_db_query(0.05)
        profiler.record_db_query(0.15)
        
        assert len(profiler.metrics.db_queries) == 2
        assert profiler.db_query_avg == 0.1
    
    def test_db_query_timing(self):
        """Test start/end db query timing"""
        profiler = PerformanceProfiler()
        
        profiler.start_db_query()
        time.sleep(0.05)
        profiler.end_db_query()
        
        assert len(profiler.metrics.db_queries) == 1
        assert profiler.metrics.db_queries[0] >= 0.05
    
    def test_cache_hit_recording(self):
        """Test cache hit/miss recording"""
        profiler = PerformanceProfiler()
        
        profiler.record_cache_hit()
        profiler.record_cache_hit()
        profiler.record_cache_miss()
        
        assert profiler.metrics.cache_hits == 2
        assert profiler.metrics.cache_misses == 1
        assert profiler.cache_hit_ratio == 2/3
    
    def test_memory_peak_tracking(self):
        """Test memory peak tracking"""
        profiler = PerformanceProfiler()
        
        with profiler:
            # Initial memory
            initial_peak = profiler.memory_peak
            
            # Allocate some memory
            data = [0] * 1000000  # Large list
            profiler.update_memory_peak()
            
            # Peak should have increased
            assert profiler.memory_peak >= initial_peak


class TestPerformanceProfileFunction:
    """Test performance_profile function"""
    
    def test_performance_profile_context(self):
        """Test performance_profile context manager function"""
        with performance_profile() as prof:
            # Simulate some work
            time.sleep(0.05)
            prof.record_cache_hit()
            prof.record_cache_hit()
            prof.record_cache_miss()
        
        # Check metrics were recorded
        assert prof.metrics.duration >= 0.05
        assert prof.cache_hit_ratio > 0.5
    
    def test_acceptance_criteria_verification(self):
        """Test that profiler can verify acceptance criteria"""
        with performance_profile() as prof:
            # Simulate good performance
            prof.record_db_query(0.05)  # 50ms - under 100ms
            prof.record_db_query(0.08)  # 80ms - under 100ms
            
            # Simulate good cache performance
            for _ in range(85):
                prof.record_cache_hit()
            for _ in range(15):
                prof.record_cache_miss()
        
        # Verify acceptance criteria
        assert prof.db_query_avg < 0.1, "DB queries should be < 100ms"
        assert prof.cache_hit_ratio > 0.8, "Cache hit ratio should be > 80%"
        assert prof.memory_peak < 1.5 * 1024**3, "Memory should be < 1.5GB"
    
    def test_profiler_with_slow_queries(self):
        """Test profiler detects slow queries"""
        with performance_profile() as prof:
            # Simulate slow queries
            prof.record_db_query(0.15)  # 150ms - over 100ms
            prof.record_db_query(0.20)  # 200ms - over 100ms
        
        # Average should be over threshold
        assert prof.db_query_avg > 0.1


class TestSystemMetrics:
    """Test get_system_metrics function"""
    
    def test_get_system_metrics(self):
        """Test getting system metrics"""
        metrics = get_system_metrics()
        
        # Check all expected keys are present
        assert 'cpu_percent' in metrics
        assert 'memory_rss' in metrics
        assert 'memory_vms' in metrics
        assert 'memory_percent' in metrics
        assert 'num_threads' in metrics
        
        # Check values are reasonable
        assert metrics['cpu_percent'] >= 0
        assert metrics['memory_rss'] > 0
        assert metrics['memory_percent'] >= 0


class TestAcceptanceCriteria:
    """Test acceptance criteria from Issue #16"""
    
    def test_profiler_meets_requirements(self):
        """Test that profiler can measure all required metrics"""
        with performance_profile() as prof:
            # Simulate biography generation with good performance
            
            # Database queries under 100ms
            for _ in range(10):
                prof.record_db_query(0.08)  # 80ms each
            
            # Cache hit ratio over 80%
            for _ in range(85):
                prof.record_cache_hit()
            for _ in range(15):
                prof.record_cache_miss()
            
            # Memory tracking
            prof.update_memory_peak()
        
        # Verify all acceptance criteria
        assert prof.db_query_avg < 0.1, "Queries should average < 100ms"
        assert prof.cache_hit_ratio > 0.8, "Cache hit ratio should be > 80%"
        assert prof.memory_peak < 1.5 * 1024**3, "Memory peak should be < 1.5GB"
        
        # Additional checks
        assert len(prof.metrics.db_queries) == 10
        assert prof.metrics.cache_hits == 85
        assert prof.metrics.cache_misses == 15
