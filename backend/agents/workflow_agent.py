# agents/workflow_agent.py
"""
Workflow Agent — Background jobs, monitoring, scheduled research, multi-step execution.

Responsibilities:
- Execute background research tasks
- Monitor URLs for changes
- Schedule recurring research
- Orchestrate multi-step workflows
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from services.workflow_service import (
    create_job, get_job, cancel_job, delete_job, list_jobs,
    start_run, complete_run, get_runs, get_user_stats,
)
from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)


async def workflow_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute workflow steps."""
    if step.action == TaskAction.MONITOR:
        return await _setup_monitor(context)
    elif step.action == TaskAction.SEARCH:
        return await _list_user_jobs(context)
    elif step.action == TaskAction.EXTRACT:
        return await _get_job_status(context)
    return AgentResult(agent="workflow", action=step.action.value, data=None)


async def _setup_monitor(context: RouteContext) -> AgentResult:
    """Set up a monitoring workflow."""
    start = time.time()

    try:
        job = create_job(
            user_id=context.user_id,
            job_type="monitor",
            query=context.query,
            config={
                "conversation_id": context.conversation_id,
                "doc_id": context.doc_id,
            },
            interval_seconds=3600,  # Default: hourly
        )

        return AgentResult(
            agent="workflow",
            action="monitor",
            data={
                "job_id": job["id"],
                "status": job["status"],
                "message": f"Monitoring job created for: {context.query[:100]}",
                "interval": "hourly",
            },
            elapsed_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        logger.error(f"Failed to create monitor job: {e}")
        return AgentResult(
            agent="workflow",
            action="monitor",
            data={"error": str(e)},
            elapsed_ms=(time.time() - start) * 1000,
        )


async def _list_user_jobs(context: RouteContext) -> AgentResult:
    """List jobs for the current user."""
    start = time.time()

    try:
        jobs = list_jobs(context.user_id, limit=20)
        stats = get_user_stats(context.user_id)

        return AgentResult(
            agent="workflow",
            action="list",
            data={
                "jobs": jobs,
                "stats": stats,
            },
            elapsed_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        return AgentResult(
            agent="workflow",
            action="list",
            data={"error": str(e)},
            elapsed_ms=(time.time() - start) * 1000,
        )


async def _get_job_status(context: RouteContext) -> AgentResult:
    """Get status of a specific job."""
    start = time.time()

    # Try to extract job ID from query
    import re
    uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', context.query, re.IGNORECASE)

    if not uuid_match:
        return AgentResult(
            agent="workflow",
            action="status",
            data={"error": "No job ID found in query"},
            elapsed_ms=(time.time() - start) * 1000,
        )

    job_id = uuid_match.group(0)

    try:
        job = get_job(job_id, context.user_id)
        if not job:
            return AgentResult(
                agent="workflow",
                action="status",
                data={"error": f"Job {job_id} not found"},
                elapsed_ms=(time.time() - start) * 1000,
            )

        runs = get_runs(job_id, limit=5)

        return AgentResult(
            agent="workflow",
            action="status",
            data={
                "job": job,
                "recent_runs": runs,
            },
            elapsed_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        return AgentResult(
            agent="workflow",
            action="status",
            data={"error": str(e)},
            elapsed_ms=(time.time() - start) * 1000,
        )
