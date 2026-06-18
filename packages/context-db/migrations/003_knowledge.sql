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