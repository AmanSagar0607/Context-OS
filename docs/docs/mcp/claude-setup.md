# Claude Desktop Setup
> Connect ContextOS MCP to Claude Desktop for AI-powered context.

## Overview

This guide walks you through connecting ContextOS MCP tools to Claude Desktop. Once configured, Claude can access your memory, search, and crawl tools during conversations.

## Prerequisites

- Claude Desktop installed
- ContextOS running at `http://localhost:8000/api/v1/mcp`

## Quick Start

### 1. Locate your config file

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Add the MCP server

**macOS:**
```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp",
      "transport": "streamable-http"
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### 3. Restart Claude Desktop

Quit and reopen Claude Desktop to load the new configuration.

### 4. Verify the connection

Start a new conversation and ask Claude to list available tools. You should see `memory_add`, `search_web`, `crawl_scrape`, and others.

## Configuration Options

| Field | Description |
|-------|-------------|
| `url` | ContextOS MCP endpoint |
| `transport` | Must be `streamable-http` |
| `headers` | Optional auth headers if required |

### With auth headers

```json
{
  "mcpServers": {
    "contextos": {
      "url": "http://localhost:8000/api/v1/mcp",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tools not showing | Restart Claude Desktop after config changes |
| Connection refused | Confirm ContextOS is running on port 8000 |
| Config file missing | Create the file manually if it doesn't exist |
| Multiple servers | Each server needs its own key in `mcpServers` |
| JSON parse error | Validate your JSON syntax |

## Tips

- Check the Claude Desktop logs at `~/Library/Logs/Claude/` (macOS) for MCP errors.
- Claude will automatically discover available tools on connection.
- You can run multiple MCP servers simultaneously by adding more entries.
