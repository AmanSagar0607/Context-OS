"""
Tests for webhook system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from webhooks.service import (
    WebhookConfig,
    Webhook,
    WebhookDelivery,
    WebhookEvent,
    WebhookService,
    WebhookStatus,
)


class TestWebhookConfig:
    """Test WebhookConfig."""

    def test_default_config(self):
        config = WebhookConfig()
        assert config.max_retries == 3
        assert config.retry_delay_seconds == 60
        assert config.timeout_seconds == 30
        assert config.enabled is True

    def test_custom_config(self):
        config = WebhookConfig(max_retries=5, enabled=False)
        assert config.max_retries == 5
        assert config.enabled is False


class TestWebhookService:
    """Test WebhookService."""

    def test_register_webhook(self):
        service = WebhookService()

        webhook = service.register(
            user_id="user123",
            url="https://example.com/webhook",
            events=[WebhookEvent.MEMORY_CREATED],
        )

        assert webhook.user_id == "user123"
        assert webhook.url == "https://example.com/webhook"
        assert WebhookEvent.MEMORY_CREATED in webhook.events
        assert webhook.status == WebhookStatus.ACTIVE

    def test_unregister_webhook(self):
        service = WebhookService()

        webhook = service.register(
            user_id="user123",
            url="https://example.com/webhook",
            events=[WebhookEvent.MEMORY_CREATED],
        )

        result = service.unregister(webhook.id)
        assert result is True
        assert service.get_webhooks(user_id="user123") == []

    def test_unregister_nonexistent(self):
        service = WebhookService()
        result = service.unregister("nonexistent")
        assert result is False

    def test_get_webhooks_by_user(self):
        service = WebhookService()

        service.register(
            user_id="user1",
            url="https://example.com/1",
            events=[WebhookEvent.MEMORY_CREATED],
        )
        service.register(
            user_id="user2",
            url="https://example.com/2",
            events=[WebhookEvent.MEMORY_CREATED],
        )

        webhooks = service.get_webhooks(user_id="user1")
        assert len(webhooks) == 1
        assert webhooks[0].user_id == "user1"

    def test_get_webhooks_by_event(self):
        service = WebhookService()

        service.register(
            user_id="user1",
            url="https://example.com/1",
            events=[WebhookEvent.MEMORY_CREATED],
        )
        service.register(
            user_id="user1",
            url="https://example.com/2",
            events=[WebhookEvent.SEARCH_COMPLETED],
        )

        webhooks = service.get_webhooks(event=WebhookEvent.MEMORY_CREATED)
        assert len(webhooks) == 1

    def test_generate_signature(self):
        service = WebhookService()
        sig = service._generate_signature("test payload", "secret")
        assert len(sig) == 64  # SHA256 hex digest

    @pytest.mark.asyncio
    async def test_trigger_disabled(self):
        config = WebhookConfig(enabled=False)
        service = WebhookService(config)

        deliveries = await service.trigger(
            WebhookEvent.MEMORY_CREATED,
            {"id": "123"},
        )

        assert deliveries == []

    @pytest.mark.asyncio
    async def test_trigger_no_webhooks(self):
        service = WebhookService()

        deliveries = await service.trigger(
            WebhookEvent.MEMORY_CREATED,
            {"id": "123"},
        )

        assert deliveries == []

    def test_get_deliveries(self):
        service = WebhookService()

        # Add mock delivery
        delivery = WebhookDelivery(
            id="del1",
            webhook_id="wh1",
            event=WebhookEvent.MEMORY_CREATED,
            payload={},
            status="delivered",
        )
        service._deliveries.append(delivery)

        deliveries = service.get_deliveries(webhook_id="wh1")
        assert len(deliveries) == 1

    def test_retry_delivery(self):
        service = WebhookService()

        delivery = WebhookDelivery(
            id="del1",
            webhook_id="wh1",
            event=WebhookEvent.MEMORY_CREATED,
            payload={},
            status="failed",
        )
        service._deliveries.append(delivery)
        service._webhooks["wh1"] = Webhook(
            id="wh1",
            user_id="user1",
            url="https://example.com",
            events=[WebhookEvent.MEMORY_CREATED],
            secret="secret",
        )

        result = service.retry_delivery("del1")
        assert result is not None
        assert result.status == "pending"


class TestWebhookEvent:
    """Test WebhookEvent enum."""

    def test_events(self):
        assert WebhookEvent.MEMORY_CREATED.value == "memory.created"
        assert WebhookEvent.SEARCH_COMPLETED.value == "search.completed"
        assert WebhookEvent.CRAWL_COMPLETED.value == "crawl.completed"
