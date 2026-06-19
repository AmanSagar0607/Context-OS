---
sidebar_position: 13
title: Docker Deployment
---

# Docker Deployment

Deploy Context OS with Docker and Docker Compose.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS

# Start services
docker compose up -d

# Check status
docker compose ps
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL + pgvector |
| redis | 6379 | Redis cache |
| server | 8000 | FastAPI API server |

## Docker Compose

```yaml
version: "3.8"

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: app-agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./packages/context-db/migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/app-agent
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  pgdata:
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres:postgres@localhost:5432/app-agent` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `CONTEXT_API_KEY` | API key | — |

## Production Deployment

### 1. Build Image

```bash
docker build -t context-os:latest .
```

### 2. Configure Environment

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
export REDIS_URL="redis://host:6379"
```

### 3. Run

```bash
docker run -d \
  --name context-os \
  -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e REDIS_URL="$REDIS_URL" \
  context-os:latest
```

## Self-Hosted

See [Self-Hosted](/docs/deployment/self-hosted) for manual installation.