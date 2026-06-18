# services/payment_service.py
"""
Payment Service — BaseUPI integration for subscriptions and billing.

Handles order creation, webhooks, subscription management.
BaseUPI: zero-commission UPI payments with instant settlement.
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

BASEUPI_API_BASE = "https://baseupi.app/api/v1"


async def _baseupi_request(
    method: str,
    path: str,
    body: dict | None = None,
) -> dict | None:
    """Make an authenticated request to BaseUPI API."""
    settings = get_settings()
    api_key = getattr(settings, "baseupi_secret_key", "") or ""
    if not api_key:
        logger.warning("BaseUPI secret key not configured")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASEUPI_API_BASE}{path}"
            resp = await client.request(
                method, url, headers=headers,
                json=body, timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"BaseUPI API error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"BaseUPI request failed: {e}")
            return None


async def create_checkout_order(
    amount_paise: int,
    merchant_order_id: str,
) -> dict | None:
    """Create a BaseUPI checkout order. Returns { public_order_id, checkout_url, upi_deeplink }."""
    return await _baseupi_request("POST", "/orders", {
        "amountPaise": amount_paise,
        "merchantOrderId": merchant_order_id,
    })


async def create_subscription_order(
    amount_paise: int,
    merchant_order_id: str,
    plan_name: str,
    interval_days: int = 30,
) -> dict | None:
    """Create a subscription order (recurring checkout)."""
    return await _baseupi_request("POST", "/orders", {
        "amountPaise": amount_paise,
        "merchantOrderId": merchant_order_id,
        "metadata": {
            "type": "subscription",
            "plan": plan_name,
            "interval_days": interval_days,
        },
    })


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Verify BaseUPI webhook HMAC-SHA256 signature."""
    if not secret:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_webhook_event(event_type: str, data: dict) -> dict | None:
    """Process a verified BaseUPI webhook event."""
    settings = get_settings()

    if event_type == "BASEUPI_PAYMENT_SUCCESS":
        merchant_order_id = data.get("merchant_order_id")
        amount_paise = data.get("amount_paise")
        logger.info(f"Payment success: {merchant_order_id} — ₹{amount_paise / 100 if amount_paise else 0}")

        # Update usage_records if this is a subscription payment
        from services.postgres_store import _connect as pg_connect
        conn = pg_connect(settings)
        try:
            with conn.cursor() as cur:
                # Find user by merchant_order_id pattern
                cur.execute(
                    """SELECT user_id::text FROM usage_records
                       WHERE metadata->>'baseupi_order_id' = %s""",
                    (merchant_order_id,),
                )
                row = cur.fetchone()
                if row:
                    # Mark subscription as active
                    cur.execute(
                        """INSERT INTO subscriptions (user_id, plan, status, created_at, updated_at)
                           VALUES (%s, 'pro', 'active', NOW(), NOW())
                           ON CONFLICT (user_id) DO UPDATE SET
                           status = 'active', plan = 'pro', updated_at = NOW()""",
                        (row[0],),
                    )
                    conn.commit()
                    logger.info(f"Activated subscription for user {row[0]}")
        except Exception as e:
            logger.error(f"Webhook handler error: {e}")
        finally:
            conn.close()

        return {"processed": True, "event": event_type}

    elif event_type == "BASEUPI_PAYMENT_FAILED":
        logger.warning(f"Payment failed: {data.get('merchant_order_id')}")
        return {"processed": True, "event": event_type}

    elif event_type == "BASEUPI_REFUND_SUCCESS":
        logger.info(f"Refund processed: {data.get('merchant_order_id')}")
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
