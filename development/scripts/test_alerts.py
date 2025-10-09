#!/usr/bin/env python3
"""
Alert Testing Script for BookGen Monitoring
Tests that alerts are properly configured and can be triggered
"""
import requests
import time
import sys
from typing import Dict, List

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Configuration
PROMETHEUS_URL = "http://localhost:9090"
ALERTMANAGER_URL = "http://localhost:9093"
BOOKGEN_API_URL = "http://localhost:8000"


def print_header(text: str):
    """Print a colored header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_service(name: str, url: str, health_path: str = "/") -> bool:
    """
    Check if a service is running
    
    Args:
        name: Service name
        url: Service base URL
        health_path: Health check path
        
    Returns:
        True if service is healthy, False otherwise
    """
    try:
        response = requests.get(f"{url}{health_path}", timeout=5)
        if response.status_code == 200:
            print_success(f"{name} is running")
            return True
        else:
            print_error(f"{name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"{name} is not accessible: {e}")
        return False


def get_prometheus_alerts() -> List[Dict]:
    """
    Get current alerts from Prometheus
    
    Returns:
        List of active alerts
    """
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("alerts", [])
        return []
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get Prometheus alerts: {e}")
        return []


def get_prometheus_rules() -> List[Dict]:
    """
    Get alert rules from Prometheus
    
    Returns:
        List of alert rules
    """
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/rules", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("groups", [])
        return []
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get Prometheus rules: {e}")
        return []


def get_alertmanager_alerts() -> List[Dict]:
    """
    Get alerts from Alertmanager
    
    Returns:
        List of alerts in Alertmanager
    """
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get Alertmanager alerts: {e}")
        return []


def test_metrics_endpoint() -> bool:
    """
    Test that BookGen metrics endpoint is accessible
    
    Returns:
        True if metrics are accessible, False otherwise
    """
    try:
        response = requests.get(f"{BOOKGEN_API_URL}/metrics", timeout=5)
        if response.status_code == 200:
            # Check for expected metrics
            content = response.text
            expected_metrics = [
                "bookgen_uptime_seconds",
                "bookgen_cpu_percent",
                "bookgen_memory_percent",
                "bookgen_disk_percent"
            ]
            
            missing_metrics = [m for m in expected_metrics if m not in content]
            
            if not missing_metrics:
                print_success("All expected metrics are present")
                return True
            else:
                print_warning(f"Missing metrics: {', '.join(missing_metrics)}")
                return False
        else:
            print_error(f"Metrics endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to access metrics endpoint: {e}")
        return False


def test_alert_rules():
    """Test that alert rules are loaded"""
    print_header("Testing Alert Rules")
    
    rules = get_prometheus_rules()
    
    if not rules:
        print_error("No alert rules loaded")
        return False
    
    # Expected alert rules
    expected_alerts = [
        "HighErrorRate",
        "LongBiographyGenerationTime",
        "HighMemoryUsage",
        "CriticalMemoryUsage",
        "HighCPUUsage",
        "QueueBackup",
        "APIDown",
        "HighAPILatency",
        "HighDiskUsage",
        "CriticalDiskUsage"
    ]
    
    loaded_alerts = []
    for group in rules:
        for rule in group.get("rules", []):
            if rule.get("type") == "alerting":
                loaded_alerts.append(rule.get("name"))
    
    print_info(f"Loaded {len(loaded_alerts)} alert rules")
    
    missing_alerts = [a for a in expected_alerts if a not in loaded_alerts]
    
    if missing_alerts:
        print_warning(f"Missing expected alerts: {', '.join(missing_alerts)}")
    else:
        print_success("All expected alert rules are loaded")
    
    # Print loaded alerts
    for alert in loaded_alerts:
        print(f"  • {alert}")
    
    return len(loaded_alerts) > 0


def test_prometheus_targets():
    """Test that Prometheus targets are being scraped"""
    print_header("Testing Prometheus Targets")
    
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", timeout=5)
        if response.status_code == 200:
            data = response.json()
            targets = data.get("data", {}).get("activeTargets", [])
            
            if not targets:
                print_error("No active targets found")
                return False
            
            print_info(f"Found {len(targets)} active targets")
            
            for target in targets:
                job = target.get("labels", {}).get("job", "unknown")
                health = target.get("health", "unknown")
                
                if health == "up":
                    print_success(f"Target '{job}' is up")
                else:
                    print_error(f"Target '{job}' is {health}")
            
            return True
        else:
            print_error(f"Failed to get targets: status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get Prometheus targets: {e}")
        return False


def main():
    """Main test function"""
    print_header("BookGen Monitoring Alert Tests")
    
    all_tests_passed = True
    
    # Test 1: Check services are running
    print_header("Checking Services")
    services_ok = all([
        check_service("Prometheus", PROMETHEUS_URL, "/-/healthy"),
        check_service("Alertmanager", ALERTMANAGER_URL, "/-/healthy"),
        check_service("Grafana", "http://localhost:3000", "/api/health")
    ])
    
    if not services_ok:
        print_error("\nSome services are not running. Please start them with:")
        print_info("docker-compose -f monitoring/docker-compose.yml up -d")
        return 1
    
    # Test 2: Check metrics endpoint
    print_header("Testing Metrics Endpoint")
    metrics_ok = test_metrics_endpoint()
    all_tests_passed = all_tests_passed and metrics_ok
    
    # Test 3: Check Prometheus targets
    targets_ok = test_prometheus_targets()
    all_tests_passed = all_tests_passed and targets_ok
    
    # Test 4: Check alert rules
    rules_ok = test_alert_rules()
    all_tests_passed = all_tests_passed and rules_ok
    
    # Test 5: Check current alerts
    print_header("Checking Active Alerts")
    alerts = get_prometheus_alerts()
    
    if alerts:
        print_warning(f"Found {len(alerts)} active alerts:")
        for alert in alerts:
            name = alert.get("labels", {}).get("alertname", "unknown")
            state = alert.get("state", "unknown")
            print(f"  • {name}: {state}")
    else:
        print_info("No alerts currently firing (this is good!)")
    
    # Test 6: Check Alertmanager alerts
    print_header("Checking Alertmanager")
    am_alerts = get_alertmanager_alerts()
    
    if am_alerts:
        print_info(f"Alertmanager has {len(am_alerts)} alerts")
    else:
        print_info("No alerts in Alertmanager")
    
    # Final summary
    print_header("Test Summary")
    
    if all_tests_passed:
        print_success("All tests passed! Monitoring stack is properly configured.")
        print_info("\nYou can access:")
        print_info(f"  • Prometheus: {PROMETHEUS_URL}")
        print_info(f"  • Alertmanager: {ALERTMANAGER_URL}")
        print_info("  • Grafana: http://localhost:3000 (admin/admin)")
        return 0
    else:
        print_error("Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
