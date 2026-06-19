"""
Context OS — MCP Server Tests

Tests for MCP server protocol handling and tool definitions.
"""

import pytest
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.mcp_server import (
    MCP_TOOLS,
    MCP_SERVER_INFO,
    MCP_CAPABILITIES,
    _jsonrpc_response,
    _jsonrpc_error,
    _make_result,
    _make_error,
    _handle_request,
)


class TestMCPToolDefinitions:
    def test_tools_count(self):
        assert len(MCP_TOOLS) == 20

    def test_memory_tools(self):
        memory_tools = [t for t in MCP_TOOLS if t["group"] == "memory"]
        assert len(memory_tools) == 8

    def test_search_tools(self):
        search_tools = [t for t in MCP_TOOLS if t["group"] == "search"]
        assert len(search_tools) == 2

    def test_crawl_tools(self):
        crawl_tools = [t for t in MCP_TOOLS if t["group"] == "crawl"]
        assert len(crawl_tools) == 4

    def test_knowledge_tools(self):
        knowledge_tools = [t for t in MCP_TOOLS if t["group"] == "knowledge"]
        assert len(knowledge_tools) == 6

    def test_all_tools_have_names(self):
        for tool in MCP_TOOLS:
            assert "name" in tool
            assert tool["name"].startswith("context_os.")

    def test_all_tools_have_schemas(self):
        for tool in MCP_TOOLS:
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_all_tools_have_groups(self):
        valid_groups = {"memory", "search", "crawl", "knowledge"}
        for tool in MCP_TOOLS:
            assert "group" in tool
            assert tool["group"] in valid_groups


class TestJSONRPC:
    def test_response(self):
        resp = _jsonrpc_response(1, {"key": "value"})
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert resp["result"] == {"key": "value"}

    def test_error(self):
        resp = _jsonrpc_error(1, -32601, "Not found")
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert resp["error"]["code"] == -32601
        assert resp["error"]["message"] == "Not found"

    def test_error_with_data(self):
        resp = _jsonrpc_error(1, -32600, "Invalid", {"details": "bad input"})
        assert resp["error"]["data"] == {"details": "bad input"}


class TestResultFormatting:
    def test_make_result_dict(self):
        result = _make_result({"key": "value"})
        assert result["content"][0]["type"] == "text"
        assert "key" in result["content"][0]["text"]

    def test_make_result_string(self):
        result = _make_result("hello")
        assert result["content"][0]["text"] == "hello"

    def test_make_error(self):
        result = _make_error("something went wrong")
        assert result["isError"] is True
        assert "error" in result["content"][0]["text"]


class TestRequestHandling:
    @pytest.mark.asyncio
    async def test_initialize(self):
        resp = await _handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert resp["result"]["protocolVersion"] == "2024-11-05"
        assert resp["result"]["serverInfo"]["name"] == "context-os"

    @pytest.mark.asyncio
    async def test_tools_list(self):
        resp = await _handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        assert len(resp["result"]["tools"]) == 20

    @pytest.mark.asyncio
    async def test_ping(self):
        resp = await _handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "ping",
            "params": {},
        })
        assert resp["result"] == {}

    @pytest.mark.asyncio
    async def test_unknown_method(self):
        resp = await _handle_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "unknown/method",
            "params": {},
        })
        assert resp["error"]["code"] == -32601

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        resp = await _handle_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "unknown.tool", "arguments": {}},
        })
        assert resp["result"]["isError"] is True