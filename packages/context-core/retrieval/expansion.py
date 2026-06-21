"""
HyDE Query Expansion — Hypothetical Document Embeddings.

Generates a hypothetical answer to the query, then uses that answer's
embedding for retrieval instead of the query embedding.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class HyDEConfig:
    """Configuration for HyDE query expansion."""
    enabled: bool = True
    num_variants: int = 1  # Number of hypothetical documents to generate
    max_answer_length: int = 200  # Max words in hypothetical answer
    combine_strategy: str = "average"  # average, concatenate, best


@dataclass
class HyDEResult:
    """Result of HyDE expansion."""
    original_query: str
    expanded_queries: list[str]
    hypothetical_answers: list[str]
    strategy_used: str


# System prompt for generating hypothetical answers
HYPOTHETICAL_PROMPT = """You are a helpful AI assistant. Given a user query, generate a brief, factual answer that would be found in a document answering this query.

Rules:
1. Write as if you're quoting from a document
2. Be factual and specific
3. Keep it under {max_words} words
4. Use natural, document-like language
5. Include relevant details and context

Query: {query}

Generate a hypothetical answer:"""


# System prompt for query expansion
EXPANSION_PROMPT = """You are a search query optimizer. Given a user query, generate alternative search queries that would help find relevant information.

Rules:
1. Generate {num_variants} alternative queries
2. Each query should approach the topic from a different angle
3. Use synonyms and related terms
4. Keep queries concise and search-friendly

Original query: {query}

Generate alternative queries (JSON format):
{{
  "queries": ["<query1>", "<query2>", ...]
}}"""


class HyDEExpansion:
    """HyDE query expansion service."""

    def __init__(self, config: Optional[HyDEConfig] = None):
        self.config = config or HyDEConfig()

    async def expand_query(
        self,
        query: str,
        api_key: str,
        model: str,
    ) -> HyDEResult:
        """
        Expand a query using HyDE.

        Args:
            query: Original user query
            api_key: LLM API key
            model: LLM model name

        Returns:
            HyDEResult with expanded queries and hypothetical answers
        """
        if not self.config.enabled:
            return HyDEResult(
                original_query=query,
                expanded_queries=[query],
                hypothetical_answers=[],
                strategy_used="none",
            )

        # Generate hypothetical answers
        hypothetical_answers = await self._generate_hypothetical_answers(
            query, api_key, model
        )

        # Generate alternative queries
        alternative_queries = await self._generate_alternative_queries(
            query, api_key, model
        )

        # Combine based on strategy
        expanded_queries = self._combine_queries(
            query, alternative_queries, hypothetical_answers
        )

        return HyDEResult(
            original_query=query,
            expanded_queries=expanded_queries,
            hypothetical_answers=hypothetical_answers,
            strategy_used=self.config.combine_strategy,
        )

    async def _generate_hypothetical_answers(
        self,
        query: str,
        api_key: str,
        model: str,
    ) -> list[str]:
        """Generate hypothetical answers to the query."""
        answers = []

        for _ in range(self.config.num_variants):
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "ContextOS HyDE",
                }

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": HYPOTHETICAL_PROMPT.format(
                                query=query,
                                max_words=self.config.max_answer_length,
                            ),
                        },
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                }

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        OPENROUTER_URL, headers=headers, json=payload
                    )

                    if response.status_code == 200:
                        result = response.json()
                        answer = result["choices"][0]["message"]["content"].strip()
                        answers.append(answer)
                    else:
                        logger.warning(f"HyDE answer generation failed: {response.status_code}")

            except Exception as e:
                logger.warning(f"HyDE answer generation error: {e}")

        return answers

    async def _generate_alternative_queries(
        self,
        query: str,
        api_key: str,
        model: str,
    ) -> list[str]:
        """Generate alternative search queries."""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "ContextOS HyDE",
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a search query optimizer."},
                    {
                        "role": "user",
                        "content": EXPANSION_PROMPT.format(
                            query=query,
                            num_variants=self.config.num_variants,
                        ),
                    },
                ],
                "temperature": 0.5,
                "max_tokens": 300,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

                if response.status_code != 200:
                    return []

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                data = json.loads(content)
                return data.get("queries", [])

        except Exception as e:
            logger.warning(f"HyDE query generation error: {e}")
            return []

    def _combine_queries(
        self,
        original_query: str,
        alternative_queries: list[str],
        hypothetical_answers: list[str],
    ) -> list[str]:
        """Combine original, alternative, and hypothetical queries."""
        combined = [original_query]

        if self.config.combine_strategy == "average":
            # Add alternatives and answers as separate queries
            combined.extend(alternative_queries[:self.config.num_variants])
            # Use hypothetical answers as queries (key HyDE idea)
            combined.extend(hypothetical_answers[:self.config.num_variants])

        elif self.config.combine_strategy == "concatenate":
            # Concatenate all into one query
            all_parts = [original_query] + alternative_queries + hypothetical_answers
            combined = [" ".join(all_parts)]

        elif self.config.combine_strategy == "best":
            # Just use original + best alternative
            combined.extend(alternative_queries[:1])

        return combined[:self.config.num_variants * 2 + 1]  # Limit total


async def hyde_expand_and_search(
    query: str,
    search_fn,
    api_key: str,
    model: str,
    config: Optional[HyDEConfig] = None,
) -> tuple[list[str], HyDEResult]:
    """
    Expand query with HyDE and search with all variants.

    Args:
        query: Original user query
        search_fn: Async function(query) -> results
        api_key: LLM API key
        model: LLM model name
        config: HyDE configuration

    Returns:
        Tuple of (combined results, HyDE result)
    """
    hyde = HyDEExpansion(config)
    hyde_result = await hyde.expand_query(query, api_key, model)

    # Search with all expanded queries
    all_results = []
    for expanded_query in hyde_result.expanded_queries:
        results = await search_fn(expanded_query)
        all_results.extend(results)

    # Deduplicate results (simple approach)
    seen_ids = set()
    unique_results = []
    for result in all_results:
        result_id = getattr(result, "id", None) or id(result)
        if result_id not in seen_ids:
            seen_ids.add(result_id)
            unique_results.append(result)

    return unique_results, hyde_result
