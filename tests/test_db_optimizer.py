"""
Tests for database optimizer.
"""
import pytest
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from src.database.base import Base
from src.optimizations.db_optimizer import (
    QueryOptimizer,
    LazyLoader,
    ConnectionPool,
    with_eager_loading,
    with_selectin_loading,
    optimize_for_read_heavy,
    optimize_for_write_heavy,
)


# Test model for database operations
class TestModel(Base):
    __tablename__ = 'test_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    value = Column(Integer)


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


class TestQueryOptimizer:
    """Test QueryOptimizer class"""
    
    def test_time_query(self, test_db):
        """Test query timing"""
        optimizer = QueryOptimizer(test_db)
        
        with optimizer.time_query("test_query"):
            time.sleep(0.05)
        
        assert len(optimizer._query_times) == 1
        assert optimizer._query_times[0] >= 0.05
    
    def test_average_query_time(self, test_db):
        """Test average query time calculation"""
        optimizer = QueryOptimizer(test_db)
        
        optimizer._query_times = [0.1, 0.2, 0.3]
        assert abs(optimizer.get_average_query_time() - 0.2) < 0.001
    
    def test_average_query_time_empty(self, test_db):
        """Test average with no queries"""
        optimizer = QueryOptimizer(test_db)
        assert optimizer.get_average_query_time() == 0.0
    
    def test_reset_stats(self, test_db):
        """Test resetting statistics"""
        optimizer = QueryOptimizer(test_db)
        optimizer._query_times = [0.1, 0.2]
        
        optimizer.reset_stats()
        
        assert len(optimizer._query_times) == 0
    
    def test_batch_insert(self, test_db):
        """Test batch insert operation"""
        optimizer = QueryOptimizer(test_db)
        
        # Create test objects
        objects = [
            TestModel(name=f"item_{i}", value=i)
            for i in range(25)
        ]
        
        count = optimizer.batch_insert(objects, batch_size=10)
        
        assert count == 25
        
        # Verify all objects were inserted
        result = test_db.query(TestModel).count()
        assert result == 25
    
    def test_batch_update(self, test_db):
        """Test batch update operation"""
        # First insert some test data
        for i in range(10):
            test_db.add(TestModel(name=f"item_{i}", value=i))
        test_db.commit()
        
        optimizer = QueryOptimizer(test_db)
        
        # Prepare updates
        items = test_db.query(TestModel).all()
        updates = [
            {"id": item.id, "value": item.value * 2}
            for item in items
        ]
        
        count = optimizer.batch_update(TestModel, updates, batch_size=5)
        
        assert count == 10
        
        # Verify updates
        updated_items = test_db.query(TestModel).all()
        for i, item in enumerate(updated_items):
            assert item.value == i * 2


class TestLazyLoader:
    """Test LazyLoader class"""
    
    def test_lazy_loading(self):
        """Test that value is not loaded until accessed"""
        call_count = 0
        
        def expensive_load():
            nonlocal call_count
            call_count += 1
            time.sleep(0.05)
            return "expensive_value"
        
        loader = LazyLoader(expensive_load)
        
        # Not loaded yet
        assert not loader.is_loaded
        assert call_count == 0
        
        # Access value - should load
        value = loader.value
        assert value == "expensive_value"
        assert loader.is_loaded
        assert call_count == 1
        
        # Access again - should not reload
        value2 = loader.value
        assert value2 == "expensive_value"
        assert call_count == 1  # Still only called once
    
    def test_lazy_loader_reset(self):
        """Test resetting lazy loader"""
        call_count = 0
        
        def load_func():
            nonlocal call_count
            call_count += 1
            return f"value_{call_count}"
        
        loader = LazyLoader(load_func)
        
        # Load first time
        value1 = loader.value
        assert value1 == "value_1"
        
        # Reset and load again
        loader.reset()
        assert not loader.is_loaded
        
        value2 = loader.value
        assert value2 == "value_2"
        assert call_count == 2


class TestConnectionPool:
    """Test ConnectionPool utilities"""
    
    def test_get_pool_status(self):
        """Test getting pool status"""
        engine = create_engine("sqlite:///:memory:")
        
        status = ConnectionPool.get_pool_status(engine)
        
        assert 'pool_size' in status
        assert 'checked_in' in status
        assert 'checked_out' in status
        assert 'overflow' in status
        assert 'total_connections' in status
    
    def test_optimize_pool_size(self):
        """Test pool size optimization recommendations"""
        engine = create_engine("sqlite:///:memory:")
        
        recommendations = ConnectionPool.optimize_pool_size(engine, target_concurrency=10)
        
        assert 'recommended_pool_size' in recommendations
        assert 'recommended_max_overflow' in recommendations
        assert recommendations['recommended_pool_size'] >= 10
        assert recommendations['recommended_max_overflow'] >= 20


class TestOptimizationConfigs:
    """Test optimization configuration helpers"""
    
    def test_optimize_for_read_heavy(self):
        """Test read-heavy optimization config"""
        config = optimize_for_read_heavy()
        
        assert config['pool_size'] > 0
        assert config['max_overflow'] > 0
        assert config['pool_pre_ping'] is True
        assert 'notes' in config
        assert len(config['notes']) > 0
    
    def test_optimize_for_write_heavy(self):
        """Test write-heavy optimization config"""
        config = optimize_for_write_heavy()
        
        assert config['pool_size'] > 0
        assert config['max_overflow'] > 0
        assert config['pool_pre_ping'] is True
        assert 'notes' in config
        assert len(config['notes']) > 0


class TestAcceptanceCriteria:
    """Test acceptance criteria for database optimization"""
    
    def test_query_time_under_100ms(self, test_db):
        """Test that optimized queries are under 100ms"""
        optimizer = QueryOptimizer(test_db)
        
        # Insert test data
        for i in range(100):
            test_db.add(TestModel(name=f"item_{i}", value=i))
        test_db.commit()
        
        # Measure query time
        with optimizer.time_query("select_all"):
            results = test_db.query(TestModel).all()
        
        # Query should be fast (< 100ms)
        avg_time = optimizer.get_average_query_time()
        assert avg_time < 0.1, f"Query time {avg_time*1000:.2f}ms should be < 100ms"
        assert len(results) == 100
    
    def test_batch_operations_performance(self, test_db):
        """Test that batch operations are efficient"""
        optimizer = QueryOptimizer(test_db)
        
        # Create many objects
        objects = [
            TestModel(name=f"item_{i}", value=i)
            for i in range(1000)
        ]
        
        # Measure batch insert time
        start = time.time()
        optimizer.batch_insert(objects, batch_size=100)
        batch_time = time.time() - start
        
        # Should be fast - less than 1 second for 1000 items
        assert batch_time < 1.0, "Batch insert should be fast"
        
        # Verify all inserted
        count = test_db.query(TestModel).count()
        assert count == 1000
    
    def test_lazy_loading_memory_optimization(self):
        """Test that lazy loading defers memory allocation"""
        # Create multiple lazy loaders
        def create_large_data():
            return [0] * 1000000  # Large list
        
        loaders = [LazyLoader(create_large_data) for _ in range(10)]
        
        # None should be loaded yet
        assert all(not loader.is_loaded for loader in loaders)
        
        # Load just one
        loaders[0].value
        
        # Only one should be loaded
        loaded_count = sum(1 for loader in loaders if loader.is_loaded)
        assert loaded_count == 1
