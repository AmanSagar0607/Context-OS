"""
Reflection Loop — Self-correction in retrieval pipeline.

Evaluates answer quality and retries with modified queries if confidence is low.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class ReflectionVerdict(str, Enum):
    """Verdict on answer quality."""
    HIGH_CONFIDENCE = "high_confidence"   # Answer is good, no retry needed
    LOW_CONFIDENCE = "low_confidence"     # Answer needs improvement
    NO_CONTEXT = "no_context"            # No relevant context found
    CONTRADICTORY = "contradictory"      # Sources contradict each other


@dataclass
class ReflectionResult:
    """Result of reflection evaluation."""
    verdict: ReflectionVerdict
    confidence: float
    reasoning: str
    suggested_query: str | None = None
    suggested_strategy: str | None = None
    retry_count: int = 0


@dataclass
class ReflectionConfig:
    """Configuration for reflection loop."""
    max_retries: int = 2
    confidence_threshold: float = 0.6
    enabled: bool = True


# System prompt for reflection evaluation
REFLECTION_EVALUATE_PROMPT = """You are an AI answer quality evaluator. Given a query, retrieved context, and generated answer, determine if the answer is satisfactory.

Response format (JSON):
{
  "verdict": "<high_confidence|low_confidence|no_context|contradictory>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>",
  "suggested_query": "<improved query if low confidence, null otherwise>",
  "suggested_strategy": "<retry strategy: broaden|narrow|rephrase|expand_context|null>"
}

Verdict guidelines:
- high_confidence: Answer is complete, accurate, and well-supported by context
- low_confidence: Answer is incomplete, uncertain, or could be improved
- no_context: Retrieved context is not relevant to the query
- contradictory: Sources provide conflicting information

Strategy guidelines:
- broaden: Use more general terms, increase top_k
- narrow: Use more specific terms, add filters
- rephrase: Rephrase the query for better retrieval
- expand_context: Search with multiple query variations
- null: No retry needed

Be concise and accurate.
"""


# System prompt for query transformation
QUERY_TRANSFORM_PROMPT = """You are an AI query optimizer. Given a query and a retry strategy, transform the query to improve retrieval.

Response format (JSON):
{
  "transformed_query": "<improved query>",
  "reasoning": "<brief explanation>"
}

Strategies:
- broaden: Make query more general, remove specific terms
- narrow: Make query more specific, add constraints
- rephrase: Rephrase for clarity while keeping meaning
- expand_context: Create alternative phrasings for multi-query retrieval

Be concise. Keep the core intent of the original query.
"""


async def _call_llm(
    system_prompt: str,
    user_message: str,
    api_key: str,
    model: str,
) -> dict | None:
    """Call LLM for reflection evaluation."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "ContextOS Reflection",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

            if response.status_code != 200:
                logger.warning(f"Reflection LLM failed: {response.status_code}")
                return None

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content)

    except Exception as e:
        logger.warning(f"Reflection LLM error: {e}")
        return None


async def evaluate_answer(
    query: str,
    context: str,
    answer: str,
    api_key: str,
    model: str,
) -> ReflectionResult:
    """
    Evaluate answer quality using LLM reflection.

    Args:
        query: Original user query
        context: Retrieved context used for answer
        answer: Generated answer
        api_key: LLM API key
        model: LLM model name

    Returns:
        ReflectionResult with verdict and suggestions
    """
    user_message = f"""Query: {query}

Retrieved Context:
{context[:2000]}

Generated Answer:
{answer}

Evaluate this answer quality."""

    llm_response = await _call_llm(REFLECTION_EVALUATE_PROMPT, user_message, api_key, model)

    if not llm_response:
        # Default to high confidence if LLM fails
        return ReflectionResult(
            verdict=ReflectionVerdict.HIGH_CONFIDENCE,
            confidence=0.7,
            reasoning="Reflection evaluation unavailable, proceeding with answer",
        )

    verdict_str = llm_response.get("verdict", "high_confidence")
    verdict_map = {
        "high_confidence": ReflectionVerdict.HIGH_CONFIDENCE,
        "low_confidence": ReflectionVerdict.LOW_CONFIDENCE,
        "no_context": ReflectionVerdict.NO_CONTEXT,
        "contradictory": ReflectionVerdict.CONTRADICTORY,
    }
    verdict = verdict_map.get(verdict_str, ReflectionVerdict.HIGH_CONFIDENCE)

    return ReflectionResult(
        verdict=verdict,
        confidence=float(llm_response.get("confidence", 0.5)),
        reasoning=llm_response.get("reasoning", ""),
        suggested_query=llm_response.get("suggested_query"),
        suggested_strategy=llm_response.get("suggested_strategy"),
    )


async def transform_query(
    query: str,
    strategy: str,
    api_key: str,
    model: str,
) -> str:
    """
    Transform query based on retry strategy.

    Args:
        query: Original query
        strategy: Retry strategy (broaden, narrow, rephrase, expand_context)
        api_key: LLM API key
        model: LLM model name

    Returns:
        Transformed query string
    """
    user_message = f"""Original query: {query}
Strategy: {strategy}

Transform the query to improve retrieval."""

    llm_response = await _call_llm(QUERY_TRANSFORM_PROMPT, user_message, api_key, model)

    if not llm_response:
        return query

    return llm_response.get("transformed_query", query)


async def reflection_search(
    query: str,
    search_fn,
    generate_answer_fn,
    api_key: str,
    model: str,
    config: Optional[ReflectionConfig] = None,
) -> tuple[str, ReflectionResult]:
    """
    Execute search with reflection loop.

    Args:
        query: User query
        search_fn: Async function(query) -> context string
        generate_answer_fn: Async function(query, context) -> answer string
        api_key: LLM API key
        model: LLM model name
        config: Reflection configuration

    Returns:
        Tuple of (final answer, last reflection result)
    """
    config = config or ReflectionConfig()

    if not config.enabled:
        context = await search_fn(query)
        answer = await generate_answer_fn(query, context)
        return answer, ReflectionResult(
            verdict=ReflectionVerdict.HIGH_CONFIDENCE,
            confidence=1.0,
            reasoning="Reflection disabled",
        )

    current_query = query
    last_reflection = None

    for attempt in range(config.max_retries + 1):
        # Search
        context = await search_fn(current_query)

        # Generate answer
        answer = await generate_answer_fn(current_query, context)

        # Reflect on quality
        reflection = await evaluate_answer(
            query=query,  # Always evaluate against original query
            context=context,
            answer=answer,
            api_key=api_key,
            model=model,
        )
        reflection.retry_count = attempt

        last_reflection = reflection

        # If high confidence or max retries reached, return
        if reflection.verdict == ReflectionVerdict.HIGH_CONFIDENCE:
            logger.info(f"Reflection: high confidence after {attempt} retries")
            return answer, reflection

        if attempt >= config.max_retries:
            logger.info(f"Reflection: max retries ({config.max_retries}) reached")
            return answer, reflection

        # Transform query for retry
        strategy = reflection.suggested_strategy or "rephrase"
        if reflection.suggested_query:
            current_query = reflection.suggested_query
        else:
            current_query = await transform_query(
                query=current_query,
                strategy=strategy,
                api_key=api_key,
                model=model,
            )

        logger.info(
            f"Reflection: retry {attempt + 1}/{config.max_retries}, "
            f"strategy={strategy}, new_query={current_query[:50]}..."
        )

    return answer, last_reflection
