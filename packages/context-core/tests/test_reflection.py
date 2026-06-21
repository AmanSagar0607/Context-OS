"""
Tests for reflection loop — Self-correction in retrieval pipeline.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from retrieval.reflection import (
    ReflectionConfig,
    ReflectionResult,
    ReflectionVerdict,
    evaluate_answer,
    transform_query,
    reflection_search,
)


class TestReflectionConfig:
    """Test ReflectionConfig."""

    def test_default_config(self):
        config = ReflectionConfig()
        assert config.max_retries == 2
        assert config.confidence_threshold == 0.6
        assert config.enabled is True

    def test_custom_config(self):
        config = ReflectionConfig(max_retries=3, confidence_threshold=0.8, enabled=False)
        assert config.max_retries == 3
        assert config.confidence_threshold == 0.8
        assert config.enabled is False


class TestReflectionResult:
    """Test ReflectionResult."""

    def test_result_creation(self):
        result = ReflectionResult(
            verdict=ReflectionVerdict.HIGH_CONFIDENCE,
            confidence=0.9,
            reasoning="Answer is complete",
        )
        assert result.verdict == ReflectionVerdict.HIGH_CONFIDENCE
        assert result.confidence == 0.9
        assert result.suggested_query is None
        assert result.retry_count == 0


class TestEvaluateAnswer:
    """Test evaluate_answer function."""

    @pytest.mark.asyncio
    async def test_high_confidence_answer(self):
        mock_response = {
            "verdict": "high_confidence",
            "confidence": 0.95,
            "reasoning": "Answer is complete and well-supported",
            "suggested_query": None,
            "suggested_strategy": None,
        }

        with patch("retrieval.reflection._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await evaluate_answer(
                query="What is AI?",
                context="AI is artificial intelligence...",
                answer="AI stands for artificial intelligence.",
                api_key="test-key",
                model="test-model",
            )

            assert result.verdict == ReflectionVerdict.HIGH_CONFIDENCE
            assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_low_confidence_answer(self):
        mock_response = {
            "verdict": "low_confidence",
            "confidence": 0.3,
            "reasoning": "Answer is incomplete",
            "suggested_query": "What is artificial intelligence?",
            "suggested_strategy": "broaden",
        }

        with patch("retrieval.reflection._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await evaluate_answer(
                query="What is AI?",
                context="Limited context...",
                answer="AI is...",
                api_key="test-key",
                model="test-model",
            )

            assert result.verdict == ReflectionVerdict.LOW_CONFIDENCE
            assert result.suggested_strategy == "broaden"

    @pytest.mark.asyncio
    async def test_llm_failure_defaults_high(self):
        with patch("retrieval.reflection._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = None

            result = await evaluate_answer(
                query="test",
                context="context",
                answer="answer",
                api_key="test-key",
                model="test-model",
            )

            assert result.verdict == ReflectionVerdict.HIGH_CONFIDENCE


class TestTransformQuery:
    """Test transform_query function."""

    @pytest.mark.asyncio
    async def test_broaden_strategy(self):
        mock_response = {
            "transformed_query": "artificial intelligence technology",
            "reasoning": "Removed specific acronym",
        }

        with patch("retrieval.reflection._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await transform_query(
                query="What is AI?",
                strategy="broaden",
                api_key="test-key",
                model="test-model",
            )

            assert result == "artificial intelligence technology"

    @pytest.mark.asyncio
    async def test_llm_failure_returns_original(self):
        with patch("retrieval.reflection._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = None

            result = await transform_query(
                query="original query",
                strategy="rephrase",
                api_key="test-key",
                model="test-model",
            )

            assert result == "original query"


class TestReflectionSearch:
    """Test reflection_search function."""

    @pytest.mark.asyncio
    async def test_disabled_reflection(self):
        config = ReflectionConfig(enabled=False)

        async def search_fn(q):
            return "context"

        async def answer_fn(q, c):
            return "answer"

        answer, reflection = await reflection_search(
            query="test",
            search_fn=search_fn,
            generate_answer_fn=answer_fn,
            api_key="test-key",
            model="test-model",
            config=config,
        )

        assert answer == "answer"
        assert reflection.verdict == ReflectionVerdict.HIGH_CONFIDENCE

    @pytest.mark.asyncio
    async def test_immediate_high_confidence(self):
        mock_eval_response = {
            "verdict": "high_confidence",
            "confidence": 0.9,
            "reasoning": "Good answer",
        }

        async def search_fn(q):
            return "context"

        async def answer_fn(q, c):
            return "answer"

        with patch("retrieval.reflection.evaluate_answer", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = ReflectionResult(
                verdict=ReflectionVerdict.HIGH_CONFIDENCE,
                confidence=0.9,
                reasoning="Good answer",
            )

            answer, reflection = await reflection_search(
                query="test",
                search_fn=search_fn,
                generate_answer_fn=answer_fn,
                api_key="test-key",
                model="test-model",
            )

            assert answer == "answer"
            assert reflection.retry_count == 0

    @pytest.mark.asyncio
    async def test_retry_on_low_confidence(self):
        call_count = 0

        async def search_fn(q):
            return f"context for {q}"

        async def answer_fn(q, c):
            return f"answer for {q}"

        # First call: low confidence, second call: high confidence
        eval_results = [
            ReflectionResult(
                verdict=ReflectionVerdict.LOW_CONFIDENCE,
                confidence=0.3,
                reasoning="Incomplete",
                suggested_strategy="broaden",
            ),
            ReflectionResult(
                verdict=ReflectionVerdict.HIGH_CONFIDENCE,
                confidence=0.8,
                reasoning="Good enough",
            ),
        ]

        with patch("retrieval.reflection.evaluate_answer", new_callable=AsyncMock) as mock_eval:
            mock_eval.side_effect = eval_results

            with patch("retrieval.reflection.transform_query", new_callable=AsyncMock) as mock_transform:
                mock_transform.return_value = "broader query"

                answer, reflection = await reflection_search(
                    query="specific query",
                    search_fn=search_fn,
                    generate_answer_fn=answer_fn,
                    api_key="test-key",
                    model="test-model",
                    config=ReflectionConfig(max_retries=2),
                )

                assert reflection.retry_count == 1
                assert mock_eval.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_reached(self):
        async def search_fn(q):
            return "context"

        async def answer_fn(q, c):
            return "answer"

        # Always low confidence
        with patch("retrieval.reflection.evaluate_answer", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = ReflectionResult(
                verdict=ReflectionVerdict.LOW_CONFIDENCE,
                confidence=0.2,
                reasoning="Still bad",
                suggested_strategy="rephrase",
            )

            with patch("retrieval.reflection.transform_query", new_callable=AsyncMock) as mock_transform:
                mock_transform.return_value = "rephrased query"

                answer, reflection = await reflection_search(
                    query="test",
                    search_fn=search_fn,
                    generate_answer_fn=answer_fn,
                    api_key="test-key",
                    model="test-model",
                    config=ReflectionConfig(max_retries=2),
                )

                # Should have tried 3 times (initial + 2 retries)
                assert reflection.retry_count == 2
                assert mock_eval.call_count == 3
