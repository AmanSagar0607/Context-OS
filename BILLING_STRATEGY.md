# BILLING STRATEGY

> Monetization and billing design.

---

## Provider

**Recommended:** Polar

**Why Polar over LemonSqueezy:**
- Better developer experience
- Usage-based billing support
- Open-source friendly
- Lower fees for indie projects
- Better API

**Alternative:** LemonSqueezy (if Polar doesn't work out)

---

## Pricing Model

### Plans

| Plan | Price | Memory | Crawl | Search | Knowledge |
|------|-------|--------|-------|--------|-----------|
| **Free** | $0 | 1K memories | 100 scrapes/day | 50 searches/day | 100 entities |
| **Pro** | $29/mo | 100K memories | 10K scrapes/day | 5K searches/day | 10K entities |
| **Team** | $99/mo | 1M memories | 100K scrapes/day | 50K searches/day | 100K entities |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited | Unlimited |

### Usage-Based Additions

| Resource | Free | Pro | Team |
|----------|------|-----|------|
| memory.store | 1K/mo | 100K/mo | 1M/mo |
| memory.search | 100/day | 10K/day | 100K/day |
| crawl.scrape | 100/day | 10K/day | 100K/day |
| crawl.crawl | 100/day | 10K/day | 100K/day |
| crawl.extract | 50/day | 5K/day | 50K/day |
| search.web | 50/day | 5K/day | 50K/day |
| knowledge.entity | 100/mo | 10K/mo | 100K/mo |
| knowledge.relationship | 100/mo | 10K/mo | 100K/mo |

---

## Resource Tracking

### What to Track

| Resource | Unit | Table Column |
|----------|------|--------------|
| memory.store | 1 memory stored | `resource_key = 'memory.store'` |
| memory.search | 1 search query | `resource_key = 'memory.search'` |
| crawl.scrape | 1 URL scraped | `resource_key = 'crawl.scrape'` |
| crawl.crawl | 1 page crawled | `resource_key = 'crawl.crawl'` |
| crawl.extract | 1 extraction | `resource_key = 'crawl.extract'` |
| search.web | 1 web search | `resource_key = 'search.web'` |
| knowledge.entity | 1 entity created | `resource_key = 'knowledge.entity'` |
| knowledge.relationship | 1 relationship created | `resource_key = 'knowledge.relationship'` |

### Where to Track

```sql
-- Existing table: usage_records
INSERT INTO usage_records (
    user_id, subscription_id, resource_key, quantity,
    model, provider, tokens_input, tokens_output,
    cost_cents, endpoint, metadata
) VALUES (...);
```

### Where to Enforce

```python
# apps/server/middleware/rate_limit.py

async def check_rate_limit(api_key: str, resource_key: str) -> bool:
    """Check if API key has remaining quota for resource."""
    # 1. Look up user's subscription
    # 2. Look up plan limits
    # 3. Check current usage
    # 4. Return True if under limit
```

---

## Architecture

```
Request
  ↓
┌──────────────┐
│ Auth Middleware│ → Identify API key → User → Subscription
└──────┬───────┘
       │
┌──────▼───────┐
│ Rate Limiter │ → Check resource_key against plan limits
└──────┬───────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
Under      Over
limit      limit
  │         │
  ▼         ▼
Process   Return 429
  │
  ▼
┌──────────────┐
│ Usage Tracker│ → Record usage in usage_records
└──────────────┘
```

---

## Implementation Plan

### Phase 1: Basic Rate Limiting (Week 1-2)

1. Add `plan_limits` lookup to middleware
2. Check limits before processing request
3. Return 429 with `X-RateLimit-*` headers

### Phase 2: Usage Recording (Week 2-3)

1. Record usage after successful request
2. Update `usage_aggregates` daily (cron job)
3. Expose usage endpoint

### Phase 3: Billing Integration (Week 3-4)

1. Integrate Polar SDK
2. Create checkout flow
3. Handle webhooks (subscription created/updated/canceled)
4. Sync plan changes

### Phase 4: Dashboard (Cloud only)

1. Usage visualization
2. Plan management
3. Invoice history

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/usage` | Current month usage |
| GET | `/api/v1/usage/history` | Usage history |
| GET | `/api/v1/subscription` | Current subscription |
| POST | `/api/v1/subscription/checkout` | Create checkout |
| POST | `/api/v1/subscription/webhook` | Handle webhooks |
| GET | `/api/v1/plans` | List available plans |

---

## Headers

### Response Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1624567890
X-Usage-Memory-Store: 50
X-Usage-Memory-Store-Limit: 1000
```

### Error Response

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded your memory.store limit",
  "resource": "memory.store",
  "limit": 1000,
  "current": 1001,
  "reset_at": "2026-07-01T00:00:00Z",
  "upgrade_url": "https://context.ai/pricing"
}
```

---

## Revenue Projections

| Month | Users | Paying | MRR |
|-------|-------|--------|-----|
| 1 | 10 | 0 | $0 |
| 2 | 50 | 2 | $58 |
| 3 | 200 | 10 | $290 |
| 6 | 1,000 | 50 | $1,450 |
| 12 | 5,000 | 200 | $5,800 |

---

*Last updated: 2026-06-19*
