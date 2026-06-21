# Examples

> Working code examples for common use cases.

## AI Chat with Memory

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

async def chat(user_id: str, message: str):
    # Get user context
    context = client.memory.get_context(
        query=message,
        scope="user",
        scope_id=user_id,
        max_tokens=2000,
    )

    # Generate response with context
    response = await llm.complete(
        f"Context:\n{context}\n\nUser: {message}"
    )

    # Store conversation
    client.memory.add(content=f"User: {message}", type="conversation", metadata={"user_id": user_id})
    client.memory.add(content=f"Assistant: {response}", type="conversation", metadata={"user_id": user_id})

    return response
```

## Research Agent

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

async def research(topic: str):
    # Search web
    web_results = client.search.web(topic, max_results=5)

    # Scrape top results
    articles = []
    for result in web_results.results[:3]:
        article = client.crawl.scrape(result.url)
        articles.append(article)

    # Build context
    context = "\n\n".join([a.content for a in articles])

    # Synthesize
    summary = await llm.complete(f"Summarize:\n{context}")

    # Store knowledge
    client.memory.add(content=summary, type="insight", metadata={"topic": topic})

    return summary
```

## Knowledge Builder

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

async def build_knowledge(url: str):
    # Crawl and extract
    result = client.crawl.extract(url, schema={
        "entities": [{"name": "string", "type": "string"}],
        "relationships": [{"source": "string", "target": "string", "type": "string"}],
    })

    # Add entities
    for entity in result.data.get("entities", []):
        client.knowledge.add_entity(
            name=entity["name"],
            type=entity["type"],
        )

    # Add relationships
    for rel in result.data.get("relationships", []):
        client.knowledge.add_relationship(
            source_id=rel["source"],
            target_id=rel["target"],
            relationship=rel["type"],
        )
```

## Web Monitor

```python
from context_ai import ContextClient
import asyncio

client = ContextClient(api_key="...")

async def monitor(url: str, interval: int = 3600):
    while True:
        # Scrape current state
        current = client.crawl.scrape(url)

        # Check for changes
        recent = client.memory.search(
            query=f"content of {url}",
            top_k=1,
        )

        if recent.results:
            previous = recent.results[0].memory.content
            if current.content != previous:
                # Store change
                client.memory.add(
                    content=f"Change detected on {url}",
                    type="insight",
                    metadata={"url": url},
                )

        # Store current state
        client.memory.add(
            content=current.content,
            type="context",
            metadata={"url": url, "type": "snapshot"},
        )

        await asyncio.sleep(interval)
```

## Customer Support Agent

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

async def support(user_id: str, issue: str):
    # Get user history
    history = client.memory.search(
        query=issue,
        scope="user",
        scope_id=user_id,
        top_k=5,
    )

    # Search knowledge base
    kb_results = client.search.internal(issue, top_k=3)

    # Build context
    context = f"User history:\n{history}\n\nKnowledge base:\n{kb_results}"

    # Generate response
    response = await llm.complete(f"Support context:\n{context}\n\nIssue: {issue}")

    # Store interaction
    client.memory.add(
        content=f"Issue: {issue}\nResolution: {response}",
        type="conversation",
        metadata={"user_id": user_id, "type": "support"},
    )

    return response
```
