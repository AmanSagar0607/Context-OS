package dev.contextos;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Crawl service.
 */
public class CrawlService {
    private final ContextOS client;

    public CrawlService(ContextOS client) {
        this.client = client;
    }

    /**
     * Crawl a URL.
     *
     * @param url URL to crawl
     * @return Crawl result
     */
    public CrawlResult crawl(String url) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("url", url);

        String response = client.post("/api/v1/crawl", body);
        return client.getGson().fromJson(response, CrawlResult.class);
    }

    /**
     * Extract content from a URL.
     *
     * @param url URL to extract
     * @return Crawl result
     */
    public CrawlResult extract(String url) throws IOException {
        Map<String, Object> body = new HashMap<>();
        body.put("url", url);
        body.put("extract", true);

        String response = client.post("/api/v1/crawl", body);
        return client.getGson().fromJson(response, CrawlResult.class);
    }
}
