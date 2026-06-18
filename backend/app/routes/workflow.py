# app/routes/workflow.py
"""
Workflow routes — Background job management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.workflow_service import (
    create_job, get_job, list_jobs, cancel_job, delete_job,
    get_runs, get_user_stats,
)
from app.auth_middleware import require_scope, AuthContext

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


class CreateJobRequest(BaseModel):
    job_type: str = Field(..., description="Job type: monitor, research, crawl, extract")
    query: str = Field(..., min_length=1, max_length=5000)
    config: dict | None = None
    priority: int = Field(default=0, ge=0, le=10)
    interval_seconds: int | None = Field(default=None, ge=60, le=86400)
    max_runs: int | None = Field(default=None, ge=1)


class JobResponse(BaseModel):
    id: str
    job_type: str
    query: str
    status: str
    config: dict | None = None
    priority: int = 0
    scheduled_at: str | None = None
    last_run_at: str | None = None
    run_count: int = 0
    max_runs: int | None = None
    interval_seconds: int | None = None
    created_at: str | None = None

    class Config:
        from_attributes = True


def _serialize_job(job: dict) -> dict:
    """Convert datetime objects to ISO strings."""
    for key in ("scheduled_at", "started_at", "completed_at", "last_run_at", "created_at"):
        val = job.get(key)
        if val and hasattr(val, "isoformat"):
            job[key] = val.isoformat()
    if "config" in job and isinstance(job["config"], str):
        try:
            job["config"] = __import__("json").loads(job["config"])
        except Exception:
            pass
    return job


@router.post("", response_model=JobResponse)
async def create_workflow_job(
    body: CreateJobRequest,
    auth: AuthContext = Depends(require_scope("agents")),
):
    """Create a new workflow job."""
    job = create_job(
        user_id=auth.user_id,
        job_type=body.job_type,
        query=body.query,
        config=body.config,
        priority=body.priority,
        interval_seconds=body.interval_seconds,
        max_runs=body.max_runs,
    )
    return _serialize_job(job)


@router.get("")
async def list_workflow_jobs(
    auth: AuthContext = Depends(require_scope("agents")),
    limit: int = 50,
):
    """List all workflow jobs for the current user."""
    jobs = list_jobs(auth.user_id, limit=limit)
    stats = get_user_stats(auth.user_id)
    return {"jobs": [_serialize_job(j) for j in jobs], "stats": stats}


@router.get("/{job_id}")
async def get_workflow_job(
    job_id: str,
    auth: AuthContext = Depends(require_scope("agents")),
):
    """Get a specific workflow job."""
    job = get_job(job_id, auth.user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    runs = get_runs(job_id, limit=10)
    return {"job": job, "runs": runs}


@router.post("/{job_id}/cancel")
async def cancel_workflow_job(
    job_id: str,
    auth: AuthContext = Depends(require_scope("agents")),
):
    """Cancel a pending workflow job."""
    cancelled = cancel_job(job_id, auth.user_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Job not found or already running")
    return {"status": "cancelled", "job_id": job_id}


@router.delete("/{job_id}")
async def delete_workflow_job(
    job_id: str,
    auth: AuthContext = Depends(require_scope("agents")),
):
    """Delete a workflow job."""
    deleted = delete_job(job_id, auth.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "deleted", "job_id": job_id}


@router.get("/{job_id}/runs")
async def get_workflow_runs(
    job_id: str,
    auth: AuthContext = Depends(require_scope("agents")),
    limit: int = 20,
):
    """Get execution history for a workflow job."""
    job = get_job(job_id, auth.user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    runs = get_runs(job_id, limit=limit)
    return {"runs": runs}
