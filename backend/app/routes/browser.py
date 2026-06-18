# app/routes/browser.py
"""
Browser Automation routes — Playwright-based dynamic content extraction.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth_middleware import AuthContext, require_auth
from services.browser_automation import render_page, extract_structured_data, take_screenshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/browser", tags=["browser"])


class RenderRequest(BaseModel):
    url: str
    wait_for: str = "networkidle"
    timeout: int = 30000
    screenshot: bool = False


class ExtractRequest(BaseModel):
    url: str
    selectors: dict[str, str]
    wait_for: str = "networkidle"
    timeout: int = 30000


class ScreenshotRequest(BaseModel):
    url: str
    full_page: bool = False
    width: int = 1920
    height: int = 1080


@router.post("/render")
async def render(body: RenderRequest, auth: AuthContext = Depends(require_auth)):
    """Render a JavaScript-heavy page with Playwright and extract content."""
    result = await render_page(
        url=body.url,
        wait_for=body.wait_for,
        timeout=body.timeout,
        screenshot=body.screenshot,
    )
    if "error" in result and not result.get("content"):
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@router.post("/extract")
async def extract(body: ExtractRequest, auth: AuthContext = Depends(require_auth)):
    """Extract structured data from a page using CSS selectors."""
    result = await extract_structured_data(
        url=body.url,
        selectors=body.selectors,
        wait_for=body.wait_for,
        timeout=body.timeout,
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@router.post("/screenshot")
async def screenshot(body: ScreenshotRequest, auth: AuthContext = Depends(require_auth)):
    """Take a screenshot of a page."""
    result = await take_screenshot(
        url=body.url,
        full_page=body.full_page,
        width=body.width,
        height=body.height,
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@router.get("/health")
async def health():
    """Check if Playwright is available."""
    try:
        from playwright.async_api import async_playwright
        return {"available": True, "status": "healthy"}
    except ImportError:
        return {"available": False, "status": "playwright not installed"}
