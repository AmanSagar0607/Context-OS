# Context Windows

> Assemble context for LLM prompts.

## Overview

Context Windows assemble relevant memories into a formatted prompt that LLMs can use to answer queries.

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Get context window
context = client.memory.get_context(
    query="What does the user prefer?",
    max_tokens=4000,
)

# Use in LLM prompt
prompt = f"""Answer based on context:

{context}

Question: What does the user prefer?
"""
```

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/memory/context \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the user prefer?",
    "max_tokens": 4000
  }'
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Context query |
| `max_tokens` | int | 4000 | Token budget |
| `top_k` | int | 10 | Max memories to include |
| `min_score` | float | 0.5 | Minimum relevance score |
| `format` | string | "text" | Output format |

## Output Formats

### Text (default)

```
Relevant context:
1. User prefers dark mode (score: 0.89)
2. User is located in India (score: 0.75)
```

### JSON

```json
{
  "memories": [...],
  "total_tokens": 2500,
  "truncated": false
}
```

### Markdown

```markdown
## Relevant Context

1. **User prefers dark mode** (score: 0.89)
2. **User is located in India** (score: 0.75)
```

## Token Budget Management

1. System prompt takes priority
2. Conversation history comes next
3. Relevant memories fill remaining budget
4. Truncation occurs if over budget
