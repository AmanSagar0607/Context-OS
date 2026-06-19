# Context AI — Python SDK

A Python client library for the **Context OS** API. Provides memory, search, crawl, and knowledge graph operations for AI agents.

## Installation

```bash
pip install context-ai
```

Or install from source:

```bash
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS/sdk/python
pip install -e .
```

## Quick Start

```python
from context_ai import ContextAI

# Initialize client
client = ContextAI(
    base_url="http://localhost:8000",
    api_key="your-api-key",  # or set CONTEXT_API_KEY env var
)

# Check health
print(client.health())
```

## Memory Operations

```python
from context_ai import MemoryCreate, MemoryType, ImportanceLevel

# Add a memory
memory = client.memory.add(MemoryCreate(
    content="User prefers dark mode and compact layouts",
    memory_type=MemoryType.SEMANTIC,
    importance=ImportanceLevel.HIGH,
    tags=["preferences", "ui"],
))
print(f"Created memory: {memory.id}")

# Search memories
results = client.memory.search(query="dark mode preferences")
for result in results:
    print(f"Score: {result.score:.2f} - {result.memory.content}")

# Get context window for a query
context = client.memory.context(
    query="What UI settings does the user prefer?",
    max_tokens=2000,
)
print(f"Context has {len(context['memories'])} memories")

# List memories
memories = client.memory.list(memory_type="semantic", limit=10)

# Get related memories
related = client.memory.related(memory_id=memory.id, limit=5)
```

## Web Search

```python
from context_ai import SearchRequest

# Web search
results = client.search.web(SearchRequest(
    query="latest AI agent frameworks 2025",
    max_results=5,
))
for result in results:
    print(f"{result.title}: {result.url}")
```

## Web Crawl

```python
# Scrape a single page
page = client.crawl.scrape(url="https://docs.example.com/api")
print(f"Title: {page.title}")
print(f"Content length: {len(page.content)} chars")

# Crawl a website
from context_ai import CrawlRequest

results = client.crawl.crawl(CrawlRequest(
    url="https://docs.example.com",
    max_pages=20,
    extract_content=True,
))
print(f"Crawled {len(results)} pages")

# Map a website (get all URLs)
urls = client.crawl.map(url="https://example.com", max_pages=100)
print(f"Found {len(urls)} URLs")
```

## Knowledge Graph

```python
from context_ai import EntityCreate, RelationshipCreate

# Create entities
entity = client.knowledge.create_entity(EntityCreate(
    name="GPT-4",
    entity_type="model",
    description="OpenAI's large language model",
    properties={"provider": "OpenAI", "parameters": "1.7T"},
))

# Create relationships
client.knowledge.create_relationship(RelationshipCreate(
    source_id=entity.id,
    target_id="other-entity-id",
    relationship_type="related_to",
    weight=0.9,
))

# Get entity graph
graph = client.knowledge.get_graph(entity.id, depth=2)
print(f"Graph has {len(graph['nodes'])} nodes")

# Search entities
entities = client.knowledge.search(query="language models", entity_type="model")
```

## Async Support

All methods have async equivalents:

```python
import asyncio
from context_ai import ContextAI, MemoryCreate

async def main():
    async with ContextAI() as client:
        # Async memory add
        memory = await client.memory.aadd(MemoryCreate(
            content="Async memory",
        ))

        # Async search
        results = await client.memory.asearch(query="async")

asyncio.run(main())
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONTEXT_API_KEY` | API key for authentication | `None` |
| `CONTEXT_API_URL` | API server URL | `http://localhost:8000` |
| `CONTEXT_OS_URL` | Alias for `CONTEXT_API_URL` | `http://localhost:8000` |
| `CONTEXT_OS_API_KEY` | Alias for `CONTEXT_API_KEY` | `None` |

### Constructor Parameters

```python
client = ContextAI(
    base_url="http://localhost:8000",  # API server URL
    api_key="your-key",                # API key
    timeout=30.0,                      # Request timeout (seconds)
)
```

## Error Handling

```python
from httpx import HTTPStatusError

try:
    memory = client.memory.get("nonexistent-id")
except HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Memory not found")
    elif e.response.status_code == 401:
        print("Authentication failed")
```

## License

MIT License — see [LICENSE](../LICENSE) for details.