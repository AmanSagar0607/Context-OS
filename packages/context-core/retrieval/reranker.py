"""
Cross-Encoder Re-ranking — bge-reranker-v2-m3 integration.

Re-ranks search results using a cross-encoder model for better precision.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Protocol

logger = logging.getLogger(__name__)


@dataclass
class RerankerConfig:
    """Configuration for cross-encoder re-ranking."""
    enabled: bool = True
    model_name: str = "BAAI/bge-reranker-v2-m3"
    top_k: int = 5  # Number of results to keep after re-ranking
    batch_size: int = 32  # Batch size for inference
    use_onnx: bool = False  # Use ONNX for faster inference
    device: str = "cpu"  # cpu or cuda


@dataclass
class RerankedResult:
    """A re-ranked search result."""
    id: str
    content: str
    original_score: float
    reranked_score: float
    rank: int
    metadata: dict = field(default_factory=dict)


class CrossEncoderReranker:
    """
    Cross-encoder re-ranking using sentence-transformers.

    Re-ranks initial search results by computing fine-grained
    query-document relevance scores.
    """

    def __init__(self, config: Optional[RerankerConfig] = None):
        self.config = config or RerankerConfig()
        self._model = None

    def _load_model(self):
        """Lazy-load the cross-encoder model."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(
                self.config.model_name,
                max_length=512,
                device=self.config.device,
            )
            logger.info(f"Loaded cross-encoder model: {self.config.model_name}")

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: Optional[int] = None,
    ) -> list[RerankedResult]:
        """
        Re-rank search results using cross-encoder.

        Args:
            query: Original search query
            results: List of dicts with 'id', 'content', 'score' keys
            top_k: Override top_k from config

        Returns:
            Re-ranked list of RerankedResult
        """
        if not self.config.enabled or not results:
            return []

        top_k = top_k or self.config.top_k

        # Lazy-load model
        self._load_model()

        if self._model is None:
            # Fallback: return original order
            return [
                RerankedResult(
                    id=r.get("id", ""),
                    content=r.get("content", ""),
                    original_score=r.get("score", 0.0),
                    reranked_score=r.get("score", 0.0),
                    rank=i,
                    metadata=r.get("metadata", {}),
                )
                for i, r in enumerate(results[:top_k])
            ]

        # Prepare pairs for cross-encoder
        pairs = [(query, r.get("content", "")) for r in results]

        # Compute scores
        scores = self._model.predict(
            pairs,
            batch_size=self.config.batch_size,
            show_progress_bar=False,
        )

        # Create reranked results
        reranked = []
        for i, (result, score) in enumerate(zip(results, scores)):
            reranked.append(RerankedResult(
                id=result.get("id", ""),
                content=result.get("content", ""),
                original_score=result.get("score", 0.0),
                reranked_score=float(score),
                rank=i,
                metadata=result.get("metadata", {}),
            ))

        # Sort by reranked score (descending)
        reranked.sort(key=lambda x: x.reranked_score, reverse=True)

        # Update ranks and take top_k
        for i, r in enumerate(reranked[:top_k]):
            r.rank = i

        return reranked[:top_k]

    async def rerank_async(
        self,
        query: str,
        results: list[dict],
        top_k: Optional[int] = None,
    ) -> list[RerankedResult]:
        """
        Async wrapper for rerank.

        Runs the synchronous rerank in a thread pool.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.rerank(query, results, top_k)
        )


class HybridReranker:
    """
    Combines multiple re-ranking strategies.

    Can use cross-encoder, diversity-based, or MMR re-ranking.
    """

    def __init__(self, config: Optional[RerankerConfig] = None):
        self.config = config or RerankerConfig()
        self.cross_encoder = CrossEncoderReranker(config)

    def rerank_with_diversity(
        self,
        query: str,
        results: list[dict],
        top_k: Optional[int] = None,
        diversity_weight: float = 0.3,
    ) -> list[RerankedResult]:
        """
        Re-rank with diversity (MMR-like approach).

        Balances relevance and diversity to avoid redundant results.

        Args:
            query: Search query
            results: Search results
            top_k: Number of results to return
            diversity_weight: Weight for diversity (0.0 = pure relevance, 1.0 = pure diversity)

        Returns:
            Re-ranked results with diversity
        """
        if not results:
            return []

        top_k = top_k or self.config.top_k

        # First, get relevance scores
        reranked = self.cross_encoder.rerank(query, results, top_k=len(results))

        if not reranked or diversity_weight == 0:
            return reranked[:top_k]

        # Apply diversity re-ranking
        selected = []
        remaining = list(reranked)

        while remaining and len(selected) < top_k:
            if not selected:
                # First item: highest relevance
                selected.append(remaining.pop(0))
                continue

            # Find best balance of relevance and diversity
            best_idx = 0
            best_score = -1

            for i, candidate in enumerate(remaining):
                # Relevance score (normalized)
                relevance = candidate.reranked_score

                # Diversity score (min similarity to selected)
                min_similarity = 1.0
                for sel in selected:
                    similarity = self._content_similarity(
                        candidate.content, sel.content
                    )
                    min_similarity = min(min_similarity, similarity)

                # Combined score
                combined = (1 - diversity_weight) * relevance + diversity_weight * (1 - min_similarity)

                if combined > best_score:
                    best_score = combined
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        # Update ranks
        for i, r in enumerate(selected):
            r.rank = i

        return selected

    def _content_similarity(self, text1: str, text2: str) -> float:
        """Simple content similarity based on word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0
