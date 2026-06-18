"""Health check endpoint."""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/v1/health")
async def health_check(request: Request):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "database": "connected",
            "embeddings": "ready",
        },
    }