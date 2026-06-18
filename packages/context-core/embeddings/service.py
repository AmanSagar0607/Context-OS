"""
Embedding Service — Pluggable embedding providers.

Supports sentence-transformers (default), OpenAI, and Cohere.
All providers expose the same interface: embed_query() and embed_texts().
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Protocol

import numpy as np


class EmbeddingProvider(Protocol):
    """Interface for embedding providers."""

    def embed_query(self, text: str) -> list[float]: ...
    def embed_texts(self, texts: list[str]) -> dict: ...


class SentenceTransformerProvider:
    """Local embeddings via sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_query(self, text: str) -> list[float]:
        model = self._load_model()
        vector = model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0]
        return vector.tolist()

    def embed_texts(self, texts: list[str]) -> dict:
        start = time.perf_counter()
        if not texts:
            return {
                "model": self.model_name,
                "dimension": 0,
                "count": 0,
                "vectors": [],
                "duration_ms": 0,
            }

        model = self._load_model()
        vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        dim = int(vectors.shape[1])

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model": self.model_name,
            "dimension": dim,
            "count": len(texts),
            "vectors": vectors.tolist(),
            "duration_ms": round(elapsed_ms, 2),
        }


class OpenAIProvider:
    """OpenAI embeddings via API."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = ""):
        self.model_name = model_name
        self.api_key = api_key

    def embed_query(self, text: str) -> list[float]:
        import httpx
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model_name, "input": text},
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    def embed_texts(self, texts: list[str]) -> dict:
        import httpx
        start = time.perf_counter()
        if not texts:
            return {
                "model": self.model_name,
                "dimension": 0,
                "count": 0,
                "vectors": [],
                "duration_ms": 0,
            }

        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model_name, "input": texts},
        )
        response.raise_for_status()
        data = response.json()["data"]
        vectors = [item["embedding"] for item in data]
        dim = len(vectors[0]) if vectors else 0

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model": self.model_name,
            "dimension": dim,
            "count": len(texts),
            "vectors": vectors,
            "duration_ms": round(elapsed_ms, 2),
        }


class EmbeddingService:
    """Pluggable embedding service with provider selection."""

    def __init__(
        self,
        provider: str = "sentence-transformers",
        model_name: str = "all-MiniLM-L6-v2",
        api_key: str = "",
        dimension: int = 384,
    ):
        self.provider_name = provider
        self.dimension = dimension

        if provider == "openai":
            self._provider = OpenAIProvider(model_name=model_name, api_key=api_key)
        else:
            self._provider = SentenceTransformerProvider(model_name=model_name)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self._provider.embed_query(text)

    def embed_texts(self, texts: list[str]) -> dict:
        """Embed multiple text strings."""
        return self._provider.embed_texts(texts)

    @classmethod
    def from_settings(cls, settings) -> "EmbeddingService":
        """Create from Settings object."""
        return cls(
            provider=settings.embedding_provider,
            model_name=settings.embedding_model,
            api_key=getattr(settings, "openai_api_key", ""),
            dimension=settings.embedding_dimension,
        )