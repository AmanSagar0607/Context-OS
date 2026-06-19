---
sidebar_position: 6
title: Knowledge Graph
---

# Knowledge Graph

Entity-relationship knowledge graph for structured knowledge.

## Overview

The knowledge graph provides:

- **Entities**: Named entities with types and properties
- **Relationships**: Typed edges between entities
- **Traversal**: Graph traversal with configurable depth
- **Search**: Entity search by name and description

## Entities

### Create Entity

```python
from context_ai import EntityCreate

entity = client.knowledge.create_entity(EntityCreate(
    name="GPT-4",
    entity_type="model",
    description="OpenAI's large language model",
    properties={
        "provider": "OpenAI",
        "parameters": "1.7T",
        "context_window": "128k",
    },
))
```

### Get Entity

```python
entity = client.knowledge.get_entity(entity_id="entity-123")
print(f"Name: {entity.name}")
print(f"Type: {entity.entity_type}")
```

### Search Entities

```python
entities = client.knowledge.search(
    query="language models",
    entity_type="model",
    top_k=10,
)
```

## Relationships

### Create Relationship

```python
from context_ai import RelationshipCreate

client.knowledge.create_relationship(RelationshipCreate(
    source_id="gpt4-entity-id",
    target_id="openai-entity-id",
    relationship_type="created_by",
    weight=1.0,
))
```

### Get Entity Graph

```python
graph = client.knowledge.get_graph(
    entity_id="gpt4-entity-id",
    depth=2,
)

print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `context_os.knowledge.create_entity` | Create entity |
| `context_os.knowledge.get_entity` | Get entity |
| `context_os.knowledge.delete_entity` | Delete entity |
| `context_os.knowledge.create_relationship` | Create relationship |
| `context_os.knowledge.get_graph` | Get entity graph |
| `context_os.knowledge.search` | Search entities |

## CLI Commands

```bash
# Create entity
context knowledge create-entity --name "GPT-4" --type model --description "LLM"

# Search entities
context knowledge search "language models" --limit 10
```

## Schema

```sql
CREATE TABLE kg_entities (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE kg_relationships (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES kg_entities(id),
    target_id UUID REFERENCES kg_entities(id),
    relationship_type TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```