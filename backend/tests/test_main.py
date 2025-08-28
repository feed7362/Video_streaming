from fastapi import FastAPI

from ..main import app


def test_app_exists():
    assert isinstance(app, FastAPI)
