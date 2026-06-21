"""
Context Infrastructure API Server

FastAPI entry point for the Context Infrastructure Platform.
Provides REST API for memory, search, crawl, knowledge, and MCP services.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent))

from context_core.config import get_settings
from context_core.memory.service import MemoryService
from context_core.embeddings.service import EmbeddingService

from routes import memory, health
from middleware.auth import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    settings = get_settings()

    # Initialize database pool
    import asyncpg
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
    )
    app.state.pool = pool

    # Initialize embedding service
    embeddings = EmbeddingService.from_settings(settings)
    app.state.embeddings = embeddings

    # Initialize memory service
    memory_service = MemoryService(pool, embeddings)
    app.state.memory_service = memory_service

    yield

    # Shutdown
    await pool.close()


app = FastAPI(
    title="Context Infrastructure API",
    description="Memory, Search, Crawl, Knowledge, and MCP for AI Agents",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])