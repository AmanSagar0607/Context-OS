# Context OS

**AI can finally remember.**

The open-source context infrastructure that gives AI agents memory, web intelligence, and structured knowledge — via a single API and MCP server.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What is Context OS?

Context OS is a unified developer platform that provides:

| Module | Purpose | Competitor |
|--------|---------|------------|
| **Memory** | Persistent agent memory with semantic search | Mem0, Zep |
| **Search** | Hybrid web + internal search | Firecrawl (partial) |
| **Crawl** | Web intelligence with fallback chain | Firecrawl, Crawl4AI |
| **Knowledge** | Entity/relationship extraction and graph | Custom |
| **MCP** | MCP servers for all of the above | Custom |

**No one else has all five capabilities in one platform.**

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS
pip install -e packages/context-core
```

### 2. Start Database

```bash
docker compose up -d postgres
```

### 3. Run Migrations

```bash
psql -U postgres -d app-agent -f packages/context-db/migrations/001_core.sql
psql -U postgres -d app-agent -f packages/context-db/migrations/002_memory.sql
psql -U postgres -d app-agent -f packages/context-db/migrations/003_knowledge.sql
psql -U postgres -d app-agent -f packages/context-db/migrations/004_subscriptions.sql
```

### 4. Store Your First Memory

```python
from context_core.memory.service import MemoryService
from context_core.memory.models import MemoryCreate

# Initialize service (requires PostgreSQL + pgvector)
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

## Project Structure

```
Context-OS/
├── apps/
│   ├── server/                    # FastAPI API server
│   │   ├── main.py               # App entry point
│   │   ├── routes/               # API endpoints
│   │   └── middleware/           # Auth, rate limiting
│   └── web/                      # Next.js dashboard (minimal)
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
│   │   └── migrations/           # SQL migrations
│   └── context-types/            # Shared TypeScript types
├── sdk/
│   ├── python/                   # Python SDK
│   └── typescript/               # TypeScript SDK
├── cli/                          # CLI tool
├── docs/                         # Documentation
└── examples/                     # Starter templates
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
| `GET` | `/api/v1/knowledge/graph/:id` | Get entity graph |

### MCP

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/mcp` | MCP JSON-RPC |
| `GET` | `/api/v1/mcp/tools` | List MCP tools |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Server | FastAPI (Python 3.11+) |
| Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (default) |
| LLM | OpenRouter (GPT-4o-mini default) |
| Payments | BaseUPI (zero-commission UPI) |
| Frontend | Next.js 15, Tailwind CSS |
| Auth | JWT + OAuth (Google, GitHub) |

---

## Database Schema

### Core Tables

- `users` — User accounts
- `auth_identities` — Auth providers (password, Google, GitHub)
- `user_sessions` — Sessions
- `api_tokens` — API tokens
- `conversations` — Chat threads
- `messages` — Chat messages

### Memory Tables

- `memories` — Unified memory store with pgvector
- `memory_links` — Graph relationships between memories
- `conversation_messages` — Conversation history

### Knowledge Tables

- `kg_entities` — Knowledge graph entities with embeddings
- `kg_relationships` — Entity relationships
- `entity_memory_links` — Entity-to-memory connections

### Subscription Tables

- `plans` — Plan definitions (free, pro, team, enterprise)
- `plan_limits` — Per-plan rate limits
- `subscriptions` — User subscriptions
- `usage_records` — Usage events

---

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- PostgreSQL 15+ (or via Docker)

### Setup

```bash
# Clone
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS

# Install Python dependencies
pip install -e packages/context-core

# Install frontend dependencies
npm install

# Start database
docker compose up -d postgres

# Run tests
cd packages/context-core
pytest tests/ -v
```

### Running

```bash
# Start API server
cd apps/server
uvicorn main:app --reload --port 8000

# Start frontend
npm run dev
```

---

## Testing

```bash
# Run all context-core tests
cd packages/context-core
pytest tests/ -v

# Run specific test file
pytest tests/test_memory_models.py -v

# Run with coverage
pytest tests/ --cov=context_core
```

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
USE_DOCKER_POSTGRES=false

# LLM
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openai/gpt-4o-mini

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Auth
AMAN_JWT_SECRET=your-secret

# Payments
BASEUPI_SECRET_KEY=your-key
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

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Links

- [GitHub](https://github.com/AmanSagar0607/Context-OS)
- [Documentation](https://contextos.dev) (coming soon)
- [API Reference](https://contextos.dev/api) (coming soon)

---

**Built with care for the AI agent community.**