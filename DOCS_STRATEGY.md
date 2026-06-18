# DOCS STRATEGY

> Documentation architecture and developer experience.

---

## Inspiration

| Source | What to Steal |
|--------|---------------|
| Mem0 | Clean API reference, quickstart-first |
| Firecrawl | Good examples, developer-focused |
| Stripe | Best-in-class API reference |
| Supabase | Good self-hosting docs |
| Resend | Clean, minimal docs |

## Tool

**Docusaurus** — static site generation, versioning, i18n.

---

## Goal

A developer should get value within 5 minutes.

### Metrics

| Metric | Target |
|--------|--------|
| Time to first API call | < 5 minutes |
| Time to first memory | < 2 minutes |
| Time to first crawl | < 2 minutes |
| Time to first MCP connection | < 5 minutes |
| Docs pages | 50+ |
| Code examples | 30+ |

---

## Navigation Tree

```
Getting Started
├── Quickstart                    # 5 minutes to first API call
├── Installation                  # Docker, pip, npm
├── Authentication                # API keys
├── First Memory                  # Store + search a memory
├── First Crawl                   # Scrape a URL
└── First MCP Connection          # Connect to Cursor/Claude

Core Concepts
├── Architecture Overview         # System design
├── Memory Model                  # Episodic, semantic, procedural
├── Retrieval Pipeline            # Hybrid search, fusion, re-ranking
├── Knowledge Graph               # Entities, relationships, graph queries
├── Context Assembly              # How context windows are built
└── Agent Integration             # How agents use context

Memory
├── Overview                      # What memory is, when to use it
├── Store Memories                # Add memories via API/SDK
├── Search Memories               # Semantic + BM25 hybrid search
├── Context Windows               # Assemble context for LLMs
├── Memory Types                  # Episodic, semantic, procedural, profile
├── Memory Consolidation          # Merge old memories
├── Memory Links                  # Graph relationships between memories
└── Memory Best Practices         # Patterns and anti-patterns

Search
├── Overview                      # Search capabilities
├── Web Search                    # Multi-provider web search
├── Internal Search               # Memory + knowledge search
├── Hybrid Search                 # Combining web + internal
└── Search Providers              # Tavily, Brave, SearXNG, DDG, Google

Crawl
├── Overview                      # Web intelligence capabilities
├── Scrape                        # Single URL scraping
├── Crawl                         # Multi-page crawling
├── Map                           # Site structure discovery
├── Extract                       # AI-powered data extraction
├── Browser Automation            # Playwright rendering
├── Fallback Chain                # Provider fallback strategy
└── Anti-Bot Bypass               # Crawl4AI, Jina, Playwright

Knowledge
├── Overview                      # Knowledge graph capabilities
├── Entities                      # Create, update, search entities
├── Relationships                 # Entity relationships
├── Graph Queries                 # Neighbor traversal, path finding
├── Auto-Extraction               # LLM-based entity extraction
└── Knowledge + Memory            # Linking entities to memories

MCP
├── Overview                      # MCP protocol support
├── Memory MCP                    # Memory tools for agents
├── Search MCP                    # Search tools for agents
├── Crawl MCP                     # Crawl tools for agents
├── Research MCP                  # Full research pipeline
├── Setup with Cursor             # IDE integration
├── Setup with Claude             # Desktop integration
└── Custom MCP Servers            # Building your own

SDKs
├── Python SDK
│   ├── Installation
│   ├── Quickstart
│   ├── Memory Operations
│   ├── Search Operations
│   ├── Crawl Operations
│   ├── Knowledge Operations
│   └── API Reference
└── TypeScript SDK
    ├── Installation
    ├── Quickstart
    ├── Memory Operations
    ├── Search Operations
    ├── Crawl Operations
    ├── Knowledge Operations
    └── API Reference

CLI
├── Installation
├── Authentication
├── Memory Commands
├── Search Commands
├── Crawl Commands
├── Knowledge Commands
├── MCP Commands
└── Configuration

API Reference
├── Authentication
├── Memory API
├── Search API
├── Crawl API
├── Knowledge API
├── MCP API
├── Errors
└── Rate Limits

Examples
├── AI Chat with Memory
├── Research Agent
├── Customer Support Agent
├── Coding Agent
├── Knowledge Builder
└── Web Monitor

Self Hosting
├── Docker
├── Docker Compose
├── Environment Variables
├── Database Setup
├── Provider Configuration
└── Production Deployment

Guides
├── Migration from Mem0
├── Migration from Firecrawl
├── Building Agent Memory
├── Hybrid Search Tuning
└── Knowledge Graph Patterns

Changelog
```

---

## Page Templates

### Quickstart Page

```markdown
# Quickstart

## Prerequisites
- Python 3.11+ or Node.js 18+
- Docker (for self-hosting) or API key (for cloud)

## Option A: Self-Host

\`\`\`bash
docker-compose up -d
\`\`\`

## Option B: Cloud

\`\`\`bash
pip install context-ai
\`\`\`

## Store Your First Memory

\`\`\`python
from context_ai import ContextClient

client = ContextClient(api_key="...")
client.memory.add(content="User prefers dark mode")
\`\`\`

## Search Your Memory

\`\`\`python
results = client.memory.search(query="user preferences")
\`\`\`

## Next Steps
- [First Memory →](/docs/memory/first)
- [First Crawl →](/docs/crawl/first)
- [First MCP →](/docs/mcp/first)
```

### API Reference Page

```markdown
# Memory API

## Store Memory

\`\`\`
POST /api/v1/memory
\`\`\`

### Request

\`\`\`json
{
  "content": "User prefers dark mode",
  "memory_type": "semantic",
  "importance": 0.5,
  "metadata": {"source": "chat"}
}
\`\`\`

### Response

\`\`\`json
{
  "id": "mem_abc123",
  "content": "User prefers dark mode",
  "memory_type": "semantic",
  "importance": 0.5,
  "created_at": "2026-06-19T12:00:00Z"
}
\`\`\`

### Errors

| Status | Code | Description |
|--------|------|-------------|
| 400 | invalid_request | Missing required fields |
| 401 | unauthorized | Invalid API key |
| 429 | rate_limit_exceeded | Quota exceeded |
```

---

## Code Examples

| Example | Language | Description |
|---------|----------|-------------|
| AI Chat with Memory | Python | Chat bot that remembers user preferences |
| Research Agent | Python | Agent that searches + crawls + synthesizes |
| Customer Support | Python | Support agent with conversation memory |
| Coding Agent | TypeScript | IDE agent with project knowledge |
| Knowledge Builder | Python | Auto-extract entities from web content |
| Web Monitor | Python | Monitor websites for changes |

---

## Documentation Standards

1. **Every page has a quickstart.** Code first, explanation second.
2. **Every API endpoint has an example.** Request + response + error.
3. **Every SDK method has an example.** Working code, not pseudocode.
4. **Every concept has a diagram.** Visual explanation.
5. **Every guide has a "Next Steps" link.** Keep developers moving.

---

*Last updated: 2026-06-19*
