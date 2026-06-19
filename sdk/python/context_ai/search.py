"""
Context AI — Search Client

Search operations for the Context OS API.
"""

from __future__ import annotations

from ._http import HTTPClient
from .types import SearchRequest, SearchResult


class SearchClient:
    """Search operations client."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def web(self, request: SearchRequest) -> list[SearchResult]:
        """
        Web search.

        Args:
            request: Search request

        Returns:
            List of search results
        """
        data = self.http.post("/api/v1/search/web", json=request.model_dump())
        return [SearchResult(**r) for r in data.get("results", [])]

    async def aweb(self, request: SearchRequest) -> list[SearchResult]:
        """Async: Web search."""
        data = await self.http.apost("/api/v1/search/web", json=request.model_dump())
        return [SearchResult(**r) for r in data.get("results", [])]

    def internal(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """
        Internal hybrid search.

        Args:
            query: Search query
            top_k: Maximum results

        Returns:
            List of search results
        """
        data = self.http.post(
            "/api/v1/search/internal",
            json={"query": query, "top_k": top_k},
        )
        return [SearchResult(**r) for r in data.get("results", [])]

    async def ainternal(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Async: Internal hybrid search."""
        data = await self.http.apost(
            "/api/v1/search/internal",
            json={"query": query, "top_k": top_k},
        )
        return [SearchResult(**r) for r in data.get("results", [])]