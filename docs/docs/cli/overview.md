# CLI Overview

> Command-line interface for ContextOS.

## Installation

```bash
pip install contextos-cli
```

## Authentication

```bash
contextos login
# Opens browser for API key setup

# Or set directly
contextos config set api_key YOUR_API_KEY
```

## Commands

### Memory

```bash
# Add memory
contextos memory add "User prefers dark mode" --type fact

# Search memories
contextos memory search "user preferences" --top-k 5

# List memories
contextos memory list --limit 10

# Delete memory
contextos memory delete mem_abc123
```

### Search

```bash
# Web search
contextos search web "latest AI news" --max-results 5

# Internal search
contextos search internal "user preferences"
```

### Crawl

```bash
# Scrape URL
contextos crawl scrape https://example.com

# Crawl site
contextos crawl crawl https://example.com --max-pages 10

# Map site
contextos crawl map https://example.com
```

### Knowledge

```bash
# Add entity
contextos knowledge add-entity --name "ContextOS" --type software

# Query graph
contextos knowledge query --entity "ContextOS"
```

### MCP

```bash
# List MCP tools
contextos mcp list-tools

# Test MCP connection
contextos mcp test
```

### Config

```bash
# Show config
contextos config show

# Set value
contextos config set api_key YOUR_API_KEY

# Get value
contextos config get api_key
```

## Options

| Option | Description |
|--------|-------------|
| `--api-key` | API key |
| `--output` | Output format: json, table, text |
| `--verbose` | Verbose output |
| `--help` | Show help |
