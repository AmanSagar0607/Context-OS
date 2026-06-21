"""
HNSW Index Migration — Upgrade pgvector indexes for >1M rows.

Replaces IVFFlat indexes with HNSW for better query performance at scale.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# HNSW index SQL migrations
HNSW_MIGRATIONS = [
    # Drop existing IVFFlat indexes
    """
    DROP INDEX IF EXISTS idx_memories_embedding;
    """,
    """
    DROP INDEX IF EXISTS idx_kg_entities_embedding;
    """,
    
    # Create HNSW index for memories
    """
    CREATE INDEX IF NOT EXISTS idx_memories_embedding_hnsw
    ON memories
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    """,
    
    # Create HNSW index for knowledge graph entities
    """
    CREATE INDEX IF NOT EXISTS idx_kg_entities_embedding_hnsw
    ON kg_entities
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    """,
    
    # Create HNSW index for documents (if table exists)
    """
    DO $$ BEGIN
        CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    EXCEPTION
        WHEN undefined_table THEN null;
    END $$;
    """,
    
    # Optimize query settings
    """
    ALTER SYSTEM SET hnsw.ef_search = 64;
    """,
]


# Alternative: IVFFlat for smaller datasets (<100K rows)
IVFFLAT_MIGRATIONS = [
    """
    DROP INDEX IF EXISTS idx_memories_embedding_hnsw;
    """,
    """
    DROP INDEX IF EXISTS idx_memories_embedding;
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_memories_embedding
    ON memories
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    """,
]


class HNSWMigration:
    """HNSW index migration service."""

    def __init__(self, pool):
        self.pool = pool

    async def migrate_to_hnsw(self) -> dict:
        """
        Migrate from IVFFlat to HNSW indexes.

        Returns:
            Dict with migration status
        """
        results = {
            "indexes_created": 0,
            "indexes_dropped": 0,
            "errors": [],
        }

        async with self.pool.acquire() as conn:
            for migration in HNSW_MIGRATIONS:
                try:
                    # Skip system ALTER
                    if migration.strip().startswith("ALTER SYSTEM"):
                        logger.info("Skipping ALTER SYSTEM (requires superuser)")
                        continue

                    await conn.execute(migration)
                    results["indexes_created"] += 1
                    logger.info(f"Migration executed: {migration[:50]}...")
                except Exception as e:
                    results["errors"].append(str(e))
                    logger.error(f"Migration failed: {e}")

        return results

    async def migrate_to_ivfflat(self) -> dict:
        """
        Migrate back to IVFFlat (for smaller datasets).

        Returns:
            Dict with migration status
        """
        results = {
            "indexes_created": 0,
            "indexes_dropped": 0,
            "errors": [],
        }

        async with self.pool.acquire() as conn:
            for migration in IVFFLAT_MIGRATIONS:
                try:
                    await conn.execute(migration)
                    results["indexes_created"] += 1
                except Exception as e:
                    results["errors"].append(str(e))
                    logger.error(f"Migration failed: {e}")

        return results

    async def get_index_info(self) -> list[dict]:
        """Get information about current vector indexes."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE indexdef LIKE '%vector%'
                ORDER BY tablename, indexname;
                """
            )

        return [
            {
                "schema": row["schemaname"],
                "table": row["tablename"],
                "index": row["indexname"],
                "definition": row["indexdef"],
            }
            for row in rows
        ]

    async def get_index_size(self) -> list[dict]:
        """Get size of vector indexes."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    indexname,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
                FROM pg_indexes
                WHERE indexdef LIKE '%vector%'
                ORDER BY pg_relation_size(indexname::regclass) DESC;
                """
            )

        return [
            {"index": row["indexname"], "size": row["size"]}
            for row in rows
        ]


# Performance comparison data
PERFORMANCE_COMPARISON = {
    "ivfflat": {
        "build_time": "Fast",
        "query_time_10k": "~5ms",
        "query_time_100k": "~10ms",
        "query_time_1m": "~50ms",
        "query_time_10m": "~200ms",
        "index_size": "Smaller",
        "best_for": "<100K rows",
    },
    "hnsw": {
        "build_time": "Slower",
        "query_time_10k": "~1ms",
        "query_time_100k": "~2ms",
        "query_time_1m": "~5ms",
        "query_time_10m": "~10ms",
        "index_size": "Larger",
        "best_for": ">100K rows",
    },
}
