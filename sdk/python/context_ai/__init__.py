"""
Context AI — Python SDK

A Python client library for the Context OS API.
Provides memory, search, crawl, and knowledge graph operations.

Usage:
    from context_ai import ContextAI, MemoryCreate, MemoryType

    client = ContextAI(api_key="your-api-key")

    # Add a memory
    memory = client.memory.add(MemoryCreate(
        content="User prefers dark mode",
        memory_type=MemoryType.SEMANTIC,
    ))

    # Search memories
    results = client.memory.search(query="dark mode")

    # Web search
    web_results = client.search.web(query="AI news")
"""

__version__ = "0.1.0"

from .client import ContextAI
from .types import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemoryType,
    ImportanceLevel,
    MemorySearchRequest,
    MemorySearchResult,
    SearchRequest,
    SearchResult,
    CrawlRequest,
    CrawlResult,
    Entity,
    EntityCreate,
    RelationshipCreate,
    APIResponse,
    HealthResponse,
)

__all__ = [
    "ContextAI",
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryType",
    "ImportanceLevel",
    "MemorySearchRequest",
    "MemorySearchResult",
    "SearchRequest",
    "SearchResult",
    "CrawlRequest",
    "CrawlResult",
    "Entity",
    "EntityCreate",
    "RelationshipCreate",
    "APIResponse",
    "HealthResponse",
]