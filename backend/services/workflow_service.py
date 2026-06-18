# services/workflow_service.py
"""
Workflow Service — Postgres-backed job scheduling and execution.

Manages background jobs: monitors, research tasks, scheduled crawls.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── SQL queries ───────────────────────────────────────────────────────────

SQL_CREATE_JOB = """
INSERT INTO workflow_jobs (user_id, job_type, query, config, status, priority, scheduled_at, interval_seconds, max_runs)
VALUES (%s, %s, %s, %s, 'created', %s, %s, %s, %s)
RETURNING id::text, user_id::text, job_type, query, config, status, priority, scheduled_at, interval_seconds, max_runs, created_at
"""

SQL_GET_JOB = """
SELECT id::text, user_id::text, job_type, query, config, status, priority,
       scheduled_at, started_at, completed_at, last_run_at, run_count,
       max_runs, interval_seconds, result, error, created_at
FROM workflow_jobs WHERE id = %s AND user_id = %s
"""

SQL_LIST_JOBS = """
SELECT id::text, user_id::text, job_type, query, config, status, priority,
       scheduled_at, last_run_at, run_count, max_runs, interval_seconds, created_at
FROM workflow_jobs WHERE user_id = %s ORDER BY created_at DESC LIMIT %s
"""

SQL_CANCEL_JOB = """
UPDATE workflow_jobs SET status = 'cancelled', updated_at = NOW()
WHERE id = %s AND user_id = %s AND status IN ('created', 'queued')
RETURNING id::text
"""

SQL_DELETE_JOB = """
DELETE FROM workflow_jobs WHERE id = %s AND user_id = %s RETURNING id::text
"""

SQL_GET_DUE_JOBS = """
SELECT id::text, user_id::text, job_type, query, config, interval_seconds, max_runs, run_count
FROM workflow_jobs
WHERE status IN ('created', 'queued')
  AND scheduled_at <= NOW()
ORDER BY priority DESC, scheduled_at ASC
LIMIT %s
"""

SQL_START_RUN = """
INSERT INTO workflow_runs (job_id, status)
VALUES (%s, 'running')
RETURNING id::text
"""

SQL_COMPLETE_RUN = """
UPDATE workflow_runs SET status = %s, completed_at = NOW(), result = %s, error = %s, duration_ms = %s
WHERE id = %s
"""

SQL_UPDATE_JOB_AFTER_RUN = """
UPDATE workflow_jobs
SET status = %s, last_run_at = NOW(), run_count = run_count + 1,
    result = %s, error = %s, started_at = CASE WHEN %s = 'running' THEN NOW() ELSE started_at END,
    completed_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE completed_at END,
    scheduled_at = CASE WHEN %s = 'completed' AND interval_seconds IS NOT NULL THEN NOW() + (interval_seconds || ' seconds')::interval ELSE scheduled_at END,
    updated_at = NOW()
WHERE id = %s
"""

SQL_GET_RUNS = """
SELECT id::text, job_id::text, status, started_at, completed_at, result, error, duration_ms
FROM workflow_runs WHERE job_id = %s ORDER BY started_at DESC LIMIT %s
"""

SQL_GET_USER_STATS = """
SELECT
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE status = 'running') as running,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM workflow_jobs WHERE user_id = %s
"""


def _connect(settings=None):
    """Get a Postgres connection."""
    import psycopg
    if settings is None:
        settings = get_settings()
    return psycopg.connect(settings.database_url)


def _row_to_dict(row, columns) -> dict:
    """Convert a psycopg row to a dict."""
    if row is None:
        return {}
    return {col: val for col, val in zip(columns, row)}


# ── Job CRUD ──────────────────────────────────────────────────────────────

def create_job(
    user_id: str,
    job_type: str,
    query: str,
    config: dict | None = None,
    priority: int = 0,
    scheduled_at: datetime | None = None,
    interval_seconds: int | None = None,
    max_runs: int | None = None,
) -> dict:
    """Create a new workflow job."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_CREATE_JOB, (
                user_id,
                job_type,
                query,
                json.dumps(config or {}),
                priority,
                scheduled_at or datetime.now(timezone.utc),
                interval_seconds,
                max_runs,
            ))
            row = cur.fetchone()
            conn.commit()
            columns = ["id", "user_id", "job_type", "query", "config", "status", "priority",
                       "scheduled_at", "interval_seconds", "max_runs", "created_at"]
            return _row_to_dict(row, columns)
    finally:
        conn.close()


def get_job(job_id: str, user_id: str) -> dict | None:
    """Get a job by ID and user."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_GET_JOB, (job_id, user_id))
            row = cur.fetchone()
            columns = ["id", "user_id", "job_type", "query", "config", "status", "priority",
                       "scheduled_at", "started_at", "completed_at", "last_run_at", "run_count",
                       "max_runs", "interval_seconds", "result", "error", "created_at"]
            return _row_to_dict(row, columns)
    finally:
        conn.close()


def list_jobs(user_id: str, limit: int = 50) -> list[dict]:
    """List all jobs for a user."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_LIST_JOBS, (user_id, limit))
            rows = cur.fetchall()
            columns = ["id", "user_id", "job_type", "query", "config", "status", "priority",
                       "scheduled_at", "last_run_at", "run_count", "max_runs", "interval_seconds", "created_at"]
            return [_row_to_dict(row, columns) for row in rows]
    finally:
        conn.close()


def cancel_job(job_id: str, user_id: str) -> bool:
    """Cancel a pending job."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_CANCEL_JOB, (job_id, user_id))
            cancelled = cur.fetchone() is not None
            conn.commit()
            return cancelled
    finally:
        conn.close()


def delete_job(job_id: str, user_id: str) -> bool:
    """Delete a job."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_DELETE_JOB, (job_id, user_id))
            deleted = cur.fetchone() is not None
            conn.commit()
            return deleted
    finally:
        conn.close()


def get_user_stats(user_id: str) -> dict:
    """Get job statistics for a user."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_GET_USER_STATS, (user_id,))
            row = cur.fetchone()
            if row:
                return {"total_jobs": row[0], "running": row[1], "completed": row[2], "failed": row[3]}
            return {"total_jobs": 0, "running": 0, "completed": 0, "failed": 0}
    finally:
        conn.close()


# ── Job Execution ─────────────────────────────────────────────────────────

def get_due_jobs(limit: int = 10) -> list[dict]:
    """Get jobs that are due for execution."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_GET_DUE_JOBS, (limit,))
            rows = cur.fetchall()
            columns = ["id", "user_id", "job_type", "query", "config", "interval_seconds", "max_runs", "run_count"]
            return [_row_to_dict(row, columns) for row in rows]
    finally:
        conn.close()


def start_run(job_id: str) -> str:
    """Start a new run for a job. Returns run ID."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_START_RUN, (job_id,))
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
    finally:
        conn.close()


def complete_run(
    run_id: str,
    job_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
    duration_ms: float | None = None,
    reschedule: bool = False,
):
    """Complete a run and update the job."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            # Complete the run
            cur.execute(SQL_COMPLETE_RUN, (
                status,
                json.dumps(result) if result else None,
                error,
                duration_ms,
                run_id,
            ))

            # Update the job
            next_status = "created" if reschedule else ("completed" if status == "completed" else "failed")
            cur.execute(SQL_UPDATE_JOB_AFTER_RUN, (
                next_status,
                json.dumps(result) if result else None,
                error,
                next_status,
                next_status,
                next_status,
                job_id,
            ))
            conn.commit()
    finally:
        conn.close()


def get_runs(job_id: str, limit: int = 20) -> list[dict]:
    """Get execution history for a job."""
    settings = get_settings()
    conn = _connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_GET_RUNS, (job_id, limit))
            rows = cur.fetchall()
            columns = ["id", "job_id", "status", "started_at", "completed_at", "result", "error", "duration_ms"]
            return [_row_to_dict(row, columns) for row in rows]
    finally:
        conn.close()
