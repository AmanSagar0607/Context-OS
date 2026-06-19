---
sidebar_position: 7
title: Web Intelligence
---

# Web Intelligence

Web crawling and search with multi-provider fallback.

## Overview

The web intelligence module provides:

- **Web Search**: Multi-provider search (Tavily, Searxng, etc.)
- **Crawl**: Website crawling with fallback chain
- **Scrape**: Single-page content extraction
- **Extract**: AI-powered data extraction
- **Map**: Website structure discovery

## Search

### Web Search

```python
from context_ai import SearchRequest

results = client.search.web(SearchRequest(
    query="AI agent frameworks 2025",
    max_results=10,
))

for result in results:
    print(f"{result.title}")
    print(f"  {result.url}")
```

## Crawl

### Scrape Single Page

```python
page = client.crawl.scrape(url="https://docs.example.com")
print(f"Title: {page.title}")
print(f"Content: {len(page.content)} chars")
```

### Crawl Website

```python
from context_ai import CrawlRequest

results = client.crawl.crawl(CrawlRequest(
    url="https://docs.example.com",
    max_pages=50,
    extract_content=True,
))

print(f"Crawled {len(results)} pages")
```

### Map Website

```python
urls = client.crawl.map(
    url="https://example.com",
    max_pages=100,
)
print(f"Found {len(urls)} URLs")
```

### AI Extraction

```python
data = client.crawl.extract(
    url="https://docs.example.com/pricing",
    prompt="Extract all pricing tiers and their features",
)
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `context_os.search.web` | Web search |
| `context_os.crawl.scrape` | Scrape single URL |
| `context_os.crawl.crawl` | Crawl website |
| `context_os.crawl.map` | Map website structure |
| `context_os.crawl.extract` | AI extraction |

## CLI Commands

```bash
# Web search
context search web "AI news" --limit 5

# Scrape
context crawl scrape https://example.com

# Map
context crawl map https://example.com --limit 50
```