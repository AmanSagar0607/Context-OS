package dev.contextos;

import java.util.Map;

/**
 * Knowledge relationship.
 */
public class KnowledgeRelationship {
    private String id;
    private String sourceId;
    private String targetId;
    private String type;
    private Map<String, String> properties;
    private double weight;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getSourceId() { return sourceId; }
    public void setSourceId(String sourceId) { this.sourceId = sourceId; }

    public String getTargetId() { return targetId; }
    public void setTargetId(String targetId) { this.targetId = targetId; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public Map<String, String> getProperties() { return properties; }
    public void setProperties(Map<String, String> properties) { this.properties = properties; }

    public double getWeight() { return weight; }
    public void setWeight(double weight) { this.weight = weight; }
}
