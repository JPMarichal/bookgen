from src.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_status_endpoint():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"
