/**
 * Context AI — Knowledge Client
 */

import { HTTPClient } from "./_http.js";
import type { Entity, EntityCreate, RelationshipCreate } from "./types.js";

export class KnowledgeClient {
  private http: HTTPClient;

  constructor(http: HTTPClient) {
    this.http = http;
  }

  async createEntity(request: EntityCreate): Promise<Entity> {
    return this.http.post<Entity>("/api/v1/knowledge/entities", request);
  }

  async getEntity(entityId: string): Promise<Entity | null> {
    try {
      return await this.http.get<Entity>(`/api/v1/knowledge/entities/${entityId}`);
    } catch {
      return null;
    }
  }

  async deleteEntity(entityId: string): Promise<boolean> {
    try {
      await this.http.delete(`/api/v1/knowledge/entities/${entityId}`);
      return true;
    } catch {
      return false;
    }
  }

  async createRelationship(request: RelationshipCreate): Promise<unknown> {
    return this.http.post("/api/v1/knowledge/relationships", request);
  }

  async getGraph(entityId: string, depth: number = 2): Promise<{
    nodes: Entity[];
    edges: unknown[];
  }> {
    return this.http.get(`/api/v1/knowledge/graph/${entityId}`, { depth });
  }

  async search(
    query: string,
    options?: { entity_type?: string; top_k?: number },
  ): Promise<Entity[]> {
    const payload: Record<string, unknown> = {
      query,
      top_k: options?.top_k ?? 10,
    };
    if (options?.entity_type) {
      payload.entity_type = options.entity_type;
    }
    const data = await this.http.post<{ entities: Entity[] }>(
      "/api/v1/knowledge/search",
      payload,
    );
    return data.entities || [];
  }
}