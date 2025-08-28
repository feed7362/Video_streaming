from fastapi import FastAPI

from ..main import app


def test_app_exists() -> None:
    assert isinstance(app, FastAPI)
