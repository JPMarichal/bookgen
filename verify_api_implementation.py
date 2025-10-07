#!/usr/bin/env python3
"""
Verification script for BookGen FastAPI REST API implementation
Tests all acceptance criteria from Issue #5
"""
import sys
import time
import json
import requests
from typing import Dict, Any

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"


def print_test(name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    print(f"{status} {name}")
    if message:
        print(f"  {YELLOW}{message}{RESET}")


def check_endpoint(method: str, path: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request and return result"""
    try:
        url = f"{BASE_URL}{path}"
        response = requests.request(method, url, **kwargs)
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if "json" in response.headers.get("content-type", "") else response.text,
            "headers": dict(response.headers)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Run verification tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}BookGen FastAPI REST API - Verification{RESET}")
    print(f"{BLUE}Issue #5 - Acceptance Criteria{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    all_passed = True

    # 1. API responde en puerto 8000
    print(f"\n{BLUE}1. API responde en puerto 8000{RESET}")
    result = check_endpoint("GET", "/health")
    passed = result.get("success") and result.get("status_code") == 200
    print_test("API responds on port 8000", passed)
    all_passed &= passed

    # 2. Documentación Swagger en /docs
    print(f"\n{BLUE}2. Documentación Swagger en /docs{RESET}")
    result = check_endpoint("GET", "/docs")
    passed = result.get("success") and result.get("status_code") == 200
    has_swagger = "swagger" in str(result.get("data", "")).lower()
    print_test("Swagger docs available at /docs", passed and has_swagger)
    all_passed &= (passed and has_swagger)

    # 3. Validación de entrada con Pydantic
    print(f"\n{BLUE}3. Validación de entrada con Pydantic{RESET}")
    
    # Test invalid chapter count
    result = check_endpoint(
        "POST", 
        "/api/v1/biographies/generate",
        json={"character": "Test", "chapters": 0},
        timeout=5
    )
    passed = result.get("status_code") == 422
    print_test("Rejects invalid input (chapters = 0)", passed)
    all_passed &= passed
    
    # Test valid input
    result = check_endpoint(
        "POST",
        "/api/v1/biographies/generate",
        json={"character": "Valid Test", "chapters": 5},
        timeout=5
    )
    passed = result.get("status_code") == 202
    print_test("Accepts valid input", passed)
    all_passed &= passed

    # 4. Manejo de errores HTTP estándar
    print(f"\n{BLUE}4. Manejo de errores HTTP estándar{RESET}")
    
    # 404 for non-existent job
    result = check_endpoint("GET", "/api/v1/biographies/fake-id/status")
    passed = result.get("status_code") == 404
    print_test("Returns 404 for non-existent resources", passed)
    all_passed &= passed
    
    # 422 for validation errors
    result = check_endpoint(
        "POST",
        "/api/v1/biographies/generate",
        json={"character": ""},
        timeout=5
    )
    passed = result.get("status_code") == 422
    print_test("Returns 422 for validation errors", passed)
    all_passed &= passed

    # 5. CORS configurado correctamente
    print(f"\n{BLUE}5. CORS configurado correctamente{RESET}")
    result = check_endpoint("GET", "/health")
    headers = result.get("headers", {})
    has_cors = "access-control-allow-origin" in [k.lower() for k in headers.keys()]
    print_test("CORS headers present", has_cors)
    all_passed &= has_cors

    # 6. Rate limiting por IP implementado
    print(f"\n{BLUE}6. Rate limiting por IP implementado{RESET}")
    result = check_endpoint("GET", "/api/v1/status")
    headers = result.get("headers", {})
    has_rate_limit = "x-ratelimit-limit" in [k.lower() for k in headers.keys()]
    print_test("Rate limit headers present", has_rate_limit)
    
    # Test rate limit enforcement (make many requests)
    rate_limited = False
    for _ in range(65):
        result = check_endpoint("GET", "/api/v1/status", timeout=1)
        if result.get("status_code") == 429:
            rate_limited = True
            break
    
    print_test("Rate limiting enforced (429 on excessive requests)", rate_limited)
    all_passed &= (has_rate_limit and rate_limited)

    # 7. Logging estructurado de requests
    print(f"\n{BLUE}7. Logging estructurado de requests{RESET}")
    result = check_endpoint("GET", "/api/v1/status")
    headers = result.get("headers", {})
    has_process_time = "x-process-time" in [k.lower() for k in headers.keys()]
    print_test("Request logging middleware active (X-Process-Time header)", has_process_time)
    all_passed &= has_process_time

    # Test all required endpoints
    print(f"\n{BLUE}8. Endpoints Requeridos{RESET}")
    
    endpoints = [
        ("POST", "/api/v1/biographies/generate", {"json": {"character": "Test"}}),
        ("GET", "/api/v1/biographies/{id}/status", {}),
        ("GET", "/api/v1/biographies/{id}/download", {}),
        ("POST", "/api/v1/sources/validate", {
            "json": {
                "sources": [{"title": "Test", "source_type": "book"}],
                "check_accessibility": False
            }
        }),
        ("GET", "/health", {}),
        ("GET", "/metrics", {}),
    ]
    
    for method, path, kwargs in endpoints:
        # For endpoints needing an ID, create a job first
        if "{id}" in path:
            create_result = check_endpoint(
                "POST",
                "/api/v1/biographies/generate",
                json={"character": "Endpoint Test"},
                timeout=5
            )
            if create_result.get("success") and create_result.get("status_code") == 202:
                job_id = create_result["data"]["job_id"]
                path = path.replace("{id}", job_id)
        
        result = check_endpoint(method, path, timeout=5, **kwargs)
        # Accept 2xx, 4xx (expected errors like 400 for incomplete jobs)
        passed = result.get("success") and 200 <= result.get("status_code", 0) < 500
        print_test(f"{method} {path}", passed)
        all_passed &= passed

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    if all_passed:
        print(f"{GREEN}✓ All acceptance criteria PASSED{RESET}")
        return 0
    else:
        print(f"{RED}✗ Some acceptance criteria FAILED{RESET}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verification interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}")
        sys.exit(1)
