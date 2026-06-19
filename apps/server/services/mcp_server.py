# apps/server/services/mcp_server.py
"""
MCP Server — Model Context Protocol implementation for Context OS.

Exposes tools via MCP protocol with 4 tool groups:
  - Memory: add, get, search, delete, context, list, related
  - Search: web, internal
  - Crawl: scrape, crawl, map, extract
  - Knowledge: create_entity, get_entity, delete_entity, create_relationship, get_graph, search

Supports both stdio and HTTP SSE transports.
MCP Protocol: JSON-RPC 2.0 over HTTP SSE or stdio.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

# ── MCP Tool Definitions ──────────────────────────────────────────────────

MCP_TOOLS = [
    # ── Memory Tools ──────────────────────────────────────────────────────
    {
        "name": "context_os.memory.add",
        "group": "memory",
        "description": "Store a new memory with content, type, importance, and tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Memory content"},
                "summary": {"type": "string", "description": "Optional summary"},
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"], "default": "episodic"},
                "importance": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                "source": {"type": "string", "description": "Optional source"},
                "agent_id": {"type": "string", "description": "Optional agent ID"},
                "session_id": {"type": "string", "description": "Optional session ID"},
            },
            "required": ["content"],
        },
    },
    {
        "name": "context_os.memory.get",
        "group": "memory",
        "description": "Get a memory by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "Memory ID"},
            },
            "required": ["memory_id"],
        },
    },
    {
        "name": "context_os.memory.update",
        "group": "memory",
        "description": "Update an existing memory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "Memory ID"},
                "content": {"type": "string", "description": "New content"},
                "summary": {"type": "string", "description": "New summary"},
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]},
                "importance": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["memory_id"],
        },
    },
    {
        "name": "context_os.memory.delete",
        "group": "memory",
        "description": "Delete a memory by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "Memory ID"},
            },
            "required": ["memory_id"],
        },
    },
    {
        "name": "context_os.memory.search",
        "group": "memory",
        "description": "Search memories using semantic vector search.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "top_k": {"type": "integer", "default": 5, "description": "Max results"},
                "min_score": {"type": "number", "default": 0.5, "description": "Min similarity score"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "context_os.memory.context",
        "group": "memory",
        "description": "Get assembled context window from memories for a given query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query to assemble context for"},
                "max_tokens": {"type": "integer", "default": 2000, "description": "Max tokens in context"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "context_os.memory.list",
        "group": "memory",
        "description": "List memories with optional type filter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]},
                "limit": {"type": "integer", "default": 50},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "context_os.memory.related",
        "group": "memory",
        "description": "Get related memories for a given memory ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "Memory ID"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["memory_id"],
        },
    },

    # ── Search Tools ──────────────────────────────────────────────────────
    {
        "name": "context_os.search.web",
        "group": "search",
        "description": "Search the web using multi-provider search.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5, "description": "Max results"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "context_os.search.internal",
        "group": "search",
        "description": "Internal hybrid search across memory, knowledge, and documents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "default": 10, "description": "Max results"},
            },
            "required": ["query"],
        },
    },

    # ── Crawl Tools ───────────────────────────────────────────────────────
    {
        "name": "context_os.crawl.scrape",
        "group": "crawl",
        "description": "Scrape a single URL and return structured content (markdown, HTML, text).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to scrape"},
                "formats": {"type": "array", "items": {"type": "string", "enum": ["markdown", "html", "text"]}, "default": ["markdown"]},
                "instruction": {"type": "string", "description": "Optional AI instruction for targeted extraction"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "context_os.crawl.crawl",
        "group": "crawl",
        "description": "Crawl a website starting from a URL, following links to extract content from multiple pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Starting URL to crawl"},
                "max_pages": {"type": "integer", "default": 10, "description": "Max pages to crawl"},
                "instruction": {"type": "string", "description": "Optional AI instruction for extraction"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "context_os.crawl.map",
        "group": "crawl",
        "description": "Map the structure of a website, discovering all internal links and pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Starting URL to map"},
                "max_pages": {"type": "integer", "default": 50, "description": "Max pages to map"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "context_os.crawl.extract",
        "group": "crawl",
        "description": "Extract structured data from a URL using AI-powered analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to extract from"},
                "instruction": {"type": "string", "description": "Instruction describing what to extract"},
            },
            "required": ["url", "instruction"],
        },
    },

    # ── Knowledge Tools ───────────────────────────────────────────────────
    {
        "name": "context_os.knowledge.create_entity",
        "group": "knowledge",
        "description": "Create an entity in the knowledge graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Entity name"},
                "entity_type": {"type": "string", "default": "concept", "description": "Entity type"},
                "description": {"type": "string", "description": "Optional description"},
                "properties": {"type": "object", "description": "Optional properties"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "context_os.knowledge.get_entity",
        "group": "knowledge",
        "description": "Get a knowledge graph entity by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "context_os.knowledge.delete_entity",
        "group": "knowledge",
        "description": "Delete a knowledge graph entity by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "context_os.knowledge.create_relationship",
        "group": "knowledge",
        "description": "Create a relationship between two entities in the knowledge graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_id": {"type": "string", "description": "Source entity ID"},
                "target_id": {"type": "string", "description": "Target entity ID"},
                "relationship_type": {"type": "string", "default": "related_to", "description": "Relationship type"},
                "weight": {"type": "number", "default": 1.0, "description": "Relationship weight"},
            },
            "required": ["source_id", "target_id"],
        },
    },
    {
        "name": "context_os.knowledge.get_graph",
        "group": "knowledge",
        "description": "Get the knowledge graph for an entity, including neighbors up to a given depth.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID"},
                "depth": {"type": "integer", "default": 2, "description": "Graph traversal depth"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "context_os.knowledge.search",
        "group": "knowledge",
        "description": "Search entities in the knowledge graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "entity_type": {"type": "string", "description": "Filter by entity type"},
                "top_k": {"type": "integer", "default": 10, "description": "Max results"},
            },
            "required": ["query"],
        },
    },
]

# ── MCP Protocol Handlers ─────────────────────────────────────────────────

MCP_SERVER_INFO = {
    "name": "context-os",
    "version": "0.1.0",
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


def _make_result(content: Any) -> dict:
    """Wrap result in MCP content format."""
    if isinstance(content, str):
        text = content
    else:
        text = json.dumps(content, indent=2, default=str)
    return {
        "content": [
            {"type": "text", "text": text}
        ],
    }


def _make_error(message: str) -> dict:
    """Build an error result."""
    return {
        "content": [
            {"type": "text", "text": json.dumps({"error": message})}
        ],
        "isError": True,
    }


async def _handle_tool_call(name: str, arguments: dict) -> dict:
    """Execute an MCP tool and return the result."""
    start = time.time()

    try:
        # ── Memory Tools ──────────────────────────────────────────────────
        if name == "context_os.memory.add":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            result = await svc.add(
                content=arguments["content"],
                summary=arguments.get("summary"),
                memory_type=arguments.get("memory_type", "episodic"),
                importance=arguments.get("importance", "medium"),
                tags=arguments.get("tags", []),
                source=arguments.get("source"),
                agent_id=arguments.get("agent_id"),
                session_id=arguments.get("session_id"),
            )
            return _make_result(result)

        elif name == "context_os.memory.get":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            result = await svc.get(arguments["memory_id"])
            if result is None:
                return _make_error(f"Memory not found: {arguments['memory_id']}")
            return _make_result(result)

        elif name == "context_os.memory.update":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            result = await svc.update(
                memory_id=arguments["memory_id"],
                content=arguments.get("content"),
                summary=arguments.get("summary"),
                memory_type=arguments.get("memory_type"),
                importance=arguments.get("importance"),
                tags=arguments.get("tags"),
            )
            if result is None:
                return _make_error(f"Memory not found: {arguments['memory_id']}")
            return _make_result(result)

        elif name == "context_os.memory.delete":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            deleted = await svc.delete(arguments["memory_id"])
            return _make_result({"deleted": deleted, "memory_id": arguments["memory_id"]})

        elif name == "context_os.memory.search":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            results = await svc.search(
                query=arguments["query"],
                memory_type=arguments.get("memory_type"),
                tags=arguments.get("tags"),
                top_k=arguments.get("top_k", 5),
                min_score=arguments.get("min_score", 0.5),
            )
            return _make_result({"results": results, "count": len(results)})

        elif name == "context_os.memory.context":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            result = await svc.context(
                query=arguments["query"],
                max_tokens=arguments.get("max_tokens", 2000),
            )
            return _make_result(result)

        elif name == "context_os.memory.list":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            results = await svc.list(
                memory_type=arguments.get("memory_type"),
                limit=arguments.get("limit", 50),
                offset=arguments.get("offset", 0),
            )
            return _make_result({"memories": results, "count": len(results)})

        elif name == "context_os.memory.related":
            from apps.server.services.memory_service import MemoryService
            svc = MemoryService()
            results = await svc.related(
                memory_id=arguments["memory_id"],
                limit=arguments.get("limit", 10),
            )
            return _make_result({"memories": results, "count": len(results)})

        # ── Search Tools ──────────────────────────────────────────────────
        elif name == "context_os.search.web":
            from apps.server.services.search_service import SearchService
            svc = SearchService()
            results = await svc.web(
                query=arguments["query"],
                max_results=arguments.get("max_results", 5),
            )
            return _make_result({"results": results, "count": len(results)})

        elif name == "context_os.search.internal":
            from apps.server.services.search_service import SearchService
            svc = SearchService()
            results = await svc.internal(
                query=arguments["query"],
                top_k=arguments.get("top_k", 10),
            )
            return _make_result({"results": results, "count": len(results)})

        # ── Crawl Tools ───────────────────────────────────────────────────
        elif name == "context_os.crawl.scrape":
            from backend.services.crawl_service import scrape_url
            result = await scrape_url(
                url=arguments["url"],
                formats=arguments.get("formats", ["markdown"]),
                instruction=arguments.get("instruction"),
            )
            return _make_result(result)

        elif name == "context_os.crawl.crawl":
            from backend.services.crawl_service import crawl_site
            result = await crawl_site(
                url=arguments["url"],
                max_pages=arguments.get("max_pages", 10),
                instruction=arguments.get("instruction"),
            )
            return _make_result(result)

        elif name == "context_os.crawl.map":
            from backend.services.crawl_service import map_site
            result = await map_site(
                url=arguments["url"],
                max_pages=arguments.get("max_pages", 50),
            )
            return _make_result(result)

        elif name == "context_os.crawl.extract":
            from backend.services.agent_service import scrape_and_extract
            result = await scrape_and_extract(
                url=arguments["url"],
                instruction=arguments["instruction"],
            )
            return _make_result(result)

        # ── Knowledge Tools ───────────────────────────────────────────────
        elif name == "context_os.knowledge.create_entity":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            result = await svc.create_entity(
                name=arguments["name"],
                entity_type=arguments.get("entity_type", "concept"),
                description=arguments.get("description"),
                properties=arguments.get("properties", {}),
            )
            return _make_result(result)

        elif name == "context_os.knowledge.get_entity":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            result = await svc.get_entity(arguments["entity_id"])
            if result is None:
                return _make_error(f"Entity not found: {arguments['entity_id']}")
            return _make_result(result)

        elif name == "context_os.knowledge.delete_entity":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            deleted = await svc.delete_entity(arguments["entity_id"])
            return _make_result({"deleted": deleted, "entity_id": arguments["entity_id"]})

        elif name == "context_os.knowledge.create_relationship":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            result = await svc.create_relationship(
                source_id=arguments["source_id"],
                target_id=arguments["target_id"],
                relationship_type=arguments.get("relationship_type", "related_to"),
                weight=arguments.get("weight", 1.0),
            )
            return _make_result(result)

        elif name == "context_os.knowledge.get_graph":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            result = await svc.get_graph(
                entity_id=arguments["entity_id"],
                depth=arguments.get("depth", 2),
            )
            return _make_result(result)

        elif name == "context_os.knowledge.search":
            from apps.server.services.knowledge_service import KnowledgeService
            svc = KnowledgeService()
            results = await svc.search(
                query=arguments["query"],
                entity_type=arguments.get("entity_type"),
                top_k=arguments.get("top_k", 10),
            )
            return _make_result({"entities": results, "count": len(results)})

        else:
            return _make_error(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"MCP tool call {name} failed: {e}")
        return _make_error(str(e))


async def _handle_request(body: dict) -> dict | None:
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


# ── HTTP Transport ────────────────────────────────────────────────────────

@router.post("")
async def mcp_http_endpoint(request: Request):
    """
    MCP HTTP endpoint. Accepts JSON-RPC requests and returns responses.
    Supports both single requests and batch requests.
    """
    body = await request.json()

    if isinstance(body, list):
        responses = []
        for req in body:
            resp = await _handle_request(req)
            if resp is not None:
                responses.append(resp)
        return responses

    resp = await _handle_request(body)
    if resp is None:
        return {"status": "ok"}
    return resp


@router.post("/sse")
async def mcp_sse_endpoint(request: Request):
    """
    MCP SSE endpoint. Accepts JSON-RPC requests and streams responses via SSE.
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
    """List available MCP tools grouped by category."""
    groups = {}
    for tool in MCP_TOOLS:
        group = tool.get("group", "other")
        if group not in groups:
            groups[group] = []
        groups[group].append(tool)
    return {
        "tools": MCP_TOOLS,
        "groups": groups,
        "total": len(MCP_TOOLS),
    }


@router.get("/health")
async def mcp_health():
    """MCP server health check."""
    groups = {}
    for tool in MCP_TOOLS:
        group = tool.get("group", "other")
        groups[group] = groups.get(group, 0) + 1

    return {
        "status": "ok",
        "server": MCP_SERVER_INFO,
        "tools_count": len(MCP_TOOLS),
        "groups": groups,
        "protocol_version": "2024-11-05",
    }