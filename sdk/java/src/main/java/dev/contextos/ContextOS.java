package dev.contextos;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.Gson;

/**
 * ContextOS API client.
 *
 * <p>Usage:
 * <pre>{@code
 * ContextOS client = new ContextOS("https://api.contextos.dev", "your-api-key");
 *
 * // Add memory
 * Memory memory = client.getMemory().add("Important information");
 *
 * // Search
 * SearchResponse results = client.getSearch().search("important information");
 * }</pre>
 */
public class ContextOS {
    private static final String DEFAULT_BASE_URL = "https://api.contextos.dev";

    private final String baseUrl;
    private final String apiKey;
    private final OkHttpClient httpClient;
    private final Gson gson;

    private final MemoryService memoryService;
    private final SearchService searchService;
    private final CrawlService crawlService;
    private final KnowledgeService knowledgeService;

    /**
     * Create a new ContextOS client.
     *
     * @param baseUrl API base URL
     * @param apiKey  API key
     */
    public ContextOS(String baseUrl, String apiKey) {
        this.baseUrl = (baseUrl == null || baseUrl.isEmpty()) ? DEFAULT_BASE_URL : baseUrl;
        this.apiKey = apiKey;
        this.gson = new Gson();

        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();

        this.memoryService = new MemoryService(this);
        this.searchService = new SearchService(this);
        this.crawlService = new CrawlService(this);
        this.knowledgeService = new KnowledgeService(this);
    }

    /**
     * Create a new ContextOS client with default URL.
     *
     * @param apiKey API key
     */
    public ContextOS(String apiKey) {
        this(DEFAULT_BASE_URL, apiKey);
    }

    public MemoryService getMemory() {
        return memoryService;
    }

    public SearchService getSearch() {
        return searchService;
    }

    public CrawlService getCrawl() {
        return crawlService;
    }

    public KnowledgeService getKnowledge() {
        return knowledgeService;
    }

    /**
     * Perform a GET request.
     */
    String get(String path) throws IOException {
        Request request = new Request.Builder()
                .url(baseUrl + path)
                .header("Authorization", "Bearer " + apiKey)
                .get()
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new APIException(response.code(), response.body() != null ? response.body().string() : "Unknown error");
            }
            return response.body() != null ? response.body().string() : "";
        }
    }

    /**
     * Perform a POST request.
     */
    String post(String path, Object body) throws IOException {
        RequestBody requestBody = RequestBody.create(
                gson.toJson(body),
                okhttp3.MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(baseUrl + path)
                .header("Authorization", "Bearer " + apiKey)
                .post(requestBody)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new APIException(response.code(), response.body() != null ? response.body().string() : "Unknown error");
            }
            return response.body() != null ? response.body().string() : "";
        }
    }

    /**
     * Perform a PUT request.
     */
    String put(String path, Object body) throws IOException {
        RequestBody requestBody = RequestBody.create(
                gson.toJson(body),
                okhttp3.MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(baseUrl + path)
                .header("Authorization", "Bearer " + apiKey)
                .put(requestBody)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new APIException(response.code(), response.body() != null ? response.body().string() : "Unknown error");
            }
            return response.body() != null ? response.body().string() : "";
        }
    }

    /**
     * Perform a DELETE request.
     */
    String delete(String path) throws IOException {
        Request request = new Request.Builder()
                .url(baseUrl + path)
                .header("Authorization", "Bearer " + apiKey)
                .delete()
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new APIException(response.code(), response.body() != null ? response.body().string() : "Unknown error");
            }
            return response.body() != null ? response.body().string() : "";
        }
    }

    Gson getGson() {
        return gson;
    }
}
