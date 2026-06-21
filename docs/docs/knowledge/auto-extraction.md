# Auto-Extraction

> Extract entities and relationships from text using LLM-powered analysis.

## Overview

Auto-extraction uses LLMs via OpenRouter to automatically identify entities and relationships in unstructured text. Feed it documents, URLs, or raw strings and get structured knowledge graph data back.

The extraction pipeline detects entity types (people, organizations, technologies, locations), infers relationships between them, and returns results ready to ingest into your knowledge base.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

# Extract from raw text
result = client.knowledge.extract_from_text(
    text="Amy Chen is a senior engineer at Acme Corp. She built the payments service using Go and PostgreSQL.",
    entity_types=["person", "organization", "technology", "service"]
)

print(result.entities)    # [Amy Chen, Acme Corp, Go, PostgreSQL, payments service]
print(result.relationships)  # [works_at, built_with]

# Extract from a URL
result = client.knowledge.extract_from_url(
    url="https://docs.example.com/architecture",
    entity_types=["service", "technology", "database"]
)

# Save extracted data to the knowledge graph
for entity in result.entities:
    client.knowledge.add_entity(
        name=entity.name,
        entity_type=entity.entity_type,
        metadata=entity.metadata
    )

for rel in result.relationships:
    client.knowledge.add_relationship(
        source_id=rel.source_id,
        target_id=rel.target_id,
        relationship_type=rel.relationship_type
    )
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/knowledge/extract` | Extract from text or URL |

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | Either raw text or a URL (auto-detected) |
| `source_type` | string | no | `text` or `url` (default: auto-detect) |
| `entity_types` | string[] | no | Restrict extraction to these types |
| `relationship_types` | string[] | no | Restrict extraction to these types |
| `max_entities` | integer | no | Max entities to extract (default: `50`) |
| `model` | string | no | Override LLM model (default: provider default) |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `entities` | array | Extracted entities with name, type, and metadata |
| `relationships` | array | Extracted relationships with source, target, and type |
| `raw_response` | string | Raw LLM output for debugging |

## Examples

### Extract from a Technical Document

```python
doc = """
Our platform runs on AWS ECS. The API gateway is built with Kong.
User data is stored in DynamoDB. We use Kafka for event streaming.
The ML pipeline depends on the feature store, which reads from S3.
"""

result = client.knowledge.extract_from_text(
    text=doc,
    entity_types=["technology", "service", "database"],
    relationship_types=["built_with", "depends_on"]
)

for rel in result.relationships:
    print(f"{rel.source_name} --[{rel.relationship_type}]--> {rel.target_name}")

# Output:
# API gateway --[built_with]--> Kong
# User data --[stored_in]--> DynamoDB
# ML pipeline --[depends_on]--> feature store
```

### Batch Extract from Multiple URLs

```python
urls = [
    "https://wiki.internal/architecture-overview",
    "https://wiki.internal/data-pipeline",
    "https://wiki.internal/ml-systems",
]

all_entities = []
all_relationships = []

for url in urls:
    result = client.knowledge.extract_from_url(
        url=url,
        entity_types=["service", "technology", "person", "team"]
    )
    all_entities.extend(result.entities)
    all_relationships.extend(result.relationships)

# Deduplicate and ingest
seen = set()
for entity in all_entities:
    if entity.name not in seen:
        client.knowledge.add_entity(
            name=entity.name,
            entity_type=entity.entity_type
        )
        seen.add(entity.name)
```
