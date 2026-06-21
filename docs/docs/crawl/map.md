# Map

> Discover the full structure of a website as a hierarchical URL tree.

## Overview

The Map endpoint builds a sitemap-like tree of a website without fetching page content. It discovers all reachable internal links from a seed URL and organizes them into a nested structure. Use this to understand site architecture, plan crawl jobs, or validate URL coverage before running a full crawl.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

site_map = client.crawl.map(url="https://docs.example.com")

for branch in site_map.tree:
    print(f"{branch.url} ({len(branch.children)} children)")
```

### Filter results

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

site_map = client.crawl.map(
    url="https://docs.example.com",
    max_depth=2,
    include_patterns=["/docs/*"]
)

for url in site_map.urls:
    print(url)
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/map` | Discover site structure as a URL tree |

### Request parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | Seed URL to map from |
| `max_depth` | `integer` | `5` | Maximum depth to traverse |
| `include_patterns` | `string[]` | `[]` | URL glob patterns to include |
| `exclude_patterns` | `string[]` | `[]` | URL glob patterns to exclude |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `tree` | `Node[]` | Hierarchical tree of URL nodes |
| `tree[].url` | `string` | Page URL |
| `tree[].children` | `Node[]` | Child URL nodes |
| `urls` | `string[]` | Flat list of all discovered URLs |
| `total` | `integer` | Total number of URLs found |

## Examples

### Map and visualize site structure

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.map(url="https://docs.example.com", max_depth=3)

def print_tree(nodes, indent=0):
    for node in nodes:
        print(f"{'  ' * indent}{node.url}")
        print_tree(node.children, indent + 1)

print_tree(result.tree)
```

### Plan a targeted crawl

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

site_map = client.crawl.map(
    url="https://docs.example.com",
    include_patterns=["/guides/*", "/tutorials/*"]
)

print(f"Found {site_map.total} pages to crawl")
print("\n".join(site_map.urls[:20]))
```
