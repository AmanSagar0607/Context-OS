# PRODUCT STRATEGY

> Positioning, thesis, and competitive analysis.

---

## Positioning Statement

> The open-source context infrastructure that gives AI agents memory, web intelligence, and structured knowledge — via a single API and MCP server.

## One Paragraph

> Context is the missing infrastructure layer for AI agents. Every AI application eventually needs memory, retrieval, knowledge, and web intelligence. Today these capabilities are fragmented across Mem0, Firecrawl, LangGraph, and custom code. Context unifies them into a single developer platform with REST APIs, Python/TypeScript SDKs, a CLI, and MCP servers. Self-hostable. Open source. API-first.

## Homepage Headline

> Power AI agents with persistent memory, web intelligence, and structured knowledge.

## Homepage Subheadline

> One API for memory, search, crawl, and knowledge. Open source. Self-hostable. MCP-native.

## Tagline

> AI can finally remember.

---

## Product Thesis

Every AI application eventually needs:

1. **Memory** — What happened before? What does the user prefer?
2. **Context** — What information is relevant right now?
3. **Retrieval** — How do I find the right information?
4. **Knowledge** — What entities and relationships exist?
5. **Search** — What does the web know about this?
6. **Web Intelligence** — How do I scrape, crawl, and extract from the web?

Today these capabilities are fragmented across multiple tools:

| Capability | Current Tool |
|------------|--------------|
| Memory | Mem0, Zep, custom |
| Search | Tavily, Brave, custom |
| Crawl | Firecrawl, Crawl4AI, custom |
| Knowledge | Neo4j, custom |
| MCP | Custom servers |

The opportunity is to unify them into a single developer platform.

---

## Product Categories

| Category | Description | Competitor |
|----------|-------------|------------|
| **Context Memory** | Persistent agent memory with semantic search | Mem0, Zep |
| **Context Search** | Hybrid web + internal search | Firecrawl (partial) |
| **Context Crawl** | Web intelligence with fallback chain | Firecrawl, Crawl4AI |
| **Context Knowledge** | Entity/relationship extraction and graph | Custom |
| **Context MCP** | MCP servers for all of the above | Custom |

---

## Competitive Analysis

### Mem0

**What they do:** Memory layer for AI agents.

| Aspect | Assessment |
|--------|------------|
| Strengths | Clean API, good docs, growing adoption |
| Weaknesses | Memory only. No web intelligence. No knowledge graph. No MCP. |
| Our differentiation | Memory + Web Intelligence + Knowledge Graph + MCP |

**Feature comparison:**

| Feature | Mem0 | Context |
|---------|------|---------|
| Memory CRUD | ✅ | ✅ |
| Semantic search | ✅ | ✅ |
| Hybrid search | ❌ | ✅ (vector + BM25) |
| Knowledge graph | ❌ | ✅ |
| Web search | ❌ | ✅ |
| Web crawl | ❌ | ✅ |
| MCP | ❌ | ✅ |
| Self-hostable | ✅ | ✅ |

### Firecrawl

**What they do:** Web scraping/crawling API.

| Aspect | Assessment |
|--------|------------|
| Strengths | Multi-provider scraping, good DX, self-hostable |
| Weaknesses | No memory. No knowledge graph. No MCP. No internal search. |
| Our differentiation | Web intelligence + Memory + Knowledge Graph + MCP |

**Feature comparison:**

| Feature | Firecrawl | Context |
|---------|-----------|---------|
| Scrape URL | ✅ | ✅ |
| Crawl website | ✅ | ✅ |
| Site map | ✅ | ✅ |
| Web search | ❌ | ✅ |
| AI extraction | ✅ | ✅ |
| Browser render | ✅ | ✅ |
| Memory | ❌ | ✅ |
| Knowledge graph | ❌ | ✅ |
| MCP | ❌ | ✅ |

### Zep

**What they do:** Memory + knowledge for AI assistants.

| Aspect | Assessment |
|--------|------------|
| Strengths | Temporal knowledge graph, long-term memory |
| Weaknesses | Focus on chat assistants. No web intelligence. No MCP. |
| Our differentiation | Broader scope (web intelligence), MCP-native |

### Letta

**What they do:** Stateful AI agents with memory.

| Aspect | Assessment |
|--------|------------|
| Strengths | Agent state management, memory architecture |
| Weaknesses | Agent framework, not infrastructure. No web intelligence. |
| Our differentiation | Infrastructure layer, not agent framework. MCP-native |

### LangGraph

**What they do:** Agent orchestration framework.

| Aspect | Assessment |
|--------|------------|
| Strengths | Graph-based workflows, large ecosystem |
| Weaknesses | Orchestration only. No built-in memory/search/crawl infrastructure. |
| Our differentiation | Infrastructure layer that LangGraph agents can consume |

### CrewAI

**What they do:** Multi-agent orchestration.

| Aspect | Assessment |
|--------|------------|
| Strengths | Simple agent definition, role-based agents |
| Weaknesses | Orchestration only. No memory/search/crawl infrastructure. |
| Our differentiation | Infrastructure layer, not orchestration framework |

---

## Competitive Summary

| Capability | Mem0 | Firecrawl | Zep | Letta | LangGraph | CrewAI | **Context** |
|------------|------|-----------|-----|-------|-----------|--------|-------------|
| Memory | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Web Search | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Web Crawl | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Knowledge Graph | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| MCP | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Self-hostable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Open Source | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**The combination is unique. No one else has all five capabilities in one platform.**

---

## What We Are NOT Building

| Not Building | Why |
|--------------|-----|
| AI Operating System | Too broad, not focused |
| AI Workspace | Already exists (Notion, etc.) |
| ChatGPT Clone | Saturated market |
| Productivity Platform | Not infrastructure |
| PDF Chat Application | Too narrow |
| Personal Assistant | Not developer tooling |

## What We ARE Building

Context Infrastructure Platform for AI Agents.

The infrastructure layer that sits between AI agents and the information they need.

---

## Target Users

| User | Need | How We Help |
|------|------|-------------|
| AI Agent Builder | Memory for agents | Memory API + MCP |
| RAG Developer | Better retrieval | Hybrid retrieval pipeline |
| Chat Application | Conversation memory | Memory API + SDK |
| Research Agent | Web intelligence | Search + Crawl API |
| Knowledge Builder | Entity extraction | Knowledge API |
| IDE Integration | Tool access | MCP servers |

---

## Key Metrics

| Metric | Target (30 days) | Target (90 days) | Target (365 days) |
|--------|-------------------|-------------------|---------------------|
| Retrieval precision@5 | 70% | 80% | 85%+ |
| GitHub stars | 10 | 500 | 5,000 |
| External users | 5 | 50 | 2,000 |
| Paying customers | 0 | 10 | 500 |
| MRR | $0 | $500 | $25,000 |

---

*Last updated: 2026-06-19*
