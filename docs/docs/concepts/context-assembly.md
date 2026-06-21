# Context Assembly

> How context windows are built for LLMs.

## Overview

Context Assembly is the process of selecting, ranking, and formatting relevant information into a context window that an LLM can use to answer a query.

## How It Works

```
Query → Retrieval → Ranking → Selection → Formatting → Context Window
```

1. **Query Analysis** — Understand what information is needed
2. **Retrieval** — Fetch relevant memories, knowledge, and web content
3. **Ranking** — Score and sort by relevance
4. **Selection** — Choose top-K items within token budget
5. **Formatting** — Structure for LLM consumption

## API

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Get context window for a query
context = client.memory.get_context(
    query="What does the user prefer?",
    max_tokens=4000,
)

print(context)
# {
#   "query": "What does the user prefer?",
#   "memories": [...],
#   "total_tokens": 2500,
#   "truncated": false
# }
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_tokens` | 4000 | Maximum tokens in context window |
| `top_k` | 10 | Maximum memories to include |
| `min_score` | 0.5 | Minimum relevance score |
| `include_metadata` | true | Include memory metadata |
| `format` | "text" | Output format: text, json, markdown |

## Token Budget

The context assembler respects token budgets:

1. Allocate tokens for system prompt
2. Allocate tokens for conversation history
3. Fill remaining with relevant memories
4. Truncate if over budget

## Best Practices

- Set `max_tokens` to 80% of model context window
- Use `min_score` to filter low-quality matches
- Include metadata for better LLM understanding
- Test with real queries to tune parameters
