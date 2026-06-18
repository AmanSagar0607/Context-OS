# services/oauth_service.py
"""
OAuth Service — Google and GitHub OAuth provider integration.

Handles OAuth authorization URLs, callback processing, and account linking.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── OAuth Provider Configs ────────────────────────────────────────────────

PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scopes": ["read:user", "user:email"],
    },
}


def get_provider_config(provider: str) -> dict | None:
    """Get OAuth provider configuration."""
    return PROVIDERS.get(provider)


def get_client_credentials(provider: str) -> tuple[str, str]:
    """Get client ID and secret for a provider."""
    settings = get_settings()

    if provider == "google":
        return (
            getattr(settings, "google_client_id", "") or "",
            getattr(settings, "google_client_secret", "") or "",
        )
    elif provider == "github":
        return (
            getattr(settings, "github_client_id", "") or "",
            getattr(settings, "github_client_secret", "") or "",
        )
    return "", ""


def generate_oauth_state() -> str:
    """Generate a secure random state parameter."""
    return secrets.token_urlsafe(32)


def get_authorization_url(provider: str, redirect_uri: str, state: str) -> str | None:
    """Build the OAuth authorization URL."""
    config = get_provider_config(provider)
    client_id, _ = get_client_credentials(provider)

    if not config or not client_id:
        return None

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": " ".join(config["scopes"]),
    }

    if provider == "google":
        params["response_type"] = "code"
        params["access_type"] = "offline"
        params["prompt"] = "consent"
    elif provider == "github":
        params["scope"] = "read:user user:email"

    return f"{config['auth_url']}?{urlencode(params)}"


async def exchange_code_for_token(
    provider: str,
    code: str,
    redirect_uri: str,
) -> dict | None:
    """Exchange authorization code for access token."""
    config = get_provider_config(provider)
    client_id, client_secret = get_client_credentials(provider)

    if not config or not client_id:
        return None

    async with httpx.AsyncClient() as client:
        try:
            if provider == "google":
                token_data = {
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            elif provider == "github":
                token_data = {
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
            else:
                return None

            resp = await client.post(config["token_url"], data=token_data, timeout=10)
            resp.raise_for_status()

            if provider == "github":
                # GitHub returns form-encoded data
                from urllib.parse import parse_qs
                data = parse_qs(resp.text)
                return {
                    "access_token": data.get("access_token", [None])[0],
                    "token_type": data.get("token_type", [None])[0],
                }
            else:
                return resp.json()

        except Exception as e:
            logger.error(f"Token exchange failed for {provider}: {e}")
            return None


async def get_user_info(provider: str, access_token: str) -> dict | None:
    """Get user info from the OAuth provider."""
    config = get_provider_config(provider)
    if not config:
        return None

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            if provider == "github":
                headers["Accept"] = "application/json"

            resp = await client.get(config["userinfo_url"], headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Normalize user info across providers
            if provider == "google":
                return {
                    "provider": "google",
                    "provider_user_id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "avatar_url": data.get("picture"),
                }
            elif provider == "github":
                return {
                    "provider": "github",
                    "provider_user_id": str(data.get("id")),
                    "email": data.get("email"),
                    "name": data.get("name") or data.get("login"),
                    "avatar_url": data.get("avatar_url"),
                }

        except Exception as e:
            logger.error(f"Failed to get user info from {provider}: {e}")
            return None

    return None


def find_or_create_oauth_user(user_info: dict) -> dict | None:
    """Find or create a user from OAuth info. Returns user dict."""
    from services.postgres_store import _connect as pg_connect
    from services.auth_store import _hash_token

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            # Check if OAuth identity already exists
            cur.execute(
                """SELECT user_id::text FROM auth_identities
                   WHERE provider = %s AND provider_user_id = %s""",
                (user_info["provider"], user_info["provider_user_id"]),
            )
            row = cur.fetchone()

            if row:
                # Existing OAuth user — get their user record
                user_id = row[0]
                cur.execute(
                    "SELECT id::text, email, plan FROM users WHERE id = %s",
                    (user_id,),
                )
                user_row = cur.fetchone()
                conn.close()
                if user_row:
                    return {"id": user_row[0], "email": user_row[1], "plan": user_row[2]}
                return None

            # New user — create account
            if not user_info.get("email"):
                logger.error("OAuth provider did not return email")
                conn.close()
                return None

            # Check if email already exists
            cur.execute("SELECT id::text, plan FROM users WHERE email = %s", (user_info["email"],))
            existing = cur.fetchone()

            if existing:
                user_id = existing[0]
                plan = existing[1]
            else:
                # Create new user
                import uuid
                user_id = str(uuid.uuid4())
                cur.execute(
                    """INSERT INTO users (id, email, plan, created_at, updated_at)
                       VALUES (%s, %s, 'free', NOW(), NOW())
                       RETURNING id::text""",
                    (user_id, user_info["email"]),
                )
                plan = "free"

            # Link OAuth identity
            cur.execute(
                """INSERT INTO auth_identities (user_id, provider, provider_user_id, display_name, avatar_url, created_at)
                   VALUES (%s, %s, %s, %s, %s, NOW())
                   ON CONFLICT (provider, provider_user_id) DO NOTHING""",
                (user_id, user_info["provider"], user_info["provider_user_id"],
                 user_info.get("name"), user_info.get("avatar_url")),
            )
            conn.commit()
            conn.close()

            return {"id": user_id, "email": user_info["email"], "plan": plan}

    except Exception as e:
        logger.error(f"Failed to find or create OAuth user: {e}")
        conn.close()
        return None
