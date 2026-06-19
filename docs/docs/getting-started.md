---
sidebar_position: 2
title: Quickstart
---

# Quickstart

Get up and running with Context OS in 5 minutes.

## Prerequisites

- Python 3.10+ or Node.js 18+
- Docker (for self-hosted)
- API key from [Context OS Cloud](https://console.context-ai.dev) (or self-host)

## Install SDK

```bash
# Python
pip install context-ai

# TypeScript
npm install context-ai
```

## Initialize Client

```python
from context_ai import ContextAI

client = ContextAI(
    base_url="http://localhost:8000",  # or your cloud URL
    api_key="your-api-key",
)
```

```typescript
import { ContextAI } from "context-ai";

const client = new ContextAI({
  baseUrl: "http://localhost:8000",
  apiKey: "your-api-key",
});
```

## Memory Operations

### Add a Memory

```python
from context_ai import MemoryCreate, MemoryType, ImportanceLevel

memory = client.memory.add(MemoryCreate(
    content="User prefers dark mode and compact layouts",
    memory_type=MemoryType.SEMANTIC,
    importance=ImportanceLevel.HIGH,
    tags=["preferences", "ui"],
))
print(f"Created: {memory.id}")
```

### Search Memories

```python
results = client.memory.search(query="dark mode preferences")
for result in results:
    print(f"Score: {result.score:.2f} — {result.memory.content}")
```

### Get Context Window

```python
context = client.memory.context(
    query="What UI settings does the user prefer?",
    max_tokens=2000,
)
print(f"Found {len(context['memories'])} memories")
```

## Web Search

```python
from context_ai import SearchRequest

results = client.search.web(SearchRequest(
    query="latest AI agent frameworks 2025",
    max_results=5,
))
for result in results:
    print(f"{result.title}: {result.url}")
```

## Web Crawl

```python
# Scrape a single page
page = client.crawl.scrape(url="https://docs.example.com")
print(f"Title: {page.title}")

# Crawl a website
from context_ai import CrawlRequest
results = client.crawl.crawl(CrawlRequest(
    url="https://docs.example.com",
    max_pages=20,
))
print(f"Crawled {len(results)} pages")
```

## Knowledge Graph

```python
from context_ai import EntityCreate

entity = client.knowledge.create_entity(EntityCreate(
    name="GPT-4",
    entity_type="model",
    description="OpenAI's large language model",
))
print(f"Created entity: {entity.id}")
```

## CLI Usage

```bash
# Check health
context health

# Add memory
context memory add -c "User prefers dark mode" --type semantic

# Search
context memory search "dark mode"

# Web search
context search web "AI news"
```

## Next Steps

- [Architecture](/docs/architecture) — Understand the system design
- [Memory Concepts](/docs/concepts/memory) — Deep dive into memory
- [API Reference](/docs/api-reference) — Full API documentation
- [MCP Server](/docs/mcp) — Use with any MCP client