# agents/memory_agent.py
"""
Memory Agent — Memory extraction, preference learning, context retrieval, memory ranking.

Responsibilities:
- Extract and store new memories from conversations
- Learn user preferences over time
- Retrieve relevant memories for context
- Rank memories by relevance and recency
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from services.memory_store import (
    get_profile_memories,
    get_recent_messages,
    maybe_store_profile_memory,
    upsert_profile_memory,
)
from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)

# Keywords that trigger memory storage
STORE_TRIGGERS = {
    "remember", "save", "store", "keep", "don't forget", "note that",
    "my name is", "i am", "i'm", "i work", "i like", "i prefer",
    "my email", "my phone", "i live", "my address",
}

FORGET_TRIGGERS = {"forget", "delete memory", "remove memory", "clear memory"}


async def memory_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute memory steps."""
    if step.action == TaskAction.RETRIEVE:
        return await _retrieve_memories(context)
    elif step.action == TaskAction.REMEMBER:
        return await _store_memory(context)
    elif step.action == TaskAction.ANSWER:
        return await _answer_with_memory(context)
    return AgentResult(agent="memory", action=step.action.value, data=None)


async def _retrieve_memories(context: RouteContext) -> AgentResult:
    """Retrieve relevant memories and preferences."""
    start = time.time()
    memories = []
    
    try:
        # Get recent conversation messages
        if context.conversation_id:
            recent = get_recent_messages(context.conversation_id, limit=10)
            memories.extend([{"type": "conversation", **m} for m in recent])
        
        # Get profile memories
        profile = get_profile_memories(context.user_id, limit=10)
        memories.extend([{"type": "profile", **m} for m in profile])
        
        # Rank by relevance (simple keyword matching)
        query_words = set(context.query.lower().split())
        for mem in memories:
            content = mem.get("content", mem.get("text", "")).lower()
            mem_words = set(content.split())
            overlap = len(query_words & mem_words)
            mem["_relevance"] = overlap / max(len(query_words), 1)
        
        memories.sort(key=lambda m: m.get("_relevance", 0), reverse=True)
        context.memories = memories[:10]
        
    except Exception as e:
        logger.error(f"Memory retrieval failed: {e}")
    
    return AgentResult(
        agent="memory",
        action="retrieve",
        data={"memory_count": len(context.memories)},
        confidence=min(len(context.memories) / 3, 1.0),
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _store_memory(context: RouteContext) -> AgentResult:
    """Extract and store new memory from user query."""
    start = time.time()
    stored = False
    
    try:
        # Check if query contains memory triggers
        query_lower = context.query.lower()
        has_trigger = any(t in query_lower for t in STORE_TRIGGERS)
        
        if has_trigger:
            # Store as profile memory
            content = context.query
            # Clean up trigger phrases
            for phrase in ["remember that", "save this", "store this", "don't forget"]:
                content = content.replace(phrase, "").strip()
            
            upsert_profile_memory(
                user_id=context.user_id,
                category="user_input",
                content=content,
                importance=0.7,
            )
            stored = True
        
        # Also use auto-detection from memory_store
        maybe_store_profile_memory(context.user_id, context.query)
        
    except Exception as e:
        logger.error(f"Memory storage failed: {e}")
    
    return AgentResult(
        agent="memory",
        action="remember",
        data={"stored": stored},
        confidence=1.0 if stored else 0.0,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _answer_with_memory(context: RouteContext) -> AgentResult:
    """Generate answer incorporating memory context."""
    memory_context = ""
    if context.memories:
        memory_parts = []
        for mem in context.memories[:5]:
            content = mem.get("content", mem.get("text", ""))
            if content:
                memory_parts.append(f"- {content[:200]}")
        memory_context = "\n".join(memory_parts)
    
    return AgentResult(
        agent="memory",
        action="answer",
        data={
            "memory_context": memory_context,
            "memory_count": len(context.memories),
        },
    )
