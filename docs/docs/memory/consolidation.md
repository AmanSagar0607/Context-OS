# Memory Consolidation

> Merge old, low-importance memories.

## Overview

Memory Consolidation automatically merges old, low-importance memories into summaries to reduce noise and improve retrieval quality.

## How It Works

1. Find memories older than threshold
2. Filter by importance below threshold
3. Group related memories
4. Generate summary via LLM
5. Replace originals with summary

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Trigger consolidation
result = client.memory.consolidate(
    older_than_days=30,
    max_importance=0.3,
)
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `older_than_days` | int | 30 | Consolidate memories older than N days |
| `max_importance` | float | 0.3 | Only consolidate memories below this importance |
| `min_similar` | int | 3 | Minimum similar memories to trigger consolidation |
| `dry_run` | bool | false | Preview without making changes |

## Benefits

- Reduces storage usage
- Improves retrieval speed
- Maintains important information
- Removes noise from old data
