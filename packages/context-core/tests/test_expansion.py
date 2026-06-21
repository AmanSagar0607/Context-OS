"""
Tests for HyDE query expansion.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import AsyncMock, patch

from retrieval.expansion import (
    HyDEConfig,
    HyDEResult,
    HyDEExpansion,
    hyde_expand_and_search,
)


class TestHyDEConfig:
    """Test HyDEConfig."""

    def test_default_config(self):
        config = HyDEConfig()
        assert config.enabled is True
        assert config.num_variants == 1
        assert config.max_answer_length == 200
        assert config.combine_strategy == "average"

    def test_custom_config(self):
        config = HyDEConfig(
            enabled=False,
            num_variants=3,
            combine_strategy="concatenate",
        )
        assert config.enabled is False
        assert config.num_variants == 3
        assert config.combine_strategy == "concatenate"


class TestHyDEResult:
    """Test HyDEResult."""

    def test_result_creation(self):
        result = HyDEResult(
            original_query="test",
            expanded_queries=["test", "alternative"],
            hypothetical_answers=["answer1"],
            strategy_used="average",
        )
        assert result.original_query == "test"
        assert len(result.expanded_queries) == 2
        assert len(result.hypothetical_answers) == 1


class TestHyDEExpansion:
    """Test HyDEExpansion."""

    def test_combine_queries_average(self):
        config = HyDEConfig(combine_strategy="average", num_variants=1)
        hyde = HyDEExpansion(config)

        combined = hyde._combine_queries(
            original_query="original",
            alternative_queries=["alt1"],
            hypothetical_answers=["answer1"],
        )

        assert "original" in combined
        assert "alt1" in combined
        assert "answer1" in combined

    def test_combine_queries_concatenate(self):
        config = HyDEConfig(combine_strategy="concatenate", num_variants=1)
        hyde = HyDEExpansion(config)

        combined = hyde._combine_queries(
            original_query="original",
            alternative_queries=["alt1"],
            hypothetical_answers=["answer1"],
        )

        assert len(combined) == 1
        assert "original" in combined[0]
        assert "alt1" in combined[0]

    def test_combine_queries_best(self):
        config = HyDEConfig(combine_strategy="best", num_variants=1)
        hyde = HyDEExpansion(config)

        combined = hyde._combine_queries(
            original_query="original",
            alternative_queries=["alt1", "alt2"],
            hypothetical_answers=["answer1"],
        )

        assert len(combined) == 2  # original + best alternative

    @pytest.mark.asyncio
    async def test_disabled_hyde(self):
        config = HyDEConfig(enabled=False)
        hyde = HyDEExpansion(config)

        result = await hyde.expand_query(
            query="test",
            api_key="key",
            model="model",
        )

        assert result.expanded_queries == ["test"]
        assert result.hypothetical_answers == []


class TestHyDEExpandAndSearch:
    """Test hyde_expand_and_search function."""

    @pytest.mark.asyncio
    async def test_basic_search(self):
        async def search_fn(q):
            return [{"id": "1", "content": f"result for {q}"}]

        with patch.object(
            HyDEExpansion, "expand_query", new_callable=AsyncMock
        ) as mock_expand:
            mock_expand.return_value = HyDEResult(
                original_query="test",
                expanded_queries=["test", "expanded"],
                hypothetical_answers=["answer"],
                strategy_used="average",
            )

            results, hyde_result = await hyde_expand_and_search(
                query="test",
                search_fn=search_fn,
                api_key="key",
                model="model",
            )

            assert len(results) == 2  # One from each query
            assert hyde_result.original_query == "test"
