/**
 * Context AI — HTTP Client
 */

export interface HTTPClientOptions {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
}

export class HTTPClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(options: HTTPClientOptions = {}) {
    this.baseUrl = (options.baseUrl || "http://localhost:8000").replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.timeout = options.timeout ?? 30000;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    params?: Record<string, string | number | boolean>,
  ): Promise<T> {
    let url = `${this.baseUrl}${path}`;

    if (params) {
      const searchParams = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        searchParams.set(key, String(value));
      }
      url += `?${searchParams.toString()}`;
    }

    const response = await fetch(url, {
      method,
      headers: this.getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  async get<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
    return this.request<T>("GET", path, undefined, params);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, body);
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PUT", path, body);
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}