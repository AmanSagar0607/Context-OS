"""
Multi-User Memory — Shared knowledge graph entities.

Enables sharing of entities and relationships across users
while maintaining user-specific context.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

logger = logging.getLogger(__name__)


class SharingLevel(str, Enum):
    PRIVATE = "private"      # Only owner can access
    SHARED = "shared"        # Shared with specific users
    TEAM = "team"            # Shared within team
    PUBLIC = "public"        # Visible to all users


class EntityOrigin(str, Enum):
    USER_CREATED = "user_created"
    SYSTEM_IMPORTED = "system_imported"
    SHARED_COPY = "shared_copy"


@dataclass
class SharedEntity:
    """A shared knowledge graph entity."""
    id: str
    entity_type: str
    name: str
    properties: dict = field(default_factory=dict)
    owner_user_id: str
    sharing_level: SharingLevel = SharingLevel.PRIVATE
    shared_with: list[str] = field(default_factory=list)
    team_id: Optional[str] = None
    origin: EntityOrigin = EntityOrigin.USER_CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SharedRelationship:
    """A shared knowledge graph relationship."""
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: dict = field(default_factory=dict)
    confidence: float = 1.0
    owner_user_id: str
    sharing_level: SharingLevel = SharingLevel.PRIVATE
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MultiUserConfig:
    """Configuration for multi-user memory."""
    default_sharing_level: SharingLevel = SharingLevel.PRIVATE
    allow_public_entities: bool = True
    allow_team_sharing: bool = True
    max_shares_per_entity: int = 100
    enable_entity_forking: bool = True


class MultiUserMemoryService:
    """Multi-user memory service for shared knowledge graph."""

    def __init__(self, pool: asyncpg.Pool, config: Optional[MultiUserConfig] = None):
        self.pool = pool
        self.config = config or MultiUserConfig()

    async def create_entity(
        self,
        user_id: str,
        entity_type: str,
        name: str,
        properties: Optional[dict] = None,
        sharing_level: SharingLevel = SharingLevel.PRIVATE,
        team_id: Optional[str] = None,
    ) -> SharedEntity:
        """
        Create a new entity with sharing capabilities.

        Args:
            user_id: Owner user ID
            entity_type: Entity type
            name: Entity name
            properties: Optional properties
            sharing_level: Sharing level
            team_id: Optional team ID for team sharing

        Returns:
            Created SharedEntity
        """
        entity_id = str(uuid4())
        now = datetime.utcnow()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO kg_entities (
                    id, entity_type, name, properties,
                    source_user_id, sharing_level, shared_with,
                    team_id, origin, created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7,
                    $8, $9, $10, $11
                )
                """,
                entity_id,
                entity_type,
                name,
                json.dumps(properties or {}),
                user_id,
                sharing_level.value,
                [],
                team_id,
                EntityOrigin.USER_CREATED.value,
                now,
                now,
            )

        return SharedEntity(
            id=entity_id,
            entity_type=entity_type,
            name=name,
            properties=properties or {},
            owner_user_id=user_id,
            sharing_level=sharing_level,
            team_id=team_id,
            origin=EntityOrigin.USER_CREATED,
            created_at=now,
            updated_at=now,
        )

    async def share_entity(
        self,
        entity_id: str,
        owner_user_id: str,
        share_with_user_id: str,
    ) -> bool:
        """
        Share an entity with another user.

        Args:
            entity_id: Entity to share
            owner_user_id: Owner of the entity
            share_with_user_id: User to share with

        Returns:
            True if successful
        """
        async with self.pool.acquire() as conn:
            # Check ownership
            row = await conn.fetchrow(
                "SELECT id, shared_with FROM kg_entities WHERE id = $1 AND source_user_id = $2",
                entity_id,
                owner_user_id,
            )

            if not row:
                return False

            # Check share limit
            current_shares = row["shared_with"] or []
            if len(current_shares) >= self.config.max_shares_per_entity:
                return False

            # Add to shared_with
            if share_with_user_id not in current_shares:
                current_shares.append(share_with_user_id)
                await conn.execute(
                    """
                    UPDATE kg_entities
                    SET shared_with = $1, updated_at = NOW()
                    WHERE id = $2
                    """,
                    current_shares,
                    entity_id,
                )

            return True

    async def unshare_entity(
        self,
        entity_id: str,
        owner_user_id: str,
        unshare_user_id: str,
    ) -> bool:
        """Remove sharing for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, shared_with FROM kg_entities WHERE id = $1 AND source_user_id = $2",
                entity_id,
                owner_user_id,
            )

            if not row:
                return False

            current_shares = row["shared_with"] or []
            if unshare_user_id in current_shares:
                current_shares.remove(unshare_user_id)
                await conn.execute(
                    """
                    UPDATE kg_entities
                    SET shared_with = $1, updated_at = NOW()
                    WHERE id = $2
                    """,
                    current_shares,
                    entity_id,
                )

            return True

    async def get_accessible_entities(
        self,
        user_id: str,
        entity_type: Optional[str] = None,
        team_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[SharedEntity]:
        """
        Get entities accessible to a user.

        Includes:
        - User's own entities
        - Entities shared with the user
        - Public entities
        - Team entities (if team_id provided)
        """
        conditions = []
        params = []
        param_idx = 1

        # User's own entities
        own_clause = f"source_user_id = ${param_idx}"
        params.append(user_id)
        param_idx += 1

        # Shared with user
        shared_clause = f"${param_idx} = ANY(shared_with)"
        params.append(user_id)
        param_idx += 1

        # Public entities
        public_clause = f"sharing_level = ${param_idx}"
        params.append(SharingLevel.PUBLIC.value)
        param_idx += 1

        # Combine conditions
        conditions.append(f"({own_clause} OR {shared_clause} OR {public_clause})")

        # Team entities
        if team_id and self.config.allow_team_sharing:
            conditions.append(f"(team_id = ${param_idx} OR sharing_level = 'public')")
            params.append(team_id)
            param_idx += 1

        # Entity type filter
        if entity_type:
            conditions.append(f"entity_type = ${param_idx}")
            params.append(entity_type)
            param_idx += 1

        where_clause = " AND ".join(conditions)
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT id, entity_type, name, properties,
                       source_user_id, sharing_level, shared_with,
                       team_id, origin, created_at, updated_at
                FROM kg_entities
                WHERE {where_clause}
                ORDER BY updated_at DESC
                LIMIT ${param_idx}
                """,
                *params,
            )

        return [
            SharedEntity(
                id=row["id"],
                entity_type=row["entity_type"],
                name=row["name"],
                properties=json.loads(row["properties"]) if row["properties"] else {},
                owner_user_id=row["source_user_id"],
                sharing_level=SharingLevel(row["sharing_level"]),
                shared_with=row["shared_with"] or [],
                team_id=row["team_id"],
                origin=EntityOrigin(row["origin"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    async def fork_entity(
        self,
        entity_id: str,
        new_user_id: str,
        new_name: Optional[str] = None,
    ) -> Optional[SharedEntity]:
        """
        Fork an entity (create a copy under new ownership).

        Args:
            entity_id: Entity to fork
            new_user_id: User creating the fork
            new_name: Optional new name

        Returns:
            Forked entity or None
        """
        if not self.config.enable_entity_forking:
            return None

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, entity_type, name, properties
                FROM kg_entities
                WHERE id = $1
                """,
                entity_id,
            )

            if not row:
                return None

            # Create fork
            fork = await self.create_entity(
                user_id=new_user_id,
                entity_type=row["entity_type"],
                name=new_name or f"{row['name']} (fork)",
                properties=json.loads(row["properties"]) if row["properties"] else {},
                sharing_level=SharingLevel.PRIVATE,
            )

            # Update origin
            await conn.execute(
                """
                UPDATE kg_entities
                SET origin = $1
                WHERE id = $2
                """,
                EntityOrigin.SHARED_COPY.value,
                fork.id,
            )

            return fork

    async def get_entity_lineage(
        self,
        entity_id: str,
    ) -> list[SharedEntity]:
        """
        Get the lineage of an entity (forks and copies).

        Returns list of related entities.
        """
        async with self.pool.acquire() as conn:
            # Get original entity
            row = await conn.fetchrow(
                """
                SELECT id, entity_type, name, properties, origin
                FROM kg_entities
                WHERE id = $1
                """,
                entity_id,
            )

            if not row:
                return []

            # Find forks (entities with similar names or properties)
            rows = await conn.fetch(
                """
                SELECT id, entity_type, name, properties,
                       source_user_id, sharing_level, shared_with,
                       team_id, origin, created_at, updated_at
                FROM kg_entities
                WHERE entity_type = $1
                  AND (name LIKE $2 OR id = $3)
                ORDER BY created_at ASC
                """,
                row["entity_type"],
                f"%{row['name'].split('(')[0].strip()}%",
                entity_id,
            )

        return [
            SharedEntity(
                id=r["id"],
                entity_type=r["entity_type"],
                name=r["name"],
                properties=json.loads(r["properties"]) if r["properties"] else {},
                owner_user_id=r["source_user_id"],
                sharing_level=SharingLevel(r["sharing_level"]),
                shared_with=r["shared_with"] or [],
                team_id=r["team_id"],
                origin=EntityOrigin(r["origin"]),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]
