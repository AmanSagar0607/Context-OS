# services/knowledge_graph.py
"""
Knowledge Graph Service — Entity and relationship storage in Postgres.

Manages:
- Entity CRUD (Person, Company, Product, Technology, Project, Repository, Website, Document, API, Organization)
- Relationship CRUD (created_by, owned_by, depends_on, integrates_with, references, related_to, competitor_of, mentioned_in)
- Entity deduplication and merging
- Graph queries (neighbors, paths, clusters)
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import psycopg
from psycopg.rows import dict_row

from .postgres_store import _connect
from app.config import get_settings

logger = logging.getLogger(__name__)

# Entity types
ENTITY_TYPES = [
    "person", "company", "product", "technology", "project",
    "repository", "website", "document", "api", "organization",
]

# Relationship types
RELATIONSHIP_TYPES = [
    "created_by", "owned_by", "depends_on", "integrates_with",
    "references", "related_to", "competitor_of", "mentioned_in",
]


def init_knowledge_schema():
    """Create knowledge graph tables if they don't exist."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            # Create enum types first
            entity_enum = ", ".join(f"'{e}'" for e in ENTITY_TYPES)
            rel_enum = ", ".join(f"'{r}'" for r in RELATIONSHIP_TYPES)
            
            cur.execute(f"""
                DO $$ BEGIN
                    CREATE TYPE entity_type_enum AS ENUM ({entity_enum});
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """)
            
            cur.execute(f"""
                DO $$ BEGIN
                    CREATE TYPE relationship_type_enum AS ENUM ({rel_enum});
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kg_entities (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    properties JSONB DEFAULT '{}',
                    source_user_id UUID,
                    source_type TEXT,
                    source_ref TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (entity_type, name)
                );
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kg_relationships (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    source_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
                    target_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
                    relationship_type TEXT NOT NULL,
                    properties JSONB DEFAULT '{}',
                    confidence FLOAT DEFAULT 1.0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (source_entity_id, target_entity_id, relationship_type)
                );
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_kg_entities_type ON kg_entities(entity_type);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_kg_entities_name ON kg_entities USING gin(to_tsvector('english', name));
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_kg_rel_source ON kg_relationships(source_entity_id);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_kg_rel_target ON kg_relationships(target_entity_id);
            """)
            
            conn.commit()
            logger.info("Knowledge graph schema initialized")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to init knowledge graph schema: {e}")
    finally:
        conn.close()


def upsert_entity(
    entity_type: str,
    name: str,
    properties: dict | None = None,
    source_user_id: str | None = None,
    source_type: str | None = None,
    source_ref: str | None = None,
) -> str:
    """Insert or update an entity. Returns entity ID."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO kg_entities (entity_type, name, properties, source_user_id, source_type, source_ref)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (entity_type, name) DO UPDATE SET
                    properties = kg_entities.properties || EXCLUDED.properties,
                    updated_at = now()
                RETURNING id;
            """, (
                entity_type, name,
                json.dumps(properties or {}),
                source_user_id, source_type, source_ref,
            ))
            row = cur.fetchone()
            conn.commit()
            return str(row["id"])
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to upsert entity: {e}")
        raise
    finally:
        conn.close()


def upsert_relationship(
    source_entity_id: str,
    target_entity_id: str,
    relationship_type: str,
    properties: dict | None = None,
    confidence: float = 1.0,
) -> str:
    """Insert or update a relationship. Returns relationship ID."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO kg_relationships (source_entity_id, target_entity_id, relationship_type, properties, confidence)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_entity_id, target_entity_id, relationship_type) DO UPDATE SET
                    properties = kg_relationships.properties || EXCLUDED.properties,
                    confidence = GREATEST(kg_relationships.confidence, EXCLUDED.confidence)
                RETURNING id;
            """, (
                source_entity_id, target_entity_id,
                relationship_type,
                json.dumps(properties or {}),
                confidence,
            ))
            row = cur.fetchone()
            conn.commit()
            return str(row["id"])
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to upsert relationship: {e}")
        raise
    finally:
        conn.close()


def search_entities(
    query: str,
    entity_type: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search entities by name."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            if entity_type:
                cur.execute("""
                    SELECT id, entity_type, name, properties, created_at
                    FROM kg_entities
                    WHERE entity_type = %s
                      AND to_tsvector('english', name) @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(to_tsvector('english', name), plainto_tsquery('english', %s)) DESC
                    LIMIT %s;
                """, (entity_type, query, query, limit))
            else:
                cur.execute("""
                    SELECT id, entity_type, name, properties, created_at
                    FROM kg_entities
                    WHERE to_tsvector('english', name) @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(to_tsvector('english', name), plainto_tsquery('english', %s)) DESC
                    LIMIT %s;
                """, (query, query, limit))
            
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Failed to search entities: {e}")
        return []
    finally:
        conn.close()


def get_entity(entity_id: str) -> dict | None:
    """Get entity by ID."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, entity_type, name, properties, source_user_id, source_type, source_ref, created_at, updated_at
                FROM kg_entities WHERE id = %s;
            """, (entity_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get entity: {e}")
        return None
    finally:
        conn.close()


def get_entity_neighbors(
    entity_id: str,
    direction: str = "both",
    relationship_type: str | None = None,
    limit: int = 50,
) -> dict:
    """Get neighboring entities in the knowledge graph."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            neighbors = {"outgoing": [], "incoming": []}
            
            # Outgoing relationships
            if direction in ("outgoing", "both"):
                query = """
                    SELECT r.id as rel_id, r.relationship_type, r.confidence, r.properties as rel_props,
                           e.id, e.entity_type, e.name, e.properties
                    FROM kg_relationships r
                    JOIN kg_entities e ON e.id = r.target_entity_id
                    WHERE r.source_entity_id = %s
                """
                params = [entity_id]
                if relationship_type:
                    query += " AND r.relationship_type = %s"
                    params.append(relationship_type)
                query += " ORDER BY r.confidence DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                neighbors["outgoing"] = [dict(r) for r in cur.fetchall()]
            
            # Incoming relationships
            if direction in ("incoming", "both"):
                query = """
                    SELECT r.id as rel_id, r.relationship_type, r.confidence, r.properties as rel_props,
                           e.id, e.entity_type, e.name, e.properties
                    FROM kg_relationships r
                    JOIN kg_entities e ON e.id = r.source_entity_id
                    WHERE r.target_entity_id = %s
                """
                params = [entity_id]
                if relationship_type:
                    query += " AND r.relationship_type = %s"
                    params.append(relationship_type)
                query += " ORDER BY r.confidence DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                neighbors["incoming"] = [dict(r) for r in cur.fetchall()]
            
            return neighbors
    except Exception as e:
        logger.error(f"Failed to get neighbors: {e}")
        return {"outgoing": [], "incoming": []}
    finally:
        conn.close()


def get_stats() -> dict:
    """Get knowledge graph statistics."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) as count FROM kg_entities;")
            entity_count = cur.fetchone()["count"]
            
            cur.execute("SELECT COUNT(*) as count FROM kg_relationships;")
            rel_count = cur.fetchone()["count"]
            
            cur.execute("""
                SELECT entity_type, COUNT(*) as count
                FROM kg_entities
                GROUP BY entity_type
                ORDER BY count DESC;
            """)
            by_type = {r["entity_type"]: r["count"] for r in cur.fetchall()}
            
            cur.execute("""
                SELECT relationship_type, COUNT(*) as count
                FROM kg_relationships
                GROUP BY relationship_type
                ORDER BY count DESC;
            """)
            by_rel = {r["relationship_type"]: r["count"] for r in cur.fetchall()}
            
            return {
                "total_entities": entity_count,
                "total_relationships": rel_count,
                "entities_by_type": by_type,
                "relationships_by_type": by_rel,
            }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"total_entities": 0, "total_relationships": 0}
    finally:
        conn.close()


def store_extraction(
    entities: list[dict],
    relationships: list[dict],
    user_id: str | None = None,
) -> dict:
    """Store extracted entities and relationships."""
    entity_ids = {}
    stored_entities = 0
    stored_relationships = 0
    
    # Upsert entities first
    for ent in entities:
        etype = ent.get("type", "unknown").lower()
        name = ent.get("name", "").strip()
        if not name or etype not in ENTITY_TYPES:
            continue
        
        props = ent.get("properties", {})
        eid = upsert_entity(
            entity_type=etype,
            name=name,
            properties=props,
            source_user_id=user_id,
            source_type="extraction",
        )
        entity_ids[name.lower()] = eid
        stored_entities += 1
    
    # Upsert relationships
    for rel in relationships:
        src_name = rel.get("source", "").lower()
        tgt_name = rel.get("target", "").lower()
        rel_type = rel.get("type", "related_to").lower()
        
        src_id = entity_ids.get(src_name)
        tgt_id = entity_ids.get(tgt_name)
        
        if not src_id or not tgt_id or rel_type not in RELATIONSHIP_TYPES:
            continue
        
        props = rel.get("properties", {})
        upsert_relationship(
            source_entity_id=src_id,
            target_entity_id=tgt_id,
            relationship_type=rel_type,
            properties=props,
        )
        stored_relationships += 1
    
    return {
        "entities_stored": stored_entities,
        "relationships_stored": stored_relationships,
    }
