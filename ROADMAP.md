# ROADMAP

> Strategic roadmap for Context Infrastructure Platform.

---

## 7 Days — Launch Readiness

**Goal:** Platform foundations complete. Ready for developer adoption.

### day 1: Architecture Extraction + Memory Foundation

| Day | Task | Deliverable | Tests |
|-----|------|-------------|-------|
| 1 | Create monorepo structure | `apps/`, `packages/`, `sdk/`, `cli/`, `docs/` | — |
| 1 | Create `packages/context-core/config.py` | Shared configuration | — |
| 2 | Create `packages/context-db/migrations/001_core.sql` | Copy existing schema + pgvector | — |
| 2 | Create `packages/context-db/migrations/002_memory.sql` | Unified memories table | — |
| 3 | Create `packages/context-core/memory/service.py` | MemoryService: add, search, delete | — |
| 3 | Create `packages/context-core/memory/models.py` | Pydantic models | — |
| 4 | Create `packages/context-core/embeddings/service.py` | Pluggable embedding service | — |
| 4 | Create `packages/context-core/retrieval/vector_search.py` | pgvector search | — |
| 5 | Create `packages/context-core/retrieval/bm25_search.py` | PostgreSQL FTS | — |
| 5 | Create `packages/context-core/retrieval/fusion.py` | RRF fusion | — |
| 6 | Create `apps/server/routes/memory.py` | Memory REST API | — |
| 6 | Create `apps/server/main.py` | FastAPI app | — |
| 7 | Write memory tests | `tests/test_memory.py` | 10 tests |

**Milestone:** Unified memory on PostgreSQL + pgvector with hybrid search.

### day 2: Retrieval + Knowledge + Crawl Integration

| Day | Task | Deliverable | Tests |
|-----|------|-------------|-------|
| 8 | Create `packages/context-core/retrieval/reranker.py` | Cross-encoder re-ranking | — |
| 8 | Create `packages/context-core/retrieval/chunking.py` | Recursive chunker | — |
| 9 | Create `packages/context-core/retrieval/pipeline.py` | Full retrieval pipeline | — |
| 9 | Create `packages/context-core/retrieval/expansion.py` | HyDE + multi-query | — |
| 10 | Move `knowledge_graph.py` → `packages/context-core/knowledge/` | Knowledge service | — |
| 10 | Create `packages/context-db/migrations/003_knowledge.sql` | Entity embeddings | — |
| 11 | Create `apps/server/routes/knowledge.py` | Knowledge REST API | — |
| 11 | Create `apps/server/routes/search.py` | Search REST API | — |
| 12 | Move `crawl_service.py` → `packages/context-core/crawl/` | Crawl service | — |
| 12 | Move `search_router.py` → `packages/context-core/search/` | Search service | — |
| 13 | Create `apps/server/routes/crawl.py` | Crawl REST API | — |
| 14 | Write retrieval + knowledge tests | `tests/test_retrieval.py`, `tests/test_knowledge.py` | 20 tests |

**Milestone:** Hybrid retrieval pipeline, knowledge graph integration, all core APIs.

### day 3: SDK + CLI + MCP

| Day | Task | Deliverable | Tests |
|-----|------|-------------|-------|
| 15 | Create Python SDK package | `sdk/python/context_ai/` | — |
| 15 | Implement `context_ai/client.py` | ContextClient | — |
| 16 | Implement `context_ai/memory.py` | Memory client | — |
| 16 | Implement `context_ai/search.py`, `crawl.py`, `knowledge.py` | All clients | — |
| 17 | Create TypeScript SDK package | `sdk/typescript/src/` | — |
| 17 | Implement TypeScript clients | All clients | — |
| 18 | Create CLI package | `cli/context_cli/` | — |
| 18 | Implement CLI commands | All commands | — |
| 19 | Create `packages/context-core/mcp/server.py` | MCP server (4 tool groups) | — |
| 19 | Create `apps/server/routes/mcp.py` | MCP HTTP/SSE transport | — |
| 20 | Write SDK tests | `sdk/python/tests/`, `sdk/typescript/tests/` | 30 tests |
| 21 | Write CLI tests | `cli/tests/` | 10 tests |

**Milestone:** Python SDK, TypeScript SDK, CLI, MCP server.

### day 4: Docs + Docker + Polish

| Day | Task | Deliverable | Tests |
|-----|------|-------------|-------|
| 22 | Create Docusaurus docs site | `docs/` structure | — |
| 22 | Write Getting Started guide | Quickstart, installation | — |
| 23 | Write Memory docs | Store, search, context, types | — |
| 23 | Write Crawl docs | Scrape, crawl, map, extract | — |
| 24 | Write Knowledge docs | Entities, relationships, graph | — |
| 24 | Write MCP docs | Setup, Cursor/Claude integration | — |
| 25 | Write SDK docs | Python + TypeScript quickstart | — |
| 25 | Write CLI docs | Command reference | — |
| 26 | Write API reference | All endpoints | — |
| 26 | Write Self-hosting guide | Docker, environment | — |
| 27 | Create `docker-compose.yml` | PostgreSQL + pgvector + server | — |
| 27 | Create `docker-compose.dev.yml` | Dev with hot reload | — |
| 28 | Create root `README.md` | Product overview | — |
| 28 | Create `apps/server/Dockerfile` | Production container | — |
| 29 | Final test suite | All tests | 60+ tests |
| 29 | Final build verification | Clean builds | — |
| 30 | Package publishing prep | Ready to publish | — |
| 30 | Create examples | Python + TypeScript + MCP | — |

**Milestone:** Documentation, Docker, examples, launch-ready.

---

## 60 Days — Developer Adoption

**Goal:** 100 GitHub stars, 10 external users, 5 contributors.

| Week | Focus | Tasks |
|------|-------|-------|
| 5-6 | LLM-based planner | Replace keyword classifier with LLM reasoning |
| 6-7 | Reflection loops | Self-correction in retrieval pipeline |
| 7-8 | Memory consolidation | Merge old, low-importance memories |
| 8-9 | HyDE query expansion | Hypothetical document embedding |
| 9-10 | Cross-encoder re-ranking | bge-reranker-v2-m3 integration |

### Adoption Milestones

| Milestone | Target | Metric |
|-----------|--------|--------|
| GitHub stars | 100 | `gh api /repos/:owner/:repo` |
| External users | 10 | API key registrations |
| Contributors | 5 | Pull requests merged |
| Issues opened | 20 | GitHub issues |
| Documentation visits | 1,000 | Analytics |

---

## 90 Days — Revenue

**Goal:** Cloud deployment, 500 stars, 50 users, 10 paying customers.

| Week | Focus | Tasks |
|------|-------|-------|
| 10-11 | Knowledge auto-extraction | Extract entities from crawl results |
| 11-12 | HNSW index | Upgrade pgvector index for >1M rows |
| 12-13 | Cloud deployment | Managed hosting on Railway/Fly.io |
| 13-14 | Usage-based billing | Polar integration |
| 14-15 | Analytics dashboard | Usage visualization |
| 15-16 | Webhook system | Async notifications |

### Revenue Milestones

| Milestone | Target | Metric |
|-----------|--------|--------|
| GitHub stars | 500 | `gh api /repos/:owner/:repo` |
| External users | 50 | API key registrations |
| Paying customers | 10 | Polar subscriptions |
| MRR | $500 | Polar dashboard |
| Self-hosted deploys | 20 | Docker pulls |

---

## 180 Days — Category Leadership

**Goal:** Recognized as the leading open-source context infrastructure.

| Quarter | Focus | Tasks |
|---------|-------|-------|
| Q3 | Agent memory | Long-term agent memory across sessions |
| Q3 | Multi-user memory | Shared KG entities across users |
| Q4 | Advanced retrieval | Step-back prompting, self-ask |
| Q4 | Enterprise features | SSO, audit logs, custom providers |

### Leadership Milestones

| Milestone | Target | Metric |
|-----------|--------|--------|
| GitHub stars | 2,000 | `gh api /repos/:owner/:repo` |
| External users | 500 | API key registrations |
| Paying customers | 100 | Polar subscriptions |
| MRR | $5,000 | Polar dashboard |
| Contributors | 20 | Pull requests merged |
| Blog posts | 10 | Community content |

---

## 365 Days — Ecosystem

**Goal:** Context is the default infrastructure for AI agent memory.

| Quarter | Focus | Tasks |
|---------|-------|-------|
| Q1 | Plugin system | Community plugins for custom providers |
| Q1 | Multi-language SDKs | Go, Rust, Java SDKs |
| Q2 | Context marketplace | Shared knowledge graphs |
| Q2 | Context cloud | Multi-tenant managed service |

### Ecosystem Milestones

| Milestone | Target | Metric |
|-----------|--------|--------|
| GitHub stars | 5,000 | `gh api /repos/:owner/:repo` |
| External users | 2,000 | API key registrations |
| Paying customers | 500 | Polar subscriptions |
| MRR | $25,000 | Polar dashboard |
| Contributors | 50 | Pull requests merged |
| Plugins | 20 | Community plugins |
| Blog posts | 50 | Community content |

---

*Last updated: 2026-06-19*
