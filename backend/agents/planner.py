# agents/planner.py
"""
Planner Layer — Intent detection, query classification, and task planning.

Every request passes through the Planner before routing to agents.

Uses LLM-based planning with keyword fallback for better accuracy.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class QueryType(str, Enum):
    DOCUMENT = "document"
    MEMORY = "memory"
    RESEARCH = "research"
    KNOWLEDGE = "knowledge"
    WORKFLOW = "workflow"
    MONITORING = "monitoring"
    HYBRID = "hybrid"
    GENERAL = "general"


class TaskAction(str, Enum):
    RETRIEVE = "retrieve"
    SEARCH = "search"
    SCRAPE = "scrape"
    CRAWL = "crawl"
    MAP = "map"
    EXTRACT = "extract"
    REMEMBER = "remember"
    FORGET = "forget"
    RESEARCH = "research"
    ANALYZE = "analyze"
    MONITOR = "monitor"
    ANSWER = "answer"


@dataclass
class PlanStep:
    action: TaskAction
    description: str
    agent: str
    priority: int = 0
    params: dict = field(default_factory=dict)
    depends_on: list[int] = field(default_factory=list)


@dataclass
class Plan:
    query_type: QueryType
    steps: list[PlanStep]
    original_query: str
    refined_query: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    
    @property
    def required_agents(self) -> list[str]:
        return list(dict.fromkeys(s.agent for s in self.steps))


# Keyword patterns for intent detection
DOCUMENT_KEYWORDS = {
    "upload", "pdf", "document", "file", "chunk", "embed", "pipeline",
    "ingest", "parse", "extract text", "read file", "my document",
    "uploaded", "this pdf", "the document", "the file",
}

MEMORY_KEYWORDS = {
    "remember", "recall", "memory", "forgot", "previously", "before",
    "last time", "we discussed", "you said", "i said", "my preference",
    "my name", "who am i", "what do i", "profile", "save this",
    "don't forget", "store this", "my info",
}

RESEARCH_KEYWORDS = {
    "search", "find", "look up", "research", "investigate", "compare",
    "what is", "who is", "how does", "latest", "news", "recent",
    "scrape", "crawl", "website", "web page", "url", "http",
    "open source", "github", "alternative", "vs", "versus",
    "best tools", "top", "leading", "market",
}

WORKFLOW_KEYWORDS = {
    "schedule", "monitor", "watch", "track", "background", "job",
    "automate", "repeat", "daily", "weekly", "alert", "notify",
    "pipeline", "workflow", "task",
}

EXTRACT_KEYWORDS = {
    "extract", "pull out", "get data", "structured", "entities",
    "company name", "pricing", "founders", "contacts", "emails",
    "phone", "addresses", "dates", "amounts", "specific data",
}


def _classify_query(query: str) -> tuple[QueryType, float, str]:
    """Classify query type with confidence score."""
    query_lower = query.lower()
    
    scores = {qt: 0.0 for qt in QueryType}
    reasons = []
    
    # Check document keywords
    doc_hits = sum(1 for kw in DOCUMENT_KEYWORDS if kw in query_lower)
    if doc_hits:
        scores[QueryType.DOCUMENT] += doc_hits * 0.3
        reasons.append(f"document keywords: {doc_hits}")
    
    # Check memory keywords
    mem_hits = sum(1 for kw in MEMORY_KEYWORDS if kw in query_lower)
    if mem_hits:
        scores[QueryType.MEMORY] += mem_hits * 0.4
        reasons.append(f"memory keywords: {mem_hits}")
    
    # Check research keywords
    res_hits = sum(1 for kw in RESEARCH_KEYWORDS if kw in query_lower)
    if res_hits:
        scores[QueryType.RESEARCH] += res_hits * 0.25
        reasons.append(f"research keywords: {res_hits}")
    
    # Check workflow keywords
    wf_hits = sum(1 for kw in WORKFLOW_KEYWORDS if kw in query_lower)
    if wf_hits:
        scores[QueryType.WORKFLOW] += wf_hits * 0.35
        reasons.append(f"workflow keywords: {wf_hits}")
    
    # Check extract keywords
    ext_hits = sum(1 for kw in EXTRACT_KEYWORDS if kw in query_lower)
    if ext_hits:
        scores[QueryType.KNOWLEDGE] += ext_hits * 0.3
        reasons.append(f"extract keywords: {ext_hits}")
    
    # URL detection boosts research
    if re.search(r'https?://', query_lower):
        scores[QueryType.RESEARCH] += 0.5
        reasons.append("URL detected")
    
    # Determine winner
    best_type = max(scores, key=lambda k: scores[k])
    best_score = scores[best_type]
    
    # Check for hybrid (multiple strong signals)
    strong = [qt for qt, s in scores.items() if s > 0.3 and qt != best_type]
    if strong:
        best_type = QueryType.HYBRID
        reasons.append(f"hybrid: multiple signals ({best_type.value} + {', '.join(q.value for q in strong)})")
    
    # Fallback to general
    if best_score < 0.2:
        best_type = QueryType.GENERAL
        reasons.append("no strong signal, defaulting to general")
    
    confidence = min(best_score / 1.5, 1.0)
    reasoning = "; ".join(reasons) if reasons else "default classification"
    
    return best_type, confidence, reasoning


def _plan_steps(query_type: QueryType, query: str) -> list[PlanStep]:
    """Generate execution steps based on query type."""
    steps = []
    
    if query_type == QueryType.DOCUMENT:
        steps.append(PlanStep(
            action=TaskAction.RETRIEVE,
            description="Retrieve relevant chunks from uploaded documents",
            agent="retrieval",
            priority=1,
        ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Generate answer from retrieved context",
            agent="retrieval",
            priority=2,
            depends_on=[0],
        ))
    
    elif query_type == QueryType.MEMORY:
        steps.append(PlanStep(
            action=TaskAction.RETRIEVE,
            description="Retrieve relevant memories and preferences",
            agent="memory",
            priority=1,
        ))
        # Check if it's a "store" request
        store_triggers = {"remember", "save", "store", "don't forget", "keep this"}
        if any(t in query.lower() for t in store_triggers):
            steps.append(PlanStep(
                action=TaskAction.REMEMBER,
                description="Extract and store new memory",
                agent="memory",
                priority=2,
            ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Generate answer from memory context",
            agent="memory",
            priority=3,
            depends_on=[0],
        ))
    
    elif query_type == QueryType.RESEARCH:
        steps.append(PlanStep(
            action=TaskAction.SEARCH,
            description="Search the web for relevant information",
            agent="research",
            priority=1,
        ))
        # If URL is present, scrape it
        if re.search(r'https?://', query):
            steps.append(PlanStep(
                action=TaskAction.SCRAPE,
                description="Scrape the provided URL for content",
                agent="research",
                priority=2,
            ))
        steps.append(PlanStep(
            action=TaskAction.EXTRACT,
            description="Extract structured information from results",
            agent="knowledge",
            priority=3,
            depends_on=[0, 1] if len(steps) > 1 else [0],
        ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Synthesize research into comprehensive answer",
            agent="research",
            priority=4,
            depends_on=[len(steps) - 1],
        ))
    
    elif query_type == QueryType.KNOWLEDGE:
        steps.append(PlanStep(
            action=TaskAction.EXTRACT,
            description="Extract entities and relationships from content",
            agent="knowledge",
            priority=1,
        ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Present extracted knowledge with structure",
            agent="knowledge",
            priority=2,
            depends_on=[0],
        ))
    
    elif query_type == QueryType.WORKFLOW:
        steps.append(PlanStep(
            action=TaskAction.MONITOR,
            description="Set up or check monitoring workflow",
            agent="workflow",
            priority=1,
        ))
    
    elif query_type == QueryType.HYBRID:
        # Combine research + retrieval
        steps.append(PlanStep(
            action=TaskAction.SEARCH,
            description="Search web for external context",
            agent="research",
            priority=1,
        ))
        steps.append(PlanStep(
            action=TaskAction.RETRIEVE,
            description="Retrieve from local documents and memory",
            agent="retrieval",
            priority=1,
        ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Synthesize all sources into unified answer",
            agent="research",
            priority=3,
            depends_on=[0, 1],
        ))
    
    else:  # GENERAL
        steps.append(PlanStep(
            action=TaskAction.RETRIEVE,
            description="Check memory and documents for context",
            agent="memory",
            priority=1,
        ))
        steps.append(PlanStep(
            action=TaskAction.ANSWER,
            description="Generate helpful response",
            agent="retrieval",
            priority=2,
            depends_on=[0],
        ))
    
    return steps


def create_plan(query: str) -> Plan:
    """Create an execution plan from a user query (keyword-based)."""
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


async def create_plan_async(query: str) -> Plan:
    """
    Create an execution plan using LLM with keyword fallback.
    
    This is the recommended entry point for production use.
    It tries LLM-based planning first, then falls back to keywords.
    """
    from app.config import get_settings
    
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
