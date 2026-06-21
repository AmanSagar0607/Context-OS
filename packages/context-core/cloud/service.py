"""
Context Cloud — Multi-tenant managed service.

Provides tenant management, resource isolation, and cloud-native features.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TenantPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class TenantLimits:
    """Resource limits for a tenant."""
    memory_limit: int = 1000
    search_limit: int = 100
    crawl_limit: int = 50
    knowledge_limit: int = 25
    api_calls_per_day: int = 1000
    storage_mb: int = 100
    team_members: int = 1


@dataclass
class Tenant:
    """A cloud tenant."""
    id: str
    name: str
    slug: str
    plan: TenantPlan
    status: TenantStatus
    owner_user_id: str
    limits: TenantLimits
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class TenantUsage:
    """Tenant usage tracking."""
    tenant_id: str
    memory_count: int = 0
    search_count: int = 0
    crawl_count: int = 0
    knowledge_count: int = 0
    api_calls_today: int = 0
    storage_used_mb: float = 0.0
    period_start: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CloudConfig:
    """Cloud configuration."""
    enabled: bool = True
    default_plan: TenantPlan = TenantPlan.FREE
    require_payment: bool = False
    auto_suspend_days: int = 30
    max_tenants: int = 10000


# Plan limits
PLAN_LIMITS = {
    TenantPlan.FREE: TenantLimits(
        memory_limit=1000,
        search_limit=100,
        crawl_limit=50,
        knowledge_limit=25,
        api_calls_per_day=1000,
        storage_mb=100,
        team_members=1,
    ),
    TenantPlan.STARTER: TenantLimits(
        memory_limit=10000,
        search_limit=1000,
        crawl_limit=500,
        knowledge_limit=250,
        api_calls_per_day=10000,
        storage_mb=1000,
        team_members=5,
    ),
    TenantPlan.PRO: TenantLimits(
        memory_limit=100000,
        search_limit=10000,
        crawl_limit=5000,
        knowledge_limit=2500,
        api_calls_per_day=100000,
        storage_mb=10000,
        team_members=25,
    ),
    TenantPlan.ENTERPRISE: TenantLimits(
        memory_limit=-1,  # Unlimited
        search_limit=-1,
        crawl_limit=-1,
        knowledge_limit=-1,
        api_calls_per_day=-1,
        storage_mb=-1,
        team_members=-1,
    ),
}


class CloudService:
    """Cloud multi-tenant service."""

    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or CloudConfig()
        self._tenants: dict[str, Tenant] = {}
        self._usage: dict[str, TenantUsage] = {}

    async def create_tenant(
        self,
        name: str,
        slug: str,
        owner_user_id: str,
        plan: Optional[TenantPlan] = None,
    ) -> Tenant:
        """
        Create a new tenant.

        Args:
            name: Tenant name
            slug: URL-friendly slug
            owner_user_id: Owner user ID
            plan: Optional plan override

        Returns:
            Created Tenant
        """
        if len(self._tenants) >= self.config.max_tenants:
            raise ValueError("Max tenants reached")

        if slug in [t.slug for t in self._tenants.values()]:
            raise ValueError(f"Slug '{slug}' already taken")

        tenant_id = str(uuid4())
        tenant_plan = plan or self.config.default_plan
        limits = PLAN_LIMITS[tenant_plan]

        tenant = Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            plan=tenant_plan,
            status=TenantStatus.ACTIVE,
            owner_user_id=owner_user_id,
            limits=limits,
        )

        self._tenants[tenant_id] = tenant
        self._usage[tenant_id] = TenantUsage(tenant_id=tenant_id)

        logger.info(f"Created tenant: {name} ({slug})")
        return tenant

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        for tenant in self._tenants.values():
            if tenant.slug == slug:
                return tenant
        return None

    async def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        plan: Optional[TenantPlan] = None,
        status: Optional[TenantStatus] = None,
    ) -> Optional[Tenant]:
        """Update tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None

        if name:
            tenant.name = name
        if plan:
            tenant.plan = plan
            tenant.limits = PLAN_LIMITS[plan]
        if status:
            tenant.status = status

        tenant.updated_at = datetime.utcnow()
        return tenant

    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        if tenant_id in self._tenants:
            del self._tenants[tenant_id]
            self._usage.pop(tenant_id, None)
            return True
        return False

    async def check_usage_limit(
        self,
        tenant_id: str,
        resource: str,
    ) -> dict:
        """
        Check if tenant has exceeded usage limit.

        Returns:
            Dict with allowed, limit, remaining
        """
        tenant = self._tenants.get(tenant_id)
        usage = self._usage.get(tenant_id)

        if not tenant or not usage:
            return {"allowed": False, "limit": 0, "remaining": 0}

        limit = getattr(tenant.limits, f"{resource}_limit", 0)
        current = getattr(usage, f"{resource}_count", 0)

        allowed = limit == -1 or current < limit
        remaining = max(0, limit - current) if limit > 0 else -1

        return {
            "allowed": allowed,
            "limit": limit,
            "remaining": remaining,
            "current_usage": current,
            "plan": tenant.plan.value,
        }

    async def record_usage(
        self,
        tenant_id: str,
        resource: str,
        amount: int = 1,
    ) -> bool:
        """Record usage for a tenant."""
        usage = self._usage.get(tenant_id)
        if not usage:
            return False

        current = getattr(usage, f"{resource}_count", 0)
        setattr(usage, f"{resource}_count", current + amount)
        return True

    async def get_usage(self, tenant_id: str) -> Optional[TenantUsage]:
        """Get tenant usage."""
        return self._usage.get(tenant_id)

    async def list_tenants(
        self,
        plan: Optional[TenantPlan] = None,
        status: Optional[TenantStatus] = None,
        limit: int = 100,
    ) -> list[Tenant]:
        """List tenants with filters."""
        tenants = list(self._tenants.values())

        if plan:
            tenants = [t for t in tenants if t.plan == plan]
        if status:
            tenants = [t for t in tenants if t.status == status]

        return tenants[:limit]

    async def get_tenant_stats(self, tenant_id: str) -> dict:
        """Get tenant statistics."""
        tenant = self._tenants.get(tenant_id)
        usage = self._usage.get(tenant_id)

        if not tenant:
            return {}

        return {
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "plan": tenant.plan.value,
                "status": tenant.status.value,
            },
            "usage": {
                "memory": usage.memory_count if usage else 0,
                "search": usage.search_count if usage else 0,
                "crawl": usage.crawl_count if usage else 0,
                "knowledge": usage.knowledge_count if usage else 0,
            } if usage else {},
            "limits": {
                "memory": tenant.limits.memory_limit,
                "search": tenant.limits.search_limit,
                "crawl": tenant.limits.crawl_limit,
                "knowledge": tenant.limits.knowledge_limit,
            },
        }


# Tenant middleware for API requests
class TenantMiddleware:
    """Extract tenant from request and add to context."""

    def __init__(self, cloud_service: CloudService):
        self.cloud_service = cloud_service

    async def get_tenant_from_header(
        self,
        tenant_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Optional[Tenant]:
        """Get tenant from header or API key."""
        if tenant_id:
            return await self.cloud_service.get_tenant(tenant_id)

        # In production, lookup tenant from API key
        return None

    async def enforce_limits(
        self,
        tenant: Tenant,
        resource: str,
    ) -> bool:
        """Enforce usage limits."""
        result = await self.cloud_service.check_usage_limit(tenant.id, resource)
        return result["allowed"]
