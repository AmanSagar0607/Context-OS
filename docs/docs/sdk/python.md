---
sidebar_position: 8
title: Python SDK
---

# Python SDK

A Python client library for the Context OS API.

## Installation

```bash
pip install context-ai
```

## Quick Start

```python
from context_ai import ContextAI

client = ContextAI(
    base_url="http://localhost:8000",
    api_key="your-api-key",
)
```

## Memory Operations

### Add Memory

```python
from context_ai import MemoryCreate, MemoryType, ImportanceLevel

memory = client.memory.add(MemoryCreate(
    content="User prefers dark mode",
    memory_type=MemoryType.SEMANTIC,
    importance=ImportanceLevel.HIGH,
    tags=["preferences", "ui"],
))
```

### Search Memories

```python
results = client.memory.search(query="dark mode")
for result in results:
    print(f"{result.score:.2f}: {result.memory.content}")
```

### Get Context Window

```python
context = client.memory.context(query="UI preferences", max_tokens=2000)
```

## Async Support

```python
import asyncio
from context_ai import ContextAI

async def main():
    async with ContextAI() as client:
        memory = await client.memory.aadd(content="Async memory")
        results = await client.memory.asearch(query="async")

asyncio.run(main())
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CONTEXT_API_KEY` | API key |
| `CONTEXT_API_URL` | API server URL |

### Constructor

```python
client = ContextAI(
    base_url="http://localhost:8000",
    api_key="your-key",
    timeout=30.0,
)
```

## API Reference

### MemoryClient

| Method | Description |
|--------|-------------|
| `add(request)` | Add memory |
| `get(memory_id)` | Get memory |
| `update(memory_id, request)` | Update memory |
| `delete(memory_id)` | Delete memory |
| `search(request)` | Search memories |
| `context(query, max_tokens)` | Get context window |
| `list(memory_type, limit, offset)` | List memories |
| `related(memory_id, limit)` | Get related memories |

### SearchClient

| Method | Description |
|--------|-------------|
| `web(request)` | Web search |
| `internal(query, top_k)` | Internal search |

### CrawlClient

| Method | Description |
|--------|-------------|
| `scrape(url)` | Scrape URL |
| `crawl(request)` | Crawl website |
| `map(url, max_pages)` | Map website |
| `extract(url, prompt)` | AI extraction |

### KnowledgeClient

| Method | Description |
|--------|-------------|
| `create_entity(request)` | Create entity |
| `get_entity(entity_id)` | Get entity |
| `delete_entity(entity_id)` | Delete entity |
| `create_relationship(request)` | Create relationship |
| `get_graph(entity_id, depth)` | Get graph |
| `search(query)` | Search entities |