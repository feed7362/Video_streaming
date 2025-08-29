from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/api/health/live")
    assert response.status_code == 200
