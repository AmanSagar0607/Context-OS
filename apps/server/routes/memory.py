"""
Memory Routes — REST API for unified memory system.

Endpoints:
    POST /api/v1/memory          - Store memory
    GET  /api/v1/memory/:id      - Get memory
    PUT  /api/v1/memory/:id      - Update memory
    DELETE /api/v1/memory/:id    - Delete memory
    POST /api/v1/memory/search   - Semantic search
    POST /api/v1/memory/context  - Get context window
    GET  /api/v1/memory          - List memories
    GET  /api/v1/memory/related  - Get related memories
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from context_core.memory.models import (
    MemoryCreate,
    MemoryUpdate,
    MemorySearchRequest,
)

router = APIRouter()


def get_memory_service(request: Request):
    """Get memory service from app state."""
    return request.app.state.memory_service


def get_user_id(request: Request) -> str:
    """Extract user ID from request context."""
    # In production, this comes from auth middleware
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # For development, allow x-user-id header
        user_id = request.headers.get("x-user-id", "anonymous")
    return user_id


@router.post("")
async def create_memory(request: Request, body: MemoryCreate):
    """Store a new memory."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    memory = await service.add(user_id, body)
    return {"id": str(memory.id), "created_at": memory.created_at.isoformat()}


@router.get("/{memory_id}")
async def get_memory(request: Request, memory_id: UUID):
    """Retrieve a memory by ID."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    memory = await service.get(memory_id, user_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {
        "id": str(memory.id),
        "content": memory.content,
        "summary": memory.summary,
        "memory_type": memory.memory_type.value,
        "importance": memory.importance.value,
        "tags": memory.tags,
        "source": memory.source,
        "metadata": memory.metadata,
        "created_at": memory.created_at.isoformat(),
        "updated_at": memory.updated_at.isoformat(),
    }


@router.put("/{memory_id}")
async def update_memory(request: Request, memory_id: UUID, body: MemoryUpdate):
    """Update a memory."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    memory = await service.update(memory_id, user_id, body)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"id": str(memory.id), "updated_at": memory.updated_at.isoformat()}


@router.delete("/{memory_id}")
async def delete_memory(request: Request, memory_id: UUID):
    """Delete a memory."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    deleted = await service.delete(memory_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}


@router.post("/search")
async def search_memories(request: Request, body: MemorySearchRequest):
    """Semantic search using pgvector cosine similarity."""
    service = get_memory_service(request)
    results = await service.search(body)
    return {
        "results": [
            {
                "id": str(r.memory.id),
                "content": r.memory.content,
                "summary": r.memory.summary,
                "memory_type": r.memory.memory_type.value,
                "importance": r.memory.importance.value,
                "score": r.score,
                "created_at": r.memory.created_at.isoformat(),
            }
            for r in results
        ],
        "total": len(results),
    }


@router.post("/context")
async def get_context_window(
    request: Request,
    query: str,
    max_tokens: int = 2000,
):
    """Assemble a context window from relevant memories."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    context = await service.get_context_window(user_id, query, max_tokens)
    return {
        "memories": [
            {
                "id": str(m.id),
                "content": m.content,
                "memory_type": m.memory_type.value,
            }
            for m in context.memories
        ],
        "total_tokens": context.total_tokens,
        "truncated": context.truncated,
    }


@router.get("")
async def list_memories(
    request: Request,
    memory_type: str = None,
    limit: int = 50,
    offset: int = 0,
):
    """List memories with optional filters."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    memories = await service.list_memories(
        user_id=user_id,
        memory_type=memory_type,
        limit=limit,
        offset=offset,
    )
    return {
        "memories": [
            {
                "id": str(m.id),
                "content": m.content,
                "summary": m.summary,
                "memory_type": m.memory_type.value,
                "importance": m.importance.value,
                "tags": m.tags,
                "created_at": m.created_at.isoformat(),
            }
            for m in memories
        ],
        "total": len(memories),
    }


@router.get("/{memory_id}/related")
async def get_related_memories(
    request: Request,
    memory_id: UUID,
    limit: int = 10,
):
    """Find related memories using embedding similarity."""
    service = get_memory_service(request)
    user_id = get_user_id(request)
    related = await service.get_related(memory_id, user_id, limit)
    return {
        "memories": [
            {
                "id": str(m.id),
                "content": m.content,
                "memory_type": m.memory_type.value,
            }
            for m in related
        ],
        "total": len(related),
    }