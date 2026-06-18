# agents/router.py
"""
Routing Layer — Selects the correct agent execution path based on the Plan.

Routes queries to the appropriate agents and orchestrates multi-agent workflows.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Optional

from .planner import Plan, PlanStep, QueryType, TaskAction

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    agent: str
    action: str
    data: Any
    confidence: float = 0.0
    sources: list[dict] = field(default_factory=list)
    entities: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    elapsed_ms: float = 0.0
    error: str | None = None


@dataclass
class RouteContext:
    """Shared context passed between agents during execution."""
    query: str
    user_id: str
    conversation_id: str | None = None
    doc_id: str | None = None
    session_token: str | None = None
    scopes: list[str] = field(default_factory=list)
    
    # Accumulated results from agents
    results: list[AgentResult] = field(default_factory=list)
    
    # Shared state
    retrieved_chunks: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    search_results: list[dict] = field(default_factory=list)
    scraped_content: str = ""
    extracted_entities: list[dict] = field(default_factory=list)
    extracted_relationships: list[dict] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    
    def add_result(self, result: AgentResult):
        self.results.append(result)
    
    def get_result_by_agent(self, agent: str) -> AgentResult | None:
        for r in reversed(self.results):
            if r.agent == agent:
                return r
        return None


class AgentRegistry:
    """Registry of available agent executors."""
    
    def __init__(self):
        self._agents: dict[str, Callable] = {}
    
    def register(self, name: str, executor: Callable):
        self._agents[name] = executor
    
    def get(self, name: str) -> Callable | None:
        return self._agents.get(name)
    
    @property
    def available(self) -> list[str]:
        return list(self._agents.keys())


class Router:
    """
    Routes queries to agents based on the Plan.
    
    Handles:
    - Single agent execution
    - Multi-agent orchestration
    - Dependency resolution
    - Parallel execution where possible
    - Error recovery
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
    
    async def execute_plan(self, plan: Plan, context: RouteContext) -> list[AgentResult]:
        """Execute a plan by routing steps to appropriate agents."""
        results = []
        
        # Sort steps by priority
        sorted_steps = sorted(plan.steps, key=lambda s: s.priority)
        
        # Group by dependency level for parallel execution
        levels = self._resolve_dependencies(sorted_steps)
        
        for level in levels:
            # Execute steps in this level (can be parallel)
            tasks = []
            for step in level:
                executor = self.registry.get(step.agent)
                if executor is None:
                    logger.warning(f"No executor registered for agent: {step.agent}")
                    results.append(AgentResult(
                        agent=step.agent,
                        action=step.action.value,
                        data=None,
                        error=f"No executor for agent: {step.agent}",
                    ))
                    continue
                
                tasks.append(self._execute_step(step, executor, context))
            
            # Run level's tasks concurrently
            if tasks:
                level_results = await asyncio.gather(*tasks, return_exceptions=True)
                for r in level_results:
                    if isinstance(r, Exception):
                        logger.error(f"Step failed: {r}")
                        continue
                    if r is not None:
                        results.append(r)
                        context.add_result(r)
        
        return results
    
    async def _execute_step(
        self, step: PlanStep, executor: Callable, context: RouteContext
    ) -> AgentResult | None:
        """Execute a single plan step."""
        start = time.time()
        try:
            result = await executor(step, context)
            if result is not None:
                result.elapsed_ms = (time.time() - start) * 1000
                return result
        except Exception as e:
            logger.error(f"Agent {step.agent} failed on {step.action.value}: {e}")
            return AgentResult(
                agent=step.agent,
                action=step.action.value,
                data=None,
                error=str(e),
                elapsed_ms=(time.time() - start) * 1000,
            )
        return None
    
    def _resolve_dependencies(self, steps: list[PlanStep]) -> list[list[PlanStep]]:
        """Resolve step dependencies into execution levels."""
        if not steps:
            return []
        
        step_map = {i: s for i, s in enumerate(steps)}
        completed = set()
        levels = []
        
        while len(completed) < len(steps):
            level = []
            for i, step in enumerate(steps):
                if i in completed:
                    continue
                # Check if all dependencies are met
                deps_met = all(d in completed for d in step.depends_on)
                if deps_met:
                    level.append(step)
            
            if not level:
                # Circular dependency or error — execute remaining in order
                level = [s for i, s in enumerate(steps) if i not in completed]
            
            levels.append(level)
            for s in level:
                idx = steps.index(s)
                completed.add(idx)
        
        return levels
