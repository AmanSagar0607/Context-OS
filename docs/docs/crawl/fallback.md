# Fallback Chain

> Automatically retry failed crawls across multiple providers for maximum reliability.

## Overview

The Fallback Chain defines the order of crawl providers tried when fetching a page. If one provider fails due to rate limits, blocking, or rendering issues, the system automatically falls back to the next provider. This ensures high availability without manual intervention.

## Providers

| Order | Provider | When Used | Best For |
|-------|----------|-----------|----------|
| 1 | **Crawl4AI** | Default first choice | Fast, structured crawling at scale |
| 2 | **Jina** | Crawl4AI rate-limited or blocked | Lightweight extraction with AI parsing |
| 3 | **Playwright** | JS-heavy or SPA pages | Client-side rendered content |
| 4 | **httpx** | Final fallback | Simple static HTML pages |

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://docs.example.com",
    max_pages=50,
    fallback_chain=["crawl4ai", "jina", "playwright", "httpx"]
)

print(f"Crawled {len(result.pages)} pages")
```

## Configuration

A provider is skipped if it returns `429` (rate limit) or `403` (blocked), times out, or is not enabled for your account.

### Override per-crawl

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://spa.example.com",
    max_pages=20,
    fallback_chain=["playwright", "httpx"]
)
```

### Global default configuration

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

client.configure(
    fallback_chain=["crawl4ai", "playwright", "httpx"]
)
```

## Examples

### Monitor provider usage

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.crawl(
    url="https://docs.example.com",
    max_pages=50
)

providers_used = {}
for page in result.pages:
    providers_used[page.provider] = providers_used.get(page.provider, 0) + 1

for provider, count in providers_used.items():
    print(f"{provider}: {count} pages")
```
```
