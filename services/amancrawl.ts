/**
 * AmanCrawl API client — web intelligence for AI agents.
 *
 * Includes auth headers from localStorage when user is authenticated.
 * Supports optional AI instructions for advanced scraping/crawling.
 */

import { buildAuthHeaders } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ScrapeResult {
  url: string;
  status_code: number;
  title: string;
  description: string;
  headings: { level: string; text: string }[];
  links: { text: string; url: string }[];
  images: { src: string; alt: string }[];
  content_length: number;
  markdown?: string;
  html?: string;
  text?: string;
  answer?: string;
  ai_instruction?: string;
  provider?: string;
  latency_ms?: number;
}

export interface CrawlResult {
  start_url: string;
  pages_crawled: number;
  pages: {
    url: string;
    title: string;
    status_code: number;
    content_length: number;
    text: string;
  }[];
  answer?: string;
  ai_instruction?: string;
  provider?: string;
  latency_ms?: number;
}

export interface MapResult {
  start_url: string;
  total_links: number;
  links: string[];
  structure: Record<string, unknown>;
  ai_instruction?: string;
  provider?: string;
  latency_ms?: number;
}

export interface SearchResult {
  query: string;
  results: {
    title: string;
    url: string;
    snippet: string;
  }[];
  answer?: string;
  ai_instruction?: string;
  provider?: string;
  latency_ms?: number;
  attempted?: { provider: string; error: string; latency_ms: number }[];
}

function authHeaders(): Record<string, string> {
  return {
    "Content-Type": "application/json",
    ...buildAuthHeaders("AmanCrawl"),
  };
}

function errDetail(data: Record<string, unknown>): string {
  const d = data.detail;
  if (typeof d === "string") return d;
  if (d && typeof d === "object") return JSON.stringify(d);
  return "";
}

export interface LimitError {
  error: string;
  resource: string;
  plan: string;
  limit: number;
  used: number;
  remaining: number;
  message: string;
}

export class LimitReachedError extends Error {
  public limitData: LimitError;
  constructor(data: LimitError) {
    super(data.message);
    this.limitData = data;
  }
}

function throwIfLimitError(res: Response, data: Record<string, unknown>): void {
  if (res.status === 429 && data.detail && typeof data.detail === "object") {
    const d = data.detail as Record<string, unknown>;
    if (d.error) {
      throw new LimitReachedError({
        error: d.error as string,
        resource: d.resource as string,
        plan: d.plan as string,
        limit: d.limit as number,
        used: d.used as number,
        remaining: d.remaining as number,
        message: d.message as string,
      });
    }
  }
}

export async function scrapeUrl(
  url: string,
  formats: string[] = ["markdown"],
  instruction?: string,
  signal?: AbortSignal,
): Promise<ScrapeResult> {
  const res = await fetch(`${API_URL}/api/amancrawl/scrape`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ url, formats, instruction: instruction || undefined }),
    signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Scrape failed (${res.status})`);
  }
  return res.json();
}

export async function crawlSite(
  url: string,
  maxPages: number = 10,
  instruction?: string,
  signal?: AbortSignal,
): Promise<CrawlResult> {
  const res = await fetch(`${API_URL}/api/amancrawl/crawl`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ url, max_pages: maxPages, instruction: instruction || undefined }),
    signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Crawl failed (${res.status})`);
  }
  return res.json();
}

export async function mapSite(
  url: string,
  instruction?: string,
  signal?: AbortSignal,
): Promise<MapResult> {
  const res = await fetch(`${API_URL}/api/amancrawl/map`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ url, instruction: instruction || undefined }),
    signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Map failed (${res.status})`);
  }
  return res.json();
}

export async function searchWeb(
  query: string,
  numResults: number = 5,
  instruction?: string,
  signal?: AbortSignal,
): Promise<SearchResult> {
  const res = await fetch(`${API_URL}/api/amancrawl/search`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ query, num_results: numResults, instruction: instruction || undefined }),
    signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Search failed (${res.status})`);
  }
  return res.json();
}

export async function refinePrompt(
  instruction: string,
  context: string,
): Promise<string> {
  const res = await fetch(`${API_URL}/api/amancrawl/refine-prompt`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ instruction, context }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Refine failed (${res.status})`);
  }
  const data = await res.json();
  return data.refined;
}

// ── AI Agent extraction ──────────────────────────────────────────────────

export interface AgentExtractResult {
  url: string;
  instruction: string;
  result: unknown;
  raw_content: string;
  raw_length: number;
  model: string;
  tokens_used: number;
  error?: string;
  provider?: string;
  latency_ms?: number;
}

export async function agentExtract(
  url: string,
  instruction: string,
  outputFormat: string = "auto",
  model: string = "openai/gpt-4o-mini",
  signal?: AbortSignal,
): Promise<AgentExtractResult> {
  const res = await fetch(`${API_URL}/api/amancrawl/agent/extract`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ url, instruction, output_format: outputFormat, model }),
    signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Agent extract failed (${res.status})`);
  }
  return res.json();
}

// ── Intelligence pipeline (SSE) ─────────────────────────────────────────

export interface IntelligenceStep {
  step: string;
  status: "running" | "complete" | "error";
  elapsed_ms?: number;
}

export interface IntelligencePlan {
  query_type: string;
  steps: { action: string; agent: string; description: string }[];
  confidence: number;
  reasoning: string;
}

export interface IntelligenceResult {
  query: string;
  query_type: string;
  answer: string;
  confidence: number;
  sources: { type: string; title?: string; url?: string; snippet?: string; summary?: string }[];
  entities: { type: string; name: string; properties: Record<string, unknown> }[];
  relationships: { source: string; target: string; type: string; properties: Record<string, unknown> }[];
  citations: { type: string; title?: string; url?: string }[];
  plan: { query_type: string; steps: number; reasoning: string };
  execution_time_ms: number;
  agents_used: string[];
}

export type IntelligenceEventType =
  | "step"
  | "plan"
  | "result"
  | "knowledge_stored"
  | "error"
  | "done";

export interface IntelligenceEvent {
  type: IntelligenceEventType;
  data: IntelligenceStep | IntelligencePlan | IntelligenceResult | { message: string; issues?: string[] } | { elapsed_ms: number };
}

export interface IntelligenceCallbacks {
  onStep?: (step: IntelligenceStep) => void;
  onPlan?: (plan: IntelligencePlan) => void;
  onResult?: (result: IntelligenceResult) => void;
  onError?: (message: string, issues?: string[]) => void;
  onDone?: (elapsedMs: number) => void;
  onKnowledgeStored?: (data: { entities_stored: number; relationships_stored: number }) => void;
}

export async function intelligenceQuery(
  query: string,
  callbacks: IntelligenceCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_URL}/api/intelligence/query`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ query, mode: "auto" }),
    signal,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throwIfLimitError(res, data);
    throw new Error(errDetail(data) || `Intelligence query failed (${res.status})`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let eventType = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const raw = line.slice(6);
        try {
          const parsed = JSON.parse(raw);
          switch (eventType) {
            case "step":
              callbacks.onStep?.(parsed as IntelligenceStep);
              break;
            case "plan":
              callbacks.onPlan?.(parsed as IntelligencePlan);
              break;
            case "result":
              callbacks.onResult?.(parsed as IntelligenceResult);
              break;
            case "knowledge_stored":
              callbacks.onKnowledgeStored?.(parsed);
              break;
            case "error":
              callbacks.onError?.(parsed.message, parsed.issues);
              break;
            case "done":
              callbacks.onDone?.(parsed.elapsed_ms);
              break;
          }
        } catch {
          // Skip unparseable lines
        }
        eventType = "";
      }
    }
  }
}
