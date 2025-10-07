"""
Basic tests for the BookGen API
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected structure"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data


def test_api_status():
    """Test the API status endpoint"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert data["api_version"] == "v1"
    assert "status" in data
    assert data["status"] == "operational"
    assert "services" in data
    assert "configuration" in data


def test_health_check_structure():
    """Test health check returns all required fields"""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "timestamp", "environment", "debug"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
