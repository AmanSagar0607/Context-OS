"""
Embedding Service — Pluggable embedding providers.

Supports sentence-transformers (default), OpenAI, Cohere,
and a lightweight numpy-only fallback (random projection).
All providers expose the same interface: embed_query() and embed_texts().
"""

from __future__ import annotations

import hashlib
import time
from abc import ABC, abstractmethod
from typing import Protocol

import numpy as np


class EmbeddingProvider(Protocol):
    """Interface for embedding providers."""

    def embed_query(self, text: str) -> list[float]: ...
    def embed_texts(self, texts: list[str]) -> dict: ...


class RandomProjectionProvider:
    """Lightweight numpy-only embeddings using random projection.

    Produces deterministic, consistent vectors for cosine similarity.
    No ML models required — ideal for Docker/server deployments.
    """

    VOCAB_SIZE = 4096
    HASH_MOD = 2**31

    def __init__(self, dimension: int = 384, seed: int = 42):
        self.dimension = dimension
        rng = np.random.RandomState(seed)
        self._projection = rng.randn(self.VOCAB_SIZE, dimension).astype(np.float32)
        norms = np.linalg.norm(self._projection, axis=1, keepdims=True)
        self._projection /= np.where(norms > 0, norms, 1.0)

    def _hash_token(self, token: str) -> int:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        return h % self.VOCAB_SIZE

    def _text_to_vector(self, text: str) -> np.ndarray:
        tokens = text.lower().split()
        if not tokens:
            return np.zeros(self.dimension, dtype=np.float32)

        vec = np.zeros(self.VOCAB_SIZE, dtype=np.float32)
        for token in tokens:
            idx = self._hash_token(token)
            vec[idx] += 1.0

        total = vec.sum()
        if total > 0:
            vec /= total

        projected = vec @ self._projection
        norm = np.linalg.norm(projected)
        if norm > 0:
            projected /= norm
        return projected

    def embed_query(self, text: str) -> list[float]:
        return self._text_to_vector(text).tolist()

    def embed_texts(self, texts: list[str]) -> dict:
        start = time.perf_counter()
        if not texts:
            return {
                "model": "random-projection",
                "dimension": self.dimension,
                "count": 0,
                "vectors": [],
                "duration_ms": 0,
            }

        vectors = [self._text_to_vector(t) for t in texts]
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model": "random-projection",
            "dimension": self.dimension,
            "count": len(texts),
            "vectors": [v.tolist() for v in vectors],
            "duration_ms": round(elapsed_ms, 2),
        }


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


def _create_provider(provider: str, model_name: str, api_key: str, dimension: int):
    """Create the best available provider for the given config."""
    if provider == "openai" and api_key:
        return OpenAIProvider(model_name=model_name, api_key=api_key)

    if provider == "sentence-transformers":
        try:
            import sentence_transformers  # noqa: F401
            return SentenceTransformerProvider(model_name=model_name)
        except ImportError:
            pass

    return RandomProjectionProvider(dimension=dimension)


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
        self._provider = _create_provider(provider, model_name, api_key, dimension)

    @property
    def actual_provider(self) -> str:
        if isinstance(self._provider, RandomProjectionProvider):
            return "random-projection"
        elif isinstance(self._provider, SentenceTransformerProvider):
            return "sentence-transformers"
        elif isinstance(self._provider, OpenAIProvider):
            return "openai"
        return "unknown"

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
