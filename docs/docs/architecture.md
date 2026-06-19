---
sidebar_position: 3
title: Architecture
---

# Architecture

Context OS is designed as a modular, self-hostable context infrastructure platform.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Protocol                          │
├───────────────┬───────────────┬───────────────┬─────────────┤
│ Memory Tools  │ Search Tools  │ Crawl Tools   │ Knowledge   │
├───────────────┴───────────────┴───────────────┴─────────────┤
│                    FastAPI Server                            │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Memory   │  │ Retrieval│  │ Crawl    │  │ Knowledge  │  │
│  │ Service  │  │ Pipeline │  │ Service  │  │ Service    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                  Data Layer                                  │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐              │
│  │ PostgreSQL   │  │ pgvector │  │ Redis    │              │
│  │ + pgvector   │  │ (embeds) │  │ (cache)  │              │
│  └──────────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Monorepo Structure

```
context-os/
├── apps/
│   └── server/              # FastAPI API server
├── packages/
│   ├── context-core/        # Core engine (memory, embeddings, retrieval)
│   ├── context-db/          # Database migrations
│   └── context-types/       # Shared types
├── sdk/
│   ├── python/              # Python SDK (context-ai)
│   └── typescript/          # TypeScript SDK (context-ai)
├── cli/                     # CLI tool (context-cli)
├── docs/                    # Documentation site
└── examples/                # Usage examples
```

## Core Modules

### Memory Service

The memory service handles persistent agent memory:

- **Storage**: PostgreSQL + pgvector for vector embeddings
- **Types**: Episodic, Semantic, Procedural
- **Search**: Semantic vector search + text search
- **Context**: Assembles context windows from relevant memories

### Retrieval Pipeline

Hybrid retrieval with reciprocal rank fusion:

```
Query → [Vector Search, BM25 Search] → RRF Fusion → Results
```

- **Vector Search**: pgvector cosine similarity
- **BM25 Search**: PostgreSQL full-text search
- **Fusion**: Reciprocal Rank Fusion (RRF) with configurable weights

### Knowledge Graph

Entity-relationship knowledge graph:

- **Entities**: Named entities with types and properties
- **Relationships**: Typed edges with weights
- **Traversal**: Graph traversal with configurable depth
- **Search**: Entity search by name/description

### Crawl Service

Multi-provider web intelligence:

- **Firecrawl**: Primary provider
- **Playwright**: Fallback provider
- **Direct**: HTTP fallback
- **Extract**: AI-powered data extraction

## Database Schema

### Core Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `conversations` | Chat conversations |
| `conversation_messages` | Message history |
| `api_tokens` | API authentication |

### Memory Tables

| Table | Purpose |
|-------|---------|
| `memories` | Unified memory storage |
| `memories_embedding` | pgvector embeddings |

### Knowledge Tables

| Table | Purpose |
|-------|---------|
| `kg_entities` | Knowledge graph entities |
| `kg_relationships` | Entity relationships |
| `kg_entity_embeddings` | Entity embeddings |

## API Endpoints

### Memory API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/memory` | Add memory |
| GET | `/api/v1/memory/{id}` | Get memory |
| PUT | `/api/v1/memory/{id}` | Update memory |
| DELETE | `/api/v1/memory/{id}` | Delete memory |
| POST | `/api/v1/memory/search` | Search memories |
| POST | `/api/v1/memory/context` | Get context window |
| GET | `/api/v1/memory` | List memories |
| GET | `/api/v1/memory/{id}/related` | Get related memories |

### MCP Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mcp` | MCP JSON-RPC |
| POST | `/api/mcp/sse` | MCP SSE transport |
| GET | `/api/mcp/tools` | List MCP tools |
| GET | `/api/mcp/health` | MCP health check |

## Deployment

See [Docker Deployment](/docs/deployment/docker) for production setup.