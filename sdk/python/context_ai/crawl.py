"""
Context AI — Crawl Client

Crawl operations for the Context OS API.
"""

from __future__ import annotations

from typing import Optional

from ._http import HTTPClient
from .types import CrawlRequest, CrawlResult


class CrawlClient:
    """Crawl operations client."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def scrape(self, url: str, **kwargs) -> CrawlResult:
        """
        Scrape a single URL.

        Args:
            url: URL to scrape
            **kwargs: Additional options

        Returns:
            Crawl result
        """
        data = self.http.post(
            "/api/v1/crawl/scrape",
            json={"url": url, **kwargs},
        )
        return CrawlResult(**data)

    async def ascrape(self, url: str, **kwargs) -> CrawlResult:
        """Async: Scrape a single URL."""
        data = await self.http.apost(
            "/api/v1/crawl/scrape",
            json={"url": url, **kwargs},
        )
        return CrawlResult(**data)

    def crawl(self, request: CrawlRequest) -> list[CrawlResult]:
        """
        Crawl a website.

        Args:
            request: Crawl request

        Returns:
            List of crawl results
        """
        data = self.http.post("/api/v1/crawl/crawl", json=request.model_dump())
        return [CrawlResult(**r) for r in data.get("results", [])]

    async def acrawl(self, request: CrawlRequest) -> list[CrawlResult]:
        """Async: Crawl a website."""
        data = await self.http.apost("/api/v1/crawl/crawl", json=request.model_dump())
        return [CrawlResult(**r) for r in data.get("results", [])]

    def map(self, url: str, max_pages: int = 50) -> list[str]:
        """
        Map a website (get all URLs).

        Args:
            url: Base URL
            max_pages: Maximum pages to map

        Returns:
            List of URLs
        """
        data = self.http.post(
            "/api/v1/crawl/map",
            json={"url": url, "max_pages": max_pages},
        )
        return data.get("urls", [])

    async def amap(self, url: str, max_pages: int = 50) -> list[str]:
        """Async: Map a website."""
        data = await self.http.apost(
            "/api/v1/crawl/map",
            json={"url": url, "max_pages": max_pages},
        )
        return data.get("urls", [])

    def extract(
        self,
        url: str,
        prompt: str,
        schema: Optional[dict] = None,
    ) -> dict:
        """
        AI extraction from URL.

        Args:
            url: URL to extract from
            prompt: Extraction prompt
            schema: Optional output schema

        Returns:
            Extracted data
        """
        payload = {"url": url, "prompt": prompt}
        if schema:
            payload["schema"] = schema
        return self.http.post("/api/v1/crawl/extract", json=payload)

    async def aextract(
        self,
        url: str,
        prompt: str,
        schema: Optional[dict] = None,
    ) -> dict:
        """Async: AI extraction from URL."""
        payload = {"url": url, "prompt": prompt}
        if schema:
            payload["schema"] = schema
        return await self.http.apost("/api/v1/crawl/extract", json=payload)