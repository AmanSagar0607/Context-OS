# Memory MCP Tools
> MCP tools for storing, searching, and retrieving agent memories.

## Overview

The Memory MCP tools give your AI agents persistent memory across conversations. Agents can store facts, decisions, and context, then search and retrieve them in future sessions. All operations use the ContextOS memory backend at `http://localhost:8000/api/v1/mcp`.

## Quick Start

1. Ensure ContextOS is running locally.
2. Connect your agent to the MCP endpoint.
3. Call memory tools via JSON-RPC.

## Tools

| Tool | Description |
|------|-------------|
| `memory_add` | Store a new memory with metadata |
| `memory_search` | Semantic search across stored memories |
| `memory_get` | Retrieve a specific memory by ID |
| `memory_context` | Get context-aware memories for a query |
| `memory_list` | List all stored memories with pagination |

## Examples

### Add a Memory

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "memory_add",
    "arguments": {
      "content": "User prefers dark mode in all applications",
      "category": "preference",
      "importance": "high",
      "tags": ["ui", "dark-mode"]
    }
  }
}
```

### Search Memories

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "memory_search",
    "arguments": {
      "query": "dark mode preferences",
      "limit": 5
    }
  }
}
```

### Get Context for a Conversation

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "memory_context",
    "arguments": {
      "query": "What does the user want for the dashboard?",
      "max_results": 3
    }
  }
}
```

### Retrieve a Specific Memory

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "memory_get",
    "arguments": {
      "memory_id": "mem_abc123"
    }
  }
}
```

## Best Practices

- Use `memory_context` before generating responses to ground output in known facts.
- Tag memories with descriptive categories for better retrieval.
- Set `importance` levels to prioritize critical information.
