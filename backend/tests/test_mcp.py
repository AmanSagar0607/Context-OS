# tests/test_mcp.py
"""MCP server endpoint tests."""


def test_mcp_tools_list(client):
    response = client.get("/api/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0


def test_mcp_health(client):
    response = client.get("/api/mcp/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in ["healthy", "ok"]
