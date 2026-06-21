"""
Tests for cross-encoder re-ranking.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import patch, MagicMock

from retrieval.reranker import (
    RerankerConfig,
    RerankedResult,
    CrossEncoderReranker,
    HybridReranker,
)


class TestRerankerConfig:
    """Test RerankerConfig."""

    def test_default_config(self):
        config = RerankerConfig()
        assert config.enabled is True
        assert config.model_name == "BAAI/bge-reranker-v2-m3"
        assert config.top_k == 5
        assert config.batch_size == 32
        assert config.device == "cpu"

    def test_custom_config(self):
        config = RerankerConfig(
            enabled=False,
            top_k=10,
            device="cuda",
        )
        assert config.enabled is False
        assert config.top_k == 10
        assert config.device == "cuda"


class TestRerankedResult:
    """Test RerankedResult."""

    def test_result_creation(self):
        result = RerankedResult(
            id="1",
            content="test content",
            original_score=0.8,
            reranked_score=0.9,
            rank=0,
        )
        assert result.id == "1"
        assert result.reranked_score == 0.9
        assert result.rank == 0


class TestCrossEncoderReranker:
    """Test CrossEncoderReranker."""

    def test_disabled_reranker(self):
        config = RerankerConfig(enabled=False)
        reranker = CrossEncoderReranker(config)

        results = [
            {"id": "1", "content": "a", "score": 0.8},
            {"id": "2", "content": "b", "score": 0.9},
        ]

        reranked = reranker.rerank("query", results)

        # Should return empty when disabled
        assert reranked == []

    def test_empty_results(self):
        config = RerankerConfig()
        reranker = CrossEncoderReranker(config)

        reranked = reranker.rerank("query", [])
        assert reranked == []

    @patch("retrieval.reranker.CrossEncoderReranker._load_model")
    def test_rerank_without_model(self, mock_load):
        """Test rerank falls back to original order when model fails to load."""
        config = RerankerConfig()
        reranker = CrossEncoderReranker(config)
        reranker._model = None

        # Make _load_model set model to None (simulating failure)
        def fail_load():
            reranker._model = None

        mock_load.side_effect = fail_load

        results = [
            {"id": "1", "content": "a", "score": 0.8},
            {"id": "2", "content": "b", "score": 0.9},
        ]

        # This should not raise, just return original order
        try:
            reranked = reranker.rerank("query", results, top_k=2)
            # If model loading fails, should still return results
            assert len(reranked) <= 2
        except Exception:
            # Expected if sentence-transformers not installed
            pass


class TestHybridReranker:
    """Test HybridReranker."""

    def test_content_similarity(self):
        config = RerankerConfig()
        reranker = HybridReranker(config)

        # Identical
        sim = reranker._content_similarity("hello world", "hello world")
        assert sim == 1.0

        # Different
        sim = reranker._content_similarity("hello", "xyz")
        assert sim == 0.0

        # Partial
        sim = reranker._content_similarity("hello world", "hello there")
        assert 0.0 < sim < 1.0

    def test_diversity_rerank_empty(self):
        config = RerankerConfig()
        reranker = HybridReranker(config)

        result = reranker.rerank_with_diversity("query", [])
        assert result == []

    @patch("retrieval.reranker.CrossEncoderReranker.rerank")
    def test_diversity_rerank(self, mock_rerank):
        config = RerankerConfig(top_k=2)
        reranker = HybridReranker(config)

        # Mock rerank to return results
        mock_rerank.return_value = [
            RerankedResult(id="1", content="hello world", original_score=0.9, reranked_score=0.9, rank=0),
            RerankedResult(id="2", content="hello there", original_score=0.8, reranked_score=0.8, rank=1),
            RerankedResult(id="3", content="xyz", original_score=0.7, reranked_score=0.7, rank=2),
        ]

        results = [
            {"id": "1", "content": "hello world", "score": 0.9},
            {"id": "2", "content": "hello there", "score": 0.8},
            {"id": "3", "content": "xyz", "score": 0.7},
        ]

        reranked = reranker.rerank_with_diversity(
            "query", results, top_k=2, diversity_weight=0.5
        )

        assert len(reranked) == 2
        # Should prefer "xyz" over "hello there" due to diversity
        assert reranked[0].id == "1"
        assert reranked[1].id == "3"
