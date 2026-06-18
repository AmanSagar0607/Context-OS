"""
BM25 Search — PostgreSQL Full-Text Search.

Uses PostgreSQL tsvector/tsquery for BM25-style text search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import asyncpg


@dataclass
class BM25SearchResult:
    """Single BM25 search result."""
    id: str
    content: str
    rank: float
    metadata: dict


class BM25Search:
    """PostgreSQL full-text search with BM25 ranking."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def search(
        self,
        query: str,
        table: str = "memories",
        content_column: str = "content",
        id_column: str = "id",
        user_id: Optional[str] = None,
        top_k: int = 10,
        min_rank: float = 0.0,
        filters: Optional[dict] = None,
    ) -> list[BM25SearchResult]:
        """
        Full-text search using PostgreSQL tsvector.

        Args:
            query: Search query string
            table: Table to search
            content_column: Column containing text content
            id_column: Column containing unique identifier
            user_id: Optional user ID filter
            top_k: Number of results to return
            min_rank: Minimum rank score
            filters: Additional filters

        Returns:
            List of BM25SearchResult sorted by rank descending
        """
        # Build query
        conditions = []
        params = []
        param_idx = 1

        # Add tsvector condition
        conditions.append(f"to_tsvector('english', {content_column}) @@ plainto_tsquery('english', ${param_idx})")
        params.append(query)
        param_idx += 1

        if user_id:
            conditions.append(f"user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        if filters:
            for key, value in filters.items():
                conditions.append(f"{key} = ${param_idx}")
                params.append(value)
                param_idx += 1

        where_clause = " AND ".join(conditions)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {id_column}, {content_column},
                       ts_rank_cd(to_tsvector('english', {content_column}), plainto_tsquery('english', $1)) as rank
                FROM {table}
                WHERE {where_clause}
                ORDER BY rank DESC
                LIMIT ${param_idx}
                """,
                *params,
                top_k,
            )

        results = []
        for row in rows:
            rank = float(row["rank"])
            if rank >= min_rank:
                results.append(BM25SearchResult(
                    id=str(row[id_column]),
                    content=row[content_column],
                    rank=rank,
                    metadata={},
                ))

        return results

    async def search_with_metadata(
        self,
        query: str,
        table: str = "memories",
        content_column: str = "content",
        id_column: str = "id",
        metadata_column: str = "metadata",
        user_id: Optional[str] = None,
        top_k: int = 10,
        min_rank: float = 0.0,
    ) -> list[BM25SearchResult]:
        """
        Full-text search with metadata retrieval.
        """
        conditions = []
        params = []
        param_idx = 1

        conditions.append(f"to_tsvector('english', {content_column}) @@ plainto_tsquery('english', ${param_idx})")
        params.append(query)
        param_idx += 1

        if user_id:
            conditions.append(f"user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {id_column}, {content_column}, {metadata_column},
                       ts_rank_cd(to_tsvector('english', {content_column}), plainto_tsquery('english', $1)) as rank
                FROM {table}
                WHERE {where_clause}
                ORDER BY rank DESC
                LIMIT ${param_idx}
                """,
                *params,
                top_k,
            )

        results = []
        for row in rows:
            rank = float(row["rank"])
            if rank >= min_rank:
                import json
                metadata = json.loads(row[metadata_column]) if row[metadata_column] else {}
                results.append(BM25SearchResult(
                    id=str(row[id_column]),
                    content=row[content_column],
                    rank=rank,
                    metadata=metadata,
                ))

        return results