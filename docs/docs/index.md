---
slug: /
sidebar_position: 1
title: Introduction
---

# Context OS

**The open-source context infrastructure for AI agents.**

AI can finally remember.

## What is Context OS?

Context OS is a unified developer platform that gives AI agents:

- **Memory** — Persistent, searchable memory across sessions
- **Search** — Hybrid web + internal search with RRF fusion
- **Crawl** — Web intelligence with multi-provider fallback
- **Knowledge** — Entity/relationship extraction and knowledge graphs
- **MCP** — Model Context Protocol servers for all of the above

## Why Context OS?

Every AI application eventually needs memory, context, retrieval, knowledge, and search. Today these capabilities are fragmented across multiple tools.

Context OS unifies them into a single developer platform.

```
Memory Layer + Retrieval Layer + Knowledge Layer + Web Intelligence Layer + MCP Layer
```

## Quick Start

```bash
# Install the Python SDK
pip install context-ai

# Or the CLI
pip install context-cli
```

```python
from context_ai import ContextAI

client = ContextAI(api_key="your-api-key")

# Add a memory
memory = client.memory.add(content="User prefers dark mode")

# Search memories
results = client.memory.search(query="dark mode")

# Web search
web_results = client.search.web(query="AI news")
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MCP Protocol                       │
├─────────────┬─────────────┬─────────────┬───────────┤
│   Memory    │   Search    │   Crawl     │ Knowledge │
│   Tools     │   Tools     │   Tools     │   Tools   │
├─────────────┴─────────────┴─────────────┴───────────┤
│              Context OS Core Engine                  │
├─────────────────────────────────────────────────────┤
│         PostgreSQL + pgvector + Redis                │
└─────────────────────────────────────────────────────┘
```

## Modules

| Module | Purpose | Competitor |
|--------|---------|------------|
| Memory | Persistent agent memory with semantic search | Mem0, Zep |
| Search | Hybrid web + internal search | Firecrawl (partial) |
| Crawl | Web intelligence with fallback chain | Firecrawl, Crawl4AI |
| Knowledge | Entity/relationship extraction and graph | Custom |
| MCP | MCP servers for all of the above | Custom |

## Links

- [GitHub](https://github.com/AmanSagar0607/Context-OS)
- [Discord](https://discord.gg/YrSpR43UB)
- [Twitter](https://x.com/AmanSagar0607a)