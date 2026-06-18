# Firecrawl Market Research — Lessons for AmanAgentLab

If you're doing **market research on Firecrawl** to improve AmanAgentLab, don't think of Firecrawl as "a scraper."

Think of it as a **Web Context Operating System for AI Agents**.

Their entire product is basically:

```text
Find → Access → Extract → Structure → Reason
```

---

## Firecrawl's Product Layers

### 1. Search

User says:

```text
Find AI startups building browser agents
```

Firecrawl:

```text
Search Query
    ↓
Search Providers
    ↓
Top URLs
    ↓
Clean Content
```

Value:

- No Google scraping code
- No SERP parsing
- Returns content, not links

This is why `/search` exists. It combines search + scrape.

---

### 2. Scrape

User already knows the URL.

```text
https://langchain.com
```

Firecrawl:

```text
URL
 ↓
Browser
 ↓
Cleanup
 ↓
Markdown
```

Output:

```markdown
# LangChain

Build AI applications...
```

instead of:

```html
<div class="hero">
...
```

This is their biggest value proposition: **LLM-ready content.**

---

### 3. Crawl

User wants:

```text
Entire documentation site
```

Firecrawl:

```text
Root URL
   ↓
Discover Links
   ↓
Visit Pages
   ↓
Extract
   ↓
Return Dataset
```

Example:

```text
docs.langchain.com
```

returns:

```text
1000+
pages
```

This powers:

- Documentation RAG
- Knowledge bases
- Website indexing

---

### 4. Map

This one is underrated.

```text
Website
   ↓
Map
   ↓
URL Inventory
```

Example:

```text
amanagentlab.com
```

returns:

```text
/
/docs
/blog
/pricing
/features
...
```

without crawling everything.

Useful for:

- Site discovery
- Competitive intelligence
- Documentation indexing

---

### 5. Extract

Instead of:

```text
Get page text
```

you ask:

```text
Extract:
- company name
- founders
- pricing
```

Firecrawl:

```text
Web Page
     ↓
LLM
     ↓
Structured JSON
```

Output:

```json
{
  "company":"Firecrawl",
  "pricing":"$16/month"
}
```

This is a huge market research feature.

---

### 6. Agent

This is where they're heading.

User:

```text
Find the top browser AI startups
and compare them
```

Firecrawl Agent:

```text
Search
 ↓
Browse
 ↓
Extract
 ↓
Reason
 ↓
Report
```

Instead of manually chaining APIs.

Their `/agent` endpoint is essentially "deep research as a service."

---

### 7. Browser

Most people miss this.

Firecrawl isn't only scraping.

It also provides:

```text
Remote Browser Sessions
```

```text
Open Browser
 ↓
Click
 ↓
Type
 ↓
Wait
 ↓
Extract
```

Similar conceptually to:

- Browserbase
- Browser Use
- BrowserStation

---

## How This Applies to AmanAgentLab

Right now you have:

```text
PDF Upload
     ↓
Milvus
     ↓
RAG
```

Firecrawl teaches a bigger lesson:

**Context comes from many sources, not just PDFs.**

Future AmanAgentLab:

```text
Context Sources

PDFs
Websites
Documentation
GitHub Repos
Notion
Conversations
Memory
Monitoring Jobs
```

---

## AmanAgentLab Equivalent Services

| Firecrawl | AmanAgentLab                  |
| --------- | ----------------------------- |
| Search    | Research Service              |
| Scrape    | URL Ingestion Service         |
| Crawl     | Site Knowledge Builder        |
| Map       | Site Discovery Service        |
| Extract   | Structured Extraction Service |
| Agent     | Research Agent                |
| Browser   | Browser Agent                 |

---

## The Biggest Opportunity

Firecrawl is optimized for:

```text
Web → AI
```

Your opportunity is:

```text
Everything → AI
```

```text
PDF
GitHub
Notion
Web
Memory
Conversations
Files
Monitoring
```

into one knowledge layer.

That means AmanAgentLab eventually becomes:

```text
Personal Knowledge OS
          +
Research Agent Platform
          +
Memory System
```

while Firecrawl remains focused on being the best **web context infrastructure**. That's a larger and potentially more defensible product direction than competing head-to-head as another scraper.
