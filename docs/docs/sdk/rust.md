# Rust SDK

> ContextOS SDK for Rust.

## Installation

Add to `Cargo.toml`:

```toml
[dependencies]
contextos = "0.1.0"
tokio = { version = "1.0", features = ["full"] }
```

## Quick Start

```rust
use contextos::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new("https://api.contextos.dev", "your-api-key")?;

    // Add memory
    let memory = client.memory().add("User prefers dark mode").await?;
    println!("Created memory: {}", memory.id);

    // Search
    let results = client.search().search("user preferences", Some(5)).await?;
    for hit in results.hits {
        println!("[{:.2}] {}", hit.score, hit.content);
    }

    Ok(())
}
```

## Services

### Memory

```rust
// Add
let memory = client.memory().add("content").await?;

// Get
let memory = client.memory().get("mem_abc123").await?;

// Search
let results = client.memory().search("query", Some(5)).await?;

// Delete
client.memory().delete("mem_abc123").await?;
```

### Search

```rust
// Hybrid search
let results = client.search().search("query", Some(5)).await?;

// Semantic search
let results = client.search().semantic_search("query", Some(5)).await?;
```

### Crawl

```rust
// Scrape
let result = client.crawl().crawl("https://example.com").await?;

// Extract
let result = client.crawl().extract("https://example.com").await?;
```

### Knowledge

```rust
// Add entity
let entity = client.knowledge().add_entity(&entity).await?;

// Query
let result = client.knowledge().query(Some("ContextOS"), None).await?;
```

## Error Handling

```rust
use contextos::Error;

match client.memory().add("content").await {
    Ok(memory) => println!("Created: {}", memory.id),
    Err(Error::Api { status, message }) => eprintln!("API error {}: {}", status, message),
    Err(e) => eprintln!("Error: {}", e),
}
```
