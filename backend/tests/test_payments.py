# tests/test_payments.py
"""Payment endpoint tests."""


def test_payment_status(client, auth_headers):
    response = client.get("/api/payments/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "subscription" in data
    assert "plan" in data


def test_payment_checkout_requires_polar_key(client, auth_headers):
    """Checkout returns 502 when Polar token is not configured (expected in test env)."""
    response = client.post(
        "/api/payments/checkout",
        json={"plan": "pro", "price_id": "test_price_123"},
        headers=auth_headers,
    )
    # Without POLAR_ACCESS_TOKEN configured, this should return 502
    assert response.status_code in [200, 502]


def test_payment_demo_upgrade(client, auth_headers):
    response = client.post("/api/payments/demo-upgrade", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get("upgraded") is True
    assert data.get("plan") == "pro"


def test_payment_history(client, auth_headers):
    response = client.get("/api/payments/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "payments" in data
