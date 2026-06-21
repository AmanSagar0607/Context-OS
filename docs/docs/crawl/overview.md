# Crawl Overview

> Web intelligence capabilities.

## Overview

ContextOS provides web intelligence through multiple capabilities:

1. **Scrape** — Extract content from a single URL
2. **Crawl** — Walk through multiple pages
3. **Map** — Discover site structure
4. **Extract** — AI-powered data extraction
5. **Browser** — Playwright rendering for JS-heavy sites

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Scrape a URL
result = client.crawl.scrape("https://example.com")

# Crawl a site
results = client.crawl.crawl("https://example.com", max_pages=10)

# Map a site
sitemap = client.crawl.map("https://example.com")

# Extract with AI
data = client.crawl.extract("https://example.com", schema={"name": "string", "price": "number"})
```

## Capabilities

| Capability | Description | Use Case |
|------------|-------------|----------|
| Scrape | Single URL extraction | Article reading |
| Crawl | Multi-page traversal | Site indexing |
| Map | Structure discovery | Navigation planning |
| Extract | AI data extraction | Structured data |
| Browser | JS rendering | SPA content |

## Providers

| Provider | Speed | Anti-Bot | Cost |
|----------|-------|----------|------|
| Crawl4AI | Fast | Good | Free |
| Jina | Fast | Good | Freemium |
| Playwright | Slow | Excellent | Free |
| httpx | Fast | None | Free |

## Fallback Chain

ContextOS automatically falls back between providers:

```
Crawl4AI → Jina → Playwright → httpx
```

## REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/crawl/scrape` | POST | Scrape URL |
| `/api/v1/crawl/crawl` | POST | Crawl site |
| `/api/v1/crawl/map` | POST | Map structure |
| `/api/v1/crawl/extract` | POST | AI extraction |
