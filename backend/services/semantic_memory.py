# services/semantic_memory.py
"""
Semantic Memory — Vector-based memory search using sentence-transformers.

Extends the SQLite memory store with embedding generation and cosine similarity search.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded model
_model = None
_model_name = "all-MiniLM-L6-v2"


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(_model_name)
            logger.info(f"Loaded embedding model: {_model_name}")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
            return None
    return _model


def _db_path(settings) -> Path:
    return Path(settings.memory_db_path)


def _connect(settings) -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(settings))
    conn.row_factory = sqlite3.Row
    return conn


def init_semantic_memory(settings) -> None:
    """Initialize the semantic memory tables."""
    path = _db_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                memory_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, memory_type, memory_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_user
            ON memory_embeddings (user_id, memory_type)
            """
        )
        conn.commit()
    logger.info("Semantic memory tables initialized")


def generate_embedding(text: str) -> list[float] | None:
    """Generate an embedding vector for the given text."""
    model = _get_model()
    if model is None:
        return None

    try:
        # Clean and truncate text
        cleaned = re.sub(r'\s+', ' ', text.strip())[:1000]
        if not cleaned:
            return None

        embedding = model.encode(cleaned, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def store_memory_embedding(
    settings,
    *,
    user_id: str,
    memory_type: str,
    memory_id: int,
    content: str,
) -> bool:
    """Store an embedding for a memory."""
    embedding = generate_embedding(content)
    if embedding is None:
        return False

    timestamp = datetime.now(UTC).isoformat()
    embedding_blob = json.dumps(embedding)

    with _connect(settings) as conn:
        conn.execute(
            """
            INSERT INTO memory_embeddings (user_id, memory_type, memory_id, content, embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, memory_type, memory_id)
            DO UPDATE SET
                content = excluded.content,
                embedding = excluded.embedding,
                created_at = excluded.created_at
            """,
            (user_id, memory_type, memory_id, content, embedding_blob, timestamp),
        )
        conn.commit()
    return True


def search_memories_semantic(
    settings,
    *,
    user_id: str,
    query: str,
    memory_type: str | None = None,
    limit: int = 5,
    min_score: float = 0.3,
) -> list[dict]:
    """Search memories using semantic similarity."""
    query_embedding = generate_embedding(query)
    if query_embedding is None:
        # Fallback to keyword search
        return _keyword_search(settings, user_id=user_id, query=query, memory_type=memory_type, limit=limit)

    query_vec = np.array(query_embedding, dtype=np.float32)

    with _connect(settings) as conn:
        if memory_type:
            rows = conn.execute(
                "SELECT id, memory_type, memory_id, content, embedding, created_at FROM memory_embeddings WHERE user_id = ? AND memory_type = ?",
                (user_id, memory_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, memory_type, memory_id, content, embedding, created_at FROM memory_embeddings WHERE user_id = ?",
                (user_id,),
            ).fetchall()

    results = []
    for row in rows:
        try:
            mem_vec = np.array(json.loads(row["embedding"]), dtype=np.float32)
            # Cosine similarity (embeddings are already normalized)
            score = float(np.dot(query_vec, mem_vec))
            if score >= min_score:
                results.append({
                    "id": row["id"],
                    "memory_type": row["memory_type"],
                    "memory_id": row["memory_id"],
                    "content": row["content"],
                    "score": round(score, 4),
                    "created_at": row["created_at"],
                })
        except Exception:
            continue

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def _keyword_search(
    settings,
    *,
    user_id: str,
    query: str,
    memory_type: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Fallback keyword search when embeddings are unavailable."""
    keywords = query.lower().split()

    with _connect(settings) as conn:
        if memory_type:
            rows = conn.execute(
                "SELECT id, memory_type, memory_id, content, created_at FROM memory_embeddings WHERE user_id = ? AND memory_type = ?",
                (user_id, memory_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, memory_type, memory_id, content, created_at FROM memory_embeddings WHERE user_id = ?",
                (user_id,),
            ).fetchall()

    results = []
    for row in rows:
        content_lower = row["content"].lower()
        score = sum(1 for kw in keywords if kw in content_lower) / max(len(keywords), 1)
        if score > 0:
            results.append({
                "id": row["id"],
                "memory_type": row["memory_type"],
                "memory_id": row["memory_id"],
                "content": row["content"],
                "score": round(score, 4),
                "created_at": row["created_at"],
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def sync_embeddings_from_memories(settings, user_id: str) -> int:
    """Sync embeddings from existing profile memories. Returns count of embedded memories."""
    count = 0
    with _connect(settings) as conn:
        # Get memories without embeddings
        rows = conn.execute(
            """
            SELECT pm.id, pm.memory_key, pm.content
            FROM profile_memories pm
            LEFT JOIN memory_embeddings me ON me.user_id = pm.user_id AND me.memory_type = 'profile' AND me.memory_id = pm.id
            WHERE pm.user_id = ? AND me.id IS NULL
            """,
            (user_id,),
        ).fetchall()

        for row in rows:
            content = f"{row['memory_key']}: {row['content']}"
            if store_memory_embedding(
                settings,
                user_id=user_id,
                memory_type="profile",
                memory_id=row["id"],
                content=content,
            ):
                count += 1

    return count
