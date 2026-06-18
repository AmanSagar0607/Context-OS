# services/mcp_server.py
"""
MCP Server — Model Context Protocol implementation for AmanCrawl.

Exposes AmanCrawl tools (scrape, crawl, map, search, extract) via the MCP protocol.
Supports both stdio and HTTP SSE transports.

MCP Protocol: JSON-RPC 2.0 over HTTP SSE or stdio.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from services.crawl_service import scrape_url, crawl_site, map_site, search_web
from services.agent_service import scrape_and_extract

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

# ── MCP Tool Definitions ──────────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "amancrawl.scrape",
        "description": "Scrape a single URL and return structured content (markdown, HTML, text). Supports AI instructions for targeted extraction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape",
                },
                "formats": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["markdown", "html", "text"]},
                    "default": ["markdown"],
                    "description": "Output formats to return",
                },
                "instruction": {
                    "type": "string",
                    "description": "Optional AI instruction for targeted extraction",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "amancrawl.crawl",
        "description": "Crawl a website starting from a URL, following links to extract content from multiple pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The starting URL to crawl",
                },
                "max_pages": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of pages to crawl",
                },
                "instruction": {
                    "type": "string",
                    "description": "Optional AI instruction for extraction",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "amancrawl.map",
        "description": "Map the structure of a website, discovering all internal links and pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The starting URL to map",
                },
                "instruction": {
                    "type": "string",
                    "description": "Optional instruction for what to look for",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "amancrawl.search",
        "description": "Search the web for information using multi-provider search.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
                "num_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Number of results to return",
                },
                "instruction": {
                    "type": "string",
                    "description": "Optional instruction for what to find",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "amancrawl.extract",
        "description": "Extract structured data from a URL using AI-powered analysis. Returns extracted entities, relationships, and structured information.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to extract data from",
                },
                "instruction": {
                    "type": "string",
                    "description": "Instruction describing what data to extract",
                },
            },
            "required": ["url", "instruction"],
        },
    },
]

# ── MCP Protocol Handlers ─────────────────────────────────────────────────

MCP_SERVER_INFO = {
    "name": "amancrawl",
    "version": "1.0.0",
}

MCP_CAPABILITIES = {
    "tools": {},
}


def _jsonrpc_response(request_id: int | str, result: Any) -> dict:
    """Build a JSON-RPC 2.0 success response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _jsonrpc_error(request_id: int | str | None, code: int, message: str, data: Any = None) -> dict:
    """Build a JSON-RPC 2.0 error response."""
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error,
    }


async def _handle_tool_call(name: str, arguments: dict) -> dict:
    """Execute an MCP tool and return the result."""
    start = time.time()

    try:
        if name == "amancrawl.scrape":
            result = await scrape_url(
                url=arguments["url"],
                formats=arguments.get("formats", ["markdown"]),
                instruction=arguments.get("instruction"),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        elif name == "amancrawl.crawl":
            result = await crawl_site(
                url=arguments["url"],
                max_pages=arguments.get("max_pages", 10),
                instruction=arguments.get("instruction"),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        elif name == "amancrawl.map":
            result = await map_site(
                url=arguments["url"],
                instruction=arguments.get("instruction"),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        elif name == "amancrawl.search":
            result = await search_web(
                query=arguments["query"],
                num_results=arguments.get("num_results", 5),
                instruction=arguments.get("instruction"),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        elif name == "amancrawl.extract":
            result = await scrape_and_extract(
                url=arguments["url"],
                instruction=arguments["instruction"],
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"error": f"Unknown tool: {name}"}),
                    }
                ],
                "isError": True,
            }

    except Exception as e:
        logger.error(f"MCP tool call {name} failed: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": str(e)}),
                }
            ],
            "isError": True,
        }


async def _handle_request(body: dict) -> dict:
    """Handle a single JSON-RPC request."""
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if method == "initialize":
        return _jsonrpc_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": MCP_CAPABILITIES,
            "serverInfo": MCP_SERVER_INFO,
        })

    elif method == "notifications/initialized":
        # Client notification, no response needed
        return None

    elif method == "tools/list":
        return _jsonrpc_response(request_id, {
            "tools": MCP_TOOLS,
        })

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = await _handle_tool_call(tool_name, arguments)
        return _jsonrpc_response(request_id, result)

    elif method == "ping":
        return _jsonrpc_response(request_id, {})

    else:
        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")


# ── HTTP SSE Transport ────────────────────────────────────────────────────

@router.post("")
async def mcp_http_endpoint(request: Request):
    """
    MCP HTTP endpoint. Accepts JSON-RPC requests and returns responses.
    Supports both single requests and batch requests.
    """
    body = await request.json()

    # Handle batch requests
    if isinstance(body, list):
        responses = []
        for req in body:
            resp = await _handle_request(req)
            if resp is not None:
                responses.append(resp)
        return responses

    # Handle single request
    resp = await _handle_request(body)
    if resp is None:
        return {"status": "ok"}
    return resp


@router.post("/sse")
async def mcp_sse_endpoint(request: Request):
    """
    MCP SSE endpoint. Accepts JSON-RPC requests and streams responses via SSE.
    For clients that prefer Server-Sent Events transport.
    """
    body = await request.json()

    async def event_stream():
        resp = await _handle_request(body)
        if resp is not None:
            yield f"data: {json.dumps(resp)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/tools")
async def list_tools():
    """List available MCP tools (convenience endpoint)."""
    return {"tools": MCP_TOOLS}


@router.get("/health")
async def mcp_health():
    """MCP server health check."""
    return {
        "status": "ok",
        "server": MCP_SERVER_INFO,
        "tools_count": len(MCP_TOOLS),
        "protocol_version": "2024-11-05",
    }
