---
sidebar_position: 5
title: Retrieval
---

# Retrieval

Hybrid retrieval with reciprocal rank fusion.

## Overview

The retrieval pipeline combines multiple search strategies:

```
Query → [Vector Search, BM25 Search] → RRF Fusion → Results
```

## Search Strategies

### Vector Search (pgvector)

Semantic search using cosine similarity:

```sql
SELECT id, content, 1 - (embedding <=> query_embedding) as score
FROM memories
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

**Strengths**: Finds semantically similar content
**Weakness**: May miss keyword-specific matches

### BM25 Search (PostgreSQL FTS)

Full-text search using PostgreSQL's built-in ranking:

```sql
SELECT id, content, ts_rank_cd(search_vector, query) as score
FROM memories, plainto_tsquery('english', 'dark mode') query
WHERE search_vector @@ query
ORDER BY ts_rank_cd(search_vector, query) DESC
LIMIT 10;
```

**Strengths**: Precise keyword matching
**Weakness**: Misses semantic similarity

### Reciprocal Rank Fusion (RRF)

Combines results from multiple sources:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

Where:
- `d` = document
- `rank_i(d)` = rank of document in source i
- `k` = constant (default: 60)

**Advantages**:
- No need to normalize scores across sources
- Robust to different score distributions
- Simple to implement and tune

## Configuration

### Pipeline Config

```python
from packages.context_core.retrieval.pipeline import RetrievalPipeline

pipeline = RetrievalPipeline(
    vector_weight=0.7,    # Weight for vector search
    bm25_weight=0.3,      # Weight for BM25 search
    rrf_k=60,             # RRF constant
    top_k=10,             # Max results
)
```

### Chunking

Documents are chunked before indexing:

```python
from packages.context_core.retrieval.chunking import RecursiveChunker

chunker = RecursiveChunker(
    chunk_size=500,       # Characters per chunk
    overlap=50,           # Overlap between chunks
)

chunks = chunker.chunk(document)
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `context_os.search.internal` | Internal hybrid search |

## API Usage

```python
# Internal search
results = client.search.internal(
    query="user preferences",
    top_k=10,
)
```

## CLI Usage

```bash
# Internal search
context search internal "user preferences" --limit 10
```