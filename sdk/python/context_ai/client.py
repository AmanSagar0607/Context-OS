"""
Context AI — Main Client

Unified entry point for all Context OS API operations.
"""

from __future__ import annotations

import os
from typing import Optional

from ._http import HTTPClient
from .memory import MemoryClient
from .search import SearchClient
from .crawl import CrawlClient
from .knowledge import KnowledgeClient


class ContextAI:
    """
    Context OS Python Client

    Usage:
        from context_ai import ContextAI

        client = ContextAI(api_key="your-api-key")

        # Memory
        memory = client.memory.add(content="User prefers dark mode")

        # Search
        results = client.search.web(query="latest AI news")

        # Crawl
        page = client.crawl.scrape(url="https://example.com")

        # Knowledge
        entity = client.knowledge.create_entity(name="GPT-4", entity_type="model")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize Context AI client.

        Args:
            base_url: API server URL (default: http://localhost:8000)
            api_key: API key for authentication (default: from CONTEXT_API_KEY env)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv(
            "CONTEXT_API_URL",
            os.getenv("CONTEXT_OS_URL", "http://localhost:8000"),
        )
        self.api_key = api_key or os.getenv(
            "CONTEXT_API_KEY",
            os.getenv("CONTEXT_OS_API_KEY"),
        )

        self._http = HTTPClient(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=timeout,
        )

        # Initialize sub-clients
        self.memory = MemoryClient(self._http)
        self.search = SearchClient(self._http)
        self.crawl = CrawlClient(self._http)
        self.knowledge = KnowledgeClient(self._http)

    def health(self) -> dict:
        """
        Check API health status.

        Returns:
            Health status dict
        """
        return self._http.get("/api/v1/health")

    async def ahealth(self) -> dict:
        """Async: Check API health status."""
        return await self._http.aget("/api/v1/health")

    def close(self):
        """Close HTTP connections."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return f"ContextAI(base_url={self.base_url!r})"