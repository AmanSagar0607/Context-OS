---
sidebar_position: 12
title: API Reference
---

# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

```bash
Authorization: Bearer <your-api-key>
```

## Memory API

### Add Memory

```
POST /api/v1/memory
```

**Request:**

```json
{
  "content": "User prefers dark mode",
  "summary": "UI preference",
  "memory_type": "semantic",
  "importance": "high",
  "tags": ["preferences", "ui"],
  "source": "user-settings"
}
```

**Response:**

```json
{
  "id": "mem-123",
  "content": "User prefers dark mode",
  "summary": "UI preference",
  "memory_type": "semantic",
  "importance": "high",
  "tags": ["preferences", "ui"],
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Get Memory

```
GET /api/v1/memory/{id}
```

### Update Memory

```
PUT /api/v1/memory/{id}
```

### Delete Memory

```
DELETE /api/v1/memory/{id}
```

### Search Memories

```
POST /api/v1/memory/search
```

**Request:**

```json
{
  "query": "dark mode",
  "memory_type": "semantic",
  "top_k": 10,
  "min_score": 0.7
}
```

### Get Context Window

```
POST /api/v1/memory/context
```

**Request:**

```json
{
  "query": "UI preferences",
  "max_tokens": 2000
}
```

### List Memories

```
GET /api/v1/memory?memory_type=semantic&limit=50&offset=0
```

### Get Related Memories

```
GET /api/v1/memory/{id}/related?limit=10
```

## Search API

### Web Search

```
POST /api/v1/search/web
```

**Request:**

```json
{
  "query": "AI news",
  "max_results": 5
}
```

### Internal Search

```
POST /api/v1/search/internal
```

## Knowledge API

### Create Entity

```
POST /api/v1/knowledge/entities
```

**Request:**

```json
{
  "name": "GPT-4",
  "entity_type": "model",
  "description": "Large language model",
  "properties": {"provider": "OpenAI"}
}
```

### Get Entity

```
GET /api/v1/knowledge/entities/{id}
```

### Delete Entity

```
DELETE /api/v1/knowledge/entities/{id}
```

### Create Relationship

```
POST /api/v1/knowledge/relationships
```

### Get Graph

```
GET /api/v1/knowledge/graph/{id}?depth=2
```

### Search Entities

```
POST /api/v1/knowledge/search
```

## MCP API

### MCP Endpoint

```
POST /api/mcp
```

### MCP SSE

```
POST /api/mcp/sse
```

### List Tools

```
GET /api/mcp/tools
```

### MCP Health

```
GET /api/mcp/health
```

## Health API

```
GET /api/v1/health
```