"""
LLM-based Planner — Uses OpenRouter for intelligent query classification and planning.

Replaces keyword-based classification with LLM reasoning for better accuracy.
Falls back to keyword-based if LLM is unavailable or fails.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

import httpx

from app.config import get_settings
from agents.planner import Plan, PlanStep, QueryType, TaskAction, _classify_query, _plan_steps

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# System prompt for the planner LLM
PLANNER_SYSTEM_PROMPT = """You are an AI query planner. Your job is to analyze user queries and create execution plans.

Given a user query, you must:
1. Classify the query type (document, memory, research, knowledge, workflow, hybrid, general)
2. Determine the confidence level (0.0 to 1.0)
3. Generate a step-by-step execution plan
4. Provide reasoning for your decisions

Response format (JSON):
{
  "query_type": "<type>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>",
  "refined_query": "<improved query if needed>",
  "steps": [
    {
      "action": "<action>",
      "description": "<what to do>",
      "agent": "<agent name>",
      "priority": <1-10>,
      "params": {},
      "depends_on": [<indices of dependencies>]
    }
  ]
}

Available query types:
- document: User asking about uploaded documents/files
- memory: User wants to remember/recall something
- research: User needs web search or external information
- knowledge: User wants to extract entities/relationships
- workflow: User wants to automate/monitor something
- hybrid: Query spans multiple types
- general: Default/fallback

Available actions:
- retrieve: Get data from documents/memory
- search: Web search
- scrape: Extract content from URL
- crawl: Crawl website
- map: Map website structure
- extract: Extract structured data
- remember: Store new memory
- forget: Delete memory
- research: Research topic
- analyze: Analyze content
- monitor: Set up monitoring
- answer: Generate response

Available agents:
- memory: Memory operations
- research: Web research
- knowledge: Knowledge graph
- retrieval: Document retrieval
- workflow: Automation
- security: Security checks

Be concise and accurate. Focus on the most relevant actions.
"""


async def _call_llm_for_planning(query: str, api_key: str, model: str) -> dict | None:
    """Call LLM to generate a plan for the query."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "ContextOS Planner",
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Plan this query: {query}"}
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.warning(f"LLM planner failed: {response.status_code}")
                return None
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
            
    except Exception as e:
        logger.warning(f"LLM planner error: {e}")
        return None


def _parse_llm_plan(llm_response: dict, original_query: str) -> Plan | None:
    """Parse LLM response into a Plan object."""
    try:
        query_type_str = llm_response.get("query_type", "general")
        confidence = float(llm_response.get("confidence", 0.5))
        reasoning = llm_response.get("reasoning", "")
        refined_query = llm_response.get("refined_query", original_query)
        steps_data = llm_response.get("steps", [])
        
        # Map query type string to enum
        query_type_map = {
            "document": QueryType.DOCUMENT,
            "memory": QueryType.MEMORY,
            "research": QueryType.RESEARCH,
            "knowledge": QueryType.KNOWLEDGE,
            "workflow": QueryType.WORKFLOW,
            "hybrid": QueryType.HYBRID,
            "general": QueryType.GENERAL,
        }
        query_type = query_type_map.get(query_type_str, QueryType.GENERAL)
        
        # Parse steps
        steps = []
        for step_data in steps_data:
            action_str = step_data.get("action", "answer")
            action_map = {
                "retrieve": TaskAction.RETRIEVE,
                "search": TaskAction.SEARCH,
                "scrape": TaskAction.SCRAPE,
                "crawl": TaskAction.CRAWL,
                "map": TaskAction.MAP,
                "extract": TaskAction.EXTRACT,
                "remember": TaskAction.REMEMBER,
                "forget": TaskAction.FORGET,
                "research": TaskAction.RESEARCH,
                "analyze": TaskAction.ANALYZE,
                "monitor": TaskAction.MONITOR,
                "answer": TaskAction.ANSWER,
            }
            action = action_map.get(action_str, TaskAction.ANSWER)
            
            step = PlanStep(
                action=action,
                description=step_data.get("description", ""),
                agent=step_data.get("agent", "retrieval"),
                priority=int(step_data.get("priority", 1)),
                params=step_data.get("params", {}),
                depends_on=step_data.get("depends_on", []),
            )
            steps.append(step)
        
        if not steps:
            return None
        
        return Plan(
            query_type=query_type,
            steps=steps,
            original_query=original_query,
            refined_query=refined_query,
            confidence=confidence,
            reasoning=reasoning,
        )
        
    except Exception as e:
        logger.warning(f"Failed to parse LLM plan: {e}")
        return None


async def create_plan_with_llm(query: str) -> Plan:
    """
    Create an execution plan using LLM, with keyword fallback.
    
    1. Try LLM-based planning
    2. If LLM fails or is unavailable, fall back to keyword-based
    """
    settings = get_settings()
    
    # Try LLM planning if API key is available
    if settings.openrouter_api_key:
        llm_response = await _call_llm_for_planning(
            query, 
            settings.openrouter_api_key, 
            settings.openrouter_model
        )
        
        if llm_response:
            plan = _parse_llm_plan(llm_response, query)
            if plan:
                logger.info(f"LLM planned: {plan.query_type.value} with {len(plan.steps)} steps")
                return plan
    
    # Fallback to keyword-based planning
    logger.info("Using keyword-based planner fallback")
    query_type, confidence, reasoning = _classify_query(query)
    steps = _plan_steps(query_type, query)
    
    return Plan(
        query_type=query_type,
        steps=steps,
        original_query=query,
        refined_query=query,
        confidence=confidence,
        reasoning=reasoning,
    )
