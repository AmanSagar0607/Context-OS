"""
Webhook System — Async notifications for events.

Manages webhook registration, delivery, and retry logic.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Awaitable
from uuid import UUID, uuid4

import httpx

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    SEARCH_COMPLETED = "search.completed"
    CRAWL_COMPLETED = "crawl.completed"
    KNOWLEDGE_EXTRACTED = "knowledge.extracted"
    SUBSCRIPTION_CHANGED = "subscription.changed"
    USAGE_LIMIT_REACHED = "usage.limit_reached"


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


@dataclass
class Webhook:
    """Webhook registration."""
    id: str
    user_id: str
    url: str
    events: list[WebhookEvent]
    secret: str
    status: WebhookStatus = WebhookStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    failure_count: int = 0
    last_triggered_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class WebhookDelivery:
    """Webhook delivery record."""
    id: str
    webhook_id: str
    event: WebhookEvent
    payload: dict
    status: str = "pending"
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    max_retries: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 30
    max_payload_size: int = 1024 * 1024  # 1MB
    enabled: bool = True


# Event payloads
EVENT_PAYLOADS = {
    WebhookEvent.MEMORY_CREATED: {
        "type": "memory.created",
        "description": "New memory created",
    },
    WebhookEvent.MEMORY_UPDATED: {
        "type": "memory.updated",
        "description": "Memory updated",
    },
    WebhookEvent.MEMORY_DELETED: {
        "type": "memory.deleted",
        "description": "Memory deleted",
    },
    WebhookEvent.SEARCH_COMPLETED: {
        "type": "search.completed",
        "description": "Search query completed",
    },
    WebhookEvent.CRAWL_COMPLETED: {
        "type": "crawl.completed",
        "description": "Web crawl completed",
    },
    WebhookEvent.KNOWLEDGE_EXTRACTED: {
        "type": "knowledge.extracted",
        "description": "Knowledge extracted from content",
    },
    WebhookEvent.SUBSCRIPTION_CHANGED: {
        "type": "subscription.changed",
        "description": "Subscription plan changed",
    },
    WebhookEvent.USAGE_LIMIT_REACHED: {
        "type": "usage.limit_reached",
        "description": "Usage limit reached",
    },
}


class WebhookService:
    """Webhook management and delivery service."""

    def __init__(self, config: Optional[WebhookConfig] = None):
        self.config = config or WebhookConfig()
        self._webhooks: dict[str, Webhook] = {}
        self._deliveries: list[WebhookDelivery] = []

    def register(
        self,
        user_id: str,
        url: str,
        events: list[WebhookEvent],
        metadata: Optional[dict] = None,
    ) -> Webhook:
        """Register a new webhook."""
        webhook_id = str(uuid4())
        secret = hmac.new(
            uuid4().bytes,
            b"webhook",
            hashlib.sha256,
        ).hexdigest()

        webhook = Webhook(
            id=webhook_id,
            user_id=user_id,
            url=url,
            events=events,
            secret=secret,
            metadata=metadata or {},
        )

        self._webhooks[webhook_id] = webhook
        return webhook

    def unregister(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False

    def get_webhooks(
        self,
        user_id: Optional[str] = None,
        event: Optional[WebhookEvent] = None,
    ) -> list[Webhook]:
        """Get webhooks with optional filters."""
        webhooks = list(self._webhooks.values())

        if user_id:
            webhooks = [w for w in webhooks if w.user_id == user_id]

        if event:
            webhooks = [w for w in webhooks if event in w.events]

        return webhooks

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    async def trigger(
        self,
        event: WebhookEvent,
        data: dict,
    ) -> list[WebhookDelivery]:
        """
        Trigger webhooks for an event.

        Args:
            event: Event type
            data: Event data

        Returns:
            List of delivery records
        """
        if not self.config.enabled:
            return []

        webhooks = self.get_webhooks(event=event)
        deliveries = []

        for webhook in webhooks:
            if webhook.status != WebhookStatus.ACTIVE:
                continue

            delivery = await self._deliver(webhook, event, data)
            deliveries.append(delivery)

        return deliveries

    async def _deliver(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        data: dict,
    ) -> WebhookDelivery:
        """Deliver a webhook."""
        delivery = WebhookDelivery(
            id=str(uuid4()),
            webhook_id=webhook.id,
            event=event,
            payload={
                "event": event.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            },
        )

        payload_str = json.dumps(delivery.payload)

        # Check payload size
        if len(payload_str.encode()) > self.config.max_payload_size:
            delivery.status = "failed"
            delivery.error = "Payload too large"
            return delivery

        # Generate signature
        signature = self._generate_signature(payload_str, webhook.secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.value,
            "X-Webhook-ID": delivery.id,
            "User-Agent": "ContextOS-Webhook/1.0",
        }

        # Retry logic
        for attempt in range(self.config.max_retries):
            delivery.attempts += 1

            try:
                async with httpx.AsyncClient(
                    timeout=self.config.timeout_seconds
                ) as client:
                    response = await client.post(
                        webhook.url,
                        content=payload_str,
                        headers=headers,
                    )

                    delivery.response_code = response.status_code
                    delivery.response_body = response.text[:1000]

                    if 200 <= response.status_code < 300:
                        delivery.status = "delivered"
                        delivery.delivered_at = datetime.utcnow()
                        webhook.last_triggered_at = datetime.utcnow()
                        webhook.failure_count = 0
                        break
                    else:
                        delivery.status = "failed"
                        delivery.error = f"HTTP {response.status_code}"

            except Exception as e:
                delivery.status = "failed"
                delivery.error = str(e)

            # Wait before retry
            if attempt < self.config.max_retries - 1:
                import asyncio
                await asyncio.sleep(self.config.retry_delay_seconds * (attempt + 1))

        # Update webhook status on repeated failures
        if delivery.status == "failed":
            webhook.failure_count += 1
            if webhook.failure_count >= 5:
                webhook.status = WebhookStatus.FAILED

        self._deliveries.append(delivery)
        return delivery

    def get_deliveries(
        self,
        webhook_id: Optional[str] = None,
        event: Optional[WebhookEvent] = None,
        limit: int = 100,
    ) -> list[WebhookDelivery]:
        """Get delivery records."""
        deliveries = self._deliveries

        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]

        if event:
            deliveries = [d for d in deliveries if d.event == event]

        return deliveries[-limit:]

    def retry_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Retry a failed delivery."""
        for delivery in self._deliveries:
            if delivery.id == delivery_id and delivery.status == "failed":
                webhook = self._webhooks.get(delivery.webhook_id)
                if webhook:
                    # Queue for retry (in production, use a task queue)
                    delivery.status = "pending"
                    delivery.attempts = 0
                    return delivery
        return None
