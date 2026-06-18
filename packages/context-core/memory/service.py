"""
Memory Service — Unified memory management on PostgreSQL + pgvector.

Replaces the old split SQLite/PostgreSQL memory system with a single,
scalable memory layer.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

from .models import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryContextWindow,
    MemoryType,
    ImportanceLevel,
)
from ..embeddings.service import EmbeddingService


class MemoryService:
    """Unified memory service backed by PostgreSQL + pgvector."""

    def __init__(self, pool: asyncpg.Pool, embeddings: EmbeddingService):
        self.pool = pool
        self.embeddings = embeddings

    async def add(self, user_id: str, request: MemoryCreate) -> Memory:
        """Store a new memory with embedding."""
        memory_id = uuid4()
        now = datetime.utcnow()

        # Generate embedding
        embedding_result = self.embeddings.embed_texts([request.content])
        embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None

        # Convert embedding to pgvector format
        embedding_str = f"[{','.join(str(x) for x in embedding)}]" if embedding else None

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO memories (
                    id, user_id, agent_id, session_id,
                    content, summary, memory_type, importance,
                    tags, source, metadata,
                    embedding, created_at, updated_at,
                    parent_id
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8,
                    $9, $10, $11,
                    $12::vector, $13, $14,
                    $15
                )
                """,
                memory_id,
                user_id,
                request.agent_id,
                request.session_id,
                request.content,
                request.summary,
                request.memory_type.value,
                request.importance.value,
                request.tags,
                request.source,
                json.dumps(request.metadata),
                embedding_str,
                now,
                now,
                request.parent_id,
            )

        return Memory(
            id=memory_id,
            user_id=user_id,
            agent_id=request.agent_id,
            session_id=request.session_id,
            content=request.content,
            summary=request.summary,
            memory_type=request.memory_type,
            importance=request.importance,
            tags=request.tags,
            source=request.source,
            metadata=request.metadata,
            created_at=now,
            updated_at=now,
            parent_id=request.parent_id,
        )

    async def get(self, memory_id: UUID, user_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, agent_id, session_id,
                       content, summary, memory_type, importance,
                       tags, source, metadata,
                       created_at, updated_at, accessed_at, expires_at,
                       parent_id
                FROM memories
                WHERE id = $1 AND user_id = $2
                """,
                memory_id,
                user_id,
            )

        if not row:
            return None

        return Memory(
            id=row["id"],
            user_id=row["user_id"],
            agent_id=row["agent_id"],
            session_id=row["session_id"],
            content=row["content"],
            summary=row["summary"],
            memory_type=MemoryType(row["memory_type"]),
            importance=ImportanceLevel(row["importance"]),
            tags=row["tags"] or [],
            source=row["source"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            accessed_at=row["accessed_at"],
            expires_at=row["expires_at"],
            parent_id=row["parent_id"],
        )

    async def update(
        self, memory_id: UUID, user_id: str, request: MemoryUpdate
    ) -> Optional[Memory]:
        """Update a memory."""
        updates = []
        params = []
        param_idx = 1

        if request.content is not None:
            updates.append(f"content = ${param_idx}")
            params.append(request.content)
            param_idx += 1
        if request.summary is not None:
            updates.append(f"summary = ${param_idx}")
            params.append(request.summary)
            param_idx += 1
        if request.memory_type is not None:
            updates.append(f"memory_type = ${param_idx}")
            params.append(request.memory_type.value)
            param_idx += 1
        if request.importance is not None:
            updates.append(f"importance = ${param_idx}")
            params.append(request.importance.value)
            param_idx += 1
        if request.tags is not None:
            updates.append(f"tags = ${param_idx}")
            params.append(request.tags)
            param_idx += 1
        if request.metadata is not None:
            updates.append(f"metadata = ${param_idx}")
            params.append(json.dumps(request.metadata))
            param_idx += 1
        if request.expires_at is not None:
            updates.append(f"expires_at = ${param_idx}")
            params.append(request.expires_at)
            param_idx += 1

        if not updates:
            return await self.get(memory_id, user_id)

        updates.append(f"updated_at = ${param_idx}")
        params.append(datetime.utcnow())
        param_idx += 1

        params.extend([memory_id, user_id])

        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                UPDATE memories
                SET {', '.join(updates)}
                WHERE id = ${param_idx - 1} AND user_id = ${param_idx}
                """,
                *params,
            )

        return await self.get(memory_id, user_id)

    async def delete(self, memory_id: UUID, user_id: str) -> bool:
        """Delete a memory."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM memories WHERE id = $1 AND user_id = $2",
                memory_id,
                user_id,
            )
        return result == "DELETE 1"

    async def search(self, request: MemorySearchRequest) -> list[MemorySearchResult]:
        """Semantic search using pgvector cosine similarity."""
        # Generate query embedding
        embedding_result = self.embeddings.embed_texts([request.query])
        query_embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None

        if not query_embedding:
            return []

        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        async with self.pool.acquire() as conn:
            # Build query
            conditions = ["user_id = $1"]
            params = [request.user_id]
            param_idx = 2

            if request.agent_id:
                conditions.append(f"agent_id = ${param_idx}")
                params.append(request.agent_id)
                param_idx += 1

            if request.memory_type:
                conditions.append(f"memory_type = ${param_idx}")
                params.append(request.memory_type.value)
                param_idx += 1

            if request.tags:
                conditions.append(f"tags && ${param_idx}")
                params.append(request.tags)
                param_idx += 1

            where_clause = " AND ".join(conditions)

            rows = await conn.fetch(
                f"""
                SELECT id, user_id, agent_id, session_id,
                       content, summary, memory_type, importance,
                       tags, source, metadata,
                       created_at, updated_at, accessed_at, expires_at,
                       parent_id,
                       1 - (embedding <=> $2::vector) as similarity
                FROM memories
                WHERE {where_clause}
                  AND embedding IS NOT NULL
                  AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY embedding <=> $2::vector
                LIMIT $3
                """,
                *params,
                embedding_str,
                request.top_k,
            )

        results = []
        for row in rows:
            score = float(row["similarity"])
            if score >= request.min_score:
                memory = Memory(
                    id=row["id"],
                    user_id=row["user_id"],
                    agent_id=row["agent_id"],
                    session_id=row["session_id"],
                    content=row["content"],
                    summary=row["summary"],
                    memory_type=MemoryType(row["memory_type"]),
                    importance=ImportanceLevel(row["importance"]),
                    tags=row["tags"] or [],
                    source=row["source"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    accessed_at=row["accessed_at"],
                    expires_at=row["expires_at"],
                    parent_id=row["parent_id"],
                )
                results.append(MemorySearchResult(memory=memory, score=score))

        return results

    async def get_context_window(
        self, user_id: str, query: str, max_tokens: int = 2000
    ) -> MemoryContextWindow:
        """Assemble a context window from relevant memories."""
        search_request = MemorySearchRequest(
            query=query,
            user_id=user_id,
            top_k=10,
            min_score=0.3,
        )
        search_results = await self.search(search_request)

        # Simple token estimation (4 chars per token)
        total_tokens = 0
        selected_memories = []
        truncated = False

        for result in search_results:
            memory_tokens = len(result.memory.content) // 4
            if total_tokens + memory_tokens > max_tokens:
                truncated = True
                break
            selected_memories.append(result.memory)
            total_tokens += memory_tokens

        return MemoryContextWindow(
            memories=selected_memories,
            total_tokens=total_tokens,
            truncated=truncated,
            query=query,
            filters={"user_id": user_id},
        )

    async def list_memories(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Memory]:
        """List memories with optional filters."""
        conditions = ["user_id = $1"]
        params = [user_id]
        param_idx = 2

        if agent_id:
            conditions.append(f"agent_id = ${param_idx}")
            params.append(agent_id)
            param_idx += 1

        if memory_type:
            conditions.append(f"memory_type = ${param_idx}")
            params.append(memory_type.value)
            param_idx += 1

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT id, user_id, agent_id, session_id,
                       content, summary, memory_type, importance,
                       tags, source, metadata,
                       created_at, updated_at, accessed_at, expires_at,
                       parent_id
                FROM memories
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """,
                *params,
            )

        return [
            Memory(
                id=row["id"],
                user_id=row["user_id"],
                agent_id=row["agent_id"],
                session_id=row["session_id"],
                content=row["content"],
                summary=row["summary"],
                memory_type=MemoryType(row["memory_type"]),
                importance=ImportanceLevel(row["importance"]),
                tags=row["tags"] or [],
                source=row["source"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                accessed_at=row["accessed_at"],
                expires_at=row["expires_at"],
                parent_id=row["parent_id"],
            )
            for row in rows
        ]

    async def get_related(
        self, memory_id: UUID, user_id: str, limit: int = 10
    ) -> list[Memory]:
        """Find related memories using embedding similarity."""
        # First get the memory's embedding
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT embedding FROM memories WHERE id = $1 AND user_id = $2",
                memory_id,
                user_id,
            )

        if not row or not row["embedding"]:
            return []

        embedding_str = str(row["embedding"])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, agent_id, session_id,
                       content, summary, memory_type, importance,
                       tags, source, metadata,
                       created_at, updated_at, accessed_at, expires_at,
                       parent_id
                FROM memories
                WHERE user_id = $1
                  AND id != $2
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> $3::vector
                LIMIT $4
                """,
                user_id,
                memory_id,
                embedding_str,
                limit,
            )

        return [
            Memory(
                id=row["id"],
                user_id=row["user_id"],
                agent_id=row["agent_id"],
                session_id=row["session_id"],
                content=row["content"],
                summary=row["summary"],
                memory_type=MemoryType(row["memory_type"]),
                importance=ImportanceLevel(row["importance"]),
                tags=row["tags"] or [],
                source=row["source"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                accessed_at=row["accessed_at"],
                expires_at=row["expires_at"],
                parent_id=row["parent_id"],
            )
            for row in rows
        ]