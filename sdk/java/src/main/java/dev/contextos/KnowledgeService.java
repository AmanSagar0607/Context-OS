package dev.contextos;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Knowledge service.
 */
public class KnowledgeService {
    private final ContextOS client;

    public KnowledgeService(ContextOS client) {
        this.client = client;
    }

    /**
     * Add a knowledge entity.
     *
     * @param name Entity name
     * @param type Entity type
     * @return Created entity
     */
    public KnowledgeEntity addEntity(String name, String type) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("name", name);
        body.put("type", type);

        String response = client.post("/api/v1/knowledge/entities", body);
        return client.getGson().fromJson(response, KnowledgeEntity.class);
    }

    /**
     * Query the knowledge graph.
     *
     * @param entityName Entity name to query
     * @param maxDepth   Max traversal depth
     * @return Query results
     */
    public KnowledgeQueryResult query(String entityName, int maxDepth) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("entity_name", entityName);
        body.put("max_depth", maxDepth);

        String response = client.post("/api/v1/knowledge/query", body);
        return client.getGson().fromJson(response, KnowledgeQueryResult.class);
    }
}
