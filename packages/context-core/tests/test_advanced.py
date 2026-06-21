"""
Tests for advanced retrieval.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch

from retrieval.advanced import (
    AdvancedRetrievalConfig,
    AdvancedRetrievalResult,
    AdvancedRetrieval,
    RetrievalStrategy,
    SubQuestion,
    StepBackQuery,
)


class TestAdvancedRetrievalConfig:
    """Test AdvancedRetrievalConfig."""

    def test_default_config(self):
        config = AdvancedRetrievalConfig()
        assert config.strategy == RetrievalStrategy.STANDARD
        assert config.max_sub_questions == 3
        assert config.max_step_back_levels == 2
        assert config.confidence_threshold == 0.7

    def test_custom_config(self):
        config = AdvancedRetrievalConfig(
            strategy=RetrievalStrategy.SELF_ASK,
            max_sub_questions=5,
        )
        assert config.strategy == RetrievalStrategy.SELF_ASK
        assert config.max_sub_questions == 5


class TestAdvancedRetrievalResult:
    """Test AdvancedRetrievalResult."""

    def test_result_creation(self):
        result = AdvancedRetrievalResult(
            strategy_used=RetrievalStrategy.STANDARD,
            original_query="test",
        )
        assert result.strategy_used == RetrievalStrategy.STANDARD
        assert result.original_query == "test"
        assert result.expanded_queries == []


class TestAdvancedRetrieval:
    """Test AdvancedRetrieval."""

    @pytest.mark.asyncio
    async def test_standard_retrieval(self):
        async def search_fn(q):
            return [{"content": f"result for {q}"}]

        config = AdvancedRetrievalConfig(strategy=RetrievalStrategy.STANDARD)
        retrieval = AdvancedRetrieval(config)

        result = await retrieval.retrieve(
            query="test query",
            search_fn=search_fn,
            api_key="key",
            model="model",
        )

        assert result.strategy_used == RetrievalStrategy.STANDARD
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_multi_query_retrieval(self):
        async def search_fn(q):
            return [{"content": f"result for {q}"}]

        with patch.object(
            AdvancedRetrieval, "multi_query", new_callable=AsyncMock
        ) as mock_multi:
            mock_multi.return_value = ["test query", "alternative query"]

            config = AdvancedRetrievalConfig(strategy=RetrievalStrategy.MULTI_QUERY)
            retrieval = AdvancedRetrieval(config)

            result = await retrieval.retrieve(
                query="test query",
                search_fn=search_fn,
                api_key="key",
                model="model",
            )

            assert result.strategy_used == RetrievalStrategy.MULTI_QUERY
            assert len(result.expanded_queries) == 2


class TestSubQuestion:
    """Test SubQuestion."""

    def test_sub_question(self):
        sq = SubQuestion(
            question="What is X?",
            answer="X is Y",
            source="search",
        )
        assert sq.question == "What is X?"
        assert sq.answer == "X is Y"


class TestStepBackQuery:
    """Test StepBackQuery."""

    def test_step_back(self):
        sb = StepBackQuery(
            original_query="specific question",
            step_back_query="general question",
            level=1,
            reasoning="Step back for context",
        )
        assert sb.level == 1
        assert sb.original_query == "specific question"


class TestRetrievalStrategy:
    """Test RetrievalStrategy enum."""

    def test_strategies(self):
        assert RetrievalStrategy.STANDARD.value == "standard"
        assert RetrievalStrategy.STEP_BACK.value == "step_back"
        assert RetrievalStrategy.SELF_ASK.value == "self_ask"
        assert RetrievalStrategy.MULTI_QUERY.value == "multi_query"
