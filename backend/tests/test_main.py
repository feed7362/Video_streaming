from fastapi.testclient import TestClient

from ..main import create_app


def test_read_root() -> None:
    app = create_app(use_lifespan=False)
    client = TestClient(app)
    response = client.get("/api/health/live")
    assert response.status_code == 200
