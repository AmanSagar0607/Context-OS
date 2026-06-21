# Entities

> Create and manage knowledge entities.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Create entity
entity = client.knowledge.add_entity(
    name="ContextOS",
    type="software",
    properties={"language": "Python", "version": "0.1.0"},
)

# Get entity
entity = client.knowledge.get_entity("contextos")

# Delete entity
client.knowledge.delete_entity(entity.id)
```

## REST API

```bash
# Create
curl -X POST http://localhost:8000/api/v1/knowledge/entities \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "ContextOS", "type": "software", "properties": {"language": "Python"}}'

# Get
curl http://localhost:8000/api/v1/knowledge/entities/contextos \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Entity name |
| `type` | string | required | Entity type |
| `properties` | object | {} | Key-value properties |

## Response

```json
{
  "id": "ent_abc123",
  "name": "ContextOS",
  "type": "software",
  "properties": {"language": "Python", "version": "0.1.0"},
  "created_at": "2026-06-21T12:00:00Z"
}
```
