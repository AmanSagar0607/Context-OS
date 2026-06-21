# Knowledge Graph Patterns

> Best practices for building and using knowledge graphs with ContextOS.

## Overview

ContextOS knowledge graphs enable structured representation of entities and relationships. This guide covers extraction, modeling, traversal, and maintenance patterns.

## Setup

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")
```

## Patterns

### Entity Extraction

Automatically extract entities from text:

```python
def extract_entities(text: str) -> list:
    return client.knowledge.extract(
        content=text,
        entity_types=["person", "organization", "concept", "technology"]
    )
```

### Relationship Modeling

Define relationships between entities:

```python
client.knowledge.add_entity(
    name="Python",
    type="technology",
    properties={"language": True, "paradigm": "multi-paradigm"}
)

client.knowledge.add_entity(
    name="FastAPI",
    type="framework",
    properties={"language": "python", "type": "web"}
)

client.knowledge.add_relationship(
    source="FastAPI",
    target="Python",
    relation="built_with",
    properties={"version": "3.11+"}
)
```

### Graph Traversal

Query relationships and paths:

```python
# Get direct connections
connections = client.knowledge.get_neighbors(
    entity="Python",
    relation_type="built_with",
    direction="incoming"
)

# Find shortest path
path = client.knowledge.find_path(
    source="FastAPI",
    target="Docker",
    max_depth=4
)

# Get subgraph
subgraph = client.knowledge.get_subgraph(
    center="Python",
    radius=2,
    relation_types=["built_with", "used_by"]
)
```

### Auto-Updating

Keep knowledge graph current with changes:

```python
def update_knowledge(content: str):
    entities = client.knowledge.extract(content)

    for entity in entities:
        existing = client.knowledge.get_entity(entity.name)
        if existing:
            client.knowledge.update_entity(
                name=entity.name,
                properties=entity.properties
            )
        else:
            client.knowledge.add_entity(**entity)

    client.knowledge.update_relationships(entities)
```

## Examples

**Build from documentation:**

```python
def build_from_docs(doc_urls: list):
    for url in doc_urls:
        crawl_result = client.crawl(url=url, index=False)

        entities = client.knowledge.extract(crawl_result.content)
        client.knowledge.add_batch(entities)

        relationships = client.knowledge.infer_relationships(entities)
        client.knowledge.add_relationships_batch(relationships)
```

**Query with context:**

```python
def query_with_graph(query: str, user_id: str):
    # Search memory
    memory_results = client.memory.search(query=query, user_id=user_id)

    # Enrich with graph context
    for result in memory_results:
        entities = client.knowledge.extract(result.content)
        result.graph_context = client.knowledge.get_subgraph(
            center=entities[0].name if entities else None,
            radius=1
        )

    return memory_results
```
