# Memory Types

> Understanding different memory categories.

## Overview

ContextOS supports multiple memory types to organize information effectively. Each type has different characteristics and use cases.

## Types

### Fact

Stored information about the world or user.

```python
client.memory.add(content="User is located in India", type="fact")
```

### Insight

Derived understanding from patterns.

```python
client.memory.add(content="User prefers concise answers", type="insight")
```

### Code

Code snippets and implementations.

```python
client.memory.add(content="def hello(): print('world')", type="code")
```

### Decision

Choices made and their rationale.

```python
client.memory.add(content="Chose PostgreSQL for ACID compliance", type="decision")
```

### Error

Problems encountered and solutions.

```python
client.memory.add(content="API timeout at /v1/search — increased timeout to 30s", type="error")
```

### Learning

Knowledge acquired over time.

```python
client.memory.add(content="Crawl4AI handles Cloudflare better than Jina", type="learning")
```

### Context

Background information.

```python
client.memory.add(content="Project uses Next.js 14 with App Router", type="context")
```

### Conversation

Chat history turns.

```python
client.memory.add(content="User: Hi\nAgent: Hello! How can I help?", type="conversation")
```

## Choosing Types

| Use Case | Type |
|----------|------|
| User preferences | `fact` or `insight` |
| Chat history | `conversation` |
| Debugging notes | `error` |
| Architecture decisions | `decision` |
| Code snippets | `code` |
| Project setup | `context` |
| Tool comparisons | `learning` |
