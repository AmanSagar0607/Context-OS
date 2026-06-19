"""
Context AI — Python SDK Types

Pydantic models for API requests and responses.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# --- Enums ---

class MemoryType(str, Enum):
    """Memory classification."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class ImportanceLevel(str, Enum):
    """Memory importance."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --- Memory Models ---

class MemoryCreate(BaseModel):
    """Request to create a memory."""
    content: str
    summary: Optional[str] = None
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


class MemoryUpdate(BaseModel):
    """Request to update a memory."""
    content: Optional[str] = None
    summary: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    importance: Optional[ImportanceLevel] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class Memory(BaseModel):
    """Memory record."""
    id: str
    content: str
    summary: Optional[str] = None
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MemorySearchRequest(BaseModel):
    """Request to search memories."""
    query: str
    memory_type: Optional[MemoryType] = None
    tags: Optional[list[str]] = None
    top_k: int = Field(default=5, ge=1, le=100)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)


class MemorySearchResult(BaseModel):
    """Single search result."""
    memory: Memory
    score: float = Field(ge=0.0, le=1.0)


# --- Search Models ---

class SearchRequest(BaseModel):
    """Web search request."""
    query: str
    max_results: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Single search result."""
    title: str
    url: str
    snippet: str
    score: Optional[float] = None


# --- Crawl Models ---

class CrawlRequest(BaseModel):
    """Crawl request."""
    url: str
    max_pages: int = Field(default=10, ge=1, le=100)
    extract_content: bool = True


class CrawlResult(BaseModel):
    """Single crawl result."""
    url: str
    title: Optional[str] = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# --- Knowledge Models ---

class EntityCreate(BaseModel):
    """Request to create an entity."""
    name: str
    entity_type: str = "concept"
    description: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    """Knowledge graph entity."""
    id: str
    name: str
    entity_type: str
    description: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class RelationshipCreate(BaseModel):
    """Request to create a relationship."""
    source_id: str
    target_id: str
    relationship_type: str = "related_to"
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


# --- API Response Models ---

class APIResponse(BaseModel):
    """Generic API response."""
    success: bool
    data: Any = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: dict[str, str] = Field(default_factory=dict)