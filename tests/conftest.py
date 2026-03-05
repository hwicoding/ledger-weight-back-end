"""
pytest fixtures for ledger-weight-back-end tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient bound to the app."""
    return TestClient(app)
