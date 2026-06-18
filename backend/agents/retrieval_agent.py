# agents/retrieval_agent.py
"""
Retrieval Agent — Vector search, semantic retrieval, RAG context building, citation collection.

Responsibilities:
- Query Milvus/Zilliz for relevant document chunks
- Build RAG context from retrieved chunks
- Collect citations with source attribution
"""

from __future__ import annotations

import logging
import time
from typing import Any

from rag.retriever import retrieve_chunks
from embeddings.embedder import embed_query
from services.postgres_store import resolve_user_id
from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)


async def retrieval_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute retrieval steps."""
    if step.action == TaskAction.RETRIEVE:
        return await _retrieve(context)
    elif step.action == TaskAction.ANSWER:
        return await _generate_answer(context)
    return AgentResult(agent="retrieval", action=step.action.value, data=None)


async def _retrieve(context: RouteContext) -> AgentResult:
    """Retrieve relevant chunks from vector store."""
    start = time.time()
    sources = []
    chunks = []
    
    # If doc_id is provided, retrieve from that document
    if context.doc_id:
        try:
            query_embedding = embed_query(context.query)
            retrieved = retrieve_chunks(
                query_embedding,
                collection_name="pdf_chunks",
                doc_id=context.doc_id,
                top_k=10,
            )
            chunks = retrieved
            for chunk in retrieved:
                sources.append({
                    "type": "document",
                    "doc_id": context.doc_id,
                    "chunk_index": chunk.get("chunk_index", 0),
                    "page": chunk.get("page", 0),
                    "preview": chunk.get("text", "")[:200],
                    "score": chunk.get("score", 0),
                })
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
    
    # Also check memory for context
    try:
        from services.memory_store import get_recent_messages, get_profile_memories
        if context.conversation_id:
            recent = get_recent_messages(context.conversation_id, limit=5)
            context.memories.extend([{"type": "message", **m} for m in recent])
        
        profile = get_profile_memories(context.user_id, limit=5)
        context.memories.extend([{"type": "profile", **m} for m in profile])
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")
    
    context.retrieved_chunks = chunks
    context.citations.extend(sources)
    
    return AgentResult(
        agent="retrieval",
        action="retrieve",
        data={"chunks": len(chunks), "sources": len(sources)},
        confidence=min(len(chunks) / 5, 1.0),
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _generate_answer(context: RouteContext) -> AgentResult:
    """Generate answer using retrieved context via OpenRouter."""
    # Build context from all retrieved sources
    context_parts = []
    
    if context.retrieved_chunks:
        context_parts.append("=== DOCUMENT CONTEXT ===")
        for i, chunk in enumerate(context.retrieved_chunks[:5]):
            text = chunk.get("text", "")
            page = chunk.get("page", "?")
            context_parts.append(f"[Source {i+1}, Page {page}]: {text[:500]}")
    
    if context.memories:
        context_parts.append("\n=== MEMORY CONTEXT ===")
        for mem in context.memories[:3]:
            context_parts.append(f"- {mem.get('content', mem.get('text', ''))[:200]}")
    
    if context.search_results:
        context_parts.append("\n=== WEB SEARCH CONTEXT ===")
        for res in context.search_results[:3]:
            context_parts.append(f"- {res.get('title', '')}: {res.get('snippet', '')[:200]}")
    
    full_context = "\n".join(context_parts) if context_parts else "No context available."
    
    return AgentResult(
        agent="retrieval",
        action="answer",
        data={
            "context": full_context,
            "has_context": bool(context_parts),
            "source_count": len(context.citations),
        },
        sources=context.citations,
    )
