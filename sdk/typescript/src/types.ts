/**
 * Context AI — TypeScript SDK Types
 */

// --- Enums ---

export enum MemoryType {
  EPISODIC = "episodic",
  SEMANTIC = "semantic",
  PROCEDURAL = "procedural",
}

export enum ImportanceLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

// --- Memory Types ---

export interface MemoryCreate {
  content: string;
  summary?: string;
  memory_type?: MemoryType;
  importance?: ImportanceLevel;
  tags?: string[];
  source?: string;
  metadata?: Record<string, unknown>;
  agent_id?: string;
  session_id?: string;
}

export interface MemoryUpdate {
  content?: string;
  summary?: string;
  memory_type?: MemoryType;
  importance?: ImportanceLevel;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface Memory {
  id: string;
  content: string;
  summary?: string;
  memory_type: MemoryType;
  importance: ImportanceLevel;
  tags: string[];
  source?: string;
  metadata: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface MemorySearchRequest {
  query: string;
  memory_type?: MemoryType;
  tags?: string[];
  top_k?: number;
  min_score?: number;
}

export interface MemorySearchResult {
  memory: Memory;
  score: number;
}

// --- Search Types ---

export interface SearchRequest {
  query: string;
  max_results?: number;
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  score?: number;
}

// --- Crawl Types ---

export interface CrawlRequest {
  url: string;
  max_pages?: number;
  extract_content?: boolean;
}

export interface CrawlResult {
  url: string;
  title?: string;
  content: string;
  metadata: Record<string, unknown>;
}

// --- Knowledge Types ---

export interface EntityCreate {
  name: string;
  entity_type?: string;
  description?: string;
  properties?: Record<string, unknown>;
}

export interface Entity {
  id: string;
  name: string;
  entity_type: string;
  description?: string;
  properties: Record<string, unknown>;
  created_at?: string;
}

export interface RelationshipCreate {
  source_id: string;
  target_id: string;
  relationship_type?: string;
  weight?: number;
  properties?: Record<string, unknown>;
}

// --- API Response Types ---

export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}