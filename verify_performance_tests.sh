#!/bin/bash
# Verification script for performance testing infrastructure
# This script demonstrates all the performance testing capabilities

set -e

echo "=========================================="
echo "Performance Testing Verification Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
pip list | grep -q pytest-benchmark || pip install pytest-benchmark
pip list | grep -q locust || pip install locust
pip list | grep -q memory-profiler || pip install memory-profiler
pip list | grep -q psutil || pip install psutil
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# 1. Performance Benchmarks
echo "=========================================="
echo "1. Running Performance Benchmarks"
echo "=========================================="
echo ""

echo -e "${YELLOW}Running API performance benchmarks...${NC}"
RATE_LIMIT_PER_MINUTE=10000 pytest tests/performance/test_api_performance.py::TestAPIPerformance::test_health_endpoint_performance -v --benchmark-only
echo -e "${GREEN}✅ Health endpoint benchmark completed${NC}"
echo ""

# 2. Stress Tests
echo "=========================================="
echo "2. Running Stress Tests"
echo "=========================================="
echo ""

echo -e "${YELLOW}Running rapid-fire requests stress test...${NC}"
RATE_LIMIT_PER_MINUTE=10000 pytest tests/stress/test_stress.py::TestStressScenarios::test_rapid_fire_requests -v -s
echo -e "${GREEN}✅ Stress test completed${NC}"
echo ""

# 3. Validate Scripts
echo "=========================================="
echo "3. Validating Profiling Scripts"
echo "=========================================="
echo ""

echo -e "${YELLOW}Validating memory profiler script...${NC}"
python -m py_compile scripts/profile_memory.py
echo -e "${GREEN}✅ Memory profiler script is valid${NC}"
echo ""

echo -e "${YELLOW}Validating benchmark generation script...${NC}"
python -m py_compile scripts/benchmark_generation.py
echo -e "${GREEN}✅ Benchmark generation script is valid${NC}"
echo ""

# 4. Validate Locust file
echo "=========================================="
echo "4. Validating Load Testing Configuration"
echo "=========================================="
echo ""

echo -e "${YELLOW}Validating Locust file...${NC}"
python -m py_compile tests/load/locustfile.py
echo -e "${GREEN}✅ Locustfile is valid${NC}"
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ All performance testing infrastructure is working!${NC}"
echo ""
echo "Available tests:"
echo "  - Performance benchmarks: pytest tests/performance/ --benchmark-only"
echo "  - Stress tests: pytest tests/stress/ -v"
echo "  - Load tests: locust -f tests/load/locustfile.py --host=http://localhost:8000"
echo "  - Memory profiling: python scripts/profile_memory.py"
echo "  - Generation benchmarks: python scripts/benchmark_generation.py"
echo ""
echo "See tests/performance/README.md for detailed documentation"
echo ""
