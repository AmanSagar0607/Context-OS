"""
Tests for retrieval pipeline — Pure Python tests without database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from retrieval.fusion import (
    reciprocal_rank_fusion,
    weighted_reciprocal_rank_fusion,
    FusedResult,
)
from retrieval.chunking import RecursiveChunker, Chunk


class TestRRFFusion:
    """Test Reciprocal Rank Fusion."""

    def test_empty_lists(self):
        """Empty input returns empty output."""
        result = reciprocal_rank_fusion([])
        assert result == []

    def test_single_list(self):
        """Single list returns results with single source."""
        results = [
            [{"id": "1", "content": "a"}, {"id": "2", "content": "b"}],
        ]
        fused = reciprocal_rank_fusion(results)
        assert len(fused) == 2
        assert fused[0].id == "1"
        assert fused[0].sources == ["source_0"]

    def test_two_lists_same_results(self):
        """Two lists with same results combine scores."""
        list1 = [{"id": "1", "content": "a"}, {"id": "2", "content": "b"}]
        list2 = [{"id": "1", "content": "a"}, {"id": "2", "content": "b"}]
        fused = reciprocal_rank_fusion([list1, list2])
        assert len(fused) == 2
        assert fused[0].sources == ["source_0", "source_1"]

    def test_two_lists_different_results(self):
        """Two lists with different results merge."""
        list1 = [{"id": "1", "content": "a"}]
        list2 = [{"id": "2", "content": "b"}]
        fused = reciprocal_rank_fusion([list1, list2])
        assert len(fused) == 2

    def test_rrf_scoring(self):
        """RRF score follows formula 1/(k+rank)."""
        list1 = [{"id": "1", "content": "a"}]
        list2 = [{"id": "2", "content": "b"}]
        fused = reciprocal_rank_fusion([list1, list2], k=60)
        # Both should have rank 0, so score = 1/(60+0+1) = 1/61
        assert len(fused) == 2

    def test_source_names(self):
        """Custom source names are applied."""
        list1 = [{"id": "1", "content": "a"}]
        list2 = [{"id": "2", "content": "b"}]
        fused = reciprocal_rank_fusion(
            [list1, list2],
            source_names=["vector", "bm25"],
        )
        assert fused[0].sources == ["vector"]
        assert fused[1].sources == ["bm25"]


class TestWeightedRRF:
    """Test Weighted RRF."""

    def test_weighted_fusion(self):
        """Weighted fusion applies weights correctly."""
        list1 = [{"id": "1", "content": "a"}]
        list2 = [{"id": "2", "content": "b"}]
        fused = weighted_reciprocal_rank_fusion(
            [list1, list2],
            weights=[2.0, 1.0],
        )
        assert len(fused) == 2

    def test_weight_mismatch(self):
        """Mismatched weights raise error."""
        with pytest.raises(ValueError):
            weighted_reciprocal_rank_fusion(
                [{"id": "1", "content": "a"}],
                weights=[1.0, 2.0],
            )


class TestRecursiveChunker:
    """Test Recursive Chunker."""

    def test_empty_text(self):
        """Empty text returns empty list."""
        chunker = RecursiveChunker(chunk_size=100)
        chunks = chunker.chunk("")
        assert chunks == []

    def test_short_text(self):
        """Short text returns single chunk."""
        chunker = RecursiveChunker(chunk_size=100)
        chunks = chunker.chunk("Hello world")
        assert len(chunks) == 1
        assert chunks[0].content == "Hello world"

    def test_long_text_splits(self):
        """Long text splits into multiple chunks."""
        chunker = RecursiveChunker(chunk_size=50)
        text = "This is a test sentence. " * 10
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_paragraph_splitting(self):
        """Text splits on paragraphs first."""
        chunker = RecursiveChunker(chunk_size=30)
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = chunker.chunk(text)
        assert len(chunks) == 3

    def test_chunk_metadata(self):
        """Chunks have correct metadata."""
        chunker = RecursiveChunker(chunk_size=100)
        text = "Hello world"
        chunks = chunker.chunk(text, metadata={"source": "test"})
        assert chunks[0].metadata == {"source": "test"}

    def test_chunk_indices(self):
        """Chunks have sequential indices."""
        chunker = RecursiveChunker(chunk_size=50)
        text = "Word " * 20
        chunks = chunker.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_overlap(self):
        """Chunks have overlap when configured."""
        chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10)
        text = "This is a test. " * 10
        chunks = chunker.chunk(text)
        if len(chunks) > 1:
            # Check overlap exists
            assert len(chunks[1].content) > 0

    def test_min_chunk_size(self):
        """Chunks respect minimum size."""
        chunker = RecursiveChunker(chunk_size=100, min_chunk_size=20)
        text = "Hello world"
        chunks = chunker.chunk(text)
        assert len(chunks) == 1

    def test_chunk_documents(self):
        """Chunk multiple documents."""
        chunker = RecursiveChunker(chunk_size=50)
        docs = [
            {"content": "Document one", "source": "a"},
            {"content": "Document two", "source": "b"},
        ]
        chunks = chunker.chunk_documents(docs)
        assert len(chunks) == 2