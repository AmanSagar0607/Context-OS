/**
 * Context AI — TypeScript SDK
 *
 * Usage:
 *   import { ContextAI } from "context-ai";
 *
 *   const client = new ContextAI({ apiKey: "your-key" });
 *
 *   // Memory
 *   const memory = await client.memory.add({ content: "User prefers dark mode" });
 *
 *   // Search
 *   const results = await client.search.web({ query: "AI news" });
 */

import { HTTPClient, type HTTPClientOptions } from "./_http.js";
import { MemoryClient } from "./memory.js";
import { SearchClient } from "./search.js";
import { CrawlClient } from "./crawl.js";
import { KnowledgeClient } from "./knowledge.js";

export interface ContextAIOptions extends HTTPClientOptions {}

export class ContextAI {
  private http: HTTPClient;

  readonly memory: MemoryClient;
  readonly search: SearchClient;
  readonly crawl: CrawlClient;
  readonly knowledge: KnowledgeClient;

  constructor(options: ContextAIOptions = {}) {
    const apiKey =
      options.apiKey ||
      (typeof process !== "undefined"
        ? process.env?.CONTEXT_API_KEY || process.env?.CONTEXT_OS_API_KEY
        : undefined);

    const baseUrl =
      options.baseUrl ||
      (typeof process !== "undefined"
        ? process.env?.CONTEXT_API_URL || process.env?.CONTEXT_OS_URL
        : undefined) ||
      "http://localhost:8000";

    this.http = new HTTPClient({
      baseUrl,
      apiKey,
      timeout: options.timeout,
    });

    this.memory = new MemoryClient(this.http);
    this.search = new SearchClient(this.http);
    this.crawl = new CrawlClient(this.http);
    this.knowledge = new KnowledgeClient(this.http);
  }

  async health(): Promise<unknown> {
    return this.http.get("/api/v1/health");
  }
}

// Re-export everything
export { MemoryClient } from "./memory.js";
export { SearchClient } from "./search.js";
export { CrawlClient } from "./crawl.js";
export { KnowledgeClient } from "./knowledge.js";
export * from "./types.js";