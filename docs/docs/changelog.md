---
sidebar_position: 16
title: Changelog
---

# Changelog

## 0.1.0 (2025-06-19)

### Features

- Initial release
- Memory system (add, get, update, delete, search, context)
- Retrieval pipeline (vector search, BM25, RRF fusion)
- Knowledge graph (entities, relationships, traversal)
- Web intelligence (search, crawl, scrape, extract)
- MCP server (20 tools)
- Python SDK (`context-ai`)
- TypeScript SDK (`context-ai`)
- CLI tool (`context-cli`)
- REST API (8 memory endpoints)
- Docker deployment
- Documentation site

### Architecture

- PostgreSQL + pgvector for storage
- FastAPI for API server
- MCP protocol (JSON-RPC 2.0)
- Monorepo structure (apps, packages, sdk, cli, docs)