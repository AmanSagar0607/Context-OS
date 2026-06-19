---
sidebar_position: 11
title: MCP Server
---

# MCP Server

Model Context Protocol server for Context OS.

## Overview

The MCP server exposes Context OS tools via the MCP protocol:

- **Memory Tools** (8): Add, get, update, delete, search, context, list, related
- **Search Tools** (2): Web search, internal search
- **Crawl Tools** (4): Scrape, crawl, map, extract
- **Knowledge Tools** (6): Create entity, get entity, delete entity, create relationship, get graph, search

## Transport

### HTTP (JSON-RPC)

```bash
# Single request
curl -X POST http://localhost:8000/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# SSE
curl -X POST http://localhost:8000/api/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "context_os.memory.add",
      "arguments": {
        "content": "User prefers dark mode"
      }
    }
  }'
```

## Tools

### Memory Tools

| Tool | Description |
|------|-------------|
| `context_os.memory.add` | Store a new memory |
| `context_os.memory.get` | Get a memory by ID |
| `context_os.memory.update` | Update a memory |
| `context_os.memory.delete` | Delete a memory |
| `context_os.memory.search` | Search memories |
| `context_os.memory.context` | Get context window |
| `context_os.memory.list` | List memories |
| `context_os.memory.related` | Get related memories |

### Search Tools

| Tool | Description |
|------|-------------|
| `context_os.search.web` | Web search |
| `context_os.search.internal` | Internal hybrid search |

### Crawl Tools

| Tool | Description |
|------|-------------|
| `context_os.crawl.scrape` | Scrape a URL |
| `context_os.crawl.crawl` | Crawl a website |
| `context_os.crawl.map` | Map a website |
| `context_os.crawl.extract` | AI extraction |

### Knowledge Tools

| Tool | Description |
|------|-------------|
| `context_os.knowledge.create_entity` | Create entity |
| `context_os.knowledge.get_entity` | Get entity |
| `context_os.knowledge.delete_entity` | Delete entity |
| `context_os.knowledge.create_relationship` | Create relationship |
| `context_os.knowledge.get_graph` | Get graph |
| `context_os.knowledge.search` | Search entities |

## Usage with Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "context-os": {
      "url": "http://localhost:8000/api/mcp"
    }
  }
}
```

## Usage with Cursor

Add to your Cursor MCP config:

```json
{
  "mcpServers": {
    "context-os": {
      "url": "http://localhost:8000/api/mcp"
    }
  }
}
```