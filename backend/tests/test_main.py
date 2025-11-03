import sys
import types

from fastapi.testclient import TestClient


class FakeVaultClient:
    def __init__(self, *a, **kw) -> None:
        pass

    def read_secret(self, path: str, mount_point: str = "secret") -> dict:
        return {
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
        }


fake_vault_module = types.ModuleType("src.infrastructure.vault")
fake_vault_module.VaultClient = FakeVaultClient  # type: ignore[attr-defined]
sys.modules["src.infrastructure.vault"] = fake_vault_module

from ..main import create_app  # noqa: E402


def test_read_root() -> None:
    app = create_app(use_lifespan=False)
    client = TestClient(app)
    response = client.get("/api/health/live")
    assert response.status_code == 200
