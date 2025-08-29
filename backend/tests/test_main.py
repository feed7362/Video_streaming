from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..src import services

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_services(monkeypatch) -> None:
    monkeypatch.setattr(services.rabbit_client.rabbit_broker, "connect", AsyncMock())
    monkeypatch.setattr(services.rabbit_client.rabbit_broker, "close", AsyncMock())
    monkeypatch.setattr(services.s3_client, "check_bucket_exists", AsyncMock())


def test_read_root() -> None:
    response = client.get("/api/health/live")
    assert response.status_code == 200
