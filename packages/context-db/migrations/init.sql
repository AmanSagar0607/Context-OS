
-- 001_core.sql
-- 001_core.sql
-- Core tables for Context Infrastructure Platform.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT NOT NULL UNIQUE,
    username CITEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'invited', 'suspended', 'deleted')),
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    timezone TEXT DEFAULT 'UTC',
    locale TEXT DEFAULT 'en',
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auth identities (password, OAuth)
CREATE TABLE IF NOT EXISTS auth_identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL CHECK (provider IN ('password', 'google', 'github')),
    provider_user_id TEXT,
    password_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_user_id),
    UNIQUE (user_id, provider)
);

-- Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- API tokens
CREATE TABLE IF NOT EXISTS api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    scopes JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'archived', 'deleted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant')),
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_tokens_user ON api_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at ASC);

-- Default roles
INSERT INTO roles (role_key, role_name, description)
VALUES
    ('admin', 'Admin', 'Full administrative access'),
    ('user', 'User', 'Standard user'),
    ('viewer', 'Viewer', 'Read-only access')
ON CONFLICT (role_key) DO NOTHING;

-- 002_memory.sql
-- 002_memory.sql
-- Unified memory system with pgvector for semantic search.

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Unified memories table
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    agent_id TEXT,
    session_id TEXT,
    
    -- Content
    content TEXT NOT NULL,
    summary TEXT,
    memory_type TEXT NOT NULL DEFAULT 'episodic' 
        CHECK (memory_type IN ('episodic', 'semantic', 'procedural')),
    importance TEXT NOT NULL DEFAULT 'medium'
        CHECK (importance IN ('low', 'medium', 'high', 'critical')),
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    source TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding vector(384),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- Relationships
    parent_id UUID REFERENCES memories(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT memories_user_id_check CHECK (user_id != '')
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_user_agent ON memories(user_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_parent ON memories(parent_id);

-- Vector similarity index (HNSW for production, IVFFlat for small datasets)
-- For <1M rows, IVFFlat is fine. For >1M, switch to HNSW.
CREATE INDEX IF NOT EXISTS idx_memories_embedding 
    ON memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_memories_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_memories_updated_at
    BEFORE UPDATE ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_memories_updated_at();

-- Memory links (graph relationships between memories)
CREATE TABLE IF NOT EXISTS memory_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL CHECK (relationship != ''),
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(source_id, target_id, relationship)
);

CREATE INDEX IF NOT EXISTS idx_memory_links_source ON memory_links(source_id);
CREATE INDEX IF NOT EXISTS idx_memory_links_target ON memory_links(target_id);

-- Conversation messages (for context retrieval)
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    embedding vector(384),
    tokens_used INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT conversation_messages_user_id_check CHECK (user_id != '')
);

CREATE INDEX IF NOT EXISTS idx_conv_messages_conv ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conv_messages_user ON conversation_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_conv_messages_created ON conversation_messages(created_at DESC);

-- 003_knowledge.sql
-- 003_knowledge.sql
-- Knowledge graph tables with embeddings.

-- Knowledge graph entities
CREATE TABLE IF NOT EXISTS kg_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'concept'
        CHECK (entity_type IN ('concept', 'person', 'organization', 'location', 'event', 'document', 'custom')),
    name TEXT NOT NULL,
    description TEXT,
    properties JSONB DEFAULT '{}',
    embedding vector(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT kg_entities_name_check CHECK (name != '')
);

-- Knowledge graph relationships
CREATE TABLE IF NOT EXISTS kg_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL DEFAULT 'related_to',
    weight FLOAT DEFAULT 1.0,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(source_entity_id, target_entity_id, relationship_type),
    CONSTRAINT kg_relationships_type_check CHECK (relationship_type != '')
);

-- Entity-to-memory links
CREATE TABLE IF NOT EXISTS entity_memory_links (
    entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
    memory_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    relevance FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (entity_id, memory_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kg_entities_user ON kg_entities(user_id);
CREATE INDEX IF NOT EXISTS idx_kg_entities_type ON kg_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_kg_entities_name ON kg_entities USING GIN(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_kg_relationships_source ON kg_relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_kg_relationships_target ON kg_relationships(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_kg_relationships_type ON kg_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_entity_memory_entity ON entity_memory_links(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_memory_memory ON entity_memory_links(memory_id);

-- Vector similarity index for entities
CREATE INDEX IF NOT EXISTS idx_kg_entities_embedding 
    ON kg_entities USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- roles
CREATE TABLE IF NOT EXISTS roles (
    role_key TEXT PRIMARY KEY,
    role_name TEXT NOT NULL,
    description TEXT
);

INSERT INTO roles (role_key, role_name, description)
VALUES
    ('admin', 'Admin', 'Full administrative access'),
    ('user', 'User', 'Standard user'),
    ('viewer', 'Viewer', 'Read-only access')
ON CONFLICT (role_key) DO NOTHING;

-- 004_subscriptions.sql
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
    billing_provider TEXT DEFAULT 'polar',
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
