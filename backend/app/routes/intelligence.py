# app/routes/intelligence.py
"""
Unified Intelligence Endpoint — Orchestrates all agents through Planner → Router → Agents → Output.

POST /api/intelligence/query — Main entry point for all intelligent queries
GET  /api/intelligence/plan — Preview plan without execution
GET  /api/intelligence/stats — Knowledge graph statistics
"""

from __future__ import annotations

import json
import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.planner import create_plan, QueryType
from agents.router import AgentRegistry, Router, RouteContext, AgentResult
from agents.retrieval_agent import retrieval_executor
from agents.memory_agent import memory_executor
from agents.research_agent import research_executor
from agents.knowledge_agent import knowledge_executor
from agents.citation_agent import citation_executor
from agents.security_agent import security_executor
from agents.workflow_agent import workflow_executor
from services.knowledge_graph import store_extraction, get_stats
from app.auth_middleware import require_scope, AuthContext
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

# Build agent registry
_registry = AgentRegistry()
_registry.register("retrieval", retrieval_executor)
_registry.register("memory", memory_executor)
_registry.register("research", research_executor)
_registry.register("knowledge", knowledge_executor)
_registry.register("citation", citation_executor)
_registry.register("security", security_executor)
_registry.register("workflow", workflow_executor)

_router = Router(_registry)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    doc_id: str | None = None
    conversation_id: str | None = None
    mode: str = Field(default="auto", description="auto, plan, execute")


class PlanPreview(BaseModel):
    query_type: str
    steps: list[dict]
    confidence: float
    reasoning: str
    required_agents: list[str]


class IntelligenceResponse(BaseModel):
    query: str
    query_type: str
    answer: str | None = None
    confidence: float
    sources: list[dict]
    entities: list[dict]
    relationships: list[dict]
    citations: list[dict]
    plan: dict
    execution_time_ms: float
    agents_used: list[str]


def _extract_answer(results: list[AgentResult], context: RouteContext) -> str:
    """Extract the final answer from agent results."""
    # Look for answer results
    for result in results:
        if result.action in ("answer", "synthesize", "present"):
            data = result.data or {}
            if isinstance(data, dict):
                return data.get("context", data.get("answer", ""))
            return str(data)
    
    # Fallback: combine all data
    parts = []
    for result in results:
        if result.data and isinstance(result.data, dict):
            for key in ("context", "memory_context", "answer", "summary"):
                if key in result.data and result.data[key]:
                    parts.append(str(result.data[key]))
    
    return "\n\n".join(parts) if parts else "No answer generated."


def _build_sse_event(event_type: str, data: dict) -> str:
    """Build SSE event string."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def _stream_intelligence(
    request: QueryRequest,
    auth: AuthContext,
) -> AsyncIterator[str]:
    """Stream intelligence pipeline execution as SSE events."""
    start = time.time()
    
    # Step 1: Security check
    yield _build_sse_event("step", {"step": "security", "status": "running"})
    
    security_context = RouteContext(
        query=request.query,
        user_id=auth.user_id,
        scopes=auth.scopes,
    )
    from agents.security_agent import security_executor
    from agents.planner import PlanStep, TaskAction
    
    security_step = PlanStep(
        action=TaskAction.EXTRACT,
        description="Validate request security",
        agent="security",
    )
    security_result = await security_executor(security_step, security_context)
    
    if not security_result.data.get("safe", True):
        yield _build_sse_event("error", {
            "message": "Request failed security validation",
            "issues": security_result.data.get("issues", []),
        })
        return
    
    yield _build_sse_event("step", {"step": "security", "status": "complete", "elapsed_ms": security_result.elapsed_ms})
    
    # Step 2: Plan
    yield _build_sse_event("step", {"step": "planner", "status": "running"})
    
    plan = create_plan(request.query)
    
    yield _build_sse_event("plan", {
        "query_type": plan.query_type.value,
        "steps": [{"action": s.action.value, "agent": s.agent, "description": s.description} for s in plan.steps],
        "confidence": plan.confidence,
        "reasoning": plan.reasoning,
    })
    yield _build_sse_event("step", {"step": "planner", "status": "complete"})
    
    # Step 3: Execute plan
    yield _build_sse_event("step", {"step": "router", "status": "running"})
    
    context = RouteContext(
        query=request.query,
        user_id=auth.user_id,
        conversation_id=request.conversation_id,
        doc_id=request.doc_id,
        scopes=auth.scopes,
    )
    
    results = await _router.execute_plan(plan, context)
    yield _build_sse_event("step", {"step": "router", "status": "complete"})
    
    # Step 4: Store knowledge
    yield _build_sse_event("step", {"step": "knowledge_store", "status": "running"})
    
    if context.extracted_entities or context.extracted_relationships:
        try:
            kg_result = store_extraction(
                entities=context.extracted_entities,
                relationships=context.extracted_relationships,
                user_id=auth.user_id,
            )
            yield _build_sse_event("knowledge_stored", kg_result)
        except Exception as e:
            logger.warning(f"Knowledge storage failed: {e}")
    
    yield _build_sse_event("step", {"step": "knowledge_store", "status": "complete"})
    
    # Step 5: Build response
    answer = _extract_answer(results, context)
    
    response = IntelligenceResponse(
        query=request.query,
        query_type=plan.query_type.value,
        answer=answer,
        confidence=plan.confidence,
        sources=[s for r in results for s in r.sources],
        entities=context.extracted_entities,
        relationships=context.extracted_relationships,
        citations=context.citations,
        plan={
            "query_type": plan.query_type.value,
            "steps": len(plan.steps),
            "reasoning": plan.reasoning,
        },
        execution_time_ms=(time.time() - start) * 1000,
        agents_used=plan.required_agents,
    )
    
    yield _build_sse_event("result", response.model_dump())
    yield _build_sse_event("done", {"elapsed_ms": response.execution_time_ms})


@router.post("/query")
async def intelligence_query(
    body: QueryRequest,
    auth: AuthContext = Depends(require_scope("rag")),
    request: Request = None,
):
    """
    Main intelligence endpoint. Accepts any query and routes it through the agent pipeline.
    
    - Security validation
    - Intent classification
    - Multi-agent execution
    - Knowledge storage
    - Structured response
    """
    settings = get_settings()
    
    async def event_generator():
        async for event in _stream_intelligence(body, auth):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/plan", response_model=PlanPreview)
async def preview_plan(
    body: QueryRequest,
    auth: AuthContext = Depends(require_scope("rag")),
):
    """Preview the execution plan without running it."""
    plan = create_plan(body.query)
    return PlanPreview(
        query_type=plan.query_type.value,
        steps=[
            {
                "action": s.action.value,
                "agent": s.agent,
                "description": s.description,
                "priority": s.priority,
                "depends_on": s.depends_on,
            }
            for s in plan.steps
        ],
        confidence=plan.confidence,
        reasoning=plan.reasoning,
        required_agents=plan.required_agents,
    )


@router.get("/stats")
async def knowledge_graph_stats(
    auth: AuthContext = Depends(require_scope("rag")),
):
    """Get knowledge graph statistics."""
    return get_stats()


@router.get("/health")
async def intelligence_health():
    """Health check for intelligence system."""
    return {
        "status": "ok",
        "agents": _registry.available,
        "planner": "ready",
        "router": "ready",
    }
