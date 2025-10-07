# Performance Testing and Benchmarks

This directory contains performance benchmarks, load testing, and stress tests for the BookGen system.

## 📊 Performance Targets

Based on the requirements in Issue #15:

- ✅ **Biography Generation**: < 30 minutes for complete biography
- ✅ **API Response Time**: < 200ms for synchronous endpoints
- ✅ **Concurrent Users**: Handle minimum 10 simultaneous users
- ✅ **Memory Usage**: < 2GB per worker
- ✅ **Throughput**: 2-3 biographies per hour
- ✅ **Error Rate**: < 1% under normal load

## 🧪 Test Categories

### 1. Performance Benchmarks (`tests/performance/`)

Pytest-based benchmarks for API endpoints and core functionality.

```bash
# Run all performance benchmarks
pytest tests/performance/ --benchmark-only

# Run with autosave for comparison
pytest tests/performance/ --benchmark-only --benchmark-autosave

# Run specific test
pytest tests/performance/test_api_performance.py::TestAPIPerformance::test_health_endpoint_performance -v

# Compare with previous runs
pytest tests/performance/ --benchmark-compare
```

**What it tests:**
- API endpoint response times
- Concurrent request handling
- Cold start vs warm cache performance
- Individual endpoint latency

### 2. Load Testing (`tests/load/`)

Locust-based load testing to simulate real user behavior.

```bash
# Run load test (headless)
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=60s --headless

# Run with web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Run stress test
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5 --run-time=120s --headless
```

**What it tests:**
- Multiple concurrent users (target: 10+)
- API latency under load
- Error rates under load
- System stability with sustained traffic

**User Classes:**
- `BookGenUser`: Normal user behavior with realistic wait times
- `StressTestUser`: Aggressive testing with minimal wait times

### 3. Stress Tests (`tests/stress/`)

Pytest-based stress tests for extreme conditions.

```bash
# Run all stress tests
pytest tests/stress/ -v

# Run specific stress test
pytest tests/stress/test_stress.py::TestStressScenarios::test_concurrent_job_creation -v

# Run with verbose output
pytest tests/stress/ -v -s
```

**What it tests:**
- Rapid-fire requests
- Concurrent job creation
- Mixed load scenarios
- Sustained load over time
- Error recovery
- Memory leak detection

## 📈 Profiling and Benchmarking Scripts

### Memory Profiling (`scripts/profile_memory.py`)

Profile memory usage of core components.

```bash
# Run all memory profiling tests
python scripts/profile_memory.py

# Run specific test
python scripts/profile_memory.py --test openrouter

# Test concurrent operations
python scripts/profile_memory.py --test concurrent --concurrent-users 10

# Detailed line-by-line profiling
python -m memory_profiler scripts/profile_memory.py
```

**What it tests:**
- Memory usage of OpenRouter client
- Memory usage of length validation service
- Memory behavior with concurrent operations
- Memory leak detection

### Generation Benchmarks (`scripts/benchmark_generation.py`)

Benchmark biography generation performance.

```bash
# Run all benchmarks
python scripts/benchmark_generation.py

# Quick test (small generation)
python scripts/benchmark_generation.py --quick

# API response times only
python scripts/benchmark_generation.py --api-only

# Save results to JSON
python scripts/benchmark_generation.py --save
```

**What it tests:**
- API response times for all endpoints
- Chapter generation speed
- Full biography time estimation
- System throughput (biographies/hour)

## 📋 Running All Tests

**Important:** To avoid rate limiting during tests, set the `RATE_LIMIT_PER_MINUTE` environment variable to a high value:

```bash
# Install dependencies
pip install -r requirements.txt

# Run performance benchmarks (disable rate limiting)
RATE_LIMIT_PER_MINUTE=10000 pytest tests/performance/ --benchmark-only -v

# Run stress tests
RATE_LIMIT_PER_MINUTE=10000 pytest tests/stress/ -v

# Run load tests (requires running server)
# Terminal 1: Start the server
uvicorn src.main:app --reload

# Terminal 2: Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=60s --headless

# Run memory profiling
python scripts/profile_memory.py

# Run generation benchmarks
python scripts/benchmark_generation.py

# Quick verification of all tests
./verify_performance_tests.sh
```

## 📊 Understanding Results

### Performance Benchmark Results

Example output from pytest-benchmark:

```
---------------------------------------------------- benchmark: 1 tests ---------------------------------------------------
Name (time in ms)                       Min     Max    Mean  StdDev  Median     IQR  Outliers       OPS  Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------
test_health_endpoint_performance     1.2818  2.5393  1.3730  0.1412  1.3372  0.0516      8;15  728.3064     105           1
---------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```

**Interpretation:**
- **Mean: 1.37ms** - Average response time (target: < 50ms for health, < 200ms for API endpoints)
- **Min/Max: 1.28ms / 2.54ms** - Range of response times
- **OPS: 728** - Operations per second (requests/second this endpoint can handle)
- **✅ PASS** - 1.37ms is well under the 50ms target for health endpoint

### Load Test Results

Example output from Locust:

```
Total requests: 1234
Total failures: 5
Average response time: 145.32ms
Median response time: 132.15ms
95th percentile: 189.45ms
99th percentile: 245.78ms
Error rate: 0.4%
✅ PASS: All metrics within targets
```

**Interpretation:**
- **Average: 145ms** - Well under 200ms target
- **95th percentile: 189ms** - 95% of requests completed under 200ms
- **Error rate: 0.4%** - Well under 1% target

### Memory Profiling Results

Example output:

```
==========================================
System Information
==========================================
CPU count: 4
CPU percent: 15.2%
Total memory: 16.00 GB
Available memory: 12.34 GB
Memory percent used: 22.9%
==========================================

==========================================
Testing OpenRouter Client Memory Usage
==========================================
Baseline (before client creation)
Current memory: 125.45 MB
Memory increase: 0.00 MB
Memory percent: 0.78%

After client initialization
Current memory: 156.23 MB
Memory increase: 30.78 MB
Memory percent: 0.98%

==========================================
Maximum memory usage: 0.153 GB
✅ PASS: Memory usage (0.153 GB) < 2GB target
==========================================
```

### Stress Test Results

Example output:

```
tests/stress/test_stress.py::TestStressScenarios::test_rapid_fire_requests
Processed 677.37 requests/second
PASSED
```

**Interpretation:**
- System handled 100 rapid requests in ~0.15 seconds
- Throughput: ~677 requests/second
- All requests succeeded without errors

## 🚨 Alerting and Monitoring

The test suite provides built-in alerts for performance issues:

- **API Latency**: Warns if average response time > 200ms
- **Error Rate**: Warns if failure rate > 1%
- **Memory Usage**: Warns if memory > 2GB per worker
- **Throughput**: Warns if < 2 biographies/hour

## 📝 Adding New Tests

### Adding a Performance Benchmark

```python
# tests/performance/test_api_performance.py

def test_new_endpoint_performance(self, benchmark):
    """Benchmark new endpoint"""
    def request():
        response = client.get("/api/v1/new-endpoint")
        assert response.status_code == 200
        return response
    
    result = benchmark(request)
    stats = benchmark.stats
    assert stats.mean < 0.2, "Too slow"
```

### Adding a Load Test Task

```python
# tests/load/locustfile.py

@task(5)  # Weight: 5
def new_endpoint_task(self):
    """Test new endpoint under load"""
    with self.client.get("/api/v1/new-endpoint", catch_response=True) as response:
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Status: {response.status_code}")
```

### Adding a Stress Test

```python
# tests/stress/test_stress.py

def test_new_stress_scenario(self):
    """Test new stress scenario"""
    # Your stress test logic here
    pass
```

## 🔍 Troubleshooting

### High Response Times

1. Check server logs for errors
2. Monitor CPU/memory usage during tests
3. Run profiling to identify bottlenecks
4. Check database connection pool settings

### High Error Rates

1. Check error logs for specific failures
2. Verify all services are running
3. Check rate limiting configuration
4. Verify database connectivity

### Memory Issues

1. Run memory profiler to identify leaks
2. Check for circular references
3. Verify proper cleanup in services
4. Monitor memory over extended periods

## 📚 References

- [Locust Documentation](https://docs.locust.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [memory-profiler Documentation](https://github.com/pythonprofilers/memory_profiler)

## 🎯 Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: |
    pytest tests/performance/ --benchmark-only
    pytest tests/stress/ -v

- name: Run Load Tests
  run: |
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=10 --run-time=60s --headless
```

## ✅ Acceptance Criteria Verification

All acceptance criteria from Issue #15 can be verified:

- ✅ **Biography < 30 min**: `python scripts/benchmark_generation.py`
- ✅ **API < 200ms**: `pytest tests/performance/test_api_performance.py`
- ✅ **10 concurrent users**: `locust -f tests/load/locustfile.py --users=10`
- ✅ **Memory < 2GB**: `python scripts/profile_memory.py`
- ✅ **Stress tests documented**: This README
- ✅ **Automatic alerts**: Built into test outputs
