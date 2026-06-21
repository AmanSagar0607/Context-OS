# Go SDK

> ContextOS SDK for Go.

## Installation

```bash
go get github.com/contextos/sdk-go
```

## Quick Start

```go
package main

import (
    "fmt"
    contextos "github.com/contextos/sdk-go"
)

func main() {
    client := contextos.NewClient("https://api.contextos.dev", "your-api-key")

    // Add memory
    memory, err := client.Memory.Add(context.Background(), &contextos.AddMemoryRequest{
        Content: "User prefers dark mode",
        Type:    contextos.MemoryTypeFact,
    })
    if err != nil {
        panic(err)
    }
    fmt.Println("Created memory:", memory.ID)

    // Search
    results, err := client.Search.Search(context.Background(), &contextos.SearchRequest{
        Query: "user preferences",
        TopK:  5,
    })
    if err != nil {
        panic(err)
    }
    for _, hit := range results.Hits {
        fmt.Printf("[%.2f] %s\n", hit.Score, hit.Content)
    }
}
```

## Services

### Memory

```go
// Add
memory, err := client.Memory.Add(ctx, &contextos.AddMemoryRequest{
    Content: "content",
    Type:    contextos.MemoryTypeFact,
})

// Get
memory, err := client.Memory.Get(ctx, "mem_abc123")

// Search
results, err := client.Memory.Search(ctx, &contextos.SearchMemoryRequest{
    Query: "query",
    TopK:  5,
})

// Delete
err := client.Memory.Delete(ctx, "mem_abc123")
```

### Search

```go
// Hybrid search
results, err := client.Search.Search(ctx, &contextos.SearchRequest{
    Query: "query",
    TopK:  5,
})

// Semantic search
results, err := client.Search.SemanticSearch(ctx, "query", 5)
```

### Crawl

```go
// Scrape
result, err := client.Crawl.Crawl(ctx, &contextos.CrawlRequest{
    URL: "https://example.com",
})

// Extract
result, err := client.Crawl.Extract(ctx, "https://example.com")
```

### Knowledge

```go
// Add entity
entity, err := client.Knowledge.AddEntity(ctx, &contextos.KnowledgeEntity{
    Name: "ContextOS",
    Type: "software",
})

// Query
result, err := client.Knowledge.Query(ctx, &contextos.KnowledgeQueryRequest{
    EntityName: "ContextOS",
})
```
