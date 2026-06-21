# MCP Overview

> MCP protocol support in ContextOS.

## Overview

ContextOS provides MCP (Model Context Protocol) servers that AI agents can use to access memory, search, crawl, and knowledge capabilities.

## Quick Start

### With Cursor

Add to your Cursor settings:

```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp"
    }
  }
}
```

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp"
    }
  }
}
```

## MCP Tools

### Memory Tools

| Tool | Description |
|------|-------------|
| `memory_add` | Add a new memory |
| `memory_search` | Search memories |
| `memory_get` | Get a memory by ID |
| `memory_context` | Get context window |

### Search Tools

| Tool | Description |
|------|-------------|
| `search_web` | Search the internet |
| `search_internal` | Search internal knowledge |

### Crawl Tools

| Tool | Description |
|------|-------------|
| `crawl_scrape` | Scrape a URL |
| `crawl_crawl` | Crawl a website |
| `crawl_map` | Map site structure |
| `crawl_extract` | AI extraction |

### Knowledge Tools

| Tool | Description |
|------|-------------|
| `knowledge_add_entity` | Add knowledge entity |
| `knowledge_add_relationship` | Add relationship |
| `knowledge_query` | Query knowledge graph |

## REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/mcp` | POST | MCP JSON-RPC |
| `/api/v1/mcp/tools` | GET | List available tools |
