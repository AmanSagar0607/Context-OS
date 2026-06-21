# Memory Best Practices

> Patterns and anti-patterns for effective memory usage.

## Best Practices

### 1. Use Appropriate Types

```python
# Good — specific type
client.memory.add(content="User prefers dark mode", type="fact")

# Bad — generic type
client.memory.add(content="User prefers dark mode", type="context")
```

### 2. Set Importance Scores

```python
# Good — important information
client.memory.add(content="Critical security vulnerability", importance=0.9)

# Good — less important
client.memory.add(content="User said hello", importance=0.2)
```

### 3. Use Metadata for Filtering

```python
# Good — filterable
client.memory.add(
    content="User prefers dark mode",
    metadata={"source": "chat", "user_id": "user_123"},
)

# Bad — no metadata
client.memory.add(content="User prefers dark mode")
```

### 4. Store Conversations as Turns

```python
# Good — individual turns
client.memory.add(content="User: Hi", type="conversation")
client.memory.add(content="Agent: Hello!", type="conversation")

# Bad — entire conversation
client.memory.add(content="User: Hi\nAgent: Hello!\n...", type="conversation")
```

### 5. Use Scopes for Isolation

```python
# User-specific memory
client.memory.add(content="User prefers dark mode", scope="user", scope_id="user_123")

# Session-specific memory
client.memory.add(content="Current task: build API", scope="session", scope_id="session_abc")
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Storing everything | Noise overwhelms retrieval | Filter and prioritize |
| No importance scores | Old junk clogs system | Set importance 0.0-1.0 |
| Huge content | Token waste | Chunk long content |
| No metadata | Can't filter by source | Add source, user, session |
| Duplicate memories | Redundant results | Check before adding |

## Memory Lifecycle

```
Create → Access (boost) → Age (decay) → Consolidate → Archive
```

1. **Create** — Store new memory
2. **Access** — Retrieval boosts importance
3. **Age** — Unused memories decay
4. **Consolidate** — Merge old, related memories
5. **Archive** — Move to cold storage
