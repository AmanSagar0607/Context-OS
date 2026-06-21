# Memory Links

> Graph relationships between memories.

## Overview

Memory Links create relationships between memories, forming a knowledge graph of connected information.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Create link between memories
client.memory.link(
    source_id="mem_abc",
    target_id="mem_def",
    relationship="related_to",
    weight=0.8,
)
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/memory/links \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "mem_abc",
    "target_id": "mem_def",
    "relationship": "related_to",
    "weight": 0.8
  }'
```

## Link Types

| Type | Description |
|------|-------------|
| `related_to` | General relationship |
| `caused_by` | Causal relationship |
| `part_of` | Hierarchical relationship |
| `contradicts` | Conflicting information |
| `supports` | Supporting evidence |
| `follows` | Temporal sequence |

## Traversal

```python
# Get related memories
related = client.memory.get_related(
    memory_id="mem_abc",
    max_depth=2,
)
```

## Use Cases

- Link conversation turns to topics
- Connect decisions to reasoning
- Build topic hierarchies
- Track cause-effect chains
