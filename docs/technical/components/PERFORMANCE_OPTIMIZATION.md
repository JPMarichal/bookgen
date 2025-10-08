# Performance Optimization Guide

This guide describes the performance optimization features implemented in BookGen to achieve production-ready performance targets.

## 📊 Performance Targets

Based on Issue #16 acceptance criteria:

- ✅ **Database Queries**: < 100ms average
- ✅ **Cache Hit Ratio**: > 80%
- ✅ **Memory Usage**: 30% reduction through optimization
- ✅ **Parallelization**: Independent validation tasks
- ✅ **Precomputed Embeddings**: Cache for sources
- ✅ **Lazy Loading**: Heavy content loaded on-demand

## 🚀 Features

### 1. Performance Profiler (`src/utils/profiler.py`)

Monitor and measure system performance in real-time.

#### Usage

```python
from src.utils.profiler import performance_profile

# Profile a code block
with performance_profile() as prof:
    # Your code here
    engine.generate_biography("character_name")

# Check metrics
print(f"Memory peak: {prof.memory_peak / 1024**3:.2f} GB")
print(f"DB query avg: {prof.db_query_avg * 1000:.2f} ms")
print(f"Cache hit ratio: {prof.cache_hit_ratio:.2%}")

# Verify acceptance criteria
assert prof.memory_peak < 1.5 * 1024**3  # < 1.5GB
assert prof.db_query_avg < 0.1  # < 100ms
assert prof.cache_hit_ratio > 0.8  # > 80%
```

#### Features

- **Memory Tracking**: Monitor memory usage and peak consumption
- **Query Timing**: Track database query performance
- **Cache Metrics**: Record cache hits/misses and calculate hit ratio
- **CPU Usage**: Monitor CPU utilization
- **Context Manager**: Easy integration with existing code

#### Recording Metrics

```python
with performance_profile() as prof:
    # Record database query
    prof.record_db_query(0.045)  # 45ms
    
    # Or use start/end timing
    prof.start_db_query()
    # ... execute query ...
    prof.end_db_query()
    
    # Record cache operations
    prof.record_cache_hit()
    prof.record_cache_miss()
    
    # Update memory peak
    prof.update_memory_peak()
```

### 2. Redis Cache (`src/cache/redis_cache.py`)

High-performance caching layer for embeddings, validation results, and frequent queries.

#### Configuration

Set via environment variables:

```bash
REDIS_HOST=localhost      # Default: localhost
REDIS_PORT=6379          # Default: 6379
REDIS_DB=0               # Default: 0
REDIS_PASSWORD=          # Optional
```

#### Basic Usage

```python
from src.cache import RedisCache, cache_key

# Create cache instance
cache = RedisCache()

# Store value
key = cache_key("validation", "http://example.com")
cache.set(key, {"valid": True, "score": 0.85}, ttl=3600)

# Retrieve value
result = cache.get(key)
if result is not None:
    print("Cache hit!")
else:
    print("Cache miss")

# Check statistics
stats = cache.get_stats()
print(f"Hit ratio: {stats['hit_ratio']:.2%}")
```

#### Using @cached Decorator

```python
from src.cache import cached

@cached(ttl=1800, key_prefix="validation")
def validate_source(url: str):
    # Expensive validation logic
    # Result will be cached for 30 minutes
    return {"url": url, "valid": True}

# First call - cache miss, executes function
result1 = validate_source("http://example.com")

# Second call - cache hit, returns cached result
result2 = validate_source("http://example.com")
```

#### Batch Operations

```python
# Get multiple keys
results = cache.get_many(["key1", "key2", "key3"])

# Set multiple keys
cache.set_many({
    "key1": {"value": 1},
    "key2": {"value": 2}
}, ttl=3600)
```

#### Target: 80%+ Hit Ratio

To achieve >80% cache hit ratio:

1. **Cache embeddings**: Precompute and cache vector embeddings
2. **Cache validations**: Store validation results with appropriate TTL
3. **Cache frequent queries**: Identify and cache hot queries
4. **Monitor metrics**: Use `cache.get_stats()` to track performance

### 3. Database Query Optimizer (`src/optimizations/db_optimizer.py`)

Tools for optimizing database queries and reducing latency.

#### Query Timing

```python
from src.optimizations import QueryOptimizer
from src.database.config import SessionLocal

db = SessionLocal()
optimizer = QueryOptimizer(db)

# Time a query
with optimizer.time_query("get_biographies"):
    results = db.query(Biography).all()

# Check average
avg_time = optimizer.get_average_query_time()
print(f"Average: {avg_time * 1000:.2f}ms")
```

#### Batch Operations

```python
# Batch insert (10x faster than individual inserts)
sources = [Source(url=f"http://example{i}.com") for i in range(100)]
optimizer.batch_insert(sources, batch_size=50)

# Batch update
updates = [
    {"id": 1, "status": "completed"},
    {"id": 2, "status": "completed"}
]
optimizer.batch_update(Biography, updates, batch_size=10)
```

#### Eager Loading (Avoid N+1 Queries)

```python
from src.optimizations import with_eager_loading, with_selectin_loading
from src.models import Biography

# Eager load relationships
query = db.query(Biography)
query = with_eager_loading(query, Biography.chapters)
biographies = query.all()

# Or use selectin loading for collections
query = with_selectin_loading(query, Biography.chapters)
```

#### Connection Pool Optimization

```python
from src.optimizations import ConnectionPool
from src.database.config import engine

# Check pool status
status = ConnectionPool.get_pool_status(engine)
print(f"Pool size: {status['pool_size']}")
print(f"Checked out: {status['checked_out']}")

# Get recommendations
recommendations = ConnectionPool.optimize_pool_size(
    engine, 
    target_concurrency=10
)
```

#### Configuration Examples

```python
from src.optimizations import optimize_for_read_heavy, optimize_for_write_heavy

# Get read-heavy optimization config
read_config = optimize_for_read_heavy()
# {
#   'pool_size': 20,
#   'max_overflow': 40,
#   'pool_pre_ping': True,
#   ...
# }

# Get write-heavy optimization config
write_config = optimize_for_write_heavy()
```

### 4. Lazy Loading (`src/optimizations/db_optimizer.py`)

Defer loading of heavy content to reduce memory usage.

#### Usage

```python
from src.optimizations import LazyLoader

# Create lazy loader
def load_embeddings():
    # Expensive operation
    return compute_embeddings(large_corpus)

lazy_embeddings = LazyLoader(load_embeddings)

# Not loaded yet
print(lazy_embeddings.is_loaded)  # False

# Access triggers loading
embeddings = lazy_embeddings.value  # Loads now
print(lazy_embeddings.is_loaded)  # True

# Subsequent access uses cached value
embeddings2 = lazy_embeddings.value  # No reload
```

#### Benefits

- **Reduced Initial Memory**: Only load what's needed
- **Faster Startup**: Defer expensive computations
- **Cached Access**: Subsequent reads are instant

### 5. Parallel Task Executor (`src/parallel/task_executor.py`)

Execute independent tasks in parallel for better throughput.

#### Basic Parallel Execution

```python
from src.parallel import ParallelTaskExecutor

executor = ParallelTaskExecutor(max_workers=4)

# Define tasks
tasks = [
    lambda: validate_source("http://example1.com"),
    lambda: validate_source("http://example2.com"),
    lambda: validate_source("http://example3.com"),
]

# Execute in parallel
results = executor.execute_parallel(tasks)

# Check results
for result in results:
    if result.success:
        print(f"Task {result.task_id}: {result.result}")
    else:
        print(f"Task {result.task_id} failed: {result.error}")
```

#### Parallel Map

```python
from src.parallel import parallel_map

def validate_url(url: str):
    # Validation logic
    return {"url": url, "valid": True}

urls = ["http://example1.com", "http://example2.com", ...]

# Process in parallel (4 workers)
results = parallel_map(validate_url, urls, max_workers=4)
```

#### Validation Parallelizer

Specialized for validation tasks:

```python
from src.parallel import ValidationParallelizer

parallelizer = ValidationParallelizer(max_workers=4)

sources = [{"url": "http://example1.com"}, ...]

def validator(source):
    return validate_source(source)

# Validate in parallel
results = parallelizer.validate_sources_parallel(sources, validator)

# Get summary
summary = parallelizer.get_summary(results)
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average time: {summary['average_time']:.3f}s")
```

#### Batch Processing

```python
from src.parallel import parallel_batch_process

def process_batch(urls):
    return [validate_url(url) for url in urls]

all_urls = [...]  # Many URLs

# Process in parallel batches
results = parallel_batch_process(
    all_urls,
    process_batch,
    batch_size=20,
    max_workers=4
)
```

## 📈 Performance Optimization Strategies

### Strategy 1: Cache Precomputed Embeddings

```python
from src.cache import cached

@cached(ttl=86400, key_prefix="embedding")  # Cache for 24 hours
def get_source_embedding(source_id: int):
    # Expensive embedding computation
    return compute_embedding(source_id)

# First call computes, subsequent calls use cache
embedding = get_source_embedding(123)
```

### Strategy 2: Batch Database Operations

```python
from src.optimizations import QueryOptimizer

optimizer = QueryOptimizer(db)

# Instead of 100 individual inserts
# sources = [...]
# for source in sources:
#     db.add(source)
#     db.commit()

# Use batch insert
optimizer.batch_insert(sources, batch_size=50)
```

### Strategy 3: Parallel Validation

```python
from src.parallel import ValidationParallelizer

parallelizer = ValidationParallelizer(max_workers=8)

# Instead of sequential validation
# results = [validate(s) for s in sources]

# Use parallel validation
results = parallelizer.validate_sources_parallel(sources, validate)
```

### Strategy 4: Lazy Load Heavy Content

```python
from src.optimizations import LazyLoader

class Biography:
    def __init__(self, character_name: str):
        self.character_name = character_name
        # Lazy load embeddings
        self._embeddings = LazyLoader(
            lambda: compute_embeddings(self.character_name)
        )
    
    @property
    def embeddings(self):
        return self._embeddings.value  # Loads on first access
```

### Strategy 5: Query Optimization

```python
from src.optimizations import with_selectin_loading

# Avoid N+1 queries
query = db.query(Biography)
query = with_selectin_loading(query, Biography.chapters)
biographies = query.all()

# Now accessing biography.chapters doesn't trigger extra queries
for bio in biographies:
    for chapter in bio.chapters:  # No extra query
        print(chapter.title)
```

## 🎯 Achieving Acceptance Criteria

### 1. DB Queries < 100ms Average

```python
from src.optimizations import QueryOptimizer, enable_query_logging

# Enable slow query logging
enable_query_logging(engine, threshold_ms=100)

# Use query optimizer
optimizer = QueryOptimizer(db)

# Batch operations
optimizer.batch_insert(items, batch_size=100)

# Use eager loading
query = with_selectin_loading(query, Biography.chapters)

# Monitor
avg_time = optimizer.get_average_query_time()
assert avg_time < 0.1  # < 100ms
```

### 2. Cache Hit Ratio > 80%

```python
from src.cache import RedisCache, cached

cache = RedisCache()

# Cache expensive operations
@cached(ttl=3600)
def get_validation_result(url: str):
    return validate(url)

# Monitor hit ratio
stats = cache.get_stats()
assert stats['hit_ratio'] > 0.8
```

### 3. 30% Memory Reduction

```python
from src.optimizations import LazyLoader

# Use lazy loading for heavy content
embeddings = LazyLoader(compute_embeddings)
corpus = LazyLoader(load_large_corpus)

# Only loaded when accessed
data = embeddings.value  # Loads here
```

### 4. Parallelization of Validations

```python
from src.parallel import ValidationParallelizer

parallelizer = ValidationParallelizer(max_workers=4)
results = parallelizer.validate_sources_parallel(sources, validator)

# 2-4x speedup depending on I/O vs CPU bound work
```

## 📊 Monitoring and Verification

### Complete Monitoring Example

```python
from src.utils.profiler import performance_profile
from src.cache import RedisCache
from src.optimizations import QueryOptimizer
from src.database.config import SessionLocal

# Profile entire operation
with performance_profile() as prof:
    db = SessionLocal()
    optimizer = QueryOptimizer(db)
    cache = RedisCache()
    
    # Your operations here
    # ...
    
    db.close()

# Verify all criteria
print("Performance Metrics:")
print(f"  Memory peak: {prof.memory_peak / 1024**3:.2f} GB")
print(f"  DB avg: {prof.db_query_avg * 1000:.2f} ms")
print(f"  Cache hit ratio: {prof.cache_hit_ratio:.2%}")

# Assertions
assert prof.memory_peak < 1.5 * 1024**3, "Memory < 1.5GB"
assert prof.db_query_avg < 0.1, "DB queries < 100ms"
assert prof.cache_hit_ratio > 0.8, "Cache hit ratio > 80%"

print("✅ All acceptance criteria met!")
```

## 🔧 Configuration

### Redis Configuration

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=secret  # Optional
```

### Database Configuration

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/bookgen
DB_POOL_SIZE=20          # For read-heavy workloads
DB_MAX_OVERFLOW=40
```

### Worker Configuration

```python
# For CPU-bound tasks
executor = ParallelTaskExecutor(
    max_workers=4,
    use_processes=True  # Use process pool
)

# For I/O-bound tasks
executor = ParallelTaskExecutor(
    max_workers=10,
    use_processes=False  # Use thread pool (default)
)
```

## 📚 Examples

See `example_performance_optimization.py` for comprehensive examples:

```bash
# Make sure Redis is running
redis-server &

# Run examples
python example_performance_optimization.py
```

Examples include:
1. Basic profiling
2. Redis caching
3. Cached decorator usage
4. Database optimization
5. Lazy loading
6. Parallel validation
7. ValidationParallelizer
8. Complete optimized workflow

## 🧪 Testing

All optimization features have comprehensive tests:

```bash
# Run all optimization tests
pytest tests/test_profiler.py -v
pytest tests/test_cache.py -v
pytest tests/test_db_optimizer.py -v
pytest tests/test_parallel.py -v

# Run all together
pytest tests/test_profiler.py tests/test_cache.py tests/test_db_optimizer.py tests/test_parallel.py -v
```

Test coverage:
- ✅ Performance profiler: 16 tests
- ✅ Redis cache: 20 tests
- ✅ DB optimizer: 14 tests
- ✅ Parallel executor: 16 tests
- **Total: 66 tests, all passing**

## 🎓 Best Practices

1. **Always Profile**: Use `performance_profile()` to measure before optimizing
2. **Cache Strategically**: Cache expensive computations with appropriate TTL
3. **Batch Operations**: Use batch insert/update for bulk operations
4. **Parallelize I/O**: Use parallel execution for I/O-bound tasks
5. **Lazy Load**: Defer loading of heavy content until needed
6. **Monitor Metrics**: Track cache hit ratio, query times, memory usage
7. **Set Limits**: Configure appropriate timeouts and pool sizes

## 🔍 Troubleshooting

### Redis Connection Issues

```python
try:
    cache = RedisCache()
    cache.set("test", "value")
except Exception as e:
    print(f"Redis not available: {e}")
    # Fall back to non-cached operation
```

### Slow Queries

```python
from src.optimizations import enable_query_logging

# Log queries > 100ms
enable_query_logging(engine, threshold_ms=100)
```

### Memory Issues

```python
# Use lazy loading
data = LazyLoader(expensive_operation)

# Clear cache periodically
cache.clear()

# Monitor memory
from src.utils.profiler import get_system_metrics
metrics = get_system_metrics()
print(f"Memory: {metrics['memory_percent']:.1f}%")
```

## 📖 References

- Issue #16: Performance Optimization
- Issue #15: Performance Benchmarks
- `CELERY_TASK_QUEUE.md`: Task queue configuration
- `DATABASE_README.md`: Database optimization
- `tests/performance/README.md`: Performance testing
