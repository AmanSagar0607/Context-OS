# Context OS — CLI

Command-line interface for Context OS operations.

## Installation

```bash
pip install context-cli
```

Or install from source:

```bash
git clone https://github.com/AmanSagar0607/Context-OS.git
cd Context-OS/cli
pip install -e .
```

## Configuration

Set environment variables:

```bash
export CONTEXT_API_URL="http://localhost:8000"  # API server
export CONTEXT_API_KEY="your-api-key"           # API key (optional)
```

## Commands

### Memory

```bash
# Add a memory
context memory add -c "User prefers dark mode" --type semantic --importance high --tags "ui,preferences"

# Get a memory
context memory get <memory-id>

# Search memories
context memory search "dark mode" --limit 10

# List memories
context memory list --type semantic --limit 20

# Delete a memory
context memory delete <memory-id>
```

### Search

```bash
# Web search
context search web "AI news 2025" --limit 5

# Internal hybrid search
context search internal "user preferences" --limit 10
```

### Crawl

```bash
# Scrape a URL
context crawl scrape https://example.com

# Map a website
context crawl map https://example.com --limit 50
```

### Knowledge

```bash
# Create an entity
context knowledge create-entity --name "GPT-4" --type model --description "Large language model"

# Search entities
context knowledge search "language models" --limit 10
```

### Health

```bash
# Check API health
context health
```

## License

MIT License