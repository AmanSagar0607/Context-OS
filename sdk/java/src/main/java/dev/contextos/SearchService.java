package dev.contextos;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Search service.
 */
public class SearchService {
    private final ContextOS client;

    public SearchService(ContextOS client) {
        this.client = client;
    }

    /**
     * Perform a hybrid search.
     *
     * @param query Search query
     * @param topK  Number of results
     * @return Search results
     */
    public SearchResponse search(String query, int topK) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("query", query);
        body.put("top_k", topK);

        String response = client.post("/api/v1/search", body);
        return client.getGson().fromJson(response, SearchResponse.class);
    }

    /**
     * Perform a semantic search.
     *
     * @param query Search query
     * @param topK  Number of results
     * @return Search results
     */
    public SearchResponse semanticSearch(String query, int topK) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("query", query);
        body.put("top_k", topK);
        body.put("mode", "vector");

        String response = client.post("/api/v1/search", body);
        return client.getGson().fromJson(response, SearchResponse.class);
    }
}
