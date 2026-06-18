# OSS STRATEGY

> Open source, cloud, and enterprise strategy.

---

## Philosophy

Open source is the moat. The community is the distribution. The cloud is the revenue.

**Never paywall what developers need to adopt the platform.**

---

## Tiers

### Community (OSS)

**Price:** Free

**Features:**
- Memory API (CRUD, search, context)
- Search API (web + internal)
- Crawl API (scrape, crawl, map, extract)
- Knowledge API (entities, relationships, graph)
- MCP servers (all 4 tool groups)
- Python SDK
- TypeScript SDK
- CLI tool
- Self-hosting (Docker)
- PostgreSQL + pgvector (no external dependencies)
- Basic search providers (SearXNG, DuckDuckGo, Jina)
- Crawl4AI fallback
- OpenRouter BYOK for LLM
- Documentation
- Examples

### Cloud

**Price:** $29-99/mo

**Features:**
- Everything in Community
- Managed hosting (no Docker needed)
- All 5 search providers (Tavily, Brave, SearXNG, DDG, Google)
- Cross-encoder re-ranking (bge-reranker-v2-m3)
- Usage analytics dashboard
- Webhook notifications
- Priority support
- 99.9% SLA
- Team collaboration (multi-user)
- Custom domain

### Enterprise

**Price:** Custom

**Features:**
- Everything in Cloud
- SSO/SAML authentication
- Audit logs
- Custom search providers
- Custom crawl providers
- Dedicated support
- On-prem deployment
- Custom SLA
- Contract terms
- Training sessions

---

## Anti-Paywall Rules

| Rule | Explanation |
|------|-------------|
| Core API never paywalled | Memory, Search, Crawl, Knowledge APIs always free |
| Self-hosting never paywalled | Docker deployment always works |
| SDK never paywalled | Python and TypeScript SDKs always free |
| CLI never paywalled | CLI tool always free |
| MCP never paywalled | MCP servers always work locally |
| Documentation never paywalled | All docs always accessible |

**Cloud must be strictly better, not the only way to use it.**

---

## What Stays OSS

| Component | Stays OSS? | Reason |
|-----------|------------|--------|
| Memory API | ✅ Yes | Core value |
| Search API | ✅ Yes | Core value |
| Crawl API | ✅ Yes | Core value |
| Knowledge API | ✅ Yes | Core value |
| MCP Servers | ✅ Yes | Agent adoption |
| Python SDK | ✅ Yes | Adoption driver |
| TypeScript SDK | ✅ Yes | Adoption driver |
| CLI | ✅ Yes | Adoption driver |
| Docker | ✅ Yes | Self-hosting |
| pgvector | ✅ Yes | No external deps |
| SearXNG search | ✅ Yes | Free provider |
| DDG search | ✅ Yes | Free provider |
| Jina scrape | ✅ Yes | Freemium provider |
| Crawl4AI | ✅ Yes | Open source |
| Documentation | ✅ Yes | Adoption driver |
| Examples | ✅ Yes | Adoption driver |

## What Becomes Paid (Cloud)

| Component | Paid? | Reason |
|-----------|-------|--------|
| Managed hosting | ✅ Cloud | Convenience |
| Tavily search | ✅ Cloud | Paid provider cost |
| Brave search | ✅ Cloud | Paid provider cost |
| Google search | ✅ Cloud | Paid provider cost |
| Cross-encoder reranking | ✅ Cloud | Compute cost |
| Analytics dashboard | ✅ Cloud | Differentiation |
| Webhooks | ✅ Cloud | Infrastructure cost |
| Priority support | ✅ Cloud | Service value |
| Team collaboration | ✅ Cloud | Multi-user features |
| Custom domain | ✅ Cloud | Branding |

## What Becomes Enterprise

| Component | Enterprise? | Reason |
|-----------|-------------|--------|
| SSO/SAML | ✅ Enterprise | Compliance |
| Audit logs | ✅ Enterprise | Compliance |
| Custom providers | ✅ Enterprise | Customization |
| Dedicated support | ✅ Enterprise | SLA |
| On-prem deployment | ✅ Enterprise | Air-gapped |
| Custom SLA | ✅ Enterprise | Contract |
| Training | ✅ Enterprise | Service |

---

## OSS Moat Strategy

The moat is NOT features. The moat is:

### 1. Community Adoption

Developers use Context locally → recommend to team → team adopts Cloud.

### 2. MCP Integration

Context MCP works in Cursor/Claude → developers build on Context → switching cost increases.

### 3. Knowledge Graph

As more users build knowledge graphs, the shared entity graph becomes more valuable.

### 4. Provider Abstraction

Context works with any search/crawl provider → no lock-in → developers trust it.

### 5. Ecosystem

Plugins, examples, tutorials, blog posts → community creates content → organic growth.

---

## Distribution Strategy

| Channel | Strategy |
|---------|----------|
| GitHub | Star-worthy README, good first issues, active maintenance |
| Product Hunt | Launch Cloud product |
| Hacker News | Technical deep-dive post |
| Dev.to | Tutorial series |
| Twitter/X | Technical threads, demos |
| Discord | Community support |
| YouTube | Video tutorials |
| Conferences | Talks at AI/LLM conferences |

---

## Community Health

| Metric | Target (30 days) | Target (90 days) |
|--------|-------------------|-------------------|
| GitHub stars | 10 | 500 |
| Contributors | 1 | 5 |
| Issues opened | 5 | 20 |
| PRs merged | 2 | 10 |
| Discord members | 10 | 100 |
| Blog posts | 1 | 5 |

---

*Last updated: 2026-06-19*
