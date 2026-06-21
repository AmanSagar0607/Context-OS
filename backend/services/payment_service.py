# services/payment_service.py
"""
Payment Service — Polar integration for subscriptions and billing.

Handles checkout, webhooks, subscription management.
Polar: developer-first billing with usage-based support.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

POLAR_API_BASE = "https://api.polar.sh/v1"


async def _polar_request(
    method: str,
    path: str,
    body: dict | None = None,
) -> dict | None:
    """Make an authenticated request to Polar API."""
    settings = get_settings()
    api_key = getattr(settings, "polar_client_secret", "") or ""
    if not api_key:
        logger.warning("Polar client secret not configured")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient() as client:
        try:
            url = f"{POLAR_API_BASE}{path}"
            resp = await client.request(
                method, url, headers=headers,
                json=body, timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Polar API error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Polar request failed: {e}")
            return None


async def create_checkout_session(
    product_id: str,
    user_email: str,
    user_id: str,
    success_url: str,
    cancel_url: str,
) -> dict | None:
    """Create a Polar checkout session."""
    return await _polar_request("POST", "/checkouts", {
        "product_price_id": product_id,
        "customer_email": user_email,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {
            "user_id": user_id,
        },
    })


async def create_subscription(
    customer_id: str,
    price_id: str,
) -> dict | None:
    """Create a Polar subscription."""
    return await _polar_request("POST", "/subscriptions", {
        "customer_id": customer_id,
        "price_id": price_id,
    })


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Verify Polar webhook HMAC-SHA256 signature."""
    if not secret:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_webhook_event(event_type: str, data: dict) -> dict | None:
    """Process a verified Polar webhook event."""
    settings = get_settings()

    if event_type == "subscription.created":
        subscription_id = data.get("id")
        user_id = data.get("metadata", {}).get("user_id")
        logger.info(f"Subscription created: {subscription_id} for user {user_id}")

        if user_id:
            from services.postgres_store import _connect as pg_connect
            conn = pg_connect(settings)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO subscriptions (user_id, plan, status, created_at, updated_at)
                           VALUES (%s, 'pro', 'active', NOW(), NOW())
                           ON CONFLICT (user_id) DO UPDATE SET
                           status = 'active', plan = 'pro', updated_at = NOW()""",
                        (user_id,),
                    )
                    conn.commit()
                    logger.info(f"Activated subscription for user {user_id}")
            except Exception as e:
                logger.error(f"Webhook handler error: {e}")
            finally:
                conn.close()

        return {"processed": True, "event": event_type}

    elif event_type == "subscription.updated":
        subscription_id = data.get("id")
        status = data.get("status")
        logger.info(f"Subscription updated: {subscription_id} — status: {status}")
        return {"processed": True, "event": event_type}

    elif event_type == "subscription.canceled":
        subscription_id = data.get("id")
        logger.info(f"Subscription canceled: {subscription_id}")
        return {"processed": True, "event": event_type}

    elif event_type == "subscription.revoked":
        subscription_id = data.get("id")
        logger.info(f"Subscription revoked: {subscription_id}")
        return {"processed": True, "event": event_type}

    logger.warning(f"Unhandled webhook event: {event_type}")
    return {"processed": False, "event": event_type}


async def get_subscription_status(user_id: str) -> dict:
    """Get user's subscription status."""
    from services.postgres_store import _connect as pg_connect

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT p.plan_key, s.status, s.created_at
                   FROM subscriptions s
                   JOIN plans p ON p.id = s.plan_id
                   WHERE s.user_id = %s""",
                (user_id,),
            )
            row = cur.fetchone()
        conn.close()

        if row:
            return {
                "plan": row[0],
                "status": row[1],
                "subscribed_at": row[2].isoformat() if row[2] else None,
            }
        return {"plan": "free", "status": "inactive"}
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        conn.close()
        return {"plan": "free", "status": "inactive"}


async def get_payment_history(user_id: str, limit: int = 20) -> list[dict]:
    """Get user's payment history."""
    from services.postgres_store import _connect as pg_connect

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, amount, currency, status, created_at
                   FROM usage_records
                   WHERE user_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s""",
                (user_id, limit),
            )
            rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": str(row[0]),
                "amount": row[1],
                "currency": row[2],
                "status": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        conn.close()
        return []
