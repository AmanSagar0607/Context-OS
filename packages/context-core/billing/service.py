"""
Billing Service — Polar integration for usage-based billing.

Manages subscriptions, usage tracking, and billing operations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import httpx

logger = logging.getLogger(__name__)

POLAR_API_URL = "https://api.polar.sh/v1"


class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"


@dataclass
class Plan:
    """Subscription plan."""
    id: str
    name: str
    plan_type: PlanType
    price_monthly: float
    price_yearly: float
    features: dict = field(default_factory=dict)
    limits: dict = field(default_factory=dict)


@dataclass
class Subscription:
    """User subscription."""
    id: str
    user_id: str
    plan_id: str
    status: BillingStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at: Optional[datetime] = None
    trial_end: Optional[datetime] = None


@dataclass
class UsageRecord:
    """Usage record for metered billing."""
    id: str
    user_id: str
    subscription_id: str
    metric: str  # e.g., "memory_add", "search_query", "crawl_page"
    quantity: int
    timestamp: datetime
    metadata: dict = field(default_factory=dict)


@dataclass
class BillingConfig:
    """Billing configuration."""
    polar_api_key: str = ""
    polar_product_id: str = ""
    enabled: bool = True


# Plan definitions
PLANS = {
    PlanType.FREE: Plan(
        id="free",
        name="Free",
        plan_type=PlanType.FREE,
        price_monthly=0,
        price_yearly=0,
        features={
            "memory_add": 100,
            "search_query": 50,
            "crawl_page": 10,
            "knowledge_extract": 5,
        },
        limits={
            "memory_add": 1000,
            "search_query": 500,
            "crawl_page": 100,
            "knowledge_extract": 50,
        },
    ),
    PlanType.STARTER: Plan(
        id="starter",
        name="Starter",
        plan_type=PlanType.STARTER,
        price_monthly=19,
        price_yearly=190,
        features={
            "memory_add": 1000,
            "search_query": 500,
            "crawl_page": 100,
            "knowledge_extract": 50,
        },
        limits={
            "memory_add": 10000,
            "search_query": 5000,
            "crawl_page": 1000,
            "knowledge_extract": 500,
        },
    ),
    PlanType.PRO: Plan(
        id="pro",
        name="Pro",
        plan_type=PlanType.PRO,
        price_monthly=49,
        price_yearly=490,
        features={
            "memory_add": 5000,
            "search_query": 2500,
            "crawl_page": 500,
            "knowledge_extract": 250,
        },
        limits={
            "memory_add": 50000,
            "search_query": 25000,
            "crawl_page": 5000,
            "knowledge_extract": 2500,
        },
    ),
    PlanType.ENTERPRISE: Plan(
        id="enterprise",
        name="Enterprise",
        plan_type=PlanType.ENTERPRISE,
        price_monthly=199,
        price_yearly=1990,
        features={
            "memory_add": -1,  # Unlimited
            "search_query": -1,
            "crawl_page": -1,
            "knowledge_extract": -1,
        },
        limits={
            "memory_add": -1,
            "search_query": -1,
            "crawl_page": -1,
            "knowledge_extract": -1,
        },
    ),
}


class BillingService:
    """Polar billing service."""

    def __init__(self, config: BillingConfig):
        self.config = config

    async def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's subscription."""
        if not self.config.enabled or not self.config.polar_api_key:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.config.polar_api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{POLAR_API_URL}/subscriptions",
                    headers=headers,
                    params={"external_customer_id": user_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("items"):
                        sub_data = data["items"][0]
                        return Subscription(
                            id=sub_data["id"],
                            user_id=user_id,
                            plan_id=sub_data.get("plan_id", "free"),
                            status=BillingStatus(sub_data.get("status", "active")),
                            current_period_start=datetime.fromisoformat(
                                sub_data.get("current_period_start", datetime.utcnow().isoformat())
                            ),
                            current_period_end=datetime.fromisoformat(
                                sub_data.get("current_period_end", datetime.utcnow().isoformat())
                            ),
                        )

        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")

        return None

    async def create_checkout(
        self,
        user_id: str,
        plan_type: PlanType,
        success_url: str,
        cancel_url: str,
    ) -> Optional[str]:
        """
        Create a Polar checkout session.

        Returns checkout URL.
        """
        if not self.config.enabled or not self.config.polar_api_key:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.config.polar_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "product_price_id": self.config.polar_product_id,
                "external_customer_id": user_id,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "plan_type": plan_type.value,
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{POLAR_API_URL}/checkout/custom",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("checkout_url")

        except Exception as e:
            logger.error(f"Failed to create checkout: {e}")

        return None

    async def record_usage(
        self,
        user_id: str,
        subscription_id: str,
        metric: str,
        quantity: int,
    ) -> Optional[UsageRecord]:
        """Record usage for metered billing."""
        if not self.config.enabled or not self.config.polar_api_key:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.config.polar_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "subscription_id": subscription_id,
                "name": metric,
                "quantity": quantity,
                "timestamp": datetime.utcnow().isoformat(),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{POLAR_API_URL}/usage",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return UsageRecord(
                        id=data.get("id", str(uuid4())),
                        user_id=user_id,
                        subscription_id=subscription_id,
                        metric=metric,
                        quantity=quantity,
                        timestamp=datetime.utcnow(),
                    )

        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

        return None

    async def check_usage_limit(
        self,
        user_id: str,
        metric: str,
        current_usage: int,
    ) -> dict:
        """
        Check if user has exceeded usage limit.

        Returns:
            Dict with allowed, limit, remaining, upgrade_required
        """
        subscription = await self.get_subscription(user_id)

        if not subscription:
            # Free tier
            plan = PLANS[PlanType.FREE]
        else:
            # Find plan from subscription
            plan = PLANS.get(PlanType.FREE)  # Default to free
            for pt, p in PLANS.items():
                if p.id == subscription.plan_id:
                    plan = p
                    break

        limit = plan.limits.get(metric, 0)
        allowed = limit == -1 or current_usage < limit
        remaining = max(0, limit - current_usage) if limit > 0 else -1

        return {
            "allowed": allowed,
            "limit": limit,
            "remaining": remaining,
            "current_usage": current_usage,
            "plan": plan.plan_type.value,
            "upgrade_required": not allowed and plan.plan_type != PlanType.ENTERPRISE,
        }


def get_plan_limits(plan_type: PlanType) -> dict:
    """Get limits for a plan type."""
    return PLANS[plan_type].limits


def get_plan_features(plan_type: PlanType) -> dict:
    """Get features for a plan type."""
    return PLANS[plan_type].features
