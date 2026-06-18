# ARCHITECTURE

> Target architecture for Context Infrastructure Platform.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTS                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Python   │  │ TypeScript│  │   CLI    │  │   MCP    │   │
│  │ SDK      │  │ SDK      │  │          │  │ Clients  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────────┼─────────────┼──────────────┘         │
└──────────────────────┼─────────────┼────────────────────────┘
                       │             │
                       ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    API SERVER (FastAPI)                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Memory  │  │  Search  │  │  Crawl   │  │ Knowledge│   │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────────┼─────────────┼──────────────┘         │
│                      │             │                         │
│  ┌───────────────────┴─────────────┴───────────────────┐   │
│  │              Middleware (Auth, Rate Limit)            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONTEXT CORE (Python)                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Memory  │  │ Retrieval│  │Knowledge │  │  Crawl   │   │
│  │ Service  │  │ Pipeline │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  │
│  │Embeddings│  │ Vector   │  │ Graph    │  │ Search   │  │
│  │ Service  │  │ Search   │  │ Queries  │  │ Router   │  │
│  └──────────┘  │ + BM25   │  └──────────┘  └──────────┘  │
│                │ + Rerank  │                                │
│                └──────────┘                                 │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   MCP    │  │ Context  │  │   LLM    │                  │
│  │  Server  │  │ Assembly │  │ Service  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL + pgvector                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ memories │  │ kg_ent-  │  │ users    │  │ usage_   │   │
│  │ +embeds  │  │ ities    │  │ sessions │  │ records  │   │
│  └──────────┘  │ +embeds  │  └──────────┘  └──────────┘   │
│                └──────────┘                                  │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ kg_rel-  │  │ con-     │  │ plans    │                  │
│  │ ations   │  │ versat-  │  │ subscr-  │                  │
│  │          │  │ ions     │  │ iptions  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
context-platform/
├── apps/
│   ├── server/                    # FastAPI API server
│   │   ├── main.py               # App entry point
│   │   ├── config.py             # Server configuration
│   │   ├── routes/
│   │   │   ├── memory.py         # POST/GET/PUT/DELETE /api/v1/memory
│   │   │   ├── search.py         # POST /api/v1/search/*
│   │   │   ├── crawl.py          # POST /api/v1/crawl/*
│   │   │   ├── knowledge.py      # POST/GET/DELETE /api/v1/knowledge/*
│   │   │   ├── mcp.py            # POST /api/v1/mcp
│   │   │   ├── auth.py           # POST /api/v1/auth/*
│   │   │   └── health.py         # GET /api/v1/health
│   │   ├── middleware/
│   │   │   ├── auth.py           # API key + JWT auth
│   │   │   └── rate_limit.py     # Rate limiting by API key
│   │   ├── services/
│   │   │   ├── subscription.py   # Subscription management
│   │   │   ├── payment.py        # BaseUPI integration
│   │   │   ├── oauth.py          # Google/GitHub OAuth
│   │   │   └── auth.py           # Email/password auth
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                       # Next.js dashboard (minimal)
│       ├── app/
│       ├── components/
│       └── package.json
├── packages/
│   ├── context-core/              # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py             # Shared configuration
│   │   ├── llm.py                # OpenRouter LLM service
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── service.py        # MemoryService class
│   │   │   ├── models.py         # Pydantic models
│   │   │   └── agent.py          # Memory agent logic
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py       # Full retrieval pipeline
│   │   │   ├── vector_search.py  # pgvector search
│   │   │   ├── bm25_search.py    # PostgreSQL FTS
│   │   │   ├── fusion.py         # RRF fusion
│   │   │   ├── reranker.py       # Cross-encoder re-ranking
│   │   │   ├── chunking.py       # Recursive chunker
│   │   │   └── expansion.py      # Query expansion (HyDE, multi-query)
│   │   ├── knowledge/
│   │   │   ├── __init__.py
│   │   │   ├── service.py        # KnowledgeService class
│   │   │   ├── models.py         # Entity, Relationship models
│   │   │   └── agent.py          # Knowledge extraction agent
│   │   ├── crawl/
│   │   │   ├── __init__.py
│   │   │   ├── service.py        # CrawlService class
│   │   │   ├── providers/
│   │   │   │   ├── crawl4ai.py   # Crawl4AI provider
│   │   │   │   ├── jina.py       # Jina Reader provider
│   │   │   │   └── httpx.py      # httpx fallback
│   │   │   ├── browser.py        # Playwright automation
│   │   │   ├── extract.py        # AI extraction
│   │   │   └── agent.py          # Research agent
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # Multi-provider search
│   │   │   └── providers/
│   │   │       ├── tavily.py
│   │   │       ├── brave.py
│   │   │       ├── searxng.py
│   │   │       ├── duckduckgo.py
│   │   │       └── google.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   └── service.py        # Pluggable embedding service
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py         # MCP server
│   │   │   ├── tools/
│   │   │   │   ├── memory.py     # Memory MCP tools
│   │   │   │   ├── search.py     # Search MCP tools
│   │   │   │   ├── crawl.py      # Crawl MCP tools
│   │   │   │   └── knowledge.py  # Knowledge MCP tools
│   │   │   └── transport.py      # HTTP/SSE transport
│   │   ├── context/
│   │   │   ├── __init__.py
│   │   │   ├── assembly.py       # Context window assembly
│   │   │   └── compression.py    # Context compression
│   │   └── agent/
│   │       ├── __init__.py
│   │       ├── router.py         # Agent routing
│   │       └── planner.py        # LLM-based planner
│   ├── context-db/                # Database
│   │   ├── migrations/
│   │   │   ├── 001_core.sql      # Users, auth, conversations
│   │   │   ├── 002_memory.sql    # Unified memories + pgvector
│   │   │   ├── 003_knowledge.sql # KG entities + embeddings
│   │   │   └── 004_subscriptions.sql # Plans, usage
│   │   └── seed.sql
│   └── context-types/             # TypeScript types
│       └── src/
├── sdk/
│   ├── python/                    # Python SDK
│   │   ├── context_ai/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── memory.py
│   │   │   ├── search.py
│   │   │   ├── crawl.py
│   │   │   ├── knowledge.py
│   │   │   ├── types.py
│   │   │   └── _http.py
│   │   ├── pyproject.toml
│   │   └── tests/
│   └── typescript/                # TypeScript SDK
│       ├── src/
│       │   ├── index.ts
│       │   ├── client.ts
│       │   ├── memory.ts
│       │   ├── search.ts
│       │   ├── crawl.ts
│       │   ├── knowledge.ts
│       │   ├── types.ts
│       │   └── _http.ts
│       ├── package.json
│       └── tsconfig.json
├── cli/                           # CLI tool
│   ├── context_cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── login.py
│   │   │   ├── memory.py
│   │   │   ├── search.py
│   │   │   ├── crawl.py
│   │   │   ├── knowledge.py
│   │   │   ├── mcp.py
│   │   │   ├── usage.py
│   │   │   └── doctor.py
│   │   ├── config.py
│   │   └── _output.py
│   └── pyproject.toml
├── docs/                          # Documentation
│   ├── docs/
│   ├── src/
│   ├── docusaurus.config.js
│   └── package.json
├── examples/
│   ├── python/
│   ├── typescript/
│   └── mcp/
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml
└── README.md
```

---

## Code Migration Map

| Current | Future | Action |
|---------|--------|--------|
| `backend/main.py` | `apps/server/main.py` | Move |
| `backend/app/routes/*` | `apps/server/routes/*` | Move |
| `backend/app/config.py` | `apps/server/config.py` | Move |
| `backend/app/auth_middleware.py` | `apps/server/middleware/auth.py` | Move |
| `backend/services/memory_store.py` | DELETE | Replace |
| `backend/services/semantic_memory.py` | DELETE | Replace |
| `backend/services/knowledge_graph.py` | `packages/context-core/knowledge/service.py` | Move |
| `backend/services/crawl_service.py` | `packages/context-core/crawl/service.py` | Move |
| `backend/services/crawl4ai_service.py` | `packages/context-core/crawl/providers/crawl4ai.py` | Move |
| `backend/services/search_router.py` | `packages/context-core/search/router.py` | Move |
| `backend/services/browser_automation.py` | `packages/context-core/crawl/browser.py` | Move |
| `backend/services/agent_service.py` | `packages/context-core/crawl/extract.py` | Move |
| `backend/services/postgres_store.py` | `packages/context-core/db.py` | Move |
| `backend/services/openrouter.py` | `packages/context-core/llm.py` | Move |
| `backend/services/mcp_server.py` | `packages/context-core/mcp/server.py` | Move |
| `backend/agents/retrieval_agent.py` | `packages/context-core/retrieval/` | Merge |
| `backend/agents/memory_agent.py` | `packages/context-core/memory/agent.py` | Move |
| `backend/agents/research_agent.py` | `packages/context-core/crawl/agent.py` | Move |
| `backend/agents/knowledge_agent.py` | `packages/context-core/knowledge/agent.py` | Move |
| `backend/agents/router.py` | `packages/context-core/agent/router.py` | Move |
| `backend/rag/retriever.py` | DELETE | Replace |
| `backend/rag/prompt_builder.py` | `packages/context-core/context/` | Move |
| `backend/embeddings/embedder.py` | `packages/context-core/embeddings/service.py` | Move |
| `backend/vector_db/*` | DELETE | Replace with pgvector |
| `backend/services/chunking.py` | `packages/context-core/retrieval/chunking.py` | Move |

### Files Deleted

| File | Reason |
|------|--------|
| `backend/services/memory_store.py` | SQLite replaced |
| `backend/services/semantic_memory.py` | SQLite replaced |
| `backend/vector_db/*` | Milvus replaced |
| `backend/rag/retriever.py` | Merged into retrieval |
| `backend/rag/prompt_builder.py` | Merged into context |
| `backend/agents/planner.py` | Replaced by LLM planner |
| `backend/agents/citation_agent.py` | Merged into retrieval |
| `backend/agents/workflow_agent.py` | Postponed |
| `backend/agents/tools.py` | CrewAI postponed |
| `backend/agents/flows.py` | CrewAI postponed |
| `backend/agents/crawl_agents.py` | CrewAI postponed |
| `backend/services/ag_ui_events.py` | Workspace feature |
| `backend/services/pdf_*.py` | Workspace feature |
| `backend/services/tokenizer_viz.py` | Workspace feature |
| `backend/services/document_store.py` | Workspace feature |
| `backend/services/pipeline_runner.py` | Workspace feature |
| `backend/services/web_search.py` | Merged into search router |

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/memory` | Store memory |
| GET | `/api/v1/memory/:id` | Get memory |
| PUT | `/api/v1/memory/:id` | Update memory |
| DELETE | `/api/v1/memory/:id` | Delete memory |
| POST | `/api/v1/memory/search` | Semantic search |
| POST | `/api/v1/memory/context` | Get context window |
| GET | `/api/v1/memory/timeline` | Episodic timeline |
| GET | `/api/v1/memory/related` | Related memories |
| POST | `/api/v1/memory/batch` | Batch operations |
| POST | `/api/v1/search/web` | Web search |
| POST | `/api/v1/search/internal` | Internal hybrid search |
| POST | `/api/v1/crawl/scrape` | Scrape URL |
| POST | `/api/v1/crawl/crawl` | Crawl website |
| POST | `/api/v1/crawl/map` | Map website |
| POST | `/api/v1/crawl/extract` | AI extraction |
| POST | `/api/v1/crawl/browser` | Playwright render |
| POST | `/api/v1/knowledge/entities` | Create entity |
| GET | `/api/v1/knowledge/entities/:id` | Get entity |
| DELETE | `/api/v1/knowledge/entities/:id` | Delete entity |
| POST | `/api/v1/knowledge/relationships` | Create relationship |
| GET | `/api/v1/knowledge/graph/:id` | Get entity graph |
| POST | `/api/v1/knowledge/search` | Search entities |
| POST | `/api/v1/mcp` | MCP JSON-RPC |
| GET | `/api/v1/mcp/tools` | List MCP tools |
| POST | `/api/v1/auth/signup` | Register |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/health` | Health check |

---

## Database Schema

### Core Tables (001_core.sql)

- `users` — User accounts
- `user_profiles` — Profile data
- `auth_identities` — Auth providers
- `user_sessions` — Sessions
- `api_tokens` — API tokens
- `roles` — RBAC roles
- `permissions` — RBAC permissions
- `conversations` — Chat threads
- `messages` — Chat messages

### Memory Tables (002_memory.sql)

- `memories` — Unified memory store with pgvector
- `memory_links` — Graph relationships between memories
- `conversation_messages` — Conversation history

### Knowledge Tables (003_knowledge.sql)

- `kg_entities` — Knowledge graph entities with embeddings
- `kg_relationships` — Entity relationships
- `entity_memory_links` — Entity-to-memory connections

### Subscription Tables (004_subscriptions.sql)

- `plans` — Plan definitions
- `plan_limits` — Per-plan rate limits
- `subscriptions` — User subscriptions
- `usage_records` — Usage events
- `usage_aggregates` — Pre-computed usage

---

*Last updated: 2026-06-19*
