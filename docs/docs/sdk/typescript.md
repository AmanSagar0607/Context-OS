---
sidebar_position: 9
title: TypeScript SDK
---

# TypeScript SDK

A TypeScript client library for the Context OS API.

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
  apiKey: "your-api-key",
});
```

## Memory Operations

### Add Memory

```typescript
import { MemoryType, ImportanceLevel } from "context-ai";

const memory = await client.memory.add({
  content: "User prefers dark mode",
  memory_type: MemoryType.SEMANTIC,
  importance: ImportanceLevel.HIGH,
  tags: ["preferences", "ui"],
});
```

### Search Memories

```typescript
const results = await client.memory.search({
  query: "dark mode",
});

results.forEach((r) => {
  console.log(`${r.score.toFixed(2)}: ${r.memory.content}`);
});
```

### Get Context Window

```typescript
const context = await client.memory.context("UI preferences", 2000);
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CONTEXT_API_KEY` | API key |
| `CONTEXT_API_URL` | API server URL |

### Constructor

```typescript
const client = new ContextAI({
  baseUrl: "http://localhost:8000",
  apiKey: "your-key",
  timeout: 30000,
});
```

## API Reference

### MemoryClient

| Method | Description |
|--------|-------------|
| `add(request)` | Add memory |
| `get(memoryId)` | Get memory |
| `update(memoryId, request)` | Update memory |
| `delete(memoryId)` | Delete memory |
| `search(request)` | Search memories |
| `context(query, maxTokens)` | Get context window |
| `list(options)` | List memories |
| `related(memoryId, limit)` | Get related memories |

### SearchClient

| Method | Description |
|--------|-------------|
| `web(request)` | Web search |
| `internal(query, topK)` | Internal search |

### CrawlClient

| Method | Description |
|--------|-------------|
| `scrape(url)` | Scrape URL |
| `crawl(request)` | Crawl website |
| `map(url, maxPages)` | Map website |
| `extract(url, prompt)` | AI extraction |

### KnowledgeClient

| Method | Description |
|--------|-------------|
| `createEntity(request)` | Create entity |
| `getEntity(entityId)` | Get entity |
| `deleteEntity(entityId)` | Delete entity |
| `createRelationship(request)` | Create relationship |
| `getGraph(entityId, depth)` | Get graph |
| `search(query)` | Search entities |