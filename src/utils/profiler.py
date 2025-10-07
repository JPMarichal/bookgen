"""
Performance profiler for monitoring system performance metrics.

Provides context manager for profiling memory usage, database queries,
cache hit ratios, and CPU usage during biography generation.
"""
import time
import psutil
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    memory_peak: float = 0.0  # Peak memory in bytes
    memory_start: float = 0.0  # Starting memory in bytes
    memory_end: float = 0.0  # Ending memory in bytes
    db_queries: List[float] = field(default_factory=list)  # Query times in seconds
    cache_hits: int = 0
    cache_misses: int = 0
    cpu_percent: float = 0.0  # Average CPU usage
    duration: float = 0.0  # Total duration in seconds
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def db_query_avg(self) -> float:
        """Average database query time in seconds"""
        if not self.db_queries:
            return 0.0
        return sum(self.db_queries) / len(self.db_queries)
    
    @property
    def cache_hit_ratio(self) -> float:
        """Cache hit ratio (0.0 to 1.0)"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    @property
    def memory_increase(self) -> float:
        """Memory increase during profiling in bytes"""
        return self.memory_end - self.memory_start


class PerformanceProfiler:
    """
    Context manager for profiling performance metrics.
    
    Usage:
        with performance_profile() as prof:
            # Code to profile
            engine.generate_biography("character_name")
        
        print(f"Memory peak: {prof.memory_peak / 1024**3:.2f} GB")
        print(f"DB query avg: {prof.db_query_avg * 1000:.2f} ms")
        print(f"Cache hit ratio: {prof.cache_hit_ratio:.2%}")
    """
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.process = psutil.Process()
        self._db_query_start: Optional[float] = None
        
    def __enter__(self):
        """Start profiling"""
        self.metrics.start_time = time.time()
        self.metrics.memory_start = self.process.memory_info().rss
        self.metrics.memory_peak = self.metrics.memory_start
        logger.info("Performance profiling started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End profiling"""
        self.metrics.end_time = time.time()
        self.metrics.duration = self.metrics.end_time - self.metrics.start_time
        self.metrics.memory_end = self.process.memory_info().rss
        self.metrics.cpu_percent = self.process.cpu_percent()
        
        logger.info(
            f"Performance profiling completed: "
            f"Duration={self.metrics.duration:.2f}s, "
            f"Memory peak={self.metrics.memory_peak / 1024**3:.3f}GB, "
            f"DB avg={self.metrics.db_query_avg * 1000:.2f}ms, "
            f"Cache hit ratio={self.metrics.cache_hit_ratio:.2%}"
        )
        return False
    
    def record_db_query(self, query_time: float):
        """
        Record a database query time.
        
        Args:
            query_time: Query duration in seconds
        """
        self.metrics.db_queries.append(query_time)
    
    def start_db_query(self):
        """Start timing a database query"""
        self._db_query_start = time.time()
    
    def end_db_query(self):
        """End timing a database query and record it"""
        if self._db_query_start is not None:
            query_time = time.time() - self._db_query_start
            self.record_db_query(query_time)
            self._db_query_start = None
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.metrics.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.metrics.cache_misses += 1
    
    def update_memory_peak(self):
        """Update peak memory usage"""
        current_memory = self.process.memory_info().rss
        if current_memory > self.metrics.memory_peak:
            self.metrics.memory_peak = current_memory
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current metrics"""
        return self.metrics
    
    @property
    def memory_peak(self) -> float:
        """Peak memory in bytes"""
        return self.metrics.memory_peak
    
    @property
    def db_query_avg(self) -> float:
        """Average DB query time in seconds"""
        return self.metrics.db_query_avg
    
    @property
    def cache_hit_ratio(self) -> float:
        """Cache hit ratio (0.0 to 1.0)"""
        return self.metrics.cache_hit_ratio


@contextmanager
def performance_profile():
    """
    Context manager for performance profiling.
    
    Yields:
        PerformanceProfiler instance
        
    Example:
        with performance_profile() as prof:
            # Code to profile
            result = expensive_operation()
        
        assert prof.memory_peak < 1.5 * 1024**3  # 1.5GB
        assert prof.db_query_avg < 0.1  # 100ms
        assert prof.cache_hit_ratio > 0.8  # 80%
    """
    profiler = PerformanceProfiler()
    with profiler:
        yield profiler


def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics.
    
    Returns:
        Dictionary with system metrics including CPU, memory, disk usage
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'cpu_percent': process.cpu_percent(interval=0.1),
        'memory_rss': memory_info.rss,
        'memory_vms': memory_info.vms,
        'memory_percent': process.memory_percent(),
        'num_threads': process.num_threads(),
        'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
    }
