# Graph Queries

> Traverse and query the knowledge graph with depth control and type filtering.

## Overview

Graph queries let you explore connections between entities beyond direct neighbors. Use them to discover indirect relationships, find shortest paths between entities, and run complex traversals with depth limits and relationship type filters.

All graph queries return structured results with full entity and relationship data, making it easy to build context windows for AI agents.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

# Query the graph from a starting entity
result = client.knowledge.query(
    start_id="entity_amy_01",
    max_depth=3,
    relationship_types=["works_at", "depends_on"]
)
print(result.entities)   # All reachable entities
print(result.edges)      # All traversed relationships

# Get direct neighbors
neighbors = client.knowledge.get_neighbors(
    entity_id="entity_backend",
    direction="both"
)
for n in neighbors:
    print(f"{n.entity.name} via {n.relationship_type}")

# Find path between two entities
path = client.knowledge.find_path(
    source_id="entity_amy_01",
    target_id="entity_redis",
    max_depth=5
)
if path:
    print(f"Found path with {len(path.hops)} hops")
    for hop in path.hops:
        print(f"  {hop.source} --[{hop.relationship_type}]--> {hop.target}")
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/knowledge/graph/query` | Run a depth-limited traversal |
| `GET` | `/api/v1/knowledge/graph/:entity_id/neighbors` | Get neighbors of an entity |
| `GET` | `/api/v1/knowledge/graph/path?source=:id&target=:id` | Find shortest path |

### Request Body — Graph Query

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_id` | string | yes | Starting entity ID |
| `max_depth` | integer | no | Max traversal depth (default: `2`, max: `10`) |
| `relationship_types` | string[] | no | Filter by these types only |
| `direction` | string | no | `incoming`, `outgoing`, or `both` (default: `both`) |
| `include_metadata` | boolean | no | Include relationship metadata (default: `false`) |

### Query Parameters — Neighbors

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `direction` | string | `both` | `incoming`, `outgoing`, or `both` |
| `type` | string | — | Filter by relationship type |

### Query Parameters — Find Path

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | string | — | Source entity ID |
| `target` | string | — | Target entity ID |
| `max_depth` | integer | `5` | Maximum path length |

## Examples

### Find All Downstream Dependencies

```python
result = client.knowledge.query(
    start_id="entity_backend_api",
    max_depth=4,
    relationship_types=["depends_on"],
    direction="outgoing"
)

for entity in result.entities:
    print(f"Dependency: {entity.name} ({entity.entity_type})")
```

### Discover Team Impact

```python
# Who is affected if Redis goes down?
result = client.knowledge.query(
    start_id="entity_redis",
    max_depth=3,
    relationship_types=["built_with", "depends_on"],
    direction="incoming"
)

services = [e for e in result.entities if e.entity_type == "service"]
print(f"{len(services)} services depend on Redis:")
for svc in services:
    print(f"  - {svc.name}")
```

### Shortest Path Discovery

```python
path = client.knowledge.find_path(
    source_id="entity_new_dev",
    target_id="entity_legacy_db",
    max_depth=6
)

if path:
    print("Connection found:")
    for i, hop in enumerate(path.hops):
        arrow = f" --[{hop.relationship_type}]--> "
        print(f"  {hop.source}" + arrow + hop.target, end="")
    print()
else:
    print("No path found within depth limit")
```
