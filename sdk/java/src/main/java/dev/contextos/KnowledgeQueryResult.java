package dev.contextos;

import java.util.List;

/**
 * Knowledge query result.
 */
public class KnowledgeQueryResult {
    private List<KnowledgeEntity> entities;
    private List<KnowledgeRelationship> relationships;

    public List<KnowledgeEntity> getEntities() { return entities; }
    public void setEntities(List<KnowledgeEntity> entities) { this.entities = entities; }

    public List<KnowledgeRelationship> getRelationships() { return relationships; }
    public void setRelationships(List<KnowledgeRelationship> relationships) { this.relationships = relationships; }
}
