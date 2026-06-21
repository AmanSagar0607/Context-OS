# Hybrid Search

> Guide to using ContextOS hybrid search with vector, BM25, and RRF fusion.

## Overview

ContextOS combines vector search, BM25 keyword search, and Reciprocal Rank Fusion (RRF) to deliver superior search results. This guide covers configuration, tuning, and best practices.

## Setup

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")
```

## Configuration

### Basic Hybrid Search

```python
results = client.search(
    query="machine learning deployment",
    mode="hybrid",
    limit=10
)
```

### Custom Weights

Adjust the balance between vector and BM25 search:

```python
results = client.search(
    query="neural network optimization",
    mode="hybrid",
    weights={"vector": 0.7, "bm25": 0.3},
    limit=10
)
```

### RRF Parameters

Tune Reciprocal Rank Fusion:

```python
results = client.search(
    query="API rate limiting",
    mode="hybrid",
    rrf_k=60,  # Controls fusion steepness
    limit=10
)
```

## Comparison

| Search Mode | Best For | Speed | Accuracy |
|-------------|----------|-------|----------|
| Vector | Semantic similarity | Fast | Good |
| BM25 | Exact keyword matches | Fast | High for terms |
| Hybrid | Balanced results | Medium | Best |

## Examples

**Filter by namespace:**

```python
results = client.search(
    query="deployment strategies",
    mode="hybrid",
    namespace="engineering",
    metadata_filter={"language": "python"}
)
```

**Performance tuning:**

```python
results = client.search(
    query="critical alerts",
    mode="hybrid",
    weights={"vector": 0.5, "bm25": 0.5},
    rrf_k=30,
    limit=20,
    timeout=5000  # ms
)
```

**With reranking:**

```python
results = client.search(
    query="authentication best practices",
    mode="hybrid",
    rerank=True,
    rerank_model="contextos-rerank-v1",
    limit=10
)
```

## Tips

- Use higher BM25 weight for technical documentation with specific terms.
- Use higher vector weight for conceptual queries.
- Set `rrf_k` between 30-100; lower values favor top results.
- Enable reranking for critical search paths.
- Cache frequent queries to reduce latency.
