# Cursor Setup
> Connect ContextOS MCP to Cursor IDE for AI-powered context.

## Overview

This guide walks you through connecting ContextOS MCP tools to Cursor IDE. Once configured, you can use memory, search, and crawl tools directly in Cursor's AI chat.

## Prerequisites

- Cursor IDE installed
- ContextOS running at `http://localhost:8000/api/v1/mcp`

## Quick Start

### 1. Create the MCP config

Create `.cursor/mcp.json` in your project root:

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

### 2. Restart Cursor

Close and reopen Cursor to load the new MCP configuration.

### 3. Verify the connection

Open Cursor Chat and ask the AI to list available MCP tools. You should see `memory_add`, `search_web`, `crawl_scrape`, and others.

### 4. Test a tool call

In Cursor Chat, try:

```
Use memory_add to store that the user is working on a React project with TypeScript.
```

## Configuration

### Project-scoped (recommended)

Place `.cursor/mcp.json` in your project root. This scopes tools to that project.

### Global config

Add to `~/.cursor/mcp.json` for system-wide access:

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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tools not appearing | Restart Cursor after adding config |
| Connection refused | Ensure ContextOS is running on port 8000 |
| Timeout errors | Check firewall settings for localhost |
| Transport error | Verify `transport` is set to `streamable-http` |

## Tips

- Use `Cmd+Shift+P` then "MCP" to see connected servers.
- MCP tools appear automatically in Cursor's tool panel.
- Restart Cursor after any config changes.
