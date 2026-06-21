# app/routes/payments.py
"""
Payment routes — Polar checkout, webhooks, and subscription management.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.auth_middleware import AuthContext, require_auth
from services.payment_service import (
    create_checkout_session,
    verify_webhook_signature,
    handle_webhook_event,
    get_subscription_status,
    get_payment_history,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CheckoutRequest(BaseModel):
    plan: str = "pro"
    price_id: str = ""


class CheckoutResponse(BaseModel):
    checkout_url: str
    checkout_id: str
    plan: str


@router.post("/checkout")
async def create_checkout(body: CheckoutRequest, auth: AuthContext = Depends(require_auth)):
    """Create a Polar checkout session for subscription."""
    settings = get_settings()

    success_url = f"{settings.frontend_url}/dashboard?checkout=success"
    cancel_url = f"{settings.frontend_url}/dashboard?checkout=cancelled"

    session = await create_checkout_session(
        product_id=body.price_id,
        user_email=auth.user_id,
        user_id=auth.user_id,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    if not session:
        raise HTTPException(status_code=502, detail="Failed to create Polar checkout session")

    return {
        "checkout_url": session.get("checkout_url"),
        "checkout_id": session.get("id"),
        "plan": body.plan,
    }


@router.get("/status")
async def payment_status(auth: AuthContext = Depends(require_auth)):
    """Get current user's subscription and payment status."""
    subscription = await get_subscription_status(auth.user_id)

    return {
        "user_id": auth.user_id,
        "subscription": subscription,
        "plan": subscription.get("plan", "free"),
    }


@router.get("/history")
async def payment_history(auth: AuthContext = Depends(require_auth)):
    """Get current user's payment history."""
    history = await get_payment_history(auth.user_id)
    return {"payments": history, "count": len(history)}


@router.post("/webhook")
async def polar_webhook(request: Request):
    """Handle Polar webhook events (subscription created/updated/canceled)."""
    body = await request.body()
    signature = request.headers.get("polar-signature", "")

    from app.config import get_settings
    settings = get_settings()
    webhook_secret = getattr(settings, "polar_webhook_secret", "") or ""

    if webhook_secret and not verify_webhook_signature(body, signature, webhook_secret):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body)
        event_type = payload.get("type", "")
        data = payload.get("data", {})
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    result = handle_webhook_event(event_type, data)
    return {"received": True, "processed": result and result.get("processed", False)}


@router.post("/demo-upgrade")
async def demo_upgrade(auth: AuthContext = Depends(require_auth)):
    """Demo mode: instantly upgrade user to pro plan (no real payment)."""
    from services.postgres_store import _connect as pg_connect

    settings = get_settings()
    conn = pg_connect(settings)

    try:
        with conn.cursor() as cur:
            # Get pro plan ID
            cur.execute("SELECT id FROM plans WHERE plan_key = 'pro'")
            plan_row = cur.fetchone()
            if not plan_row:
                raise HTTPException(status_code=500, detail="Pro plan not found")
            pro_plan_id = plan_row["id"] if isinstance(plan_row, dict) else plan_row[0]

            # Check if subscription already exists
            cur.execute("SELECT id FROM subscriptions WHERE user_id = %s", (auth.user_id,))
            existing = cur.fetchone()

            if existing:
                # Update existing subscription
                cur.execute(
                    """UPDATE subscriptions SET plan_id = %s, status = 'active',
                       current_period_start = NOW(), current_period_end = NOW() + INTERVAL '30 days',
                       updated_at = NOW() WHERE user_id = %s""",
                    (pro_plan_id, auth.user_id),
                )
            else:
                # Create new subscription
                cur.execute(
                    """INSERT INTO subscriptions (user_id, plan_id, status, current_period_start, current_period_end, created_at, updated_at)
                       VALUES (%s, %s, 'active', NOW(), NOW() + INTERVAL '30 days', NOW(), NOW())""",
                    (auth.user_id, pro_plan_id),
                )
            # Update users.plan
            cur.execute(
                "UPDATE users SET plan = 'pro' WHERE id = %s",
                (auth.user_id,),
            )
            conn.commit()
        conn.close()
        return {"upgraded": True, "plan": "pro", "demo": True}
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        import traceback
        logger.error(f"Demo upgrade failed: {e}\n{traceback.format_exc()}")
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
