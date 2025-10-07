"""
Database query optimization utilities.

Provides utilities for optimizing database queries, including
connection pooling, query batching, and lazy loading.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from contextlib import contextmanager
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, inspect
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QueryOptimizer:
    """
    Utilities for optimizing database queries.
    
    Features:
    - Query timing and logging
    - Batch operations
    - Eager loading helpers
    - Query caching integration
    """
    
    def __init__(self, db: Session):
        """
        Initialize query optimizer.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self._query_times: List[float] = []
    
    @contextmanager
    def time_query(self, query_name: str = "query"):
        """
        Context manager for timing database queries.
        
        Args:
            query_name: Name for logging
            
        Yields:
            None
            
        Example:
            with optimizer.time_query("get_biographies"):
                results = db.query(Biography).all()
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            self._query_times.append(elapsed)
            if elapsed > 0.1:  # Log slow queries (>100ms)
                logger.warning(f"Slow query '{query_name}': {elapsed*1000:.2f}ms")
            else:
                logger.debug(f"Query '{query_name}': {elapsed*1000:.2f}ms")
    
    def get_average_query_time(self) -> float:
        """
        Get average query time in seconds.
        
        Returns:
            Average query time
        """
        if not self._query_times:
            return 0.0
        return sum(self._query_times) / len(self._query_times)
    
    def reset_stats(self):
        """Reset query statistics"""
        self._query_times.clear()
    
    def batch_insert(self, objects: List[Any], batch_size: int = 100) -> int:
        """
        Insert objects in batches for better performance.
        
        Args:
            objects: List of objects to insert
            batch_size: Number of objects per batch
            
        Returns:
            Number of objects inserted
        """
        count = 0
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            with self.time_query(f"batch_insert_{i//batch_size}"):
                self.db.add_all(batch)
                self.db.flush()
                count += len(batch)
        
        self.db.commit()
        logger.info(f"Batch inserted {count} objects in {len(objects)//batch_size + 1} batches")
        return count
    
    def batch_update(
        self,
        model_class: type,
        updates: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Update objects in batches.
        
        Args:
            model_class: SQLAlchemy model class
            updates: List of dictionaries with 'id' and fields to update
            batch_size: Number of updates per batch
            
        Returns:
            Number of objects updated
        """
        count = 0
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            with self.time_query(f"batch_update_{i//batch_size}"):
                for update_data in batch:
                    obj_id = update_data.pop('id')
                    self.db.query(model_class).filter(
                        model_class.id == obj_id
                    ).update(update_data)
                    count += 1
                self.db.flush()
        
        self.db.commit()
        logger.info(f"Batch updated {count} objects")
        return count


class LazyLoader(Generic[T]):
    """
    Lazy loader for heavy content to reduce memory usage.
    
    Example:
        loader = LazyLoader(lambda: expensive_computation())
        # Not computed yet
        result = loader.value  # Computed on first access
        result2 = loader.value  # Cached, not recomputed
    """
    
    def __init__(self, load_func: Callable[[], T]):
        """
        Initialize lazy loader.
        
        Args:
            load_func: Function to call when loading value
        """
        self._load_func = load_func
        self._value: Optional[T] = None
        self._loaded = False
    
    @property
    def value(self) -> T:
        """
        Get value, loading if necessary.
        
        Returns:
            Loaded value
        """
        if not self._loaded:
            self._value = self._load_func()
            self._loaded = True
        return self._value
    
    @property
    def is_loaded(self) -> bool:
        """Check if value has been loaded"""
        return self._loaded
    
    def reset(self):
        """Reset loader to unloaded state"""
        self._value = None
        self._loaded = False


def with_eager_loading(query, *relationships):
    """
    Add eager loading to query to avoid N+1 queries.
    
    Args:
        query: SQLAlchemy query
        *relationships: Relationship attributes to eager load
        
    Returns:
        Query with eager loading options
        
    Example:
        query = db.query(Biography)
        query = with_eager_loading(query, Biography.chapters, Biography.jobs)
    """
    for relationship in relationships:
        query = query.options(joinedload(relationship))
    return query


def with_selectin_loading(query, *relationships):
    """
    Add selectin loading to query for better performance with collections.
    
    Args:
        query: SQLAlchemy query
        *relationships: Relationship attributes to load
        
    Returns:
        Query with selectin loading options
        
    Example:
        query = db.query(Biography)
        query = with_selectin_loading(query, Biography.chapters)
    """
    for relationship in relationships:
        query = query.options(selectinload(relationship))
    return query


class ConnectionPool:
    """
    Helper for managing database connection pooling.
    
    Note: Most connection pooling is configured in database config,
    but this provides utilities for monitoring and managing connections.
    """
    
    @staticmethod
    def get_pool_status(engine) -> Dict[str, Any]:
        """
        Get connection pool status.
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Dictionary with pool statistics
        """
        pool = engine.pool
        status = {}
        
        # Try to get pool size
        try:
            size = pool.size() if callable(getattr(pool, 'size', None)) else getattr(pool, 'size', 0)
            status['pool_size'] = size
        except (AttributeError, TypeError):
            status['pool_size'] = 0
        
        # Try to get checked in/out connections (not all pools support this)
        try:
            checkedin = pool.checkedin() if callable(getattr(pool, 'checkedin', None)) else getattr(pool, 'checkedin', 0)
            status['checked_in'] = checkedin
        except (AttributeError, TypeError):
            status['checked_in'] = 0
        
        try:
            checkedout = pool.checkedout() if callable(getattr(pool, 'checkedout', None)) else getattr(pool, 'checkedout', 0)
            status['checked_out'] = checkedout
        except (AttributeError, TypeError):
            status['checked_out'] = 0
        
        try:
            overflow = pool.overflow() if callable(getattr(pool, 'overflow', None)) else getattr(pool, 'overflow', 0)
            status['overflow'] = overflow
        except (AttributeError, TypeError):
            status['overflow'] = 0
        
        status['total_connections'] = status['pool_size'] + status['overflow']
        
        return status
    
    @staticmethod
    def optimize_pool_size(engine, target_concurrency: int = 10):
        """
        Provide recommendations for pool size optimization.
        
        Args:
            engine: SQLAlchemy engine
            target_concurrency: Expected concurrent connections
            
        Returns:
            Dictionary with recommendations
        """
        pool = engine.pool
        
        # Try to get current pool configuration
        try:
            current_size = pool.size() if callable(getattr(pool, 'size', None)) else getattr(pool, 'size', 0)
        except (AttributeError, TypeError):
            current_size = 0
        
        try:
            current_overflow = pool.overflow() if callable(getattr(pool, 'overflow', None)) else getattr(pool, 'overflow', 0)
        except (AttributeError, TypeError):
            current_overflow = 0
        
        recommended_size = max(10, target_concurrency)
        recommended_overflow = max(20, target_concurrency * 2)
        
        return {
            'current_pool_size': current_size,
            'current_max_overflow': current_overflow,
            'recommended_pool_size': recommended_size,
            'recommended_max_overflow': recommended_overflow,
            'notes': (
                f"For {target_concurrency} concurrent users, "
                f"recommend pool_size={recommended_size}, "
                f"max_overflow={recommended_overflow}"
            )
        }


def enable_query_logging(engine, threshold_ms: float = 100.0):
    """
    Enable logging for slow queries.
    
    Args:
        engine: SQLAlchemy engine
        threshold_ms: Log queries slower than this (in milliseconds)
    """
    from sqlalchemy import event
    
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total_time = time.time() - conn.info['query_start_time'].pop()
        if total_time * 1000 > threshold_ms:
            logger.warning(
                f"Slow query ({total_time*1000:.2f}ms): {statement[:200]}"
            )


def optimize_for_read_heavy():
    """
    Configuration suggestions for read-heavy workloads.
    
    Returns:
        Dictionary with optimization suggestions
    """
    return {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': False,
        'notes': [
            'Use larger connection pool for read-heavy workloads',
            'Enable pool_pre_ping to detect stale connections',
            'Use selectinload for collections to reduce N+1 queries',
            'Consider read replicas for scaling',
            'Enable query result caching with Redis',
        ]
    }


def optimize_for_write_heavy():
    """
    Configuration suggestions for write-heavy workloads.
    
    Returns:
        Dictionary with optimization suggestions
    """
    return {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 1800,
        'echo': False,
        'notes': [
            'Use moderate connection pool for write-heavy workloads',
            'Batch INSERT/UPDATE operations when possible',
            'Use bulk operations for better performance',
            'Consider write-ahead logging (WAL) for PostgreSQL',
            'Monitor for lock contention',
        ]
    }
