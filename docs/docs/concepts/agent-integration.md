# Agent Integration

> How AI agents use ContextOS.

## Overview

ContextOS is designed as infrastructure for AI agents. Any agent framework (LangGraph, CrewAI, AutoGen, custom) can integrate via REST API, SDK, or MCP.

## Integration Patterns

### Pattern 1: Direct API

```python
import httpx

async def agent_step(query: str, user_id: str):
    # Search memory for context
    resp = httpx.post("http://localhost:8000/api/v1/memory/search", json={
        "query": query,
        "top_k": 5,
    }, headers={"Authorization": f"Bearer {api_key}"})

    context = resp.json()["results"]

    # Use context with LLM
    answer = await llm.complete(query, context=context)

    # Store new memory
    httpx.post("http://localhost:8000/api/v1/memory", json={
        "content": f"Q: {query}\nA: {answer}",
        "type": "conversation",
        "metadata": {"user_id": user_id},
    }, headers={"Authorization": f"Bearer {api_key}"})

    return answer
```

### Pattern 2: SDK

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

async def agent_step(query: str, user_id: str):
    # Get context
    context = client.memory.get_context(query, max_tokens=2000)

    # Generate answer
    answer = await llm.complete(query, context=context)

    # Store memory
    client.memory.add(content=f"Q: {query}\nA: {answer}")

    return answer
```

### Pattern 3: MCP

```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp"
    }
  }
}
```

## Agent Types

| Agent Type | ContextOS Usage |
|------------|-----------------|
| Chat Agent | Memory search + store per turn |
| Research Agent | Web search + crawl + memory |
| Coding Agent | Knowledge graph + memory |
| Support Agent | Conversation memory + context |
| RAG Agent | Hybrid retrieval + context assembly |

## Best Practices

- Store conversations as memories
- Use metadata for user/session tracking
- Set importance scores for long-term retention
- Use context assembly for token-efficient prompts
- Leverage knowledge graph for entity relationships
