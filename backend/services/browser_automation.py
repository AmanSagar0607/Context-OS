# services/browser_automation.py
"""
Browser Automation Service — Playwright-based dynamic content extraction.

Handles JavaScript-rendered pages, SPAs, and dynamic content that
static HTTP clients cannot capture.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Lazy-loaded playwright
_playwright = None
_browser = None


async def _get_browser():
    """Get or create a Playwright browser instance."""
    global _playwright, _browser

    if _browser and _browser.is_connected():
        return _browser

    try:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
            ],
        )
        return _browser
    except ImportError:
        logger.warning("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return None
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        return None


async def close_browser():
    """Close the browser instance."""
    global _playwright, _browser
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


async def render_page(
    url: str,
    wait_for: str = "networkidle",
    timeout: int = 30000,
    screenshot: bool = False,
    extract_text: bool = True,
) -> dict[str, Any]:
    """
    Render a page with Playwright and extract content.

    Args:
        url: URL to render
        wait_for: When to consider page loaded ('load', 'domcontentloaded', 'networkidle')
        timeout: Max wait time in ms
        screenshot: Whether to capture a screenshot
        extract_text: Whether to extract text content

    Returns:
        Dict with page content, metadata, and optional screenshot
    """
    browser = await _get_browser()
    if not browser:
        return {"error": "Playwright not available", "url": url}

    start_time = time.time()
    result = {
        "url": url,
        "status": None,
        "title": None,
        "content": None,
        "markdown": None,
        "links": [],
        "metadata": {},
        "render_time_ms": 0,
    }

    try:
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        # Navigate
        response = await page.goto(url, wait_until=wait_for, timeout=timeout)
        result["status"] = response.status if response else None

        # Get title
        result["title"] = await page.title()

        # Extract text content
        if extract_text:
            result["content"] = await page.inner_text("body")
            # Try to get main content
            main_content = await page.query_selector("main, article, .content, .post, #content")
            if main_content:
                result["content"] = await main_content.inner_text()

        # Extract links
        links = await page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.textContent.trim(), href: e.href}))")
        result["links"] = [l for l in links if l.get("href") and l["href"].startswith("http")][:50]

        # Metadata
        meta_tags = await page.eval_on_selector_all("meta", """els => els.map(e => ({
            name: e.getAttribute('name') || e.getAttribute('property') || '',
            content: e.getAttribute('content') || ''
        }))""")
        result["metadata"] = {m["name"]: m["content"] for m in meta_tags if m["name"]}

        # Screenshot
        if screenshot:
            screenshot_bytes = await page.screenshot(full_page=False)
            import base64
            result["screenshot"] = base64.b64encode(screenshot_bytes).decode()

        await context.close()

    except Exception as e:
        logger.error(f"Browser render failed for {url}: {e}")
        result["error"] = str(e)

    result["render_time_ms"] = round((time.time() - start_time) * 1000)
    return result


async def extract_structured_data(
    url: str,
    selectors: dict[str, str],
    wait_for: str = "networkidle",
    timeout: int = 30000,
) -> dict[str, Any]:
    """
    Extract structured data from a page using CSS selectors.

    Args:
        url: URL to scrape
        selectors: Dict mapping field names to CSS selectors
        wait_for: When to consider page loaded
        timeout: Max wait time in ms

    Returns:
        Dict with extracted fields
    """
    browser = await _get_browser()
    if not browser:
        return {"error": "Playwright not available"}

    result = {"url": url, "data": {}, "render_time_ms": 0}
    start_time = time.time()

    try:
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        await page.goto(url, wait_until=wait_for, timeout=timeout)

        for field_name, selector in selectors.items():
            try:
                element = await page.query_selector(selector)
                if element:
                    result["data"][field_name] = await element.inner_text()
                else:
                    result["data"][field_name] = None
            except Exception:
                result["data"][field_name] = None

        await context.close()

    except Exception as e:
        result["error"] = str(e)

    result["render_time_ms"] = round((time.time() - start_time) * 1000)
    return result


async def take_screenshot(
    url: str,
    full_page: bool = False,
    width: int = 1920,
    height: int = 1080,
) -> dict[str, Any]:
    """Take a screenshot of a page."""
    browser = await _get_browser()
    if not browser:
        return {"error": "Playwright not available"}

    try:
        context = await browser.new_context(viewport={"width": width, "height": height})
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)

        screenshot_bytes = await page.screenshot(full_page=full_page)
        await context.close()

        import base64
        return {
            "url": url,
            "screenshot": base64.b64encode(screenshot_bytes).decode(),
            "width": width,
            "height": height,
        }
    except Exception as e:
        return {"error": str(e), "url": url}
