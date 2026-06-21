"""
Agent Memory — Long-term memory across sessions.

Enables agents to remember context across conversations,
maintain user preferences, and learn from interactions.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

logger = logging.getLogger(__name__)


class MemoryScope(str, Enum):
    SESSION = "session"        # Current session only
    USER = "user"              # Across all sessions for a user
    AGENT = "agent"            # Agent-specific memory
    GLOBAL = "global"          # Shared across all users/agents


class MemoryPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentMemory:
    """An agent memory entry."""
    id: str
    agent_id: str
    user_id: str
    session_id: Optional[str]
    scope: MemoryScope
    content: str
    summary: Optional[str] = None
    priority: MemoryPriority = MemoryPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed_at: Optional[datetime] = None


@dataclass
class AgentMemoryConfig:
    """Configuration for agent memory."""
    max_memories_per_user: int = 1000
    max_memories_per_agent: int = 500
    default_expiry_days: int = 90
    enable_compression: bool = True
    compression_threshold: int = 100  # Compress after this many memories


class AgentMemoryService:
    """Agent memory service for long-term context."""

    def __init__(self, pool: asyncpg.Pool, config: Optional[AgentMemoryConfig] = None):
        self.pool = pool
        self.config = config or AgentMemoryConfig()

    async def remember(
        self,
        agent_id: str,
        user_id: str,
        content: str,
        scope: MemoryScope = MemoryScope.USER,
        session_id: Optional[str] = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        expires_in_days: Optional[int] = None,
    ) -> AgentMemory:
        """
        Store a new agent memory.

        Args:
            agent_id: Agent identifier
            user_id: User identifier
            content: Memory content
            scope: Memory scope (session, user, agent, global)
            session_id: Session identifier (for session scope)
            priority: Memory priority
            tags: Optional tags
            metadata: Optional metadata
            expires_in_days: Optional expiry in days

        Returns:
            Created AgentMemory
        """
        memory_id = str(uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(days=expires_in_days or self.config.default_expiry_days)

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO agent_memories (
                    id, agent_id, user_id, session_id,
                    scope, content, summary, priority,
                    tags, metadata, created_at, updated_at,
                    expires_at, access_count
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8,
                    $9, $10, $11, $12,
                    $13, $14
                )
                """,
                memory_id,
                agent_id,
                user_id,
                session_id,
                scope.value,
                content,
                None,
                priority.value,
                tags or [],
                json.dumps(metadata or {}),
                now,
                now,
                expires_at,
                0,
            )

        return AgentMemory(
            id=memory_id,
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id,
            scope=scope,
            content=content,
            priority=priority,
            tags=tags or [],
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )

    async def recall(
        self,
        agent_id: str,
        user_id: str,
        query: Optional[str] = None,
        scope: Optional[MemoryScope] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[AgentMemory]:
        """
        Recall memories for an agent/user.

        Args:
            agent_id: Agent identifier
            user_id: User identifier
            query: Optional search query
            scope: Optional scope filter
            session_id: Optional session filter
            limit: Maximum memories to return

        Returns:
            List of AgentMemory
        """
        conditions = ["agent_id = $1", "user_id = $2"]
        params = [agent_id, user_id]
        param_idx = 3

        if scope:
            conditions.append(f"scope = ${param_idx}")
            params.append(scope.value)
            param_idx += 1

        if session_id:
            conditions.append(f"session_id = ${param_idx}")
            params.append(session_id)
            param_idx += 1

        # Exclude expired memories
        conditions.append("(expires_at IS NULL OR expires_at > NOW())")

        where_clause = " AND ".join(conditions)
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT id, agent_id, user_id, session_id,
                       scope, content, summary, priority,
                       tags, metadata, created_at, updated_at,
                       expires_at, access_count, last_accessed_at
                FROM agent_memories
                WHERE {where_clause}
                ORDER BY
                    CASE priority
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    created_at DESC
                LIMIT ${param_idx}
                """,
                *params,
            )

        memories = []
        for row in rows:
            memory = AgentMemory(
                id=row["id"],
                agent_id=row["agent_id"],
                user_id=row["user_id"],
                session_id=row["session_id"],
                scope=MemoryScope(row["scope"]),
                content=row["content"],
                summary=row["summary"],
                priority=MemoryPriority(row["priority"]),
                tags=row["tags"] or [],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                expires_at=row["expires_at"],
                access_count=row["access_count"],
                last_accessed_at=row["last_accessed_at"],
            )
            memories.append(memory)

            # Update access count
            await conn.execute(
                """
                UPDATE agent_memories
                SET access_count = access_count + 1,
                    last_accessed_at = NOW()
                WHERE id = $1
                """,
                row["id"],
            )

        return memories

    async def forget(
        self,
        memory_id: str,
        user_id: str,
    ) -> bool:
        """Delete a memory."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM agent_memories WHERE id = $1 AND user_id = $2",
                memory_id,
                user_id,
            )
        return result == "DELETE 1"

    async def compress_memories(
        self,
        agent_id: str,
        user_id: str,
    ) -> int:
        """
        Compress old, low-priority memories.

        Returns number of memories compressed.
        """
        if not self.config.enable_compression:
            return 0

        # Get old, low-priority memories
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, content, created_at
                FROM agent_memories
                WHERE agent_id = $1
                  AND user_id = $2
                  AND priority = 'low'
                  AND created_at < NOW() - INTERVAL '30 days'
                ORDER BY created_at ASC
                LIMIT $3
                """,
                agent_id,
                user_id,
                self.config.compression_threshold,
            )

        if len(rows) < 10:  # Don't compress small sets
            return 0

        # Create compressed summary
        contents = [row["content"] for row in rows]
        summary = f"Compressed {len(contents)} old memories: " + "; ".join(contents[:5])

        # Delete originals and create compressed version
        ids = [row["id"] for row in rows]
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM agent_memories WHERE id = ANY($1::text[])",
                ids,
            )

            await self.remember(
                agent_id=agent_id,
                user_id=user_id,
                content=summary,
                scope=MemoryScope.USER,
                priority=MemoryPriority.LOW,
                tags=["compressed"],
                metadata={"compressed_count": len(ids)},
            )

        return len(rows)

    async def get_stats(
        self,
        agent_id: str,
        user_id: str,
    ) -> dict:
        """Get memory statistics for an agent/user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE scope = 'session') as session_count,
                    COUNT(*) FILTER (WHERE scope = 'user') as user_count,
                    COUNT(*) FILTER (WHERE scope = 'agent') as agent_count,
                    COUNT(*) FILTER (WHERE scope = 'global') as global_count,
                    COUNT(*) FILTER (WHERE priority = 'critical') as critical_count,
                    COUNT(*) FILTER (WHERE priority = 'high') as high_count,
                    COUNT(*) FILTER (WHERE priority = 'medium') as medium_count,
                    COUNT(*) FILTER (WHERE priority = 'low') as low_count,
                    AVG(access_count) as avg_access,
                    MAX(created_at) as newest,
                    MIN(created_at) as oldest
                FROM agent_memories
                WHERE agent_id = $1 AND user_id = $2
                """,
                agent_id,
                user_id,
            )

        return {
            "total": row["total"],
            "by_scope": {
                "session": row["session_count"],
                "user": row["user_count"],
                "agent": row["agent_count"],
                "global": row["global_count"],
            },
            "by_priority": {
                "critical": row["critical_count"],
                "high": row["high_count"],
                "medium": row["medium_count"],
                "low": row["low_count"],
            },
            "avg_access_count": float(row["avg_access"] or 0),
            "newest": row["newest"].isoformat() if row["newest"] else None,
            "oldest": row["oldest"].isoformat() if row["oldest"] else None,
        }
