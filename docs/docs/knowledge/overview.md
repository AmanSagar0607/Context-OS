# Knowledge Overview

> Knowledge graph capabilities.

## Overview

ContextOS builds and maintains a knowledge graph of entities and relationships extracted from your data.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Add entity
entity = client.knowledge.add_entity(
    name="ContextOS",
    type="software",
    properties={"language": "Python", "license": "MIT"},
)

# Add relationship
client.knowledge.add_relationship(
    source_id=entity.id,
    target_id="python_entity_id",
    relationship="built_with",
)

# Query graph
result = client.knowledge.query(entity_name="ContextOS")
```

## Capabilities

| Capability | Description |
|------------|-------------|
| Entity Management | Create, update, delete entities |
| Relationship Management | Create typed relationships |
| Graph Queries | Traverse neighbors, find paths |
| Auto-Extraction | LLM-based entity extraction |
| Embeddings | Vector search on entities |

## Entity Types

| Type | Example |
|------|---------|
| person | "John Doe" |
| organization | "OpenAI" |
| software | "ContextOS" |
| concept | "Machine Learning" |
| location | "San Francisco" |
| event | "Launch Day" |

## REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/knowledge/entities` | POST | Create entity |
| `/api/v1/knowledge/entities/:id` | GET | Get entity |
| `/api/v1/knowledge/relationships` | POST | Create relationship |
| `/api/v1/knowledge/graph/:id` | GET | Get entity graph |
| `/api/v1/knowledge/search` | POST | Search entities |
