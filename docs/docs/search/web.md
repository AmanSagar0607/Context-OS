# Web Search

> Search the internet via multiple providers.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

results = client.search.web("latest AI news", max_results=5)
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/search/web \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI news", "max_results": 5}'
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `max_results` | int | 5 | Maximum results |
| `provider` | string | "auto" | Provider: tavily, brave, searxng, duckduckgo, auto |

## Response

```json
{
  "results": [
    {
      "title": "AI News Today",
      "url": "https://example.com/ai-news",
      "snippet": "Latest developments in AI...",
      "score": 0.95
    }
  ],
  "query": "latest AI news",
  "provider": "tavily"
}
```

## Provider Selection

- **auto** — Selects best available provider
- **tavily** — Best quality, requires API key
- **brave** — Good quality, requires API key
- **searxng** — Free, self-hostable
- **duckduckgo** — Free, no API key needed
