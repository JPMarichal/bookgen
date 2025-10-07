#!/usr/bin/env python3
"""
Memory profiling script for BookGen system
Profiles memory usage during biography generation

Usage:
    python -m memory_profiler scripts/profile_memory.py
    python scripts/profile_memory.py --character "Test Character" --chapters 5
    
Requirements:
    pip install memory-profiler psutil
"""
import argparse
import sys
import os
from memory_profiler import profile
import psutil
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.openrouter_client import OpenRouterClient
from src.services.length_validator import LengthValidationService


class MemoryMonitor:
    """Monitor memory usage during operations"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_usage()
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_memory_increase(self):
        """Get memory increase from baseline in MB"""
        return self.get_memory_usage() - self.baseline_memory
    
    def print_memory_stats(self, label=""):
        """Print current memory statistics"""
        current = self.get_memory_usage()
        increase = self.get_memory_increase()
        print(f"\n{label}")
        print(f"Current memory: {current:.2f} MB")
        print(f"Memory increase: {increase:.2f} MB")
        print(f"Memory percent: {self.process.memory_percent():.2f}%")


@profile
def test_openrouter_memory():
    """Profile memory usage of OpenRouter client"""
    print("\n" + "="*60)
    print("Testing OpenRouter Client Memory Usage")
    print("="*60)
    
    monitor = MemoryMonitor()
    monitor.print_memory_stats("Baseline (before client creation)")
    
    # Initialize client
    client = OpenRouterClient()
    monitor.print_memory_stats("After client initialization")
    
    # Generate small text
    prompt = "Write a short 100-word paragraph about memory profiling in Python."
    try:
        response = client.generate_content(prompt)
        monitor.print_memory_stats("After single generation")
    except Exception as e:
        print(f"Error during generation: {e}")
    
    # Check acceptance criteria: < 2GB per worker
    max_memory_mb = monitor.get_memory_usage()
    max_memory_gb = max_memory_mb / 1024
    
    print(f"\n{'='*60}")
    print(f"Maximum memory usage: {max_memory_gb:.3f} GB")
    if max_memory_gb < 2.0:
        print(f"✅ PASS: Memory usage ({max_memory_gb:.3f} GB) < 2GB target")
    else:
        print(f"❌ FAIL: Memory usage ({max_memory_gb:.3f} GB) >= 2GB target")
    print(f"{'='*60}\n")


@profile
def test_length_validation_memory():
    """Profile memory usage of length validation service"""
    print("\n" + "="*60)
    print("Testing Length Validation Service Memory Usage")
    print("="*60)
    
    monitor = MemoryMonitor()
    monitor.print_memory_stats("Baseline (before service creation)")
    
    # Initialize service
    service = LengthValidationService()
    monitor.print_memory_stats("After service initialization")
    
    # Load configuration
    try:
        config = service.get_character_config("default")
        monitor.print_memory_stats("After loading configuration")
    except Exception as e:
        print(f"Error loading config: {e}")
    
    max_memory_mb = monitor.get_memory_usage()
    max_memory_gb = max_memory_mb / 1024
    
    print(f"\n{'='*60}")
    print(f"Maximum memory usage: {max_memory_gb:.3f} GB")
    if max_memory_gb < 2.0:
        print(f"✅ PASS: Memory usage ({max_memory_gb:.3f} GB) < 2GB target")
    else:
        print(f"❌ FAIL: Memory usage ({max_memory_gb:.3f} GB) >= 2GB target")
    print(f"{'='*60}\n")


@profile
def test_concurrent_operations_memory(num_operations=10):
    """
    Profile memory usage with concurrent operations simulation
    Tests memory usage when handling multiple concurrent users
    """
    print("\n" + "="*60)
    print(f"Testing Concurrent Operations Memory Usage ({num_operations} operations)")
    print("="*60)
    
    monitor = MemoryMonitor()
    monitor.print_memory_stats("Baseline (before operations)")
    
    # Simulate concurrent operations by creating multiple clients
    clients = []
    for i in range(num_operations):
        try:
            client = OpenRouterClient()
            clients.append(client)
            if i % 3 == 0:
                monitor.print_memory_stats(f"After creating {i+1} clients")
        except Exception as e:
            print(f"Error creating client {i}: {e}")
    
    monitor.print_memory_stats(f"After creating all {num_operations} clients")
    
    # Cleanup
    clients.clear()
    monitor.print_memory_stats("After cleanup")
    
    max_memory_mb = monitor.get_memory_usage()
    max_memory_gb = max_memory_mb / 1024
    
    # With 10 concurrent users, total memory should still be reasonable
    # Each worker should use < 2GB, so 10 users shouldn't exceed ~4GB total
    max_threshold_gb = 4.0
    
    print(f"\n{'='*60}")
    print(f"Maximum memory usage: {max_memory_gb:.3f} GB")
    print(f"Memory per operation: {max_memory_mb/num_operations:.2f} MB")
    if max_memory_gb < max_threshold_gb:
        print(f"✅ PASS: Memory usage ({max_memory_gb:.3f} GB) < {max_threshold_gb}GB target for {num_operations} users")
    else:
        print(f"❌ FAIL: Memory usage ({max_memory_gb:.3f} GB) >= {max_threshold_gb}GB target for {num_operations} users")
    print(f"{'='*60}\n")


def print_system_info():
    """Print system information"""
    print("\n" + "="*60)
    print("System Information")
    print("="*60)
    
    # CPU info
    print(f"CPU count: {psutil.cpu_count()}")
    print(f"CPU percent: {psutil.cpu_percent(interval=1)}%")
    
    # Memory info
    mem = psutil.virtual_memory()
    print(f"Total memory: {mem.total / (1024**3):.2f} GB")
    print(f"Available memory: {mem.available / (1024**3):.2f} GB")
    print(f"Memory percent used: {mem.percent}%")
    
    # Disk info
    disk = psutil.disk_usage('/')
    print(f"Total disk: {disk.total / (1024**3):.2f} GB")
    print(f"Free disk: {disk.free / (1024**3):.2f} GB")
    print(f"Disk percent used: {disk.percent}%")
    print("="*60 + "\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Memory profiling for BookGen system"
    )
    parser.add_argument(
        "--test",
        choices=["openrouter", "validation", "concurrent", "all"],
        default="all",
        help="Which test to run"
    )
    parser.add_argument(
        "--concurrent-users",
        type=int,
        default=10,
        help="Number of concurrent users to simulate (default: 10)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("BookGen Memory Profiling")
    print("="*60)
    
    print_system_info()
    
    if args.test in ["openrouter", "all"]:
        test_openrouter_memory()
    
    if args.test in ["validation", "all"]:
        test_length_validation_memory()
    
    if args.test in ["concurrent", "all"]:
        test_concurrent_operations_memory(args.concurrent_users)
    
    print("\n" + "="*60)
    print("Memory Profiling Complete")
    print("="*60)
    print("\nFor detailed line-by-line profiling, run:")
    print("  python -m memory_profiler scripts/profile_memory.py")
    print("\n")


if __name__ == "__main__":
    main()
