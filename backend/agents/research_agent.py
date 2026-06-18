# agents/research_agent.py
"""
Research Agent — Search, scrape, crawl, map, extract, research.

Responsibilities:
- Web search via multi-provider search router
- URL scraping with anti-bot fallbacks
- Site crawling for multi-page extraction
- Site mapping for URL discovery
- Content extraction and structuring
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from services.crawl_service import scrape_url, crawl_site, map_site, search_web
from services.agent_service import scrape_and_extract
from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)


async def research_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute research steps."""
    if step.action == TaskAction.SEARCH:
        return await _search(context)
    elif step.action == TaskAction.SCRAPE:
        return await _scrape(context)
    elif step.action == TaskAction.CRAWL:
        return await _crawl(context)
    elif step.action == TaskAction.MAP:
        return await _map(context)
    elif step.action == TaskAction.EXTRACT:
        return await _extract(context)
    elif step.action == TaskAction.ANSWER:
        return await _synthesize(context)
    return AgentResult(agent="research", action=step.action.value, data=None)


async def _search(context: RouteContext) -> AgentResult:
    """Search the web for relevant information."""
    start = time.time()
    results = []
    sources = []
    
    try:
        search_results = search_web(context.query)
        results = search_results
        context.search_results = search_results
        
        for res in search_results:
            sources.append({
                "type": "web_search",
                "title": res.get("title", ""),
                "url": res.get("url", ""),
                "snippet": res.get("snippet", "")[:200],
                "provider": res.get("provider", "unknown"),
            })
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
    
    return AgentResult(
        agent="research",
        action="search",
        data={"result_count": len(results)},
        confidence=min(len(results) / 3, 1.0),
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _scrape(context: RouteContext) -> AgentResult:
    """Scrape a URL for content."""
    start = time.time()
    sources = []
    content = ""
    
    # Extract URL from query
    url_match = re.search(r'https?://[^\s]+', context.query)
    if not url_match:
        # Try to find a URL-like pattern
        words = context.query.split()
        for word in words:
            if '.' in word and not word.startswith('.'):
                url_match = re.search(r'https?://[^\s]+', word)
                break
    
    if url_match:
        url = url_match.group(0)
        try:
            result = await scrape_url(url)
            content = result.get("markdown", result.get("content", ""))
            context.scraped_content = content
            sources.append({
                "type": "scrape",
                "url": url,
                "content_length": len(content),
                "provider": result.get("provider", "unknown"),
            })
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
    
    return AgentResult(
        agent="research",
        action="scrape",
        data={
            "content_length": len(content),
            "url": url_match.group(0) if url_match else None,
        },
        confidence=1.0 if content else 0.0,
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _crawl(context: RouteContext) -> AgentResult:
    """Crawl a website for multi-page content."""
    start = time.time()
    sources = []
    
    url_match = re.search(r'https?://[^\s]+', context.query)
    if url_match:
        url = url_match.group(0)
        try:
            pages = await crawl_site(url, max_pages=20)
            context.scraped_content = "\n\n".join(
                p.get("content", "") for p in pages
            )
            sources.append({
                "type": "crawl",
                "url": url,
                "pages_found": len(pages),
            })
        except Exception as e:
            logger.error(f"Crawl failed for {url}: {e}")
    
    return AgentResult(
        agent="research",
        action="crawl",
        data={"pages": len(sources)},
        confidence=1.0 if sources else 0.0,
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _map(context: RouteContext) -> AgentResult:
    """Map a website structure."""
    start = time.time()
    sources = []
    
    url_match = re.search(r'https?://[^\s]+', context.query)
    if url_match:
        url = url_match.group(0)
        try:
            links = await map_site(url)
            sources.append({
                "type": "map",
                "url": url,
                "links_found": len(links),
                "links": links[:50],  # Limit for context
            })
        except Exception as e:
            logger.error(f"Map failed for {url}: {e}")
    
    return AgentResult(
        agent="research",
        action="map",
        data={"links": len(sources)},
        confidence=1.0 if sources else 0.0,
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _extract(context: RouteContext) -> AgentResult:
    """Extract structured information from content."""
    start = time.time()
    sources = []
    content = context.scraped_content
    
    if not content and context.search_results:
        # Use search results as content source
        content = "\n".join(
            f"{r.get('title', '')}: {r.get('snippet', '')}"
            for r in context.search_results
        )
    
    if content:
        try:
            # Use agent_service for LLM extraction
            result = await scrape_and_extract(
                url="",
                instruction=f"Extract key information from this content: {context.query}",
                content=content,
            )
            sources.append({
                "type": "extract",
                "structured_data": result.get("result", ""),
            })
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
    
    return AgentResult(
        agent="research",
        action="extract",
        data={"has_content": bool(content)},
        confidence=1.0 if content else 0.0,
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _synthesize(context: RouteContext) -> AgentResult:
    """Synthesize all research into a comprehensive answer."""
    # Combine all sources
    all_context = []
    
    if context.search_results:
        all_context.append("=== SEARCH RESULTS ===")
        for r in context.search_results[:5]:
            all_context.append(f"- {r.get('title', '')}: {r.get('snippet', '')}")
    
    if context.scraped_content:
        all_context.append("\n=== SCRAPED CONTENT ===")
        all_context.append(context.scraped_content[:2000])
    
    if context.retrieved_chunks:
        all_context.append("\n=== DOCUMENT CONTEXT ===")
        for chunk in context.retrieved_chunks[:3]:
            all_context.append(f"- {chunk.get('text', '')[:200]}")
    
    return AgentResult(
        agent="research",
        action="synthesize",
        data={
            "context": "\n".join(all_context),
            "source_count": len(context.citations) + len(context.search_results),
        },
        sources=context.citations,
    )
