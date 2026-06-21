# Scrape

> Extract content from a single URL.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

result = client.crawl.scrape("https://example.com/article")
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/crawl/scrape \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to scrape |
| `provider` | string | "auto" | Provider selection |
| `extract_text` | bool | true | Extract text content |
| `extract_links` | bool | false | Extract links |
| `extract_metadata` | bool | false | Extract metadata |

## Response

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Full article text...",
  "links": ["https://example.com/other"],
  "metadata": {
    "author": "John Doe",
    "published": "2026-06-21"
  }
}
```

## Use Cases

- Read article content
- Extract product information
- Monitor page changes
- Feed content to LLMs
