/**
 * Context AI — Search Client
 */

import { HTTPClient } from "./_http.js";
import type { SearchRequest, SearchResult } from "./types.js";

export class SearchClient {
  private http: HTTPClient;

  constructor(http: HTTPClient) {
    this.http = http;
  }

  async web(request: SearchRequest): Promise<SearchResult[]> {
    const data = await this.http.post<{ results: SearchResult[] }>(
      "/api/v1/search/web",
      request,
    );
    return data.results || [];
  }

  async internal(query: string, topK: number = 10): Promise<SearchResult[]> {
    const data = await this.http.post<{ results: SearchResult[] }>(
      "/api/v1/search/internal",
      { query, top_k: topK },
    );
    return data.results || [];
  }
}