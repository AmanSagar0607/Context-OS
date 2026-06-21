# Migrating from Firecrawl

> Step-by-step guide to migrate from Firecrawl to ContextOS crawl APIs.

## Overview

ContextOS provides web crawling capabilities that replace Firecrawl with additional features like automatic indexing, memory integration, and hybrid search. This guide helps you transition smoothly.

## Setup

1. Install the ContextOS SDK:

```bash
pip install context-ai
```

2. Initialize both clients during transition:

```python
from firecrawl import FirecrawlApp
from context_ai import ContextClient

firecrawl = FirecrawlApp(api_key="firecrawl-key")
context = ContextClient(api_key="contextos-key")
```

3. Update crawl calls to use ContextOS:

```python
# Before: firecrawl.crawl(url="https://example.com")
# After:
result = context.crawl(url="https://example.com")
```

4. Migrate stored crawl data:

```python
# Export from Firecrawl (if using storage)
# Import into ContextOS
context.crawl.import_data(source="firecrawl", data=exported_data)
```

5. Update webhook handlers if using crawl callbacks.
6. Remove Firecrawl dependency once migration is verified.

## Comparison

| Feature | Firecrawl | ContextOS |
|---------|-----------|-----------|
| Web crawling | Yes | Yes |
| Screenshot capture | Yes | Yes |
| Auto-indexing | No | Yes |
| Memory integration | No | Built-in |
| Hybrid search | No | Vector + BM25 |
| Rate limiting | Basic | Advanced |

## Examples

**Before (Firecrawl):**

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="key")
result = app.crawl_url("https://example.com", params={"limit": 10})
content = result["data"][0]["markdown"]
```

**After (ContextOS):**

```python
from context_ai import ContextClient

client = ContextClient(api_key="key")
result = client.crawl(
    url="https://example.com",
    limit=10,
    index=True  # Auto-index for search
)
content = result.pages[0].content

# Search crawled content
results = client.search(query="specific topic", source="crawl")
```
