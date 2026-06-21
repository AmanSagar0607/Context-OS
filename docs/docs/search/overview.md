# Search Overview

> Search capabilities in ContextOS.

## Overview

ContextOS provides two search capabilities:

1. **Web Search** — Search the internet via multiple providers
2. **Internal Search** — Search your memories and knowledge graph

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Web search
web_results = client.search.web("latest AI news")

# Internal search (hybrid)
internal_results = client.search.internal("user preferences")
```

## Search Types

| Type | Description | Use Case |
|------|-------------|----------|
| Web Search | Internet search via providers | Research, fact-checking |
| Internal Search | Memory + knowledge search | Context retrieval |
| Hybrid Search | Both combined | Comprehensive results |

## Providers

| Provider | Type | Cost | Speed |
|----------|------|------|-------|
| Tavily | Web | Paid | Fast |
| Brave | Web | Paid | Fast |
| SearXNG | Web | Free | Medium |
| DuckDuckGo | Web | Free | Medium |
| pgvector | Internal | Free | Fast |
| BM25 | Internal | Free | Fast |

## REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/search/web` | POST | Web search |
| `/api/v1/search/internal` | POST | Internal hybrid search |
| `/api/v1/memory/search` | POST | Memory search |
