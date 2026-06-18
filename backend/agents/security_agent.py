# agents/security_agent.py
"""
Security Agent — Prompt injection detection, context validation, source trust analysis, tool permission validation.

Responsibilities:
- Detect prompt injection attempts
- Validate context integrity
- Analyze source trustworthiness
- Validate tool permissions based on scopes
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)

# Prompt injection patterns
INJECTION_PATTERNS = [
    r'ignore (?:all |previous |prior |your )?(?:instructions|prompts|rules)',
    r'you are now',
    r'act as',
    r'pretend (?:to be|you are)',
    r'disregard',
    r'override',
    r'system prompt',
    r'jailbreak',
    r'DAN mode',
    r'forget everything',
    r'new instructions',
    r'override instructions',
]

# Scope requirements for different actions
SCOPE_REQUIREMENTS = {
    "scrape": ["crawl:scrape"],
    "crawl": ["crawl:scrape"],
    "map": ["crawl:map"],
    "search": ["crawl:search"],
    "extract": ["crawl:scrape"],
    "research": ["crawl:search", "crawl:scrape"],
}


async def security_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute security validation steps."""
    if step.action == TaskAction.EXTRACT:
        return await _validate_security(context)
    return AgentResult(agent="security", action=step.action.value, data=None)


async def _validate_security(context: RouteContext) -> AgentResult:
    """Validate request security."""
    start = time.time()
    issues = []
    
    # Check for prompt injection
    injection_detected = _check_injection(context.query)
    if injection_detected:
        issues.append({
            "type": "injection",
            "severity": "high",
            "message": "Potential prompt injection detected",
        })
    
    # Validate scope permissions
    scope_issues = _check_scopes(context)
    issues.extend(scope_issues)
    
    # Source trust analysis
    trust_score = _analyze_trust(context)
    
    is_safe = len([i for i in issues if i.get("severity") == "high"]) == 0
    
    return AgentResult(
        agent="security",
        action="validate",
        data={
            "safe": is_safe,
            "issues": issues,
            "trust_score": trust_score,
        },
        confidence=1.0 if is_safe else 0.3,
        elapsed_ms=(time.time() - start) * 1000,
    )


def _check_injection(query: str) -> bool:
    """Check for prompt injection patterns."""
    query_lower = query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    return False


def _check_scopes(context: RouteContext) -> list[dict]:
    """Check if user has required scopes."""
    issues = []
    for action, required_scopes in SCOPE_REQUIREMENTS.items():
        has_scope = any(s in context.scopes for s in required_scopes)
        if not has_scope:
            issues.append({
                "type": "scope",
                "severity": "medium",
                "action": action,
                "required": required_scopes,
                "message": f"Missing scope for {action}: {required_scopes}",
            })
    return issues


def _analyze_trust(context: RouteContext) -> float:
    """Analyze trust score based on sources."""
    trust = 1.0
    
    # Lower trust for web sources vs local documents
    web_sources = sum(1 for s in context.citations if s.get("type") in ("web_search", "scrape"))
    doc_sources = sum(1 for s in context.citations if s.get("type") == "document")
    
    if web_sources > 0 and doc_sources == 0:
        trust *= 0.7
    if web_sources > doc_sources:
        trust *= 0.8
    
    return trust
