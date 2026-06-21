# Self-Hosting Guide

> Deploy ContextOS on your own infrastructure.

## Prerequisites

- Docker and Docker Compose
- 4GB RAM minimum
- Port 5432 (PostgreSQL) and 8000 (API) available

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS

# Start with Docker Compose
docker-compose up -d

# Verify
curl http://localhost:8000/api/v1/health
```

## Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL + pgvector |
| server | 8000 | ContextOS API |

## Environment Variables

Create a `.env` file:

```bash
# Database
POSTGRES_DB=app-agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# LLM
OPENROUTER_API_KEY=your_key

# Auth
AMAN_JWT_SECRET=your_secret

# Frontend
FRONTEND_URL=http://localhost:3000
```

## Configuration

### Database

ContextOS uses PostgreSQL with pgvector extension. The Docker Compose file includes this automatically.

### LLM

ContextOS uses OpenRouter for LLM calls. Get an API key at [openrouter.ai](https://openrouter.ai).

### Authentication

Set `AMAN_JWT_SECRET` to a random string for JWT signing.

## Production Deployment

### Railway

1. Connect your GitHub repo
2. Add PostgreSQL service
3. Set environment variables
4. Deploy

### Fly.io

1. Install flyctl
2. `fly launch`
3. `fly deploy`

### Docker

```bash
docker build -t contextos .
docker run -p 8000:8000 contextos
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Logs

```bash
docker-compose logs -f server
```

## Backup

```bash
docker-compose exec postgres pg_dump -U postgres app-agent > backup.sql
```

## Restore

```bash
cat backup.sql | docker-compose exec -T postgres psql -U postgres app-agent
```
