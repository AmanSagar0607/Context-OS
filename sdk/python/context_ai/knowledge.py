"""
Context AI — Knowledge Client

Knowledge graph operations for the Context OS API.
"""

from __future__ import annotations

from typing import Optional

from ._http import HTTPClient
from .types import Entity, EntityCreate, RelationshipCreate


class KnowledgeClient:
    """Knowledge graph operations client."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def create_entity(self, request: EntityCreate) -> Entity:
        """
        Create a knowledge graph entity.

        Args:
            request: Entity creation request

        Returns:
            Created entity
        """
        data = self.http.post("/api/v1/knowledge/entities", json=request.model_dump())
        return Entity(**data)

    async def acreate_entity(self, request: EntityCreate) -> Entity:
        """Async: Create a knowledge graph entity."""
        data = await self.http.apost("/api/v1/knowledge/entities", json=request.model_dump())
        return Entity(**data)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity or None
        """
        try:
            data = self.http.get(f"/api/v1/knowledge/entities/{entity_id}")
            return Entity(**data)
        except Exception:
            return None

    async def aget_entity(self, entity_id: str) -> Optional[Entity]:
        """Async: Get an entity by ID."""
        try:
            data = await self.http.aget(f"/api/v1/knowledge/entities/{entity_id}")
            return Entity(**data)
        except Exception:
            return None

    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted
        """
        try:
            self.http.delete(f"/api/v1/knowledge/entities/{entity_id}")
            return True
        except Exception:
            return False

    async def adelete_entity(self, entity_id: str) -> bool:
        """Async: Delete an entity."""
        try:
            await self.http.adelete(f"/api/v1/knowledge/entities/{entity_id}")
            return True
        except Exception:
            return False

    def create_relationship(self, request: RelationshipCreate) -> dict:
        """
        Create a relationship between entities.

        Args:
            request: Relationship creation request

        Returns:
            Created relationship
        """
        return self.http.post("/api/v1/knowledge/relationships", json=request.model_dump())

    async def acreate_relationship(self, request: RelationshipCreate) -> dict:
        """Async: Create a relationship between entities."""
        return await self.http.apost("/api/v1/knowledge/relationships", json=request.model_dump())

    def get_graph(self, entity_id: str, depth: int = 2) -> dict:
        """
        Get entity graph.

        Args:
            entity_id: Entity ID
            depth: Graph traversal depth

        Returns:
            Graph data
        """
        return self.http.get(
            f"/api/v1/knowledge/graph/{entity_id}",
            params={"depth": depth},
        )

    async def aget_graph(self, entity_id: str, depth: int = 2) -> dict:
        """Async: Get entity graph."""
        return await self.http.aget(
            f"/api/v1/knowledge/graph/{entity_id}",
            params={"depth": depth},
        )

    def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        top_k: int = 10,
    ) -> list[Entity]:
        """
        Search entities.

        Args:
            query: Search query
            entity_type: Optional type filter
            top_k: Maximum results

        Returns:
            List of entities
        """
        payload = {"query": query, "top_k": top_k}
        if entity_type:
            payload["entity_type"] = entity_type
        data = self.http.post("/api/v1/knowledge/search", json=payload)
        return [Entity(**e) for e in data.get("entities", [])]

    async def asearch(
        self,
        query: str,
        entity_type: Optional[str] = None,
        top_k: int = 10,
    ) -> list[Entity]:
        """Async: Search entities."""
        payload = {"query": query, "top_k": top_k}
        if entity_type:
            payload["entity_type"] = entity_type
        data = await self.http.apost("/api/v1/knowledge/search", json=payload)
        return [Entity(**e) for e in data.get("entities", [])]