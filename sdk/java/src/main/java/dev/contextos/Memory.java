package dev.contextos;

import java.util.Map;

/**
 * Memory entry.
 */
public class Memory {
    private String id;
    private String content;
    private String type;
    private String scope;
    private String scopeId;
    private Map<String, String> metadata;
    private double importance;
    private double decay;
    private int accessCount;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getScope() { return scope; }
    public void setScope(String scope) { this.scope = scope; }

    public String getScopeId() { return scopeId; }
    public void setScopeId(String scopeId) { this.scopeId = scopeId; }

    public Map<String, String> getMetadata() { return metadata; }
    public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }

    public double getImportance() { return importance; }
    public void setImportance(double importance) { this.importance = importance; }

    public double getDecay() { return decay; }
    public void setDecay(double decay) { this.decay = decay; }

    public int getAccessCount() { return accessCount; }
    public void setAccessCount(int accessCount) { this.accessCount = accessCount; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
