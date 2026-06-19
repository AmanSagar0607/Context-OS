/**
 * Context AI — Crawl Client
 */

import { HTTPClient } from "./_http.js";
import type { CrawlRequest, CrawlResult } from "./types.js";

export class CrawlClient {
  private http: HTTPClient;

  constructor(http: HTTPClient) {
    this.http = http;
  }

  async scrape(url: string, options?: Record<string, unknown>): Promise<CrawlResult> {
    return this.http.post<CrawlResult>("/api/v1/crawl/scrape", { url, ...options });
  }

  async crawl(request: CrawlRequest): Promise<CrawlResult[]> {
    const data = await this.http.post<{ results: CrawlResult[] }>(
      "/api/v1/crawl/crawl",
      request,
    );
    return data.results || [];
  }

  async map(url: string, maxPages: number = 50): Promise<string[]> {
    const data = await this.http.post<{ urls: string[] }>(
      "/api/v1/crawl/map",
      { url, max_pages: maxPages },
    );
    return data.urls || [];
  }

  async extract(
    url: string,
    prompt: string,
    schema?: Record<string, unknown>,
  ): Promise<unknown> {
    const payload: Record<string, unknown> = { url, prompt };
    if (schema) {
      payload.schema = schema;
    }
    return this.http.post("/api/v1/crawl/extract", payload);
  }
}