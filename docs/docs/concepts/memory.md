---
sidebar_position: 4
title: Memory
---

# Memory

Persistent agent memory with semantic search.

## Overview

The memory system provides:

- **Persistent Storage**: Memory survives across sessions
- **Semantic Search**: Find memories by meaning, not just keywords
- **Context Windows**: Assemble relevant memories for any query
- **Classification**: Episodic, Semantic, Procedural memory types
- **Importance**: Priority levels for memory retrieval

## Memory Types

| Type | Description | Example |
|------|-------------|---------|
| `episodic` | Events and experiences | "User asked about pricing yesterday" |
| `semantic` | Facts and knowledge | "User prefers dark mode" |
| `procedural` | How-to knowledge | "User's deployment uses Docker Compose" |

## Importance Levels

| Level | Use Case |
|-------|----------|
| `low` | Background information |
| `medium` | Standard memories (default) |
| `high` | Important user preferences |
| `critical` | Must never forget |

## API Usage

### Add Memory

```python
from context_ai import MemoryCreate, MemoryType, ImportanceLevel

memory = client.memory.add(MemoryCreate(
    content="User prefers dark mode and compact layouts",
    memory_type=MemoryType.SEMANTIC,
    importance=ImportanceLevel.HIGH,
    tags=["preferences", "ui"],
    source="user-settings",
))
```

### Search Memories

```python
results = client.memory.search(
    query="UI preferences",
    memory_type=MemoryType.SEMANTIC,
    top_k=10,
    min_score=0.7,
)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Content: {result.memory.content}")
```

### Get Context Window

Assemble relevant memories for a query:

```python
context = client.memory.context(
    query="What settings does the user prefer?",
    max_tokens=2000,
)

# Use in LLM prompt
prompt = f"""Context from memory:
{context['memories']}

User question: What settings do I prefer?"""
```

### List Memories

```python
memories = client.memory.list(
    memory_type="semantic",
    limit=50,
    offset=0,
)
```

### Get Related Memories

```python
related = client.memory.related(
    memory_id="mem-123",
    limit=10,
)
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `context_os.memory.add` | Store a new memory |
| `context_os.memory.get` | Get a memory by ID |
| `context_os.memory.update` | Update a memory |
| `context_os.memory.delete` | Delete a memory |
| `context_os.memory.search` | Search memories |
| `context_os.memory.context` | Get context window |
| `context_os.memory.list` | List memories |
| `context_os.memory.related` | Get related memories |

## CLI Commands

```bash
# Add memory
context memory add -c "User prefers dark mode" --type semantic --importance high

# Search
context memory search "dark mode" --limit 10

# List
context memory list --type semantic

# Get
context memory get <memory-id>

# Delete
context memory delete <memory-id>
```

## How It Works

### Storage

Memories are stored in PostgreSQL with pgvector embeddings:

```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    summary TEXT,
    memory_type VARCHAR(20) NOT NULL,
    importance VARCHAR(20) NOT NULL,
    tags TEXT[] DEFAULT '{}',
    embedding VECTOR(384)
);
```

### Retrieval

1. **Embed Query**: Convert query to vector embedding
2. **Vector Search**: Find semantically similar memories
3. **Text Search**: Find memories with matching keywords
4. **Fusion**: Combine results using RRF
5. **Return**: Top-k results with scores