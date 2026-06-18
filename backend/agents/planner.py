# agents/planner.py
"""
Planner Layer — Intent detection, query classification, and task planning.

Every request passes through the Planner before routing to agents.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
    """Create an execution plan from a user query."""
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
