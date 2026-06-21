# Store Memories

> Add memories to ContextOS.

## Overview

Memories are the core unit of information in ContextOS. They can store facts, insights, code snippets, decisions, errors, and conversation history.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Add a fact
memory = client.memory.add(
    content="User prefers dark mode",
    type="fact",
    metadata={"source": "chat"},
)

# Add with importance
memory = client.memory.add(
    content="Critical security vulnerability found in auth module",
    type="error",
    importance=0.9,
)

# Add conversation turn
memory = client.memory.add(
    content="User: How do I reset my password?\nAgent: Go to Settings > Security > Change Password",
    type="conversation",
    metadata={"user_id": "user_123"},
)
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers dark mode",
    "type": "fact",
    "metadata": {"source": "chat"}
  }'
```

## Memory Types

| Type | Use Case | Example |
|------|----------|---------|
| `fact` | Stored information | "User prefers dark mode" |
| `insight` | Derived understanding | "User is most productive in mornings" |
| `code` | Code snippets | Function implementations |
| `decision` | Choices made | "Chose PostgreSQL over MySQL" |
| `error` | Problems encountered | "API timeout at /v1/search" |
| `learning` | Knowledge acquired | "Crawl4AI handles anti-bot better" |
| `context` | Background info | "Project uses Next.js 14" |
| `conversation` | Chat history | Full conversation turns |

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | string | required | Memory content |
| `type` | string | "fact" | Memory type |
| `scope` | string | "global" | Scope: global, user, session, agent |
| `scope_id` | string | null | Scope identifier |
| `importance` | float | 0.5 | Importance: 0.0 to 1.0 |
| `metadata` | object | {} | Key-value metadata |

## Response

```json
{
  "id": "mem_abc123",
  "content": "User prefers dark mode",
  "type": "fact",
  "scope": "global",
  "importance": 0.5,
  "created_at": "2026-06-21T12:00:00Z"
}
```
