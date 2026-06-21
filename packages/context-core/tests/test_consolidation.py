"""
Tests for memory consolidation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4

# Mock asyncpg
sys.modules['asyncpg'] = MagicMock()

# Mock embeddings service
mock_embeddings = MagicMock()
sys.modules['..embeddings'] = MagicMock()
sys.modules['..embeddings.service'] = MagicMock()
sys.modules['embeddings'] = MagicMock()
sys.modules['embeddings.service'] = MagicMock()

# Now import after mocking
from memory.consolidation import (
    ConsolidationConfig,
    ConsolidationResult,
    MemoryConsolidation,
)


class TestConsolidationConfig:
    """Test ConsolidationConfig."""

    def test_default_config(self):
        config = ConsolidationConfig()
        assert config.max_age_days == 30
        assert config.min_similarity == 0.7
        assert config.batch_size == 10
        assert config.delete_originals is True
        assert config.enabled is True

    def test_custom_config(self):
        config = ConsolidationConfig(
            max_age_days=60,
            min_similarity=0.8,
            batch_size=5,
            delete_originals=False,
        )
        assert config.max_age_days == 60
        assert config.min_similarity == 0.8
        assert config.batch_size == 5
        assert config.delete_originals is False


class TestConsolidationResult:
    """Test ConsolidationResult."""

    def test_result_creation(self):
        result = ConsolidationResult()
        assert result.groups_found == 0
        assert result.memories_merged == 0
        assert result.errors == []

    def test_result_with_errors(self):
        result = ConsolidationResult(errors=["Error 1", "Error 2"])
        assert len(result.errors) == 2


class TestMemoryConsolidation:
    """Test MemoryConsolidation."""

    def test_content_similarity(self):
        consolidation = MemoryConsolidation.__new__(MemoryConsolidation)
        consolidation.config = ConsolidationConfig()

        # Identical texts
        sim = consolidation._content_similarity("hello world", "hello world")
        assert sim == 1.0

        # Completely different
        sim = consolidation._content_similarity("hello", "xyz")
        assert sim == 0.0

        # Partial overlap
        sim = consolidation._content_similarity("hello world", "hello there")
        assert 0.0 < sim < 1.0

    def test_empty_similarity(self):
        consolidation = MemoryConsolidation.__new__(MemoryConsolidation)
        consolidation.config = ConsolidationConfig()

        sim = consolidation._content_similarity("", "")
        assert sim == 0.0

        sim = consolidation._content_similarity("hello", "")
        assert sim == 0.0
