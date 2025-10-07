#!/usr/bin/env python3
"""
Generation benchmark script for BookGen system
Benchmarks biography generation performance

Usage:
    python scripts/benchmark_generation.py
    python scripts/benchmark_generation.py --character "Test Character" --chapters 5
    python scripts/benchmark_generation.py --full-biography
    
Acceptance Criteria:
    - Full biography generation: < 30 minutes
    - API response time: < 200ms for synchronous endpoints
    - Throughput: 2-3 biographies per hour
"""
import argparse
import sys
import os
import time
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.openrouter_client import OpenRouterClient
from src.services.length_validator import LengthValidationService


class BenchmarkTimer:
    """Timer for benchmarking operations"""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"Starting: {self.name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
    
    def stop(self):
        """Stop the timer and calculate duration"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        print(f"\n{'='*60}")
        print(f"Completed: {self.name}")
        print(f"Duration: {self.format_duration(self.duration)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        return self.duration
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes} min {secs:.2f} sec"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours} hr {minutes} min {secs:.2f} sec"


def benchmark_api_response_time():
    """
    Benchmark API response time for synchronous operations
    Target: < 200ms
    """
    print("\n" + "="*60)
    print("Benchmarking API Response Time")
    print("="*60)
    
    from fastapi.testclient import TestClient
    from src.main import app
    
    client = TestClient(app)
    
    endpoints = [
        ("GET", "/health", {}),
        ("GET", "/api/v1/status", {}),
        ("GET", "/", {}),
        ("POST", "/api/v1/biographies/generate", {
            "json": {"character": "Benchmark Test"}
        }),
    ]
    
    results = []
    
    for method, path, kwargs in endpoints:
        # Warm up
        for _ in range(3):
            if method == "GET":
                client.get(path, **kwargs)
            else:
                client.post(path, **kwargs)
        
        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            if method == "GET":
                response = client.get(path, **kwargs)
            else:
                response = client.post(path, **kwargs)
            duration = (time.time() - start) * 1000  # Convert to ms
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        result = {
            "endpoint": f"{method} {path}",
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "passes": avg_time < 200
        }
        results.append(result)
        
        status = "✅ PASS" if result["passes"] else "❌ FAIL"
        print(f"\n{method} {path}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  {status} (target: < 200ms)")
    
    # Summary
    print(f"\n{'='*60}")
    print("API Response Time Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r["passes"])
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All endpoints meet < 200ms target")
    else:
        print(f"❌ {total - passed} endpoint(s) exceed 200ms target")
    
    return results


def benchmark_chapter_generation():
    """
    Benchmark single chapter generation
    Helps estimate full biography generation time
    """
    print("\n" + "="*60)
    print("Benchmarking Chapter Generation")
    print("="*60)
    
    timer = BenchmarkTimer("Single Chapter Generation")
    timer.start()
    
    client = OpenRouterClient()
    
    prompt = """
    Write a detailed chapter (approximately 2000 words) about the early life 
    of a fictional historical figure. Include specific details about their 
    childhood, education, and formative experiences.
    """
    
    try:
        response = client.generate_content(prompt.strip())
        duration = timer.stop()
        
        word_count = len(response.split())
        words_per_second = word_count / duration if duration > 0 else 0
        
        print(f"Words generated: {word_count}")
        print(f"Generation speed: {words_per_second:.2f} words/second")
        
        # Estimate full biography time (20 chapters, ~51000 words total)
        estimated_full_time = (51000 / word_count) * duration
        estimated_minutes = estimated_full_time / 60
        
        print(f"\nEstimated full biography time: {BenchmarkTimer.format_duration(estimated_full_time)}")
        
        # Check acceptance criteria: < 30 minutes
        if estimated_minutes < 30:
            print(f"✅ PASS: Estimated time ({estimated_minutes:.1f} min) < 30 min target")
        else:
            print(f"❌ FAIL: Estimated time ({estimated_minutes:.1f} min) >= 30 min target")
        
        return {
            "duration_seconds": duration,
            "word_count": word_count,
            "words_per_second": words_per_second,
            "estimated_full_biography_seconds": estimated_full_time,
            "estimated_full_biography_minutes": estimated_minutes,
            "meets_target": estimated_minutes < 30
        }
        
    except Exception as e:
        timer.stop()
        print(f"❌ Error during generation: {e}")
        return None


def benchmark_throughput_estimate():
    """
    Estimate system throughput
    Target: 2-3 biographies per hour
    """
    print("\n" + "="*60)
    print("Estimating System Throughput")
    print("="*60)
    
    # Run a quick benchmark to estimate throughput
    chapter_benchmark = benchmark_chapter_generation()
    
    if chapter_benchmark:
        estimated_biography_time = chapter_benchmark["estimated_full_biography_minutes"]
        
        # Calculate biographies per hour
        biographies_per_hour = 60 / estimated_biography_time if estimated_biography_time > 0 else 0
        
        print(f"\nEstimated throughput: {biographies_per_hour:.2f} biographies/hour")
        
        # Check acceptance criteria: 2-3 biographies per hour
        if 2 <= biographies_per_hour <= 3:
            print(f"✅ PASS: Throughput ({biographies_per_hour:.2f}/hr) meets 2-3/hr target")
        elif biographies_per_hour > 3:
            print(f"✅ EXCEEDS: Throughput ({biographies_per_hour:.2f}/hr) exceeds target")
        else:
            print(f"❌ FAIL: Throughput ({biographies_per_hour:.2f}/hr) below 2/hr target")
        
        return {
            "biographies_per_hour": biographies_per_hour,
            "meets_target": biographies_per_hour >= 2
        }
    
    return None


def benchmark_small_generation():
    """
    Benchmark a small generation task for quick testing
    """
    print("\n" + "="*60)
    print("Benchmarking Small Generation (Quick Test)")
    print("="*60)
    
    timer = BenchmarkTimer("Small Generation (500 words)")
    timer.start()
    
    client = OpenRouterClient()
    
    prompt = "Write a 500-word biographical paragraph about a fictional scientist."
    
    try:
        response = client.generate_content(prompt)
        duration = timer.stop()
        
        word_count = len(response.split())
        words_per_second = word_count / duration if duration > 0 else 0
        
        print(f"Words generated: {word_count}")
        print(f"Generation speed: {words_per_second:.2f} words/second")
        
        return {
            "duration_seconds": duration,
            "word_count": word_count,
            "words_per_second": words_per_second
        }
        
    except Exception as e:
        timer.stop()
        print(f"❌ Error during generation: {e}")
        return None


def save_results(results, filename="benchmark_results.json"):
    """Save benchmark results to JSON file"""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "benchmarks")
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    # Add timestamp
    results["timestamp"] = datetime.now().isoformat()
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {filepath}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Benchmark BookGen biography generation performance"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmarks only (small generation)"
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Benchmark API response times only"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("BookGen Generation Benchmarks")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_results = {}
    
    # API response time benchmarks
    if not args.quick:
        api_results = benchmark_api_response_time()
        all_results["api_response_times"] = api_results
    
    if args.api_only:
        if args.save:
            save_results(all_results)
        return
    
    # Generation benchmarks
    if args.quick:
        small_gen = benchmark_small_generation()
        all_results["small_generation"] = small_gen
    else:
        throughput = benchmark_throughput_estimate()
        all_results["throughput"] = throughput
    
    # Save results if requested
    if args.save:
        save_results(all_results)
    
    print("\n" + "="*60)
    print("Benchmarking Complete")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
