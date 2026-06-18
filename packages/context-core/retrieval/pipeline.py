"""
Retrieval Pipeline — Full hybrid retrieval with vector + BM25 + fusion.

Combines vector search, BM25 search, and RRF fusion into a single pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import asyncpg

from ..embeddings.service import EmbeddingService
from .vector_search import VectorSearch
from .bm25_search import BM25Search
from .fusion import reciprocal_rank_fusion, weighted_reciprocal_rank_fusion, FusedResult
from .chunking import RecursiveChunker, Chunk


@dataclass
class RetrievalConfig:
    """Configuration for retrieval pipeline."""
    # Search settings
    vector_top_k: int = 10
    bm25_top_k: int = 10
    final_top_k: int = 5
    min_score: float = 0.0

    # Fusion settings
    rrf_k: int = 60
    vector_weight: float = 1.0
    bm25_weight: float = 1.0

    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Table settings
    table: str = "memories"
    content_column: str = "content"
    embedding_column: str = "embedding"
    id_column: str = "id"


@dataclass
class RetrievalResult:
    """Single retrieval result."""
    id: str
    content: str
    score: float
    sources: list[str]
    metadata: dict = field(default_factory=dict)


class RetrievalPipeline:
    """
    Hybrid retrieval pipeline combining vector search, BM25, and RRF fusion.

    Flow:
    1. Generate query embedding
    2. Run vector search (semantic)
    3. Run BM25 search (keyword)
    4. Fuse results using RRF
    5. Return top-K results
    """

    def __init__(
        self,
        pool: asyncpg.Pool,
        embeddings: EmbeddingService,
        config: Optional[RetrievalConfig] = None,
    ):
        self.pool = pool
        self.embeddings = embeddings
        self.config = config or RetrievalConfig()

        # Initialize sub-searchers
        self.vector_search = VectorSearch(pool, embeddings)
        self.bm25_search = BM25Search(pool)
        self.chunker = RecursiveChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )

    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        filters: Optional[dict] = None,
        top_k: Optional[int] = None,
    ) -> list[RetrievalResult]:
        """
        Execute hybrid retrieval pipeline.

        Args:
            query: Search query
            user_id: Optional user ID filter
            filters: Optional filters
            top_k: Override final top-K

        Returns:
            List of RetrievalResult sorted by score
        """
        final_top_k = top_k or self.config.final_top_k

        # Run vector search
        vector_results = await self.vector_search.search(
            query=query,
            table=self.config.table,
            content_column=self.config.content_column,
            embedding_column=self.config.embedding_column,
            id_column=self.config.id_column,
            user_id=user_id,
            top_k=self.config.vector_top_k,
            min_score=self.config.min_score,
            filters=filters,
        )

        # Run BM25 search
        bm25_results = await self.bm25_search.search(
            query=query,
            table=self.config.table,
            content_column=self.config.content_column,
            id_column=self.config.id_column,
            user_id=user_id,
            top_k=self.config.bm25_top_k,
        )

        # Convert to dicts for fusion
        vector_dicts = [
            {"id": r.id, "content": r.content, "score": r.score}
            for r in vector_results
        ]
        bm25_dicts = [
            {"id": r.id, "content": r.content, "rank": r.rank}
            for r in bm25_results
        ]

        # Fuse results
        fused = weighted_reciprocal_rank_fusion(
            result_lists=[vector_dicts, bm25_dicts],
            weights=[self.config.vector_weight, self.config.bm25_weight],
            k=self.config.rrf_k,
            source_names=["vector", "bm25"],
        )

        # Take top-K
        top_results = fused[:final_top_k]

        return [
            RetrievalResult(
                id=r.id,
                content=r.content,
                score=r.rrf_score,
                sources=r.sources,
                metadata=r.metadata,
            )
            for r in top_results
        ]

    async def search_with_context(
        self,
        query: str,
        user_id: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> dict:
        """
        Search and assemble context window.

        Args:
            query: Search query
            user_id: Optional user ID filter
            max_tokens: Maximum tokens in context window

        Returns:
            Dict with memories, total_tokens, truncated flag
        """
        results = await self.search(query, user_id)

        # Simple token estimation (4 chars per token)
        total_tokens = 0
        selected = []
        truncated = False

        for result in results:
            result_tokens = len(result.content) // 4
            if total_tokens + result_tokens > max_tokens:
                truncated = True
                break
            selected.append(result)
            total_tokens += result_tokens

        return {
            "memories": selected,
            "total_tokens": total_tokens,
            "truncated": truncated,
            "query": query,
        }

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> list[Chunk]:
        """
        Chunk text using the configured chunker.

        Args:
            text: Text to chunk
            metadata: Optional metadata

        Returns:
            List of Chunk objects
        """
        return self.chunker.chunk(text, metadata)