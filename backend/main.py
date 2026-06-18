"""
FastAPI entrypoint — AI PDF Learning Workspace backend.

WHY this file exists:
  Single place to wire routes, CORS, and lifespan hooks.
  Production apps keep `main.py` thin and push logic into `app/` and `services/`.
"""

from contextlib import asynccontextmanager

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import auth, chat, health, pipeline, upload, amancrawl, dashboard, subscriptions, intelligence, workflow, payments, oauth, browser
from services.mcp_server import router as mcp_router
from services.memory_store import init_memory_store
from services.knowledge_graph import init_knowledge_schema
from services.semantic_memory import init_semantic_memory

# Project root: my-ai-app/.env (one level above backend/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")
load_dotenv()  # optional backend/.env override


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown — Step 7 will connect Milvus here."""
    settings = get_settings()
    app.state.settings = settings
    init_memory_store(settings)
    init_knowledge_schema()
    init_semantic_memory(settings)
    yield


app = FastAPI(
    title="AI PDF Learning Workspace API",
    description="Educational RAG pipeline backend — see README for step-by-step build.",
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

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(pipeline.router)
app.include_router(chat.router)
app.include_router(amancrawl.router)
app.include_router(dashboard.router)
app.include_router(subscriptions.router)
app.include_router(intelligence.router)
app.include_router(mcp_router)
app.include_router(workflow.router)
app.include_router(payments.router)
app.include_router(oauth.router)
app.include_router(browser.router)
