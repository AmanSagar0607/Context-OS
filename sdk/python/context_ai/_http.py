"""
Context AI — HTTP Client

Low-level HTTP client for API requests.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx


class HTTPClient:
    """HTTP client for Context OS API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize HTTP client.

        Args:
            base_url: API server URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Build headers
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

        # Async client (lazy init)
        self._async_client: Optional[httpx.AsyncClient] = None

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
            )
        return self._async_client

    def request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        """
        Make synchronous HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            json: Request body
            params: Query parameters

        Returns:
            Response JSON
        """
        response = self._client.request(
            method=method,
            url=path,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def arequest(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        """
        Make async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            json: Request body
            params: Query parameters

        Returns:
            Response JSON
        """
        client = self._get_async_client()
        response = await client.request(
            method=method,
            url=path,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        """GET request."""
        return self.request("GET", path, params=params)

    def post(self, path: str, json: Optional[dict] = None) -> Any:
        """POST request."""
        return self.request("POST", path, json=json)

    def put(self, path: str, json: Optional[dict] = None) -> Any:
        """PUT request."""
        return self.request("PUT", path, json=json)

    def delete(self, path: str) -> Any:
        """DELETE request."""
        return self.request("DELETE", path)

    async def aget(self, path: str, params: Optional[dict] = None) -> Any:
        """Async GET request."""
        return await self.arequest("GET", path, params=params)

    async def apost(self, path: str, json: Optional[dict] = None) -> Any:
        """Async POST request."""
        return await self.arequest("POST", path, json=json)

    async def aput(self, path: str, json: Optional[dict] = None) -> Any:
        """Async PUT request."""
        return await self.arequest("PUT", path, json=json)

    async def adelete(self, path: str) -> Any:
        """Async DELETE request."""
        return await self.arequest("DELETE", path)

    def close(self):
        """Close HTTP clients."""
        self._client.close()
        if self._async_client:
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(self._async_client.aclose())
            except RuntimeError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.close()