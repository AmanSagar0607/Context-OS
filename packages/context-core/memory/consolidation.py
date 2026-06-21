"""
Memory Consolidation — Merge old, low-importance memories.

Periodically consolidates memories to reduce noise and improve retrieval quality.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import asyncpg
import httpx

from embeddings.service import EmbeddingService
from memory.models import Memory, MemoryType, ImportanceLevel

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class ConsolidationConfig:
    """Configuration for memory consolidation."""
    # Age threshold: memories older than this are candidates
    max_age_days: int = 30

    # Importance threshold: memories at or below this are candidates
    max_importance: ImportanceLevel = ImportanceLevel.LOW

    # Minimum similarity to merge (0.0-1.0)
    min_similarity: float = 0.7

    # Maximum memories to merge at once
    batch_size: int = 10

    # Minimum memories required for consolidation
    min_memories_for_merge: int = 2

    # Whether to delete originals after merge
    delete_originals: bool = True

    enabled: bool = True


@dataclass
class ConsolidationResult:
    """Result of a consolidation run."""
    groups_found: int = 0
    memories_merged: int = 0
    memories_deleted: int = 0
    summaries_created: int = 0
    errors: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0


# System prompt for generating summaries
SUMMARY_PROMPT = """You are a memory consolidation assistant. Given a group of related memories, create a concise summary that captures the key information.

Rules:
1. Preserve all important facts and preferences
2. Remove redundant information
3. Keep the summary under 200 words
4. Use bullet points for multiple items
5. Maintain the original intent and meaning

Memories to consolidate:
{memories}

Provide a JSON response:
{{
  "summary": "<consolidated summary>",
  "key_facts": ["<fact1>", "<fact2>"],
  "importance": "<low|medium|high>",
  "tags": ["<tag1>", "<tag2>"]
}}"""


class MemoryConsolidation:
    """Memory consolidation service."""

    def __init__(
        self,
        pool: asyncpg.Pool,
        embeddings: EmbeddingService,
        config: Optional[ConsolidationConfig] = None,
    ):
        self.pool = pool
        self.embeddings = embeddings
        self.config = config or ConsolidationConfig()

    async def find_merge_candidates(
        self, user_id: str
    ) -> list[list[Memory]]:
        """
        Find groups of memories that should be consolidated.

        Returns groups of similar, old, low-importance memories.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.max_age_days)

        async with self.pool.acquire() as conn:
            # Find old, low-importance memories with embeddings
            rows = await conn.fetch(
                """
                SELECT id, user_id, agent_id, session_id,
                       content, summary, memory_type, importance,
                       tags, source, metadata,
                       created_at, updated_at, accessed_at, expires_at,
                       parent_id, embedding
                FROM memories
                WHERE user_id = $1
                  AND created_at < $2
                  AND importance <= $3
                  AND embedding IS NOT NULL
                  AND parent_id IS NULL
                ORDER BY created_at ASC
                LIMIT $4
                """,
                user_id,
                cutoff_date,
                self.config.max_importance.value,
                self.config.batch_size * 5,  # Fetch more to find clusters
            )

        if not rows:
            return []

        # Convert to Memory objects
        memories = []
        for row in rows:
            memories.append(Memory(
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
            ))

        # Group by similarity using embeddings
        groups = self._cluster_by_similarity(memories)

        # Filter groups that are too small
        return [
            group for group in groups
            if len(group) >= self.config.min_memories_for_merge
        ]

    def _cluster_by_similarity(self, memories: list[Memory]) -> list[list[Memory]]:
        """Simple clustering by embedding similarity."""
        if not memories:
            return []

        # Use the memory service to find similar memories
        # For now, use a simple approach: group by content similarity
        groups = []
        used = set()

        for i, mem_i in enumerate(memories):
            if i in used:
                continue

            group = [mem_i]
            used.add(i)

            for j, mem_j in enumerate(memories):
                if j in used:
                    continue

                # Simple content similarity (could use embeddings for better results)
                similarity = self._content_similarity(mem_i.content, mem_j.content)
                if similarity >= self.config.min_similarity:
                    group.append(mem_j)
                    used.add(j)

            groups.append(group)

        return groups

    def _content_similarity(self, text1: str, text2: str) -> float:
        """Simple content similarity based on word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    async def consolidate_group(
        self,
        memories: list[Memory],
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[Memory]:
        """
        Consolidate a group of memories into a single summary.

        Args:
            memories: Group of similar memories to merge
            api_key: LLM API key for summarization
            model: LLM model for summarization

        Returns:
            New consolidated memory, or None if summarization fails
        """
        if len(memories) < self.config.min_memories_for_merge:
            return None

        # Format memories for summarization
        memories_text = "\n\n".join(
            f"[{i+1}] (importance: {m.importance.value}) {m.content}"
            for i, m in enumerate(memories)
        )

        # Try LLM summarization if API key provided
        if api_key and model:
            summary_result = await self._llm_summarize(memories_text, api_key, model)
            if summary_result:
                return await self._create_consolidated_memory(
                    memories, summary_result
                )

        # Fallback: simple concatenation
        return await self._simple_consolidate(memories)

    async def _llm_summarize(
        self, memories_text: str, api_key: str, model: str
    ) -> Optional[dict]:
        """Use LLM to generate a summary."""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "ContextOS Consolidation",
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a memory consolidation assistant."},
                    {"role": "user", "content": SUMMARY_PROMPT.format(memories=memories_text)},
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

                if response.status_code != 200:
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                return json.loads(content)

        except Exception as e:
            logger.warning(f"LLM summarization failed: {e}")
            return None

    async def _create_consolidated_memory(
        self,
        original_memories: list[Memory],
        summary_result: dict,
    ) -> Memory:
        """Create a new consolidated memory from summary."""
        user_id = original_memories[0].user_id
        now = datetime.utcnow()

        # Combine tags
        all_tags = list(set(
            tag for mem in original_memories for tag in mem.tags
        ))
        extra_tags = summary_result.get("tags", [])
        all_tags = list(set(all_tags + extra_tags))

        # Determine importance
        importance_str = summary_result.get("importance", "medium")
        importance_map = {
            "low": ImportanceLevel.LOW,
            "medium": ImportanceLevel.MEDIUM,
            "high": ImportanceLevel.HIGH,
        }
        importance = importance_map.get(importance_str, ImportanceLevel.MEDIUM)

        # Generate embedding for consolidated content
        summary_text = summary_result.get("summary", "")
        embedding_result = self.embeddings.embed_texts([summary_text])
        embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None
        embedding_str = f"[{','.join(str(x) for x in embedding)}]" if embedding else None

        memory_id = uuid4()

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
                    $1, $2, 'consolidation', 'system',
                    $3, $4, 'preference', $5,
                    $6, 'consolidation', $7,
                    $8::vector, $9, $10,
                    $11
                )
                """,
                memory_id,
                user_id,
                summary_text,
                json.dumps(summary_result.get("key_facts", [])),
                importance.value,
                all_tags,
                json.dumps({"consolidated_from": [str(m.id) for m in original_memories]}),
                embedding_str,
                now,
                now,
                str(original_memories[0].id),
            )

        return Memory(
            id=memory_id,
            user_id=user_id,
            agent_id="consolidation",
            session_id="system",
            content=summary_text,
            summary=json.dumps(summary_result.get("key_facts", [])),
            memory_type=MemoryType.PREFERENCE,
            importance=importance,
            tags=all_tags,
            source="consolidation",
            metadata={"consolidated_from": [str(m.id) for m in original_memories]},
            created_at=now,
            updated_at=now,
            parent_id=original_memories[0].id,
        )

    async def _simple_consolidate(self, memories: list[Memory]) -> Memory:
        """Simple concatenation fallback."""
        user_id = memories[0].user_id
        now = datetime.utcnow()

        # Combine content
        combined_content = "\n\n".join(m.content for m in memories)

        # Combine tags
        all_tags = list(set(tag for mem in memories for tag in mem.tags))

        # Generate embedding
        embedding_result = self.embeddings.embed_texts([combined_content])
        embedding = embedding_result["vectors"][0] if embedding_result["vectors"] else None
        embedding_str = f"[{','.join(str(x) for x in embedding)}]" if embedding else None

        memory_id = uuid4()

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
                    $1, $2, 'consolidation', 'system',
                    $3, $4, 'preference', $5,
                    $6, 'consolidation', $7,
                    $8::vector, $9, $10,
                    $11
                )
                """,
                memory_id,
                user_id,
                combined_content,
                None,
                ImportanceLevel.MEDIUM.value,
                all_tags,
                json.dumps({"consolidated_from": [str(m.id) for m in memories]}),
                embedding_str,
                now,
                now,
                str(memories[0].id),
            )

        return Memory(
            id=memory_id,
            user_id=user_id,
            agent_id="consolidation",
            session_id="system",
            content=combined_content,
            summary=None,
            memory_type=MemoryType.PREFERENCE,
            importance=ImportanceLevel.MEDIUM,
            tags=all_tags,
            source="consolidation",
            metadata={"consolidated_from": [str(m.id) for m in memories]},
            created_at=now,
            updated_at=now,
            parent_id=memories[0].id,
        )

    async def delete_originals(self, memories: list[Memory]) -> int:
        """Delete original memories after consolidation."""
        if not self.config.delete_originals:
            return 0

        ids = [m.id for m in memories]
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM memories WHERE id = ANY($1::uuid[])",
                ids,
            )

        # Parse "DELETE N"
        try:
            return int(result.split()[-1])
        except (ValueError, IndexError):
            return 0

    async def run_consolidation(
        self,
        user_id: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ConsolidationResult:
        """
        Run a full consolidation cycle for a user.

        Args:
            user_id: User ID to consolidate memories for
            api_key: Optional LLM API key for summarization
            model: Optional LLM model for summarization

        Returns:
            ConsolidationResult with statistics
        """
        import time
        start = time.time()

        result = ConsolidationResult()

        if not self.config.enabled:
            return result

        try:
            # Find merge candidates
            groups = await self.find_merge_candidates(user_id)
            result.groups_found = len(groups)

            for group in groups:
                try:
                    # Consolidate the group
                    consolidated = await self.consolidate_group(group, api_key, model)

                    if consolidated:
                        result.summaries_created += 1
                        result.memories_merged += len(group)

                        # Delete originals
                        deleted = await self.delete_originals(group)
                        result.memories_deleted += deleted

                except Exception as e:
                    result.errors.append(f"Failed to consolidate group: {e}")
                    logger.error(f"Consolidation error: {e}")

        except Exception as e:
            result.errors.append(f"Failed to find merge candidates: {e}")
            logger.error(f"Consolidation error: {e}")

        result.elapsed_ms = (time.time() - start) * 1000
        return result
