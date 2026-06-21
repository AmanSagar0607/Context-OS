# Migrating from mem0

> Step-by-step guide to migrate from mem0 to ContextOS with zero downtime.

## Overview

ContextOS provides a superset of mem0's memory capabilities with additional features like hybrid search, knowledge graphs, and multi-tenant isolation. This guide walks you through the migration process.

## Setup

1. Install the ContextOS SDK alongside mem0:

```bash
pip install context-ai
```

2. Initialize both clients during transition:

```python
from mem0 import Memory
from context_ai import ContextClient

mem0 = Memory(api_key="mem0-key")
context = ContextClient(api_key="contextos-key")
```

3. Export existing memories from mem0:

```python
all_memories = mem0.get_all(user_id="user-123")
```

4. Import into ContextOS:

```python
for memory in all_memories["results"]:
    context.memory.add(
        content=memory["memory"],
        user_id=memory["user_id"],
        metadata=memory.get("metadata", {})
    )
```

5. Update your application code to use ContextOS client.
6. Remove mem0 dependency once migration is verified.

## Comparison

| Feature | mem0 | ContextOS |
|---------|------|-----------|
| Memory storage | Basic | Advanced with namespaces |
| Search | Vector only | Vector + BM25 + RRF |
| Knowledge graphs | No | Yes |
| Multi-tenancy | Limited | Full isolation |
| Crawl integration | No | Built-in |
| Metadata filtering | Basic | Advanced with types |

## Examples

**Before (mem0):**

```python
from mem0 import Memory

memory = Memory(api_key="key")
memory.add("User prefers dark mode", user_id="user-1")
results = memory.search("preferences", user_id="user-1")
```

**After (ContextOS):**

```python
from context_ai import ContextClient

client = ContextClient(api_key="key")
client.memory.add(
    content="User prefers dark mode",
    user_id="user-1",
    namespace="preferences"
)
results = client.memory.search(
    query="preferences",
    user_id="user-1",
    namespace="preferences"
)
```
