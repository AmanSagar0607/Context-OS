"""
Context OS — Knowledge Service

Service layer for knowledge graph operations.
"""

from __future__ import annotations

import os
from typing import Optional

import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/app-agent",
)


class KnowledgeService:
    """Knowledge graph operations service."""

    def __init__(self):
        self.db_url = DATABASE_URL

    async def _get_conn(self):
        """Get database connection."""
        return await psycopg.AsyncConnection.connect(self.db_url)

    async def create_entity(
        self,
        name: str,
        entity_type: str = "concept",
        description: Optional[str] = None,
        properties: dict | None = None,
    ) -> dict:
        """Create a knowledge graph entity."""
        import uuid
        from datetime import datetime, timezone

        entity_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO kg_entities (id, name, entity_type, description, properties, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (entity_id, name, entity_type, description, properties or {}, now),
                )
                await conn.commit()

        return {
            "id": entity_id,
            "name": name,
            "entity_type": entity_type,
            "description": description,
            "properties": properties or {},
            "created_at": now,
        }

    async def get_entity(self, entity_id: str) -> Optional[dict]:
        """Get an entity by ID."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT id, name, entity_type, description, properties, created_at FROM kg_entities WHERE id = %s",
                    (entity_id,),
                )
                row = await cur.fetchone()
                if row is None:
                    return None
                return {
                    "id": row[0],
                    "name": row[1],
                    "entity_type": row[2],
                    "description": row[3],
                    "properties": row[4] or {},
                    "created_at": str(row[5]) if row[5] else None,
                }

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM kg_entities WHERE id = %s", (entity_id,))
                deleted = cur.rowcount > 0
                await conn.commit()
                return deleted

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "related_to",
        weight: float = 1.0,
        properties: dict | None = None,
    ) -> dict:
        """Create a relationship between entities."""
        import uuid
        from datetime import datetime, timezone

        rel_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO kg_relationships (id, source_id, target_id, relationship_type, weight, properties, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (rel_id, source_id, target_id, relationship_type, weight, properties or {}, now),
                )
                await conn.commit()

        return {
            "id": rel_id,
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "weight": weight,
            "properties": properties or {},
            "created_at": now,
        }

    async def get_graph(
        self,
        entity_id: str,
        depth: int = 2,
    ) -> dict:
        """Get entity graph."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                # Get the entity
                await cur.execute(
                    "SELECT id, name, entity_type, description, properties FROM kg_entities WHERE id = %s",
                    (entity_id,),
                )
                entity_row = await cur.fetchone()
                if entity_row is None:
                    return {"nodes": [], "edges": []}

                # Get relationships
                await cur.execute(
                    """
                    SELECT r.id, r.source_id, r.target_id, r.relationship_type, r.weight,
                           s.name as source_name, t.name as target_name
                    FROM kg_relationships r
                    JOIN kg_entities s ON r.source_id = s.id
                    JOIN kg_entities t ON r.target_id = t.id
                    WHERE r.source_id = %s OR r.target_id = %s
                    LIMIT %s
                    """,
                    (entity_id, entity_id, 100 * depth),
                )
                rel_rows = await cur.fetchall()

                nodes = [
                    {
                        "id": entity_row[0],
                        "name": entity_row[1],
                        "entity_type": entity_row[2],
                        "description": entity_row[3],
                        "properties": entity_row[4] or {},
                    }
                ]
                edges = []
                node_ids = {entity_row[0]}

                for r in rel_rows:
                    edges.append({
                        "id": r[0],
                        "source_id": r[1],
                        "target_id": r[2],
                        "relationship_type": r[3],
                        "weight": r[4],
                    })
                    for nid in [r[1], r[2]]:
                        if nid not in node_ids:
                            node_ids.add(nid)
                            await cur.execute(
                                "SELECT id, name, entity_type, description, properties FROM kg_entities WHERE id = %s",
                                (nid,),
                            )
                            nrow = await cur.fetchone()
                            if nrow:
                                nodes.append({
                                    "id": nrow[0],
                                    "name": nrow[1],
                                    "entity_type": nrow[2],
                                    "description": nrow[3],
                                    "properties": nrow[4] or {},
                                })

                return {"nodes": nodes, "edges": edges}

    async def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Search entities."""
        async with await self._get_conn() as conn:
            async with conn.cursor() as cur:
                sql = "SELECT id, name, entity_type, description, properties, created_at FROM kg_entities WHERE name ILIKE %s OR description ILIKE %s"
                params = [f"%{query}%", f"%{query}%"]

                if entity_type:
                    sql += " AND entity_type = %s"
                    params.append(entity_type)

                sql += " ORDER BY created_at DESC LIMIT %s"
                params.append(top_k)

                await cur.execute(sql, params)
                rows = await cur.fetchall()

                return [
                    {
                        "id": r[0],
                        "name": r[1],
                        "entity_type": r[2],
                        "description": r[3],
                        "properties": r[4] or {},
                        "created_at": str(r[5]) if r[5] else None,
                    }
                    for r in rows
                ]