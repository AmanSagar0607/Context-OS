/**
 * Context AI — Memory Client
 */

import { HTTPClient } from "./_http.js";
import type {
  Memory,
  MemoryCreate,
  MemoryUpdate,
  MemorySearchRequest,
  MemorySearchResult,
} from "./types.js";

export class MemoryClient {
  private http: HTTPClient;

  constructor(http: HTTPClient) {
    this.http = http;
  }

  async add(request: MemoryCreate): Promise<Memory> {
    return this.http.post<Memory>("/api/v1/memory", request);
  }

  async get(memoryId: string): Promise<Memory | null> {
    try {
      return await this.http.get<Memory>(`/api/v1/memory/${memoryId}`);
    } catch {
      return null;
    }
  }

  async update(memoryId: string, request: MemoryUpdate): Promise<Memory | null> {
    try {
      return await this.http.put<Memory>(`/api/v1/memory/${memoryId}`, request);
    } catch {
      return null;
    }
  }

  async delete(memoryId: string): Promise<boolean> {
    try {
      await this.http.delete(`/api/v1/memory/${memoryId}`);
      return true;
    } catch {
      return false;
    }
  }

  async search(request: MemorySearchRequest): Promise<MemorySearchResult[]> {
    const data = await this.http.post<{ results: MemorySearchResult[] }>(
      "/api/v1/memory/search",
      request,
    );
    return data.results || [];
  }

  async context(query: string, maxTokens: number = 2000): Promise<{
    memories: Memory[];
    total_tokens: number;
    truncated: boolean;
  }> {
    return this.http.post("/api/v1/memory/context", { query, max_tokens: maxTokens });
  }

  async list(options?: {
    memory_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<Memory[]> {
    const params: Record<string, string | number | boolean> = {
      limit: options?.limit ?? 50,
      offset: options?.offset ?? 0,
    };
    if (options?.memory_type) {
      params.memory_type = options.memory_type;
    }
    const data = await this.http.get<{ memories: Memory[] }>("/api/v1/memory", params);
    return data.memories || [];
  }

  async related(memoryId: string, limit: number = 10): Promise<Memory[]> {
    const data = await this.http.get<{ memories: Memory[] }>(
      `/api/v1/memory/${memoryId}/related`,
      { limit },
    );
    return data.memories || [];
  }
}