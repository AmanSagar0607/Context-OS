"""
Memory Models — Pydantic models for unified memory system.

Defines memory types, importance levels, and search parameters.
"""

from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory classification."""
    EPISODIC = "episodic"       # Events, conversations, experiences
    SEMANTIC = "semantic"       # Facts, knowledge, concepts
    PROCEDURAL = "procedural"   # How-to, workflows, patterns


class ImportanceLevel(str, Enum):
    """Memory importance for consolidation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Memory(BaseModel):
    """Core memory record."""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None

    # Content
    content: str
    summary: Optional[str] = None
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: ImportanceLevel = ImportanceLevel.MEDIUM

    # Metadata
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None  # e.g., "conversation", "document", "api"
    metadata: dict = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Relationships
    parent_id: Optional[UUID] = None
    related_ids: list[UUID] = Field(default_factory=list)

    # Embedding reference (stored in pgvector)
    embedding_id: Optional[str] = None


class MemoryCreate(BaseModel):
    """Request model for creating a memory."""
    content: str
    summary: Optional[str] = None
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_id: Optional[UUID] = None


class MemoryUpdate(BaseModel):
    """Request model for updating a memory."""
    content: Optional[str] = None
    summary: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    importance: Optional[ImportanceLevel] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None
    expires_at: Optional[datetime] = None


class MemorySearchRequest(BaseModel):
    """Request model for semantic memory search."""
    query: str
    user_id: str
    agent_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    tags: Optional[list[str]] = None
    top_k: int = Field(default=5, ge=1, le=100)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)


class MemorySearchResult(BaseModel):
    """Single memory search result."""
    memory: Memory
    score: float = Field(ge=0.0, le=1.0)
    explanation: Optional[str] = None


class MemoryContextWindow(BaseModel):
    """Context window assembled from memories."""
    memories: list[Memory]
    total_tokens: int
    truncated: bool = False
    query: str
    filters: dict = Field(default_factory=dict)