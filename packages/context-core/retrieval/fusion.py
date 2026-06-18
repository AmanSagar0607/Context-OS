"""
Reciprocal Rank Fusion (RRF) — Combines multiple search result lists.

Merges vector search and BM25 results using RRF scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FusedResult:
    """Single fused search result."""
    id: str
    content: str
    rrf_score: float
    sources: list[str]
    metadata: dict = field(default_factory=dict)
    original_scores: dict = field(default_factory=dict)


def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    k: int = 60,
    source_names: Optional[list[str]] = None,
) -> list[FusedResult]:
    """
    Combine multiple ranked result lists using Reciprocal Rank Fusion.

    RRF score = sum(1 / (k + rank_i)) for each result list i

    Args:
        result_lists: List of ranked result lists. Each result must have 'id' and 'content'.
        k: RRF constant (default: 60). Higher k = less weight to top ranks.
        source_names: Optional names for each result list (e.g., ['vector', 'bm25']).

    Returns:
        List of FusedResult sorted by RRF score descending
    """
    if not result_lists:
        return []

    if source_names is None:
        source_names = [f"source_{i}" for i in range(len(result_lists))]

    # Track scores and metadata for each unique result
    result_scores: dict[str, dict] = {}

    for list_idx, result_list in enumerate(result_lists):
        source_name = source_names[list_idx] if list_idx < len(source_names) else f"source_{list_idx}"

        for rank, result in enumerate(result_list):
            result_id = result.get("id", "")
            if not result_id:
                continue

            if result_id not in result_scores:
                result_scores[result_id] = {
                    "id": result_id,
                    "content": result.get("content", ""),
                    "rrf_score": 0.0,
                    "sources": [],
                    "metadata": result.get("metadata", {}),
                    "original_scores": {},
                }

            # Add RRF score contribution
            rrf_contribution = 1.0 / (k + rank + 1)  # rank is 0-indexed
            result_scores[result_id]["rrf_score"] += rrf_contribution
            result_scores[result_id]["sources"].append(source_name)
            result_scores[result_id]["original_scores"][source_name] = {
                "rank": rank,
                "score": result.get("score", result.get("rank", 0)),
            }

    # Sort by RRF score descending
    fused_results = sorted(
        result_scores.values(),
        key=lambda x: x["rrf_score"],
        reverse=True,
    )

    return [
        FusedResult(
            id=r["id"],
            content=r["content"],
            rrf_score=r["rrf_score"],
            sources=r["sources"],
            metadata=r["metadata"],
            original_scores=r["original_scores"],
        )
        for r in fused_results
    ]


def weighted_reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    weights: list[float],
    k: int = 60,
    source_names: Optional[list[str]] = None,
) -> list[FusedResult]:
    """
    Weighted RRF — assign different weights to different search sources.

    Args:
        result_lists: List of ranked result lists
        weights: Weight for each result list (must match length of result_lists)
        k: RRF constant
        source_names: Optional names for each result list

    Returns:
        List of FusedResult sorted by weighted RRF score descending
    """
    if not result_lists:
        return []

    if len(weights) != len(result_lists):
        raise ValueError("weights length must match result_lists length")

    if source_names is None:
        source_names = [f"source_{i}" for i in range(len(result_lists))]

    result_scores: dict[str, dict] = {}

    for list_idx, result_list in enumerate(result_lists):
        source_name = source_names[list_idx] if list_idx < len(source_names) else f"source_{list_idx}"
        weight = weights[list_idx]

        for rank, result in enumerate(result_list):
            result_id = result.get("id", "")
            if not result_id:
                continue

            if result_id not in result_scores:
                result_scores[result_id] = {
                    "id": result_id,
                    "content": result.get("content", ""),
                    "rrf_score": 0.0,
                    "sources": [],
                    "metadata": result.get("metadata", {}),
                    "original_scores": {},
                }

            # Weighted RRF contribution
            rrf_contribution = weight * (1.0 / (k + rank + 1))
            result_scores[result_id]["rrf_score"] += rrf_contribution
            result_scores[result_id]["sources"].append(source_name)
            result_scores[result_id]["original_scores"][source_name] = {
                "rank": rank,
                "score": result.get("score", result.get("rank", 0)),
            }

    fused_results = sorted(
        result_scores.values(),
        key=lambda x: x["rrf_score"],
        reverse=True,
    )

    return [
        FusedResult(
            id=r["id"],
            content=r["content"],
            rrf_score=r["rrf_score"],
            sources=r["sources"],
            metadata=r["metadata"],
            original_scores=r["original_scores"],
        )
        for r in fused_results
    ]