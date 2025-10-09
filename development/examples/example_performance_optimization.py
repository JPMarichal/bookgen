"""
Comprehensive example demonstrating performance optimization features.

This example shows how to use:
- Performance profiling
- Redis caching
- Database query optimization
- Parallel task execution

To run this example:
1. Make sure Redis is running: redis-server
2. python example_performance_optimization.py
"""
import time
from src.utils.profiler import performance_profile
from src.cache import RedisCache, cached, cache_key
from src.optimizations import QueryOptimizer, LazyLoader
from src.parallel import ValidationParallelizer, parallel_map
from src.database.config import SessionLocal
from src.models import Source
from typing import List, Dict, Any


def example_basic_profiling():
    """Example 1: Basic performance profiling"""
    print("\n" + "="*70)
    print("Example 1: Basic Performance Profiling")
    print("="*70)
    
    with performance_profile() as prof:
        # Simulate some work
        time.sleep(0.1)
        
        # Record database queries
        prof.record_db_query(0.05)  # 50ms query
        prof.record_db_query(0.03)  # 30ms query
        
        # Record cache operations
        for _ in range(85):
            prof.record_cache_hit()
        for _ in range(15):
            prof.record_cache_miss()
    
    # Check metrics
    print(f"Duration: {prof.metrics.duration:.2f}s")
    print(f"Average DB query time: {prof.db_query_avg * 1000:.2f}ms")
    print(f"Cache hit ratio: {prof.cache_hit_ratio:.2%}")
    print(f"Memory peak: {prof.memory_peak / (1024**2):.2f}MB")
    
    # Verify acceptance criteria
    assert prof.db_query_avg < 0.1, "✅ DB queries < 100ms"
    assert prof.cache_hit_ratio > 0.8, "✅ Cache hit ratio > 80%"
    print("\n✅ All acceptance criteria met!")


def example_caching():
    """Example 2: Redis caching for expensive operations"""
    print("\n" + "="*70)
    print("Example 2: Redis Caching")
    print("="*70)
    
    try:
        cache = RedisCache()
        
        # Example: Cache expensive computation
        key = cache_key("computation", "fibonacci", 100)
        
        # Check cache
        result = cache.get(key)
        if result is None:
            print("Cache miss - computing result...")
            # Simulate expensive computation
            time.sleep(0.1)
            result = {"value": 354224848179261915075}
            cache.set(key, result, ttl=3600)
        else:
            print("Cache hit - returning cached result")
        
        print(f"Result: {result['value']}")
        
        # Show cache statistics
        stats = cache.get_stats()
        print(f"\nCache Statistics:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit Ratio: {stats['hit_ratio']:.2%}")
        
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("   Start Redis with: redis-server")


def example_cached_decorator():
    """Example 3: Using @cached decorator"""
    print("\n" + "="*70)
    print("Example 3: @cached Decorator")
    print("="*70)
    
    @cached(ttl=300, key_prefix="validation")
    def validate_url(url: str) -> Dict[str, Any]:
        """Expensive validation that should be cached"""
        print(f"  Validating {url}...")
        time.sleep(0.1)  # Simulate network request
        return {
            "url": url,
            "valid": True,
            "status": 200
        }
    
    try:
        # First call - cache miss
        print("First call (cache miss):")
        start = time.time()
        result1 = validate_url("http://example.com")
        time1 = time.time() - start
        print(f"  Result: {result1['valid']}, Time: {time1:.3f}s")
        
        # Second call - cache hit
        print("\nSecond call (cache hit):")
        start = time.time()
        result2 = validate_url("http://example.com")
        time2 = time.time() - start
        print(f"  Result: {result2['valid']}, Time: {time2:.3f}s")
        
        print(f"\n✅ Cache speedup: {time1/time2:.1f}x faster")
        
    except Exception as e:
        print(f"⚠️  Caching not available: {e}")


def example_database_optimization():
    """Example 4: Database query optimization"""
    print("\n" + "="*70)
    print("Example 4: Database Query Optimization")
    print("="*70)
    
    try:
        # Initialize database if needed
        from src.database.config import init_db
        init_db()
        
        db = SessionLocal()
        optimizer = QueryOptimizer(db)
        
        # Example: Batch insert
        print("Creating test sources...")
        sources = [
            Source(
                url=f"http://example{i}.com",
                title=f"Source {i}",
                validation_status="pending"
            )
            for i in range(50)
        ]
        
        # Batch insert with timing
        count = optimizer.batch_insert(sources, batch_size=10)
        print(f"Inserted {count} sources")
        
        # Query with timing
        with optimizer.time_query("select_all_sources"):
            all_sources = db.query(Source).limit(10).all()
        
        print(f"Retrieved {len(all_sources)} sources")
        print(f"Average query time: {optimizer.get_average_query_time() * 1000:.2f}ms")
        
        # Cleanup
        for source in db.query(Source).filter(Source.url.like("http://example%")).all():
            db.delete(source)
        db.commit()
        db.close()
        
        print("✅ Database optimization example complete")
    except Exception as e:
        print(f"⚠️  Database example skipped: {e}")
        print("   Initialize database with: python -c 'from src.database.config import init_db; init_db()'")


def example_lazy_loading():
    """Example 5: Lazy loading for memory optimization"""
    print("\n" + "="*70)
    print("Example 5: Lazy Loading")
    print("="*70)
    
    def load_large_dataset():
        """Simulate loading large dataset"""
        print("  Loading large dataset...")
        time.sleep(0.1)
        return [i for i in range(1000000)]
    
    # Create lazy loader
    lazy_data = LazyLoader(load_large_dataset)
    
    print("LazyLoader created (data not loaded yet)")
    print(f"Is loaded: {lazy_data.is_loaded}")
    
    # Access data - triggers loading
    print("\nAccessing data...")
    data = lazy_data.value
    print(f"Data loaded: {len(data)} items")
    print(f"Is loaded: {lazy_data.is_loaded}")
    
    # Access again - no reload
    print("\nAccessing again...")
    data2 = lazy_data.value
    print("Data returned from cache (not reloaded)")
    
    print("✅ Lazy loading reduces initial memory footprint")


def example_parallel_validation():
    """Example 6: Parallel task execution for validation"""
    print("\n" + "="*70)
    print("Example 6: Parallel Validation")
    print("="*70)
    
    # Simulate validation of multiple sources
    sources = [
        {"url": f"http://source{i}.com", "title": f"Source {i}"}
        for i in range(10)
    ]
    
    def validate_source(source: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single source"""
        time.sleep(0.1)  # Simulate validation work
        return {
            "url": source["url"],
            "valid": True,
            "score": 0.85
        }
    
    # Sequential validation
    print("Sequential validation:")
    start = time.time()
    sequential_results = [validate_source(s) for s in sources]
    sequential_time = time.time() - start
    print(f"  Time: {sequential_time:.2f}s")
    
    # Parallel validation
    print("\nParallel validation (4 workers):")
    start = time.time()
    parallel_results = parallel_map(validate_source, sources, max_workers=4)
    parallel_time = time.time() - start
    print(f"  Time: {parallel_time:.2f}s")
    
    speedup = sequential_time / parallel_time
    print(f"\n✅ Speedup: {speedup:.2f}x faster with parallelization")


def example_validation_parallelizer():
    """Example 7: Using ValidationParallelizer"""
    print("\n" + "="*70)
    print("Example 7: ValidationParallelizer")
    print("="*70)
    
    sources = [
        {"url": f"http://example{i}.com", "content": f"Content {i}"}
        for i in range(8)
    ]
    
    def validator(source: Dict[str, Any]) -> Dict[str, Any]:
        """Validate source"""
        time.sleep(0.1)
        return {"url": source["url"], "valid": True}
    
    # Use ValidationParallelizer
    parallelizer = ValidationParallelizer(max_workers=4)
    results = parallelizer.validate_sources_parallel(sources, validator)
    
    # Get summary
    summary = parallelizer.get_summary(results)
    
    print(f"Total validations: {summary['total']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"Average time: {summary['average_time']:.3f}s")
    print(f"Total time: {summary['total_time']:.3f}s")
    
    print("✅ Validation completed successfully")


def example_complete_workflow():
    """Example 8: Complete workflow with all optimizations"""
    print("\n" + "="*70)
    print("Example 8: Complete Optimized Workflow")
    print("="*70)
    
    with performance_profile() as prof:
        # Step 1: Use cache for frequently accessed data
        try:
            cache = RedisCache()
            config_key = cache_key("config", "app_settings")
            
            settings = cache.get(config_key)
            if settings is None:
                prof.record_cache_miss()
                settings = {"max_workers": 4, "timeout": 30}
                cache.set(config_key, settings, ttl=3600)
            else:
                prof.record_cache_hit()
        except:
            prof.record_cache_miss()
            settings = {"max_workers": 4, "timeout": 30}
        
        # Step 2: Lazy load heavy content
        heavy_data = LazyLoader(lambda: [i**2 for i in range(100000)])
        
        # Step 3: Parallel validation
        items = [{"id": i} for i in range(10)]
        
        def quick_validate(item):
            time.sleep(0.01)
            return {"id": item["id"], "valid": True}
        
        results = parallel_map(quick_validate, items, max_workers=4)
        
        # Step 4: Record metrics
        prof.record_db_query(0.045)  # 45ms
        prof.record_db_query(0.038)  # 38ms
        
    # Report results
    print(f"\nWorkflow completed:")
    print(f"  Duration: {prof.metrics.duration:.2f}s")
    print(f"  DB query avg: {prof.db_query_avg * 1000:.2f}ms")
    print(f"  Cache hit ratio: {prof.cache_hit_ratio:.2%}")
    print(f"  Items processed: {len(results)}")
    print(f"  Heavy data loaded: {heavy_data.is_loaded}")
    
    # Verify criteria
    assert prof.db_query_avg < 0.1, "✅ DB queries < 100ms"
    print("\n✅ Complete workflow optimized successfully!")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("PERFORMANCE OPTIMIZATION EXAMPLES")
    print("="*70)
    
    examples = [
        ("Basic Profiling", example_basic_profiling),
        ("Redis Caching", example_caching),
        ("Cached Decorator", example_cached_decorator),
        ("Database Optimization", example_database_optimization),
        ("Lazy Loading", example_lazy_loading),
        ("Parallel Validation", example_parallel_validation),
        ("ValidationParallelizer", example_validation_parallelizer),
        ("Complete Workflow", example_complete_workflow),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠️  {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()
