package dev.contextos;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Memory service.
 */
public class MemoryService {
    private final ContextOS client;

    public MemoryService(ContextOS client) {
        this.client = client;
    }

    /**
     * Add a new memory.
     *
     * @param content Memory content
     * @return Created memory
     */
    public Memory add(String content) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("content", content);
        body.put("type", "fact");

        String response = client.post("/api/v1/memory", body);
        return client.getGson().fromJson(response, Memory.class);
    }

    /**
     * Add a new memory with type.
     *
     * @param content Memory content
     * @param type    Memory type
     * @return Created memory
     */
    public Memory add(String content, String type) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("content", content);
        body.put("type", type);

        String response = client.post("/api/v1/memory", body);
        return client.getGson().fromJson(response, Memory.class);
    }

    /**
     * Get a memory by ID.
     *
     * @param memoryId Memory ID
     * @return Memory
     */
    public Memory get(String memoryId) throws IOException {
        String response = client.get("/api/v1/memory/" + memoryId);
        return client.getGson().fromJson(response, Memory.class);
    }

    /**
     * Delete a memory.
     *
     * @param memoryId Memory ID
     */
    public void delete(String memoryId) throws IOException {
        client.delete("/api/v1/memory/" + memoryId);
    }

    /**
     * Search memories.
     *
     * @param query Search query
     * @param topK  Number of results
     * @return Search results
     */
    public SearchResponse search(String query, int topK) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("query", query);
        body.put("top_k", topK);

        String response = client.post("/api/v1/memory/search", body);
        return client.getGson().fromJson(response, SearchResponse.class);
    }
}
