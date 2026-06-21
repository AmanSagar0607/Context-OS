# Extract

> Extract structured data from any URL using AI-powered parsing with custom schemas.

## Overview

The Extract endpoint uses LLMs to pull structured information from web pages. Define a schema describing the data you need, and the system reads the page content and returns typed results. This eliminates brittle CSS selectors and handles varying page layouts automatically.

## Quick Start

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.extract(
    url="https://docs.example.com/changelog",
    schema={
        "version": "string",
        "release_date": "string",
        "changes": "string[]"
    }
)

print(result.data)
# {'version': '2.4.0', 'release_date': '2025-06-15', 'changes': ['Added X', 'Fixed Y']}
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/extract` | Extract structured data from URLs |

### Request parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | — | Single URL to extract from |
| `urls` | `string[]` | — | Multiple URLs to extract from |
| `schema` | `object` | required | Output schema as `{field: type}` |
| `prompt` | `string` | — | Custom extraction instructions |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `data` | `object[]` | Extracted data matching the schema |
| `source_urls` | `string[]` | URLs that were processed |

## Examples

### Extract product info from e-commerce pages

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.extract(
    url="https://shop.example.com/products/widget-pro",
    schema={
        "name": "string",
        "price": "number",
        "currency": "string",
        "features": "string[]",
        "in_stock": "boolean"
    }
)

product = result.data[0]
print(f"{product['name']}: {product['price']} {product['currency']}")
```

### Batch extract with custom prompt

```python
from context_ai import ContextClient

client = ContextClient(api_key="your-api-key")

result = client.crawl.extract(
    urls=[
        "https://blog.example.com/post-1",
        "https://blog.example.com/post-2"
    ],
    schema={
        "title": "string",
        "author": "string",
        "summary": "string",
        "tags": "string[]"
    },
    prompt="Extract blog post metadata from the article"
)

for post in result.data:
    print(f"{post['title']} by {post['author']}")
```
