---
sidebar_position: 14
title: Self-Hosted
---

# Self-Hosted

Install and run Context OS on your own infrastructure.

## Prerequisites

- Python 3.10+
- PostgreSQL 16+ with pgvector
- Redis (optional, for caching)

## Installation

```bash
# Clone repository
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS

# Install dependencies
pip install -e "packages/context-core[dev]"
pip install -e "apps/server[dev]"
```

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE app-agent;
```

### 2. Enable pgvector

```sql
CREATE EXTENSION vector;
```

### 3. Run Migrations

```bash
psql -d app-agent -f packages/context-db/migrations/001_core.sql
psql -d app-agent -f packages/context-db/migrations/002_memory.sql
psql -d app-agent -f packages/context-db/migrations/003_knowledge.sql
psql -d app-agent -f packages/context-db/migrations/004_subscriptions.sql
```

## Start Server

```bash
cd apps/server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Verify

```bash
curl http://localhost:8000/api/v1/health
```

## Next Steps

- [API Reference](/docs/api-reference)
- [MCP Server](/docs/mcp)
- [Python SDK](/docs/sdk/python)