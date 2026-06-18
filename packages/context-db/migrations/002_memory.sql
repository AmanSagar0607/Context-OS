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