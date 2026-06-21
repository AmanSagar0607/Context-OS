# Java SDK

> ContextOS SDK for Java.

## Installation

### Maven

```xml
<dependency>
    <groupId>dev.contextos</groupId>
    <artifactId>contextos-sdk</artifactId>
    <version>0.1.0</version>
</dependency>
```

### Gradle

```groovy
implementation 'dev.contextos:contextos-sdk:0.1.0'
```

## Quick Start

```java
import dev.contextos.ContextOS;

public class Main {
    public static void main(String[] args) throws Exception {
        ContextOS client = new ContextOS("https://api.contextos.dev", "your-api-key");

        // Add memory
        Memory memory = client.getMemory().add("User prefers dark mode");
        System.out.println("Created memory: " + memory.getId());

        // Search
        SearchResponse results = client.getSearch().search("user preferences", 5);
        for (SearchResult result : results.getResults()) {
            System.out.printf("[%.2f] %s%n", result.getScore(), result.getMemory().getContent());
        }
    }
}
```

## Services

### Memory

```java
// Add
Memory memory = client.getMemory().add("content");

// Add with type
Memory memory = client.getMemory().add("content", "fact");

// Get
Memory memory = client.getMemory().get("mem_abc123");

// Search
SearchResponse results = client.getSearch().search("query", 5);

// Delete
client.getMemory().delete("mem_abc123");
```

### Search

```java
// Hybrid search
SearchResponse results = client.getSearch().search("query", 5);

// Semantic search
SearchResponse results = client.getSearch().semanticSearch("query", 5);
```

### Crawl

```java
// Scrape
CrawlResult result = client.getCrawl().scrape("https://example.com");

// Extract
CrawlResult result = client.getCrawl().extract("https://example.com");
```

### Knowledge

```java
// Add entity
KnowledgeEntity entity = client.getKnowledge().addEntity("ContextOS", "software");

// Query
KnowledgeQueryResult result = client.getKnowledge().query("ContextOS", 2);
```

## Error Handling

```java
try {
    Memory memory = client.getMemory().add("content");
} catch (APIException e) {
    System.err.println("API error " + e.getStatusCode() + ": " + e.getMessage());
}
```
