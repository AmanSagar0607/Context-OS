package dev.contextos;

import java.util.List;

/**
 * Search response.
 */
public class SearchResponse {
    private List<SearchResult> results;
    private String query;
    private int totalHits;

    public List<SearchResult> getResults() { return results; }
    public void setResults(List<SearchResult> results) { this.results = results; }

    public String getQuery() { return query; }
    public void setQuery(String query) { this.query = query; }

    public int getTotalHits() { return totalHits; }
    public void setTotalHits(int totalHits) { this.totalHits = totalHits; }
}
