# Relationships

> Manage typed relationships between entities in the knowledge graph.

## Overview

Relationships connect entities in your knowledge graph with semantic meaning. Each relationship has a source entity, a target entity, and a type that describes the connection. Use relationships to model real-world connections like team membership, technology stacks, dependencies, and geographic associations.

Relationship types are flexible strings — use whatever fits your domain. Common types include `built_with`, `works_at`, `located_in`, `depends_on`, `owns`, `authored_by`, and `part_of`.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

# Add a relationship
rel = client.knowledge.add_relationship(
    source_id="entity_amy_01",
    target_id="entity_acme_02",
    relationship_type="works_at",
    metadata={"role": "Senior Engineer", "since": "2024-03"}
)
print(rel.id)  # "rel_7f8a9b0c"

# Add another relationship
client.knowledge.add_relationship(
    source_id="entity_project_x",
    target_id="entity_react",
    relationship_type="built_with",
    metadata={"version": "18.2"}
)

# Retrieve relationships for an entity
relationships = client.knowledge.get_relationships(
    entity_id="entity_amy_01",
    direction="outgoing"
)
for r in relationships:
    print(f"{r.relationship_type} -> {r.target_id}")

# Delete a relationship
client.knowledge.delete_relationship(relationship_id="rel_7f8a9b0c")
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/knowledge/relationships` | Create a new relationship |
| `GET` | `/api/v1/knowledge/relationships/:id` | Get a relationship by ID |
| `GET` | `/api/v1/knowledge/relationships?entity_id=:id` | List relationships for an entity |
| `DELETE` | `/api/v1/knowledge/relationships/:id` | Delete a relationship |

### Request Body — Create Relationship

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_id` | string | yes | ID of the source entity |
| `target_id` | string | yes | ID of the target entity |
| `relationship_type` | string | yes | Type label (e.g. `built_with`) |
| `metadata` | object | no | Arbitrary key-value pairs |

### Query Parameters — List Relationships

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entity_id` | string | — | Filter by entity ID |
| `direction` | string | `both` | `incoming`, `outgoing`, or `both` |
| `type` | string | — | Filter by relationship type |

## Examples

### Build a Technology Stack Graph

```python
entities = {
    "backend": client.knowledge.add_entity(name="Backend API", entity_type="service"),
    "frontend": client.knowledge.add_entity(name="Web App", entity_type="service"),
    "postgres": client.knowledge.add_entity(name="PostgreSQL", entity_type="database"),
    "redis": client.knowledge.add_entity(name="Redis", entity_type="cache"),
}

stack = [
    ("backend", "postgres", "built_with"),
    ("backend", "redis", "built_with"),
    ("frontend", "backend", "depends_on"),
]

for src, tgt, rtype in stack:
    client.knowledge.add_relationship(
        source_id=entities[src].id,
        target_id=entities[tgt].id,
        relationship_type=rtype
    )
```

### Query Team Memberships

```python
# Find all people who work at a company
rels = client.knowledge.get_relationships(
    entity_id="entity_acme",
    direction="incoming",
    type="works_at"
)

for r in rels:
    person = client.knowledge.get_entity(r.source_id)
    print(f"{person.name} — {r.metadata.get('role', 'Unknown role')}")
```
