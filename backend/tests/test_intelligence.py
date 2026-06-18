# tests/test_intelligence.py
"""Intelligence pipeline tests."""


def test_intelligence_health(client):
    response = client.get("/api/intelligence/health")
    assert response.status_code == 200
    data = response.json()
    assert "planner" in data
    assert "router" in data


def test_intelligence_stats(client, auth_headers):
    response = client.get("/api/intelligence/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Stats may contain KG data or agent data
    assert isinstance(data, dict)


def test_intelligence_plan(client, auth_headers):
    response = client.post(
        "/api/intelligence/plan",
        json={"query": "What is machine learning?"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "steps" in data
    assert "query_type" in data
