# Agent Memory Patterns

> Best practices for implementing agent memory with ContextOS.

## Overview

ContextOS supports multiple memory patterns for AI agents. Choose the right pattern based on your agent's requirements for persistence, scope, and lifecycle.

## Setup

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")
```

## Patterns

### Session Memory

Short-lived memory for a single conversation. Automatically expires.

```python
def handle_message(user_id: str, session_id: str, message: str):
    client.memory.add(
        content=message,
        user_id=user_id,
        namespace=f"session:{session_id}",
        ttl=3600  # 1 hour
    )

    context = client.memory.search(
        query=message,
        user_id=user_id,
        namespace=f"session:{session_id}"
    )
    return context
```

### Long-Term Memory

Persistent memory that survives across sessions.

```python
def store_preference(user_id: str, key: str, value: str):
    client.memory.add(
        content=f"{key}: {value}",
        user_id=user_id,
        namespace="preferences",
        metadata={"type": "preference", "key": key}
    )

def get_preferences(user_id: str) -> list:
    return client.memory.search(
        query="user preferences",
        user_id=user_id,
        namespace="preferences"
    )
```

### Shared Memory

Memory shared between multiple agents or users.

```python
def share_context(team_id: str, content: str):
    client.memory.add(
        content=content,
        namespace=f"team:{team_id}",
        metadata={"shared": True}
    )

def get_team_context(team_id: str, query: str):
    return client.memory.search(
        query=query,
        namespace=f"team:{team_id}"
    )
```

### Memory Consolidation

Periodically consolidate related memories to reduce noise.

```python
def consolidate_memories(user_id: str):
    memories = client.memory.get_all(
        user_id=user_id,
        namespace="raw_interactions"
    )

    summary = client.memory.summarize(memories)

    client.memory.add(
        content=summary,
        user_id=user_id,
        namespace="consolidated",
        metadata={"consolidated": True}
    )

    # Archive originals
    client.memory.archive(
        user_id=user_id,
        namespace="raw_interactions"
    )
```

## Examples

**Full agent implementation:**

```python
from context_ai import ContextClient

class Agent:
    def __init__(self, user_id: str):
        self.client = ContextClient(api_key="key")
        self.user_id = user_id

    def process(self, message: str, session_id: str):
        # Store in session
        self.client.memory.add(
            content=message,
            user_id=self.user_id,
            namespace=f"session:{session_id}"
        )

        # Search relevant context
        session_ctx = self.client.memory.search(
            query=message,
            user_id=self.user_id,
            namespace=f"session:{session_id}",
            limit=5
        )

        long_term_ctx = self.client.memory.search(
            query=message,
            user_id=self.user_id,
            namespace="knowledge",
            limit=3
        )

        return self.generate_response(
            message,
            session=session_ctx,
            long_term=long_term_ctx
        )
```
