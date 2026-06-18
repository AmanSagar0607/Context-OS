-- 004_subscriptions.sql
-- Subscription plans, usage tracking, and billing.

-- Plans
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    features JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Plan limits (rate limiting per plan)
CREATE TABLE IF NOT EXISTS plan_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    metric TEXT NOT NULL,
    limit_value INTEGER NOT NULL,
    window_seconds INTEGER NOT NULL DEFAULT 86400,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(plan_id, metric)
);

-- User subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES plans(id),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'past_due', 'canceled', 'trialing')),
    billing_provider TEXT DEFAULT 'baseupi',
    billing_customer_id TEXT,
    billing_subscription_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Usage records (for metered billing)
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    metric TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Aggregated usage (pre-computed for fast queries)
CREATE TABLE IF NOT EXISTS usage_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, metric, period_start)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_plans_name ON plans(name);
CREATE INDEX IF NOT EXISTS idx_plan_limits_plan ON plan_limits(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_usage_records_user ON usage_records(user_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_metric ON usage_records(metric, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_aggregates_user ON usage_aggregates(user_id, metric);
CREATE INDEX IF NOT EXISTS idx_usage_aggregates_period ON usage_aggregates(period_start, period_end);

-- Seed default plans
INSERT INTO plans (name, display_name, description, features) VALUES
    ('free', 'Free', 'For individual developers', '["5000 memories", "100 searches/day", "10 crawls/day", "Community support"]'),
    ('pro', 'Pro', 'For professionals and small teams', '["50,000 memories", "1,000 searches/day", "100 crawls/day", "Priority support", "Custom agents"]'),
    ('team', 'Team', 'For growing teams', '["500,000 memories", "10,000 searches/day", "1,000 crawls/day", "Dedicated support", "SSO", "Audit logs"]'),
    ('enterprise', 'Enterprise', 'For organizations', '["Unlimited memories", "Unlimited searches", "Unlimited crawls", "24/7 support", "SLA", "On-prem deployment"]')
ON CONFLICT (name) DO NOTHING;

-- Seed plan limits
INSERT INTO plan_limits (plan_id, metric, limit_value, window_seconds)
SELECT p.id, l.metric, l.limit_value, l.window_seconds
FROM plans p
CROSS JOIN (VALUES
    ('memories', 5000, 86400),
    ('searches', 100, 86400),
    ('crawls', 10, 86400),
    ('embeddings', 10000, 86400)
) AS l(metric, limit_value, window_seconds)
WHERE p.name = 'free'
ON CONFLICT (plan_id, metric) DO NOTHING;