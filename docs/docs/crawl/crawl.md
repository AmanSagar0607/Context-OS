# Crawl

> Crawl multiple pages from a website with depth control, pattern matching, and automatic retry.

## Overview

The Crawl endpoint fetches content from a target URL and follows internal links based on your configuration. Use it to gather pages for RAG pipelines, documentation indexing, or site-wide content analysis. The crawler respects `robots.txt`, deduplicates URLs automatically, and supports both synchronous and async modes.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://docs.example.com",
    max_pages=50,
    depth=3,
    include_patterns=["/docs/*"],
    exclude_patterns=["/blog/*", "/archive/*"]
)

for page in result.pages:
    print(f"{page.url} - {len(page.markdown)} chars")
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/crawl` | Crawl a website starting from a seed URL |

### Request parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | Seed URL to begin crawling |
| `max_pages` | `integer` | `100` | Maximum pages to crawl |
| `depth` | `integer` | `3` | Maximum link-following depth |
| `include_patterns` | `string[]` | `[]` | URL glob patterns to include |
| `exclude_patterns` | `string[]` | `[]` | URL glob patterns to exclude |
| `timeout` | `integer` | `60` | Request timeout in seconds |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `pages` | `Page[]` | Array of crawled page objects |
| `pages[].url` | `string` | Page URL |
| `pages[].markdown` | `string` | Extracted markdown content |
| `pages[].metadata` | `object` | Title, description, headers |
| `pages[].status_code` | `integer` | HTTP response code |

## Examples

### Crawl documentation site with filters

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://docs.example.com/api",
    max_pages=200,
    depth=5,
    include_patterns=["/api/v1/*", "/api/v2/*"],
    exclude_patterns=["/api/legacy/*"]
)

docs = [p for p in result.pages if p.status_code == 200]
print(f"Collected {len(docs)} API docs")
```

### Feed crawled pages into a vector store

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://docs.example.com",
    max_pages=50
)

for page in result.pages:
    client.vectors.upsert(
        collection="docs",
        id=page.url,
        text=page.markdown,
        metadata={"source": page.url, "title": page.metadata["title"]}
    )
```
