"""
Tests for memory models — Pure Python tests without database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime
from uuid import uuid4

from memory.models import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryContextWindow,
    MemoryType,
    ImportanceLevel,
)


class TestMemoryModels:
    """Test memory Pydantic models."""

    def test_memory_create_defaults(self):
        """MemoryCreate has correct defaults."""
        request = MemoryCreate(content="Test memory")
        assert request.content == "Test memory"
        assert request.memory_type == MemoryType.EPISODIC
        assert request.importance == ImportanceLevel.MEDIUM
        assert request.tags == []
        assert request.metadata == {}

    def test_memory_create_with_options(self):
        """MemoryCreate accepts all options."""
        request = MemoryCreate(
            content="Important fact",
            summary="Key information",
            memory_type=MemoryType.SEMANTIC,
            importance=ImportanceLevel.HIGH,
            tags=["fact", "important"],
            source="document",
            metadata={"doc_id": "123"},
            agent_id="research-agent",
            session_id="session-456",
        )
        assert request.content == "Important fact"
        assert request.summary == "Key information"
        assert request.memory_type == MemoryType.SEMANTIC
        assert request.importance == ImportanceLevel.HIGH
        assert request.tags == ["fact", "important"]
        assert request.source == "document"
        assert request.metadata == {"doc_id": "123"}
        assert request.agent_id == "research-agent"
        assert request.session_id == "session-456"

    def test_memory_creation(self):
        """Memory model can be created."""
        memory = Memory(
            user_id="user-123",
            content="Test content",
        )
        assert memory.user_id == "user-123"
        assert memory.content == "Test content"
        assert memory.id is not None
        assert memory.created_at is not None
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.importance == ImportanceLevel.MEDIUM

    def test_memory_search_request(self):
        """MemorySearchRequest validates parameters."""
        request = MemorySearchRequest(
            query="search term",
            user_id="user-123",
            top_k=10,
            min_score=0.7,
        )
        assert request.query == "search term"
        assert request.user_id == "user-123"
        assert request.top_k == 10
        assert request.min_score == 0.7

    def test_memory_search_request_validation(self):
        """MemorySearchRequest validates bounds."""
        with pytest.raises(Exception):
            MemorySearchRequest(
                query="test",
                user_id="user-123",
                top_k=0,  # Invalid: must be >= 1
            )

    def test_memory_search_result(self):
        """MemorySearchResult combines memory with score."""
        memory = Memory(user_id="user-123", content="Result")
        result = MemorySearchResult(memory=memory, score=0.85)
        assert result.memory.content == "Result"
        assert result.score == 0.85

    def test_memory_context_window(self):
        """MemoryContextWindow assembles context."""
        memories = [
            Memory(user_id="user-123", content="Memory 1"),
            Memory(user_id="user-123", content="Memory 2"),
        ]
        context = MemoryContextWindow(
            memories=memories,
            total_tokens=100,
            truncated=False,
            query="test query",
        )
        assert len(context.memories) == 2
        assert context.total_tokens == 100
        assert context.truncated is False

    def test_memory_update_partial(self):
        """MemoryUpdate allows partial updates."""
        update = MemoryUpdate(content="Updated content")
        assert update.content == "Updated content"
        assert update.summary is None
        assert update.memory_type is None

    def test_memory_types(self):
        """MemoryType enum has all types."""
        assert MemoryType.EPISODIC == "episodic"
        assert MemoryType.SEMANTIC == "semantic"
        assert MemoryType.PROCEDURAL == "procedural"

    def test_importance_levels(self):
        """ImportanceLevel enum has all levels."""
        assert ImportanceLevel.LOW == "low"
        assert ImportanceLevel.MEDIUM == "medium"
        assert ImportanceLevel.HIGH == "high"
        assert ImportanceLevel.CRITICAL == "critical"