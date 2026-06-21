# Crawl MCP Tools
> MCP tools for web scraping, crawling, sitemap discovery, and data extraction.

## Overview

Crawl MCP tools let your agents interact with web content programmatically. Scrape individual pages, crawl entire sites, discover URLs via sitemaps, and extract structured data from HTML. All tools return clean, markdown-ready content.

## Quick Start

1. Ensure ContextOS is running locally.
2. Connect your agent to the MCP endpoint.
3. Call crawl tools via JSON-RPC.

## Tools

| Tool | Description |
|------|-------------|
| `crawl_scrape` | Scrape a single URL and return content |
| `crawl_crawl` | Crawl multiple pages following links |
| `crawl_map` | Discover all URLs from a sitemap |
| `crawl_extract` | Extract structured data from content |

## Examples

### Scrape a Single Page

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "crawl_scrape",
    "arguments": {
      "url": "https://docs.example.com/api/reference",
      "format": "markdown"
    }
  }
}
```

### Crawl a Section

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "crawl_crawl",
    "arguments": {
      "url": "https://docs.example.com/guides",
      "max_depth": 2,
      "max_pages": 10
    }
  }
}
```

### Map a Sitemap

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "crawl_map",
    "arguments": {
      "url": "https://docs.example.com/sitemap.xml"
    }
  }
}
```

### Extract Structured Data

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "crawl_extract",
    "arguments": {
      "url": "https://example.com/products",
      "schema": {
        "product_name": "h1",
        "price": ".price",
        "description": ".product-description"
      }
    }
  }
}
```

## Configuration

| Parameter | Description |
|-----------|-------------|
| `url` | Target URL (required) |
| `max_depth` | Crawl depth for `crawl_crawl` |
| `max_pages` | Max pages to visit |
| `format` | Output format: `markdown` or `html` |
| `schema` | CSS selectors for `crawl_extract` |

## Best Practices

- Use `crawl_map` first to understand site structure before crawling.
- Set `max_pages` limits to avoid excessive requests.
- Use `crawl_extract` with CSS selectors for clean, structured data.
