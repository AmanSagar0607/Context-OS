# app/routes/oauth.py
"""
OAuth routes — Google and GitHub OAuth login flows.
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.auth_middleware import AuthContext, require_auth
from app.config import get_settings
from services.oauth_service import (
    get_authorization_url, generate_oauth_state,
    exchange_code_for_token, get_user_info, find_or_create_oauth_user,
)
from services.auth_store import create_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

# In-memory state store (use Redis in production)
_oauth_states: dict[str, dict] = {}


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login flow. Returns redirect URL."""
    if provider not in ("google", "github"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    settings = get_settings()
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/oauth/{provider}/callback"

    state = generate_oauth_state()
    _oauth_states[state] = {"provider": provider, "created_at": __import__("time").time()}

    auth_url = get_authorization_url(provider, redirect_uri, state)
    if not auth_url:
        raise HTTPException(status_code=500, detail=f"OAuth not configured for {provider}")

    return {"auth_url": auth_url, "state": state}


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback. Creates session and redirects to frontend."""
    if provider not in ("google", "github"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    state_data = _oauth_states.pop(state)
    settings = get_settings()
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/oauth/{provider}/callback"

    # Exchange code for token
    token_data = await exchange_code_for_token(provider, code, redirect_uri)
    if not token_data or not token_data.get("access_token"):
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    # Get user info
    user_info = await get_user_info(provider, token_data["access_token"])
    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Failed to get user info")

    # Find or create user
    user = find_or_create_oauth_user(user_info)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Create session
    session = create_session(user["id"])

    # Redirect to frontend with session data
    frontend_url = settings.frontend_url or "http://localhost:3000"
    params = {
        "access_token": session["access_token"],
        "user_id": user["id"],
        "email": user["email"],
        "plan": user.get("plan", "free"),
    }
    redirect_url = f"{frontend_url}/auth/callback?{urlencode(params)}"

    return RedirectResponse(url=redirect_url)


@router.delete("/{provider}/unlink")
async def oauth_unlink(provider: str, auth: AuthContext = Depends(require_auth)):
    """Unlink an OAuth provider from the current user."""
    from services.postgres_store import _connect as pg_connect

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM auth_identities WHERE user_id = %s AND provider = %s",
                (auth.user_id, provider),
            )
            deleted = cur.rowcount > 0
            conn.commit()
        conn.close()
        return {"unlinked": deleted, "provider": provider}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/linked")
async def linked_providers(auth: AuthContext = Depends(require_auth)):
    """List linked OAuth providers for the current user."""
    from services.postgres_store import _connect as pg_connect

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT provider, display_name, avatar_url, created_at FROM auth_identities WHERE user_id = %s",
                (auth.user_id,),
            )
            rows = cur.fetchall()
        conn.close()

        return {
            "providers": [
                {
                    "provider": row[0],
                    "display_name": row[1],
                    "avatar_url": row[2],
                    "linked_at": row[3].isoformat() if row[3] else None,
                }
                for row in rows
            ]
        }
    except Exception as e:
        conn.close()
        return {"providers": []}
