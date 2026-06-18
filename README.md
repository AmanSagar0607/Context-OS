<h1 align="center">
    <a href="https://github.com/AmanSagar0607/Context-OS">
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AmanSagar0607/Context-OS/main/public/context-os-banner-dark.svg">
            <img alt="Context OS - Context Infrastructure for AI Agents" src="https://raw.githubusercontent.com/AmanSagar0607/Context-OS/main/public/context-os-banner.svg" width="100%">
        </picture>
    </a>
</h1>

<p align="center">
    <a href="https://github.com/AmanSagar0607/Context-OS/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/AmanSagar0607/Context-OS?style=social" alt="GitHub stars"></a>
    <a href="https://github.com/AmanSagar0607/Context-OS/network/members" target="_blank"><img src="https://img.shields.io/github/forks/AmanSagar0607/Context-OS?style=social" alt="GitHub forks"></a>
    <a href="https://github.com/AmanSagar0607/Context-OS/watchers" target="_blank"><img src="https://img.shields.io/github/watchers/AmanSagar0607/Context-OS?style=social" alt="GitHub watchers"></a>
    <br/>
    <a href="https://github.com/AmanSagar0607/Context-OS/blob/main/LICENSE" alt="License">
        <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
    <a href="https://python.org" alt="Python 3.11+">
        <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11+-green.svg"></a>
    <a href="https://github.com/AmanSagar0607/Context-OS/actions" alt="Tests">
        <img alt="Tests" src="https://github.com/AmanSagar0607/Context-OS/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://pypi.org/project/context-ai/" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/context-ai.svg"></a>
    <a href="https://pepy.tech/project/context-ai" alt="Downloads">
        <img alt="Downloads" src="https://img.shields.io/pypi/dm/context-ai"></a>
    <br/>
    <a href="https://discord.gg/contextos" alt="Discord" target="_blank">
        <img alt="Discord" src="https://img.shields.io/discord/YOUR_SERVER_ID?style=social&logo=discord"></a>
    <a href="https://x.com/contextos" alt="X (formerly Twitter)">
        <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/contextos?style=social&logo=x"></a>
    <a href="https://github.com/AmanSagar0607/Context-OS" alt="PRs Welcome">
        <img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg"></a>
    <br/>
    <a href="https://github.com/AmanSagar0607/Context-OS/pkgs/context-core" alt="Package">
        <img alt="Package" src="https://img.shields.io/badge/package-context--core-blue"></a>
    <a href="https://docs.contextos.dev" alt="Docs">
        <img alt="Docs" src="https://img.shields.io/badge/docs-contextos.dev-blue"></a>
</p>

<p align="center">
    <a href="https://docs.contextos.dev/quickstart"><strong>Quickstart</strong></a>
    &middot;
    <a href="https://docs.contextos.dev/api"><strong>API Reference</strong></a>
    &middot;
    <a href="https://docs.contextos.dev/sdk"><strong>SDKs</strong></a>
    &middot;
    <a href="https://docs.contextos.dev/mcp"><strong>MCP</strong></a>
    &middot;
    <a href="https://docs.contextos.dev/self-hosting"><strong>Self-Host</strong></a>
</p>

<p align="center">
    <b>AI can finally remember.</b> The open-source context infrastructure that gives AI agents memory, web intelligence, and structured knowledge — via a single API and MCP server.
</p>

---

<p align="center">
    <a href="https://github.com/sponsors/AmanSagar0607" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://img.shields.io/badge/Become_a-Sponsor-FF4500?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Become a Sponsor">
    </a>
</p>

---

## Why Context OS?

Every AI application eventually needs:

- **Memory** — So agents remember across sessions
- **Context** — So responses are relevant and grounded
- **Retrieval** — So knowledge is accessible and accurate
- **Knowledge** — So relationships are understood
- **Search** — So information is current and complete

Today these capabilities are fragmented across multiple tools. You cobble together Mem0 for memory, Firecrawl for crawling, a vector DB for search, and custom code for knowledge graphs.

**Context OS unifies them into a single developer platform.**

```python
from context_ai import ContextClient

client = ContextClient(api_key="...")

# Store a memory
await client.memory.add(
    content="User prefers dark mode and concise responses",
    tags=["preference", "ui"]
)

# Search memories
results = await client.memory.search(query="What UI preferences does the user have?")

# Get context window
context = await client.memory.context(query="What should I know about this user?")

# Crawl and extract knowledge
page = await client.crawl.scrape(url="https://example.com/article")
knowledge = await client.knowledge.extract(content=page.content)

# Web search
results = await client.search.web(query="AI startups 2026")
```

---

## Key Features

### Unified Memory System
- **Persistent agent memory** across sessions and conversations
- **Semantic search** using pgvector cosine similarity
- **Multiple memory types**: episodic, semantic, procedural
- **Importance levels** for memory consolidation
- **Context windows** assembled from relevant memories

### Hybrid Retrieval Pipeline
- **Vector search** via pgvector
- **BM25 search** via PostgreSQL FTS
- **Reciprocal Rank Fusion** for combining results
- **Query expansion** (HyDE, multi-query)
- **Re-ranking** with cross-encoders

### Web Intelligence
- **Multi-provider crawl** with fallback chain (Crawl4AI → Jina → httpx)
- **5-provider search** (Tavily → Brave → SearXNG → DuckDuckGo → Google)
- **Playwright browser automation** for JS-rendered pages
- **AI extraction** for structured data from unstructured content

### Knowledge Graph
- **Entity extraction** from crawled content
- **Relationship mapping** between entities
- **Semantic search** on knowledge graph
- **Memory-entity connections** for context

### MCP Native
- **4 tool groups**: Memory, Search, Crawl, Knowledge
- **JSON-RPC 2.0** compliant
- **HTTP/SSE transport** for remote servers
- **stdio transport** for local development
- Works with Claude, Cursor, and any MCP client

### Developer Experience
- **Python SDK** — async-first, type-safe
- **TypeScript SDK** — full type coverage
- **CLI tool** — manage everything from terminal
- **REST API** — 25+ endpoints
- **OpenAPI spec** — auto-generated

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Docker Desktop (optional)

### Installation

```bash
pip install context-ai
```

Or from source:

```bash
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS
pip install -e packages/context-core
```

### Quick Start

```python
import asyncio
from context_core.memory.service import MemoryService
from context_core.memory.models import MemoryCreate, MemorySearchRequest

async def main():
    # Initialize (requires PostgreSQL + pgvector)
    service = MemoryService(pool, embeddings)
    
    # Store a memory
    memory = await service.add("user-123", MemoryCreate(
        content="User prefers dark mode and concise responses",
        memory_type="semantic",
        importance="high",
        tags=["preference", "ui"],
    ))
    
    # Search memories
    results = await service.search(MemorySearchRequest(
        query="What UI preferences does the user have?",
        user_id="user-123",
    ))
    
    for result in results:
        print(f"{result.score:.2f} - {result.memory.content}")

asyncio.run(main())
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTS                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Python   │  │ TypeScript│  │   CLI    │  │   MCP    │   │
│  │ SDK      │  │ SDK      │  │          │  │ Clients  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API SERVER (FastAPI)                       │
│  Memory Routes │ Search Routes │ Crawl Routes │ MCP         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONTEXT CORE (Python)                       │
│  Memory │ Retrieval │ Knowledge │ Crawl │ Search │ MCP      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL + pgvector                        │
│  memories │ kg_entities │ users │ usage_records │ plans      │
└─────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Memory

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/memory` | Store a memory |
| `GET` | `/api/v1/memory/:id` | Get a memory |
| `PUT` | `/api/v1/memory/:id` | Update a memory |
| `DELETE` | `/api/v1/memory/:id` | Delete a memory |
| `POST` | `/api/v1/memory/search` | Semantic search |
| `POST` | `/api/v1/memory/context` | Get context window |
| `GET` | `/api/v1/memory` | List memories |
| `GET` | `/api/v1/memory/:id/related` | Related memories |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/search/web` | Web search |
| `POST` | `/api/v1/search/internal` | Internal hybrid search |

### Crawl

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/scrape` | Scrape URL |
| `POST` | `/api/v1/crawl/crawl` | Crawl website |
| `POST` | `/api/v1/crawl/map` | Map website |
| `POST` | `/api/v1/crawl/extract` | AI extraction |

### Knowledge

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/knowledge/entities` | Create entity |
| `GET` | `/api/v1/knowledge/entities/:id` | Get entity |
| `DELETE` | `/api/v1/knowledge/entities/:id` | Delete entity |
| `POST` | `/api/v1/knowledge/relationships` | Create relationship |

---

## Project Structure

```
Context-OS/
├── apps/
│   ├── server/                    # FastAPI API server
│   │   ├── main.py               # App entry point
│   │   ├── routes/               # API endpoints
│   │   └── middleware/           # Auth, rate limiting
│   └── web/                      # Next.js dashboard
├── packages/
│   ├── context-core/             # Core business logic
│   │   ├── memory/               # Memory service
│   │   ├── retrieval/            # Hybrid retrieval
│   │   ├── knowledge/            # Knowledge graph
│   │   ├── crawl/                # Web intelligence
│   │   ├── search/               # Search router
│   │   ├── embeddings/           # Embedding service
│   │   └── mcp/                  # MCP server
│   ├── context-db/               # Database migrations
│   └── context-types/            # Shared TypeScript types
├── sdk/
│   ├── python/                   # Python SDK
│   └── typescript/               # TypeScript SDK
├── cli/                          # CLI tool
├── docs/                         # Documentation
└── examples/                     # Starter templates
```

---

## Competitive Analysis

| Capability | Mem0 | Firecrawl | Zep | Letta | LangGraph | CrewAI | **Context OS** |
|------------|------|-----------|-----|-------|-----------|--------|----------------|
| Memory | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Web Search | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Web Crawl | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Knowledge Graph | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| MCP | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Self-hostable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Open Source | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**No one else has all five capabilities in one platform.**

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Server | FastAPI (Python 3.11+) |
| Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (default), OpenAI, Cohere |
| LLM | OpenRouter (GPT-4o-mini default) |
| Payments | BaseUPI (zero-commission UPI) |
| Frontend | Next.js 15, Tailwind CSS |
| Auth | JWT + OAuth (Google, GitHub) |
| MCP | JSON-RPC 2.0, HTTP/SSE |

---

## Deployment

### Docker

```bash
docker compose up -d
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/app-agent

# LLM
OPENROUTER_API_KEY=your-key

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Auth
AMAN_JWT_SECRET=your-secret

# Payments
BASEUPI_SECRET_KEY=your-key
```

---

## Testing

```bash
# Run all tests
cd packages/context-core
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=context_core
```

---

## Roadmap

### 30 Days — Launch Readiness
- [x] Monorepo structure
- [x] Unified memory system
- [x] Database migrations
- [ ] Hybrid retrieval pipeline
- [ ] Python + TypeScript SDK
- [ ] CLI tool
- [ ] MCP server refactor
- [ ] Documentation
- [ ] Docker deployment

### 60 Days — Developer Adoption
- LLM-based planner
- Memory consolidation
- HyDE query expansion
- 100 GitHub stars
- 10 external users

### 90 Days — Revenue
- Cloud deployment
- Usage-based billing (Polar)
- 500 GitHub stars
- 50 external users
- 10 paying customers

See [ROADMAP.md](ROADMAP.md) for detailed plans.

---

# Sponsors

Support Context OS development! Sponsors get visibility in this README and the project documentation.

<table>
  <tr>
    <td width="200">
      <a href="https://github.com/sponsors/AmanSagar0607" target="_blank" title="Become a Platinum Sponsor">
        <img src="https://img.shields.io/badge/Your_Logo_here-grey?style=for-the-badge&logo=github" alt="Sponsor">
      </a>
    </td>
    <td>
      <a href="https://github.com/sponsors/AmanSagar0607" target="_blank"><b>Your Company Here</b></a><br/>
      <i>Platinum sponsors get premium placement in this README and documentation.</i>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://github.com/sponsors/AmanSagar0607" target="_blank" title="Become a Platinum Sponsor">
        <img src="https://img.shields.io/badge/Your_Logo_here-grey?style=for-the-badge&logo=github" alt="Sponsor">
      </a>
    </td>
    <td>
      <a href="https://github.com/sponsors/AmanSagar0607" target="_blank"><b>Your Company Here</b></a><br/>
      <i>Platinum sponsors get premium placement in this README and documentation.</i>
    </td>
  </tr>
</table>

<!-- sponsors -->
<!-- /sponsors -->

<i><sub>Want to show your ad here? <a href="https://github.com/sponsors/AmanSagar0607">Become a sponsor</a> and choose the tier that suits you!</sub></i>

---

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) before getting started.

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## Citation

If you have used Context OS for research purposes please quote us with the following reference:

```text
  @misc{contextos,
    author = {Aman Sagar},
    title = {Context OS},
    year = {2026},
    url = {https://github.com/AmanSagar0607/Context-OS},
    note = {Context Infrastructure for AI Agents - Memory, Search, Crawl, Knowledge, MCP}
  }
```

---

## License

This work is licensed under the MIT License.

---

## Acknowledgments

Built with care for the AI agent community.

---

<div align="center">
    <small>Designed & crafted with care by Aman Sagar.</small><br/><br/>
    <a href="https://github.com/sponsors/AmanSagar0607" target="_blank">
        <img src="https://img.shields.io/badge/⭐_Star_this_repo-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Star this repo">
    </a>
</div>