"""
Vector Search — pgvector-based semantic search.

Uses PostgreSQL + pgvector for cosine similarity search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import asyncpg

from ..embeddings.service import EmbeddingService


@dataclass
class VectorSearchResult:
    """Single vector search result."""
    id: str
    content: str
    score: float
    metadata: dict


class VectorSearch:
    """pgvector-based semantic search."""

    def __init__(self, pool: asyncpg.Pool, embeddings: EmbeddingService):
        self.pool = pool
        self.embeddings = embeddings

    async def search(
        self,
        query: str,
        table: str = "memories",
        content_column: str = "content",
        embedding_column: str = "embedding",
        id_column: str = "id",
        user_id: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.0,
        filters: Optional[dict] = None,
    ) -> list[VectorSearchResult]:
        """
        Semantic search using cosine similarity.

        Args:
            query: Search query string
            table: Table to search
            content_column: Column containing text content
            embedding_column: Column containing vector embeddings
            id_column: Column containing unique identifier
            user_id: Optional user ID filter
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            filters: Additional filters

        Returns:
            List of VectorSearchResult sorted by score descending
        """
        # Generate query embedding
        embedding_result = self.embeddings.embed_texts([query])
        query_embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None

        if not query_embedding:
            return []

        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        # Build query
        conditions = []
        params = []
        param_idx = 1

        if user_id:
            conditions.append(f"user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        if filters:
            for key, value in filters.items():
                conditions.append(f"{key} = ${param_idx}")
                params.append(value)
                param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {id_column}, {content_column},
                       1 - ({embedding_column} <=> ${param_idx}::vector) as similarity
                FROM {table}
                WHERE {where_clause}
                  AND {embedding_column} IS NOT NULL
                ORDER BY {embedding_column} <=> ${param_idx}::vector
                LIMIT ${param_idx + 1}
                """,
                *params,
                embedding_str,
                top_k,
            )

        results = []
        for row in rows:
            score = float(row["similarity"])
            if score >= min_score:
                results.append(VectorSearchResult(
                    id=str(row[id_column]),
                    content=row[content_column],
                    score=score,
                    metadata={},
                ))

        return results

    async def search_with_metadata(
        self,
        query: str,
        table: str = "memories",
        content_column: str = "content",
        embedding_column: str = "embedding",
        id_column: str = "id",
        metadata_column: str = "metadata",
        user_id: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[VectorSearchResult]:
        """
        Semantic search with metadata retrieval.
        """
        embedding_result = self.embeddings.embed_texts([query])
        query_embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None

        if not query_embedding:
            return []

        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        conditions = []
        params = []
        param_idx = 1

        if user_id:
            conditions.append(f"user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {id_column}, {content_column}, {metadata_column},
                       1 - ({embedding_column} <=> ${param_idx}::vector) as similarity
                FROM {table}
                WHERE {where_clause}
                  AND {embedding_column} IS NOT NULL
                ORDER BY {embedding_column} <=> ${param_idx}::vector
                LIMIT ${param_idx + 1}
                """,
                *params,
                embedding_str,
                top_k,
            )

        results = []
        for row in rows:
            score = float(row["similarity"])
            if score >= min_score:
                import json
                metadata = json.loads(row[metadata_column]) if row[metadata_column] else {}
                results.append(VectorSearchResult(
                    id=str(row[id_column]),
                    content=row[content_column],
                    score=score,
                    metadata=metadata,
                ))

        return results