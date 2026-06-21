# Search MCP Tools
> MCP tools for web search and internal semantic search.

## Overview

Search MCP tools let your agents find information from the web and internal knowledge bases. `search_web` uses Tavily for real-time web search. `search_internal` performs semantic search across your indexed documents.

## Quick Start

1. Ensure ContextOS is running locally.
2. Connect your agent to the MCP endpoint.
3. Call search tools via JSON-RPC.

## Tools

| Tool | Description |
|------|-------------|
| `search_web` | Web search via Tavily API |
| `search_internal` | Semantic search over internal documents |

## Examples

### Web Search

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_web",
    "arguments": {
      "query": "ContextOS MCP protocol 2025",
      "max_results": 5
    }
  }
}
```

### Internal Semantic Search

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_internal",
    "arguments": {
      "query": "authentication flow for agents",
      "namespace": "docs",
      "limit": 3
    }
  }
}
```

### Combined Search in Agent Flow

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_internal",
    "arguments": {
      "query": "deployment steps",
      "namespace": "engineering"
    }
  }
}
```

## Configuration

| Parameter | Description |
|-----------|-------------|
| `query` | Search query string (required) |
| `max_results` | Maximum results to return (default: 5) |
| `namespace` | Internal search namespace filter |

## Best Practices

- Use `search_internal` first for company-specific queries before falling back to web search.
- Keep internal document namespaces organized for better relevance.
- Combine results from both tools for comprehensive answers.
