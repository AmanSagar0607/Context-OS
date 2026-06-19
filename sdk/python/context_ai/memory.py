"""
Context AI — Memory Client

Memory operations for the Context OS API.
"""

from __future__ import annotations

from typing import Optional

from ._http import HTTPClient
from .types import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemorySearchRequest,
    MemorySearchResult,
)


class MemoryClient:
    """Memory operations client."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def add(self, request: MemoryCreate) -> Memory:
        """
        Store a new memory.

        Args:
            request: Memory creation request

        Returns:
            Created memory
        """
        data = self.http.post("/api/v1/memory", json=request.model_dump())
        return Memory(**data)

    async def aadd(self, request: MemoryCreate) -> Memory:
        """Async: Store a new memory."""
        data = await self.http.apost("/api/v1/memory", json=request.model_dump())
        return Memory(**data)

    def get(self, memory_id: str) -> Optional[Memory]:
        """
        Get a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory or None
        """
        try:
            data = self.http.get(f"/api/v1/memory/{memory_id}")
            return Memory(**data)
        except Exception:
            return None

    async def aget(self, memory_id: str) -> Optional[Memory]:
        """Async: Get a memory by ID."""
        try:
            data = await self.http.aget(f"/api/v1/memory/{memory_id}")
            return Memory(**data)
        except Exception:
            return None

    def update(self, memory_id: str, request: MemoryUpdate) -> Optional[Memory]:
        """
        Update a memory.

        Args:
            memory_id: Memory ID
            request: Update request

        Returns:
            Updated memory or None
        """
        try:
            data = self.http.put(
                f"/api/v1/memory/{memory_id}",
                json=request.model_dump(exclude_unset=True),
            )
            return Memory(**data)
        except Exception:
            return None

    async def aupdate(self, memory_id: str, request: MemoryUpdate) -> Optional[Memory]:
        """Async: Update a memory."""
        try:
            data = await self.http.aput(
                f"/api/v1/memory/{memory_id}",
                json=request.model_dump(exclude_unset=True),
            )
            return Memory(**data)
        except Exception:
            return None

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted
        """
        try:
            self.http.delete(f"/api/v1/memory/{memory_id}")
            return True
        except Exception:
            return False

    async def adelete(self, memory_id: str) -> bool:
        """Async: Delete a memory."""
        try:
            await self.http.adelete(f"/api/v1/memory/{memory_id}")
            return True
        except Exception:
            return False

    def search(self, request: MemorySearchRequest) -> list[MemorySearchResult]:
        """
        Search memories.

        Args:
            request: Search request

        Returns:
            List of search results
        """
        data = self.http.post("/api/v1/memory/search", json=request.model_dump())
        return [MemorySearchResult(**r) for r in data.get("results", [])]

    async def asearch(self, request: MemorySearchRequest) -> list[MemorySearchResult]:
        """Async: Search memories."""
        data = await self.http.apost("/api/v1/memory/search", json=request.model_dump())
        return [MemorySearchResult(**r) for r in data.get("results", [])]

    def context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> dict:
        """
        Get context window from memories.

        Args:
            query: Query to assemble context for
            max_tokens: Maximum tokens in context

        Returns:
            Dict with memories, total_tokens, truncated
        """
        return self.http.post(
            "/api/v1/memory/context",
            json={"query": query, "max_tokens": max_tokens},
        )

    async def acontext(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> dict:
        """Async: Get context window from memories."""
        return await self.http.apost(
            "/api/v1/memory/context",
            json={"query": query, "max_tokens": max_tokens},
        )

    def list(
        self,
        memory_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Memory]:
        """
        List memories.

        Args:
            memory_type: Optional type filter
            limit: Maximum results
            offset: Results offset

        Returns:
            List of memories
        """
        params = {"limit": limit, "offset": offset}
        if memory_type:
            params["memory_type"] = memory_type
        data = self.http.get("/api/v1/memory", params=params)
        return [Memory(**m) for m in data.get("memories", [])]

    async def alist(
        self,
        memory_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Memory]:
        """Async: List memories."""
        params = {"limit": limit, "offset": offset}
        if memory_type:
            params["memory_type"] = memory_type
        data = await self.http.aget("/api/v1/memory", params=params)
        return [Memory(**m) for m in data.get("memories", [])]

    def related(self, memory_id: str, limit: int = 10) -> list[Memory]:
        """
        Get related memories.

        Args:
            memory_id: Memory ID
            limit: Maximum results

        Returns:
            List of related memories
        """
        data = self.http.get(f"/api/v1/memory/{memory_id}/related", params={"limit": limit})
        return [Memory(**m) for m in data.get("memories", [])]

    async def arelated(self, memory_id: str, limit: int = 10) -> list[Memory]:
        """Async: Get related memories."""
        data = await self.http.aget(f"/api/v1/memory/{memory_id}/related", params={"limit": limit})
        return [Memory(**m) for m in data.get("memories", [])]