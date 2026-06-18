# tests/test_health.py
"""Health endpoint tests."""


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_includes_postgres(client):
    response = client.get("/health")
    data = response.json()
    assert "postgres_connected" in data


def test_health_includes_step(client):
    response = client.get("/health")
    data = response.json()
    assert "step" in data
