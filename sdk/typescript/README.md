# Context AI — TypeScript SDK

A TypeScript client library for the **Context OS** API. Provides memory, search, crawl, and knowledge graph operations for AI agents.

## Installation

```bash
npm install context-ai
# or
yarn add context-ai
# or
pnpm add context-ai
```

## Quick Start

```typescript
import { ContextAI } from "context-ai";

const client = new ContextAI({
  baseUrl: "http://localhost:8000",
  apiKey: "your-api-key", // or set CONTEXT_API_KEY env var
});

// Check health
const health = await client.health();
console.log(health);
```

## Memory Operations

```typescript
import { MemoryType, ImportanceLevel } from "context-ai";

// Add a memory
const memory = await client.memory.add({
  content: "User prefers dark mode and compact layouts",
  memory_type: MemoryType.SEMANTIC,
  importance: ImportanceLevel.HIGH,
  tags: ["preferences", "ui"],
});
console.log(`Created memory: ${memory.id}`);

// Search memories
const results = await client.memory.search({
  query: "dark mode preferences",
});
results.forEach((r) => {
  console.log(`Score: ${r.score.toFixed(2)} - ${r.memory.content}`);
});

// Get context window
const context = await client.memory.context(
  "What UI settings does the user prefer?",
  2000,
);
console.log(`Context has ${context.memories.length} memories`);

// List memories
const memories = await client.memory.list({
  memory_type: "semantic",
  limit: 10,
});

// Get related memories
const related = await client.memory.related(memory.id, 5);
```

## Web Search

```typescript
// Web search
const results = await client.search.web({
  query: "latest AI agent frameworks 2025",
  max_results: 5,
});
results.forEach((r) => {
  console.log(`${r.title}: ${r.url}`);
});

// Internal hybrid search
const internal = await client.search.internal("user preferences", 10);
```

## Web Crawl

```typescript
// Scrape a single page
const page = await client.crawl.scrape("https://docs.example.com/api");
console.log(`Title: ${page.title}`);
console.log(`Content length: ${page.content.length} chars`);

// Crawl a website
const results = await client.crawl.crawl({
  url: "https://docs.example.com",
  max_pages: 20,
  extract_content: true,
});
console.log(`Crawled ${results.length} pages`);

// Map a website
const urls = await client.crawl.map("https://example.com", 100);
console.log(`Found ${urls.length} URLs`);
```

## Knowledge Graph

```typescript
// Create entities
const entity = await client.knowledge.createEntity({
  name: "GPT-4",
  entity_type: "model",
  description: "OpenAI's large language model",
  properties: { provider: "OpenAI", parameters: "1.7T" },
});

// Create relationships
await client.knowledge.createRelationship({
  source_id: entity.id,
  target_id: "other-entity-id",
  relationship_type: "related_to",
  weight: 0.9,
});

// Get entity graph
const graph = await client.knowledge.getGraph(entity.id, 2);
console.log(`Graph has ${graph.nodes.length} nodes`);

// Search entities
const entities = await client.knowledge.search("language models", {
  entity_type: "model",
});
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONTEXT_API_KEY` | API key for authentication | `undefined` |
| `CONTEXT_API_URL` | API server URL | `http://localhost:8000` |
| `CONTEXT_OS_URL` | Alias for `CONTEXT_API_URL` | `http://localhost:8000` |
| `CONTEXT_OS_API_KEY` | Alias for `CONTEXT_API_KEY` | `undefined` |

### Constructor Parameters

```typescript
const client = new ContextAI({
  baseUrl: "http://localhost:8000", // API server URL
  apiKey: "your-key",              // API key
  timeout: 30000,                   // Request timeout (ms)
});
```

## Error Handling

```typescript
try {
  const memory = await client.memory.get("nonexistent-id");
} catch (error) {
  if (error instanceof Error) {
    console.error(`Request failed: ${error.message}`);
  }
}
```

## License

MIT License — see [LICENSE](../../LICENSE) for details.