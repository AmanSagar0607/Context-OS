"""
Context AI — Python SDK Tests

Tests for the client and memory operations.
"""

import pytest
from unittest.mock import MagicMock, patch

from context_ai import (
    ContextAI,
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemoryType,
    ImportanceLevel,
    MemorySearchRequest,
)


@pytest.fixture
def client():
    """Create a test client."""
    return ContextAI(base_url="http://localhost:8000", api_key="test-key")


@pytest.fixture
def mock_http():
    """Create a mock HTTP client."""
    with patch("context_ai.client.HTTPClient") as MockHTTP:
        mock = MagicMock()
        MockHTTP.return_value = mock
        yield mock


class TestClientInit:
    """Tests for client initialization."""

    def test_default_init(self):
        client = ContextAI()
        assert client.base_url == "http://localhost:8000"

    def test_custom_url(self):
        client = ContextAI(base_url="http://custom:9000")
        assert client.base_url == "http://custom:9000"

    def test_api_key(self):
        client = ContextAI(api_key="my-key")
        assert client.api_key == "my-key"

    def test_repr(self):
        client = ContextAI(base_url="http://test:8080")
        assert "http://test:8080" in repr(client)

    def test_context_manager(self):
        with ContextAI() as client:
            assert client is not None


class TestMemoryClient:
    """Tests for memory operations."""

    def test_memory_types(self):
        assert MemoryType.EPISODIC == "episodic"
        assert MemoryType.SEMANTIC == "semantic"
        assert MemoryType.PROCEDURAL == "procedural"

    def test_importance_levels(self):
        assert ImportanceLevel.LOW == "low"
        assert ImportanceLevel.CRITICAL == "critical"

    def test_memory_create_model(self):
        req = MemoryCreate(
            content="Test memory",
            memory_type=MemoryType.SEMANTIC,
            importance=ImportanceLevel.HIGH,
            tags=["test"],
        )
        assert req.content == "Test memory"
        assert req.memory_type == MemoryType.SEMANTIC
        assert req.importance == ImportanceLevel.HIGH
        assert req.tags == ["test"]

    def test_memory_search_request(self):
        req = MemorySearchRequest(
            query="test query",
            top_k=10,
            min_score=0.7,
        )
        assert req.query == "test query"
        assert req.top_k == 10
        assert req.min_score == 0.7

    def test_memory_model(self):
        mem = Memory(
            id="mem-123",
            content="Test content",
            memory_type=MemoryType.EPISODIC,
            tags=["test"],
        )
        assert mem.id == "mem-123"
        assert mem.content == "Test content"

    def test_memory_update_partial(self):
        update = MemoryUpdate(content="Updated")
        dumped = update.model_dump(exclude_unset=True)
        assert "content" in dumped
        assert "summary" not in dumped


class TestKnowledgeClient:
    """Tests for knowledge operations."""

    def test_entity_create(self):
        from context_ai import EntityCreate
        req = EntityCreate(
            name="GPT-4",
            entity_type="model",
            description="Large language model",
        )
        assert req.name == "GPT-4"
        assert req.entity_type == "model"

    def test_relationship_create(self):
        from context_ai import RelationshipCreate
        req = RelationshipCreate(
            source_id="entity-1",
            target_id="entity-2",
            relationship_type="uses",
            weight=0.8,
        )
        assert req.source_id == "entity-1"
        assert req.weight == 0.8