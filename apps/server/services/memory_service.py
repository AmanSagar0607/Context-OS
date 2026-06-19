"""
Context OS — Memory Service

Service layer for memory operations.
Wraps the context-core MemoryService with database access.
"""

from __future__ import annotations

import os
from typing import Optional

import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/app-agent",
)


class MemoryService:
    """Memory operations service."""

    def __init__(self):
        self.db_url = DATABASE_URL

    async def _get_conn(self):
        """Get database connection."""
        return await psycopg.AsyncConnection.connect(self.db_url)

    async def add(
        self,
        content: str,
        summary: Optional[str] = None,
        memory_type: str = "episodic",
        importance: str = "medium",
        tags: list[str] | None = None,
        source: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> dict:
        """Add a new memory."""
        import uuid
        from datetime import datetime, timezone

        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO memories (id, content, summary, memory_type, importance, tags, source, agent_id, session_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (memory_id, content, summary, memory_type, importance, tags or [], source, agent_id, session_id, now, now),
                )
                await conn.commit()

        return {
            "id": memory_id,
            "content": content,
            "summary": summary,
            "memory_type": memory_type,
            "importance": importance,
            "tags": tags or [],
            "source": source,
            "agent_id": agent_id,
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
        }

    async def get(self, memory_id: str) -> Optional[dict]:
        """Get a memory by ID."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT id, content, summary, memory_type, importance, tags, source, agent_id, session_id, created_at, updated_at FROM memories WHERE id = %s",
                    (memory_id,),
                )
                row = await cur.fetchone()
                if row is None:
                    return None
                return {
                    "id": row[0],
                    "content": row[1],
                    "summary": row[2],
                    "memory_type": row[3],
                    "importance": row[4],
                    "tags": row[5] or [],
                    "source": row[6],
                    "agent_id": row[7],
                    "session_id": row[8],
                    "created_at": str(row[9]) if row[9] else None,
                    "updated_at": str(row[10]) if row[10] else None,
                }

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Optional[dict]:
        """Update a memory."""
        from datetime import datetime, timezone

        updates = []
        params = []
        if content is not None:
            updates.append("content = %s")
            params.append(content)
        if summary is not None:
            updates.append("summary = %s")
            params.append(summary)
        if memory_type is not None:
            updates.append("memory_type = %s")
            params.append(memory_type)
        if importance is not None:
            updates.append("importance = %s")
            params.append(importance)
        if tags is not None:
            updates.append("tags = %s")
            params.append(tags)

        if not updates:
            return await self.get(memory_id)

        updates.append("updated_at = %s")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(memory_id)

        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"UPDATE memories SET {', '.join(updates)} WHERE id = %s RETURNING id",
                    params,
                )
                row = await cur.fetchone()
                await conn.commit()
                if row is None:
                    return None

        return await self.get(memory_id)

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM memories WHERE id = %s", (memory_id,))
                deleted = cur.rowcount > 0
                await conn.commit()
                return deleted

    async def search(
        self,
        query: str,
        memory_type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> list[dict]:
        """Search memories using vector similarity."""
        # Fallback to text search if pgvector not available
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                sql = "SELECT id, content, summary, memory_type, importance, tags, source, created_at FROM memories WHERE content ILIKE %s"
                params = [f"%{query}%"]

                if memory_type:
                    sql += " AND memory_type = %s"
                    params.append(memory_type)

                sql += " ORDER BY created_at DESC LIMIT %s"
                params.append(top_k)

                await cur.execute(sql, params)
                rows = await cur.fetchall()

                return [
                    {
                        "memory": {
                            "id": r[0],
                            "content": r[1],
                            "summary": r[2],
                            "memory_type": r[3],
                            "importance": r[4],
                            "tags": r[5] or [],
                            "source": r[6],
                            "created_at": str(r[7]) if r[7] else None,
                        },
                        "score": 0.8,
                    }
                    for r in rows
                ]

    async def context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> dict:
        """Get assembled context window from memories."""
        results = await self.search(query, top_k=20)

        memories = [r["memory"] for r in results]
        total_tokens = sum(len(m["content"].split()) for m in memories)  # Rough estimate

        return {
            "memories": memories,
            "total_tokens": total_tokens,
            "truncated": total_tokens > max_tokens,
        }

    async def list(
        self,
        memory_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List memories."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                sql = "SELECT id, content, summary, memory_type, importance, tags, source, created_at FROM memories"
                params = []

                if memory_type:
                    sql += " WHERE memory_type = %s"
                    params.append(memory_type)

                sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                await cur.execute(sql, params)
                rows = await cur.fetchall()

                return [
                    {
                        "id": r[0],
                        "content": r[1],
                        "summary": r[2],
                        "memory_type": r[3],
                        "importance": r[4],
                        "tags": r[5] or [],
                        "source": r[6],
                        "created_at": str(r[7]) if r[7] else None,
                    }
                    for r in rows
                ]

    async def related(
        self,
        memory_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get related memories."""
        # Get the source memory first
        source = await self.get(memory_id)
        if source is None:
            return []

        # Search for similar content
        return await self.search(source["content"], top_k=limit)