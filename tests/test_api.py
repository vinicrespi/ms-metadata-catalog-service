from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_metadata_health_endpoint() -> None:
        response = client.get("/health")
        assert response.status_code == 200