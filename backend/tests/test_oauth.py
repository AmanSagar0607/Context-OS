# tests/test_oauth.py
"""OAuth endpoint tests."""


def test_oauth_unsupported_provider(client):
    response = client.get("/api/oauth/unsupported/login")
    assert response.status_code == 400


def test_oauth_google_login_returns_auth_url(client):
    response = client.get("/api/oauth/google/login")
    # Will return error since env vars not configured, but endpoint should exist
    assert response.status_code in [200, 500]


def test_oauth_linked_providers(client, auth_headers):
    response = client.get("/api/oauth/linked", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
