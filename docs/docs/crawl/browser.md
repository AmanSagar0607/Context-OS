# Browser

> Render JavaScript-heavy pages and SPAs using headless Playwright for accurate content extraction.

## Overview

Some websites render content client-side with JavaScript, making standard HTTP requests insufficient. The Browser mode launches a headless Playwright instance to execute JavaScript, wait for dynamic content, and return the fully rendered page. Use this for SPAs, React/Vue apps, and sites that load content via AJAX.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.scrape(
    url="https://spa.example.com/dashboard",
    browser=True
)

print(result.markdown)
```

### With wait conditions

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.scrape(
    url="https://app.example.com/data",
    browser=True,
    wait_for="#main-content",
    timeout=30
)

print(result.markdown)
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/scrape` | Scrape a single URL with optional browser rendering |

### Request parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | URL to scrape |
| `browser` | `boolean` | `false` | Enable Playwright rendering |
| `wait_for` | `string` | — | CSS selector to wait for before extraction |
| `timeout` | `integer` | `30` | Max seconds to wait for page load |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `markdown` | `string` | Rendered page content as markdown |
| `html` | `string` | Raw HTML of the rendered page |
| `metadata` | `object` | Title, description, and other meta tags |

## Examples

### Scrape a React SPA

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.scrape(
    url="https://app.example.com/overview",
    browser=True,
    wait_for="[data-loaded='true']"
)

print(result.markdown)
```

### Extract data from a JS-rendered table

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

data = client.crawl.extract(
    url="https://analytics.example.com/dashboard",
    browser=True,
    wait_for="table tbody tr",
    schema={"metrics": "object[]"}
)

print(data.data[0]["metrics"])
```
