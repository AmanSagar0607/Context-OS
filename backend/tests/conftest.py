# tests/conftest.py
"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    import json
    return {
        "x-auth-context": json.dumps({
            "authenticated": True,
            "user": {"id": "a4ab6f1f-492d-4713-8129-1010abb95fd2", "email": "test@gmail.com"},
            "session_token": "test-token",
            "scopes": ["rag", "agents", "memory", "documents", "crawl:search", "crawl:scrape", "crawl:map"],
        })
    }
