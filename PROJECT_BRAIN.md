# PROJECT BRAIN

> Permanent strategic memory of the Context Infrastructure Platform.
> Every future task must reference this file before making recommendations.

---

## Vision

The open-source context infrastructure that gives AI agents memory, web intelligence, and structured knowledge — via a single API and MCP server.

## Mission

Provide persistent context, memory, retrieval, knowledge, and web intelligence infrastructure for AI applications and agents.

## Positioning

The open-source alternative to Mem0 + Firecrawl + MCP — unified into a single context infrastructure platform for AI agents.

## Tagline

AI can finally remember.

## North Star

Every AI agent should be able to remember, search the web, and build knowledge — without rebuilding infrastructure from scratch.

## North Star Metric

**Retrieval precision@5.** Measure how often the top-5 retrieved chunks actually contain the answer. Target: 85%+.

## Product Thesis

Every AI application eventually needs:

- Memory
- Context
- Retrieval
- Knowledge
- Search
- Web Intelligence

Today these capabilities are fragmented across multiple tools.

The long-term opportunity is to unify them into a single developer platform.

Think:

```
Memory Layer + Retrieval Layer + Knowledge Layer + Web Intelligence Layer + MCP Layer
```

Instead of:

```
Chat UI + Productivity Tool + AI Workspace
```

---

## What We Are NOT Building

- AI Operating System
- AI Workspace
- ChatGPT Clone
- Productivity Platform
- PDF Chat Application
- Personal Assistant

## What We ARE Building

Context Infrastructure Platform for AI Agents.

Modules:

| Module | Purpose | Competitor |
|--------|---------|------------|
| Memory | Persistent agent memory with semantic search | Mem0, Zep |
| Search | Hybrid web + internal search | Firecrawl (partial) |
| Crawl | Web intelligence with fallback chain | Firecrawl, Crawl4AI |
| Knowledge | Entity/relationship extraction and graph | Custom |
| MCP | MCP servers for all of the above | Custom |

---

## Competitive Analysis

### Mem0

- **What they do:** Memory layer for AI agents.
- **Strengths:** Clean API, good docs, growing adoption.
- **Weaknesses:** Memory only. No web intelligence. No knowledge graph. No MCP.
- **Our differentiation:** Memory + Web Intelligence + Knowledge Graph + MCP in one platform.

### Firecrawl

- **What they do:** Web scraping/crawling API.
- **Strengths:** Multi-provider scraping, good DX, self-hostable.
- **Weaknesses:** No memory. No knowledge graph. No MCP. No internal search.
- **Our differentiation:** Web intelligence + Memory + Knowledge Graph + MCP.

### Zep

- **What they do:** Memory + knowledge for AI assistants.
- **Strengths:** Temporal knowledge graph, long-term memory.
- **Weaknesses:** Focus on chat assistants. No web intelligence. No MCP.
- **Our differentiation:** Broader scope (web intelligence), MCP-native.

### Letta

- **What they do:** Stateful AI agents with memory.
- **Strengths:** Agent state management, memory architecture.
- **Weaknesses:** Agent framework, not infrastructure. No web intelligence.
- **Our differentiation:** Infrastructure layer, not agent framework. MCP-native.

### LangGraph

- **What they do:** Agent orchestration framework.
- **Strengths:** Graph-based workflows, large ecosystem.
- **Weaknesses:** Orchestration only. No built-in memory/search/crawl infrastructure.
- **Our differentiation:** Infrastructure layer that LangGraph agents can consume.

### CrewAI

- **What they do:** Multi-agent orchestration.
- **Strengths:** Simple agent definition, role-based agents.
- **Weaknesses:** Orchestration only. No memory/search/crawl infrastructure.
- **Our differentiation:** Infrastructure layer, not orchestration framework.

### Competitive Summary

| Capability | Mem0 | Firecrawl | Zep | Letta | LangGraph | CrewAI | **Context** |
|------------|------|-----------|-----|-------|-----------|--------|-------------|
| Memory | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Web Search | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Web Crawl | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Knowledge Graph | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| MCP | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Self-hostable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Open Source | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**The combination is unique. No one else has all five capabilities in one platform.**

---

## Current State Assessment

### Existing Strengths

| Component | Quality | Notes |
|-----------|---------|-------|
| Crawl service | 7/10 | Multi-provider fallback (Crawl4AI→Jina→httpx). Production-quality. |
| Search router | 7/10 | 5-provider fallback (Tavily→Brave→SearXNG→DDG→Google). Battle-tested. |
| Knowledge graph schema | 6/10 | Solid PostgreSQL schema. Tables exist but are empty. |
| MCP server | 6/10 | 5 tools, JSON-RPC, HTTP/SSE. Working. |
| Agent pipeline | 5/10 | Planner→Router→7 Agents. Architecture right, implementation needs work. |
| PostgreSQL schema | 6/10 | 28+ tables. Solid foundation. |
| Docker setup | 6/10 | Compose works. |
| Test suite | 5/10 | 15 tests passing. Coverage minimal. |

### Existing Weaknesses

| Component | Quality | Notes |
|-----------|---------|-------|
| Memory system | 3/10 | Fragmented across SQLite/PostgreSQL. O(n) scan. Not scalable. |
| Retrieval | 4/10 | Vector-only. No re-ranking, no BM25, no hybrid. |
| Chunking | 3/10 | Fixed 500-char windows. Breaks mid-sentence. |
| Context assembly | 3/10 | Raw chunk concatenation. No compression, no filtering. |
| Knowledge graph | 2/10 | Schema exists but empty. Not connected to retrieval. |
| Planner | 3/10 | Keyword-based. Should be LLM-based. |
| Developer experience | 2/10 | No SDK, no CLI, no docs, no onboarding. |

### Technical Debt

| Debt | Impact | Priority |
|------|--------|----------|
| SQLite dependency | Cannot scale, not production-grade | Critical |
| Milvus/Zilliz dependency | External service, not self-hostable | Critical |
| Fixed chunking | Poor retrieval quality | High |
| Keyword-based planner | Limited query understanding | High |
| Empty knowledge graph | No value from KG infrastructure | High |
| No SDK/CLI/docs | Cannot adopt | Critical |
| Split memory systems | Confusing, un maintainable | Critical |

### Production Ready Components

| Component | Ready? | Notes |
|-----------|--------|-------|
| Crawl service | ✅ | Multi-provider fallback works. |
| Search router | ✅ | 5-provider fallback works. |
| MCP server | ✅ | 5 tools work. |
| PostgreSQL schema | ✅ | Migrations work. |
| Docker setup | ✅ | Compose works. |
| Auth system | ✅ | Email/password + OAuth + API tokens. |

### Experimental Components

| Component | Status | Notes |
|-----------|--------|-------|
| Agent pipeline | Prototype | Works for basic cases, not production-grade. |
| Knowledge graph extraction | Prototype | Pattern + LLM extraction works, but not automated. |
| Semantic memory | Prototype | SQLite + numpy. Works but doesn't scale. |
| CrewAI integration | Prototype | Tightly coupled. Needs refactor or removal. |

---

## Architecture Decisions

### ADR-001: Database

**Decision:** PostgreSQL + pgvector.

**Rationale:**
- Single database for all structured data.
- pgvector replaces Milvus (eliminates external dependency).
- Self-hostable.
- Proven at scale.

**Rejected alternatives:**
- Milvus/Zilliz: External dependency, not self-hostable.
- SQLite: Cannot scale, not production-grade.
- Separate vector DB: Adds complexity.

### ADR-002: Search Architecture

**Decision:** Hybrid Search (pgvector + PostgreSQL FTS + RRF fusion).

**Rationale:**
- Vector search handles semantic queries.
- BM25 handles exact-match queries.
- Reciprocal Rank Fusion combines results.
- All within PostgreSQL, no external dependencies.

**Rejected alternatives:**
- Vector-only: Misses exact-match queries.
- BM25-only: Misses semantic queries.
- External search (Elasticsearch): Adds complexity.

### ADR-003: Retrieval Architecture

**Decision:** Agentic Hybrid Retrieval.

**Rationale:**
- Query expansion (HyDE, multi-query) improves recall.
- Hybrid search (vector + BM25) improves coverage.
- Re-ranking improves precision.
- Agent loops enable self-correction.

**Rejected alternatives:**
- Simple RAG: Too basic for production use.
- Full agentic: Too complex for v1.

### ADR-004: Memory Architecture

**Decision:** Unified Memory System on PostgreSQL + pgvector.

**Rationale:**
- Single storage backend for all memory types.
- pgvector enables semantic search on memories.
- PostgreSQL tsvector enables BM25 on memories.
- Eliminates SQLite dependency.

**Rejected alternatives:**
- SQLite (current): Cannot scale.
- Separate memory DB: Adds complexity.
- External memory service: Adds dependency.

### ADR-005: Knowledge Architecture

**Decision:** PostgreSQL knowledge graph with entity embeddings.

**Rationale:**
- Existing schema is solid.
- Add pgvector embeddings for entity search.
- Connect to retrieval pipeline.
- Auto-extract from crawl results.

**Rejected alternatives:**
- Neo4j: External dependency.
- Separate graph DB: Adds complexity.

### ADR-006: MCP Architecture

**Decision:** Native MCP support with 4 tool groups.

**Rationale:**
- MCP is becoming the standard for agent-tool integration.
- 4 tool groups cover all platform capabilities.
- HTTP + SSE transport for flexibility.
- stdio transport for local development.

**Rejected alternatives:`
- Custom tool protocol: Non-standard.
- No MCP: Misses agent adoption channel.

### ADR-007: Embedding Strategy

**Decision:** Pluggable embedding service with sentence-transformers default.

**Rationale:**
- sentence-transformers runs locally (no API cost).
- Pluggable allows OpenAI/Cohere for better quality.
- 384-dim default (all-MiniLM-L6-v2) is efficient.
- Users can override with larger models.

### ADR-008: Chunking Strategy

**Decision:** Recursive chunking (paragraph → sentence → 500 chars).

**Rationale:**
- Respects document structure better than fixed windows.
- Preserves sentence boundaries.
- Configurable chunk size and overlap.
- Falls back gracefully for unstructured text.

**Rejected alternatives:**
- Fixed chunking: Breaks mid-sentence.
- Semantic chunking: Too expensive for v1.
- Agentic chunking: Too complex for v1.

### ADR-009: Context Assembly

**Decision:** Context windows with compression.

**Rationale:**
- Retrieve more chunks than needed.
- Re-rank to top-K.
- Compress to fit token budget.
- Assemble structured context for LLM.

### ADR-010: SDK Philosophy

**Decision:** Mirror API surface exactly.

**Rationale:**
- `context.memory.add()` maps to `POST /api/v1/memory`.
- `context.search.web()` maps to `POST /api/v1/search/web`.
- No hidden behavior.
- Easy to learn if you know the API.

---

## Product Structure

```
context-platform/
├── apps/
│   ├── server/              # FastAPI backend (API server)
│   └── web/                 # Next.js dashboard (minimal admin UI)
├── packages/
│   ├── context-core/        # Shared business logic (Python)
│   │   ├── memory/          # Memory service
│   │   ├── retrieval/       # Hybrid retrieval
│   │   ├── knowledge/       # Knowledge graph
│   │   ├── crawl/           # Web intelligence
│   │   ├── search/          # Search router
│   │   ├── embeddings/      # Embedding service
│   │   ├── mcp/             # MCP server
│   │   ├── context/         # Context assembly
│   │   └── llm.py           # LLM service
│   ├── context-db/          # Database migrations + schemas
│   └── context-types/       # Shared TypeScript types
├── sdk/
│   ├── python/              # Python SDK (context-ai)
│   └── typescript/          # TypeScript SDK (@context-ai/sdk)
├── cli/                     # CLI tool (context-cli)
├── docs/                    # Docusaurus documentation
└── examples/                # Starter templates
```

### Ownership Boundaries

| Package | Owner | Scope |
|---------|-------|-------|
| `context-core/memory` | Memory service | CRUD, search, context assembly, consolidation |
| `context-core/retrieval` | Retrieval service | Hybrid search, fusion, re-ranking, chunking |
| `context-core/knowledge` | Knowledge service | Entity/relationship CRUD, graph queries, extraction |
| `context-core/crawl` | Crawl service | Scrape, crawl, map, extract, browser |
| `context-core/search` | Search service | Web search, internal search, provider routing |
| `context-core/embeddings` | Embedding service | Model loading, embedding generation |
| `context-core/mcp` | MCP service | Tool definitions, JSON-RPC, transport |
| `context-core/context` | Context service | Context assembly, compression, token management |
| `apps/server` | API service | Routes, middleware, auth, billing |
| `sdk/python` | Python SDK | Client library |
| `sdk/typescript` | TypeScript SDK | Client library |
| `cli` | CLI tool | Command-line interface |
| `docs` | Documentation | All documentation |

---

## SDK Strategy

### Design Philosophy

1. Mirror the API surface exactly.
2. No hidden behavior.
3. Type-safe (Pydantic for Python, TypeScript types for TS).
4. Async-first for Python.
5. Configurable via constructor.

### Python SDK

Package: `context-ai`

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")
result = client.memory.search(query="user preferences")
```

### TypeScript SDK

Package: `@context-ai/sdk`

```typescript
import { ContextClient } from '@context-ai/sdk';

const client = new ContextClient({ apiKey: '...' });
const result = await client.memory.search({ query: 'user preferences' });
```

### CLI

Package: `context-cli`

```bash
context memory add "user prefers dark mode"
context search "AI startups 2026"
context crawl https://example.com
```

---

## Documentation Strategy

### Inspiration

- Mem0: Clean API reference, quickstart-first.
- Firecrawl: Good examples, developer-focused.
- Stripe: Best-in-class API reference.
- Supabase: Good self-hosting docs.
- Resend: Clean, minimal docs.

### Navigation

```
Getting Started → Quickstart → First API Call → First Memory → First Crawl
Core Concepts → Memory → Retrieval → Knowledge → Search → MCP
SDKs → Python → TypeScript
CLI → Commands → Configuration
API Reference → All endpoints
Examples → AI Chat → Research Agent → Knowledge Builder
Self Hosting → Docker → Configuration → Production
```

### Goal

A developer should get value within 5 minutes.

---

## Open Source Strategy

### Tiers

| Tier | Price | Features |
|------|-------|----------|
| Community (OSS) | Free | All core features, self-hostable |
| Cloud | $29-99/mo | Managed hosting, all providers, analytics |
| Enterprise | Custom | SSO, audit logs, custom, support |

### Anti-Paywall Rules

Never paywall:
- Core API functionality
- Self-hosting capability
- SDK/CLI access
- MCP tools

Cloud must be strictly better, not the only way to use it.

### What Stays OSS

- Memory API
- Search API
- Crawl API
- Knowledge API
- MCP servers
- Python SDK
- TypeScript SDK
- CLI
- Docker deployment
- Documentation

### What Becomes Paid

- Managed hosting (Cloud)
- Paid search providers (Tavily, Brave, Google)
- Cross-encoder re-ranking (compute-intensive)
- Analytics dashboard
- Priority support
- Team collaboration

### What Becomes Enterprise

- SSO/SAML
- Audit logs
- Custom providers
- Dedicated support
- On-prem deployment
- Custom SLA

---

## Billing Strategy

### Provider

**Polar** (recommended over LemonSqueezy).

### Model

Usage-based billing per API key.

### Resources Tracked

| Resource | Unit | Free Limit | Pro Limit |
|----------|------|------------|-----------|
| memory.store | per memory | 1K/month | 100K/month |
| memory.search | per query | 100/day | 10K/day |
| crawl.scrape | per URL | 100/day | 10K/day |
| crawl.crawl | per page | 100/day | 10K/day |
| search.web | per query | 50/day | 5K/day |
| knowledge.entity | per entity | 100/month | 10K/month |

### Implementation

- Track in `usage_records` table.
- Enforce at API middleware layer.
- Rate limit by API key.
- Monthly billing cycle.

---

## 30 Day Execution Plan

### Week 1: Architecture Extraction + Memory Foundation

**Goal:** Restructure repository and build unified memory system.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Create monorepo structure | Directory layout |
| 1 | Create `packages/context-core/` | Shared config |
| 2 | Create `packages/context-db/migrations/002_memory.sql` | Unified memories table |
| 3 | Create `packages/context-core/memory/service.py` | MemoryService class |
| 4 | Create `packages/context-core/embeddings/service.py` | EmbeddingService |
| 4 | Create `packages/context-core/retrieval/vector_search.py` | pgvector search |
| 5 | Create `packages/context-core/retrieval/bm25_search.py` | PostgreSQL FTS |
| 5 | Create `packages/context-core/retrieval/fusion.py` | RRF fusion |
| 6 | Create `apps/server/routes/memory.py` | Memory REST API |
| 7 | Write memory tests | 10 tests passing |

**Deliverable:** Unified memory with pgvector, hybrid search, REST API.

### Week 2: Retrieval + Knowledge + Crawl Integration

**Goal:** Build hybrid retrieval pipeline and connect knowledge graph.

| Day | Task | Deliverable |
|-----|------|-------------|
| 8 | Create `packages/context-core/retrieval/reranker.py` | Re-ranking |
| 8 | Create `packages/context-core/retrieval/chunking.py` | Recursive chunker |
| 9 | Create `packages/context-core/retrieval/pipeline.py` | Full pipeline |
| 10 | Move knowledge_graph.py → `packages/context-core/knowledge/` | Knowledge service |
| 11 | Create knowledge + search + crawl routes | All REST APIs |
| 12 | Move crawl_service.py → `packages/context-core/crawl/` | Crawl service |
| 13 | Move search_router.py → `packages/context-core/search/` | Search service |
| 14 | Write tests | 20 tests passing |

**Deliverable:** Hybrid retrieval, knowledge integration, all core APIs.

### Week 3: SDK + CLI + MCP

**Goal:** Build developer-facing tools.

| Day | Task | Deliverable |
|-----|------|-------------|
| 15 | Create Python SDK package | `context-ai` |
| 16 | Implement all SDK clients | Python SDK complete |
| 17 | Create TypeScript SDK package | `@context-ai/sdk` |
| 18 | Create CLI package | `context-cli` |
| 19 | Create MCP server with 4 tool groups | MCP complete |
| 20 | Write SDK tests | 30 tests passing |
| 21 | Write CLI tests | 10 tests passing |

**Deliverable:** Python SDK, TypeScript SDK, CLI, MCP server.

### Week 4: Docs + Docker + Polish

**Goal:** Make everything deployable and documented.

| Day | Task | Deliverable |
|-----|------|-------------|
| 22 | Create Docusaurus docs site | Documentation structure |
| 23 | Write Getting Started + Memory docs | Core docs |
| 24 | Write Crawl + Knowledge + MCP docs | Feature docs |
| 25 | Write SDK + CLI docs | Developer docs |
| 26 | Write API reference | Complete API docs |
| 27 | Create Docker Compose files | Deployment ready |
| 28 | Create README + examples | Repository ready |
| 29 | Final test suite | 60+ tests passing |
| 30 | Package publishing prep | Ready to publish |

**Deliverable:** Documentation, Docker, examples, launch-ready.

---

## 90 Day Plan

### 30 Days: Launch Readiness

- Unified memory system
- Hybrid retrieval
- Knowledge graph connected
- Python + TypeScript SDK
- CLI tool
- MCP server
- Documentation
- Docker deployment

### 60 Days: Developer Adoption

- Product Hunt launch
- Hacker News post
- 100 GitHub stars
- 10 external users
- 5 external contributors
- Memory consolidation feature
- HyDE query expansion
- 50+ tests

### 90 Days: Revenue

- Cloud deployment
- Usage-based billing (Polar)
- 500 GitHub stars
- 50 external users
- 10 paying customers
- Cross-encoder re-ranking
- Knowledge auto-extraction from crawl
- 100+ tests

---

## Product Principles

1. **Developer first.** Every decision optimizes for developer experience.
2. **API first.** Every feature has an API before it has a UI.
3. **SDK first.** Every API has a SDK before it has a CLI.
4. **CLI first.** Every SDK has a CLI before it has a dashboard.
5. **Self-hostable first.** Every feature works locally before it works in the cloud.
6. **Open source first.** Every core feature is open source.
7. **Context before chat.** Context infrastructure is the product, not chat.
8. **Memory before UI.** Memory system is the foundation, UI is optional.
9. **Infrastructure before applications.** Build the platform, not the app.
10. **Adoption before complexity.** Simple and adopted > complex and ignored.

---

## Current Priorities

| Priority | Status | Owner |
|----------|--------|-------|
| 1. Architecture extraction | ✅ Completed | Tech Lead |
| 2. Unified memory system | 🔄 In Progress | Tech Lead |
| 3. Hybrid retrieval | Not Started | Tech Lead |
| 4. Python SDK | Not Started | Tech Lead |
| 5. TypeScript SDK | Not Started | Tech Lead |
| 6. CLI tool | Not Started | Tech Lead |
| 7. MCP server refactor | Not Started | Tech Lead |
| 8. Documentation | Not Started | Tech Lead |
| 9. Docker deployment | Not Started | Tech Lead |
| 10. Launch preparation | Not Started | Tech Lead |

## Completed (2026-06-19)

### Week 1 Progress

- [x] Created monorepo structure (`apps/`, `packages/`, `sdk/`, `cli/`, `docs/`, `examples/`)
- [x] Created `packages/context-core/config.py` — shared configuration
- [x] Created `packages/context-core/__init__.py` — package init
- [x] Created `pyproject.toml` — root workspace config
- [x] Created `packages/context-core/memory/models.py` — Pydantic models (10 models)
- [x] Created `packages/context-core/memory/service.py` — MemoryService class
- [x] Created `packages/context-core/embeddings/service.py` — Pluggable embedding service
- [x] Created `packages/context-db/migrations/001_core.sql` — Users, auth, conversations
- [x] Created `packages/context-db/migrations/002_memory.sql` — Unified memories + pgvector
- [x] Created `packages/context-db/migrations/003_knowledge.sql` — KG entities + embeddings
- [x] Created `packages/context-db/migrations/004_subscriptions.sql` — Plans, usage
- [x] Created `apps/server/main.py` — FastAPI app entry point
- [x] Created `apps/server/routes/memory.py` — Memory REST API (8 endpoints)
- [x] Created `apps/server/routes/health.py` — Health check endpoint
- [x] Created `apps/server/middleware/auth.py` — Auth middleware
- [x] Created 15 passing tests (memory models + embeddings)

## Next Tasks

1. Create `packages/context-core/retrieval/vector_search.py` — pgvector search
2. Create `packages/context-core/retrieval/bm25_search.py` — PostgreSQL FTS
3. Create `packages/context-core/retrieval/fusion.py` — RRF fusion
4. Create `packages/context-core/retrieval/chunking.py` — Recursive chunker
5. Create `packages/context-core/retrieval/pipeline.py` — Full retrieval pipeline

## Blockers

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| SQLite dependency must be removed | Cannot scale memory | Week 1 migration to pgvector ✅ |
| Milvus dependency must be removed | Not self-hostable | Week 1 migration to pgvector ✅ |
| No SDK blocks adoption | Cannot measure adoption | Week 3 SDK build |

## Deferred Features

| Feature | Deferred To | Reason |
|---------|-------------|--------|
| LLM-based planner | Week 5-6 | Keyword planner works for v1 |
| Reflection loops | Week 6-7 | Get basics working first |
| Memory consolidation | Week 7-8 | Get basics working first |
| HyDE query expansion | Week 8-9 | Basic retrieval works first |
| Cross-encoder re-ranking | Week 9-10 | Basic retrieval works first |
| CrewAI integration | Week 12+ | Postpone, too coupled |
| Workflow agent | Week 12+ | Postpone, not core |
| Webhook system | Cloud launch | Cloud feature |
| Analytics dashboard | Cloud launch | Cloud feature |
| Team collaboration | Cloud launch | Cloud feature |
| HNSW index | >1M rows | IVFFlat sufficient |

---

## File System

| File | Purpose |
|------|---------|
| `PROJECT_BRAIN.md` | This file. Permanent strategic memory. |
| `ROADMAP.md` | Detailed roadmap with milestones. |
| `ARCHITECTURE.md` | Target architecture and code migration map. |
| `PRODUCT_STRATEGY.md` | Positioning, thesis, competitive analysis. |
| `OSS_STRATEGY.md` | Open source, cloud, enterprise strategy. |
| `BILLING_STRATEGY.md` | Monetization and billing design. |
| `DOCS_STRATEGY.md` | Documentation architecture. |
| `LAUNCH_CHECKLIST.md` | Launch readiness checklist. |

---

*Last updated: 2026-06-19*
*Next review: Before any architectural decision*
