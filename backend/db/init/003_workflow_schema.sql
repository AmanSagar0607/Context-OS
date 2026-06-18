-- Workflow jobs table for background task scheduling
CREATE TABLE IF NOT EXISTS workflow_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL,  -- 'monitor', 'research', 'crawl', 'extract'
    query TEXT NOT NULL,
    config JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'created',  -- created, queued, running, completed, failed, cancelled
    priority INTEGER DEFAULT 0,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    last_run_at TIMESTAMPTZ,
    run_count INTEGER DEFAULT 0,
    max_runs INTEGER,  -- NULL = unlimited
    interval_seconds INTEGER,  -- NULL = one-shot
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_jobs_user_id ON workflow_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_jobs_status ON workflow_jobs(status);
CREATE INDEX IF NOT EXISTS idx_workflow_jobs_scheduled_at ON workflow_jobs(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_workflow_jobs_next_run ON workflow_jobs(status, scheduled_at) WHERE status IN ('created', 'queued');

-- Workflow job runs (execution history)
CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES workflow_jobs(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'running',  -- running, completed, failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    result JSONB,
    error TEXT,
    duration_ms FLOAT
);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_job_id ON workflow_runs(job_id);
