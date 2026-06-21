# Search Memories

> Find relevant memories using hybrid search.

## Overview

ContextOS uses hybrid search combining vector similarity (pgvector) and keyword matching (BM25) with RRF fusion for optimal results.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Search memories
results = client.memory.search(
    query="user preferences",
    top_k=5,
)

for result in results.results:
    print(f"[{result.score:.2f}] {result.memory.content}")
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/memory/search \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "user preferences",
    "top_k": 5
  }'
```

## Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `hybrid` | Vector + BM25 + RRF | General use (default) |
| `vector` | Semantic similarity | Conceptual queries |
| `bm25` | Keyword matching | Exact term searches |

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `top_k` | int | 10 | Number of results |
| `threshold` | float | 0.0 | Minimum score threshold |
| `mode` | string | "hybrid" | Search mode |
| `type` | string | null | Filter by memory type |
| `scope` | string | null | Filter by scope |

## Response

```json
{
  "results": [
    {
      "memory": {
        "id": "mem_abc123",
        "content": "User prefers dark mode",
        "type": "fact"
      },
      "score": 0.89,
      "rank": 1
    }
  ],
  "query": "user preferences",
  "total_hits": 1
}
```

## How Hybrid Search Works

1. **Vector Search** — Embed query, find similar embeddings via cosine similarity
2. **BM25 Search** — Tokenize query, match against full-text index
3. **RRF Fusion** — Combine results using Reciprocal Rank Fusion
4. **Re-ranking** — Optional cross-encoder re-ranking for precision

## Tips

- Use natural language for vector search
- Use specific terms for BM25 search
- Hybrid mode handles both automatically
- Set `threshold` to filter noise
