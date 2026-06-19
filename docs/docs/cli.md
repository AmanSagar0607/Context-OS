---
sidebar_position: 10
title: CLI
---

# CLI

Command-line interface for Context OS operations.

## Installation

```bash
pip install context-cli
```

## Configuration

```bash
export CONTEXT_API_URL="http://localhost:8000"
export CONTEXT_API_KEY="your-api-key"
```

## Commands

### Memory

```bash
# Add memory
context memory add -c "User prefers dark mode" --type semantic --importance high

# Get memory
context memory get <memory-id>

# Search memories
context memory search "dark mode" --limit 10

# List memories
context memory list --type semantic --limit 20

# Delete memory
context memory delete <memory-id>
```

### Search

```bash
# Web search
context search web "AI news" --limit 5

# Internal search
context search internal "user preferences" --limit 10
```

### Crawl

```bash
# Scrape URL
context crawl scrape https://example.com

# Map website
context crawl map https://example.com --limit 50
```

### Knowledge

```bash
# Create entity
context knowledge create-entity --name "GPT-4" --type model

# Search entities
context knowledge search "language models" --limit 10
```

### Health

```bash
# Check API health
context health
```

## Help

```bash
context --help
context memory --help
context search --help
```