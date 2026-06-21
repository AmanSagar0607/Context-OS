"""
Tests for enterprise features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime, timedelta

from enterprise.service import (
    EnterpriseConfig,
    SSOConfig,
    AuditLogService,
    SSOService,
    AuditAction,
    AuditSeverity,
)


class TestEnterpriseConfig:
    """Test EnterpriseConfig."""

    def test_default_config(self):
        config = EnterpriseConfig()
        assert config.audit_log_enabled is True
        assert config.audit_log_retention_days == 365

    def test_custom_config(self):
        config = EnterpriseConfig(audit_log_enabled=False)
        assert config.audit_log_enabled is False


class TestSSOConfig:
    """Test SSOConfig."""

    def test_default_config(self):
        config = SSOConfig()
        assert config.enabled is False
        assert config.provider == "oidc"
        assert "openid" in config.scopes

    def test_custom_config(self):
        config = SSOConfig(enabled=True, provider="saml")
        assert config.enabled is True
        assert config.provider == "saml"


class TestAuditLogService:
    """Test AuditLogService."""

    def test_log_entry(self):
        config = EnterpriseConfig()
        service = AuditLogService(config)

        entry = service.log(
            action=AuditAction.LOGIN,
            user_id="user123",
            ip_address="127.0.0.1",
        )

        assert entry is not None
        assert entry.action == AuditAction.LOGIN
        assert entry.user_id == "user123"
        assert entry.success is True

    def test_disabled_logging(self):
        config = EnterpriseConfig(audit_log_enabled=False)
        service = AuditLogService(config)

        entry = service.log(action=AuditAction.LOGIN)
        assert entry is None

    def test_severity_determination(self):
        config = EnterpriseConfig()
        service = AuditLogService(config)

        # Critical
        severity = service._determine_severity(AuditAction.USER_DELETED, True)
        assert severity == AuditSeverity.CRITICAL

        # High
        severity = service._determine_severity(AuditAction.LOGIN_FAILED, False)
        assert severity == AuditSeverity.HIGH

        # Medium
        severity = service._determine_severity(AuditAction.LOGIN, True)
        assert severity == AuditSeverity.MEDIUM

    def test_get_entries(self):
        config = EnterpriseConfig()
        service = AuditLogService(config)

        service.log(action=AuditAction.LOGIN, user_id="user1")
        service.log(action=AuditAction.LOGOUT, user_id="user2")

        entries = service.get_entries(user_id="user1")
        assert len(entries) == 1
        assert entries[0].user_id == "user1"

    def test_user_activity(self):
        config = EnterpriseConfig()
        service = AuditLogService(config)

        service.log(action=AuditAction.LOGIN, user_id="user1")
        service.log(action=AuditAction.LOGIN, user_id="user1")

        activity = service.get_user_activity("user1")
        assert activity["total_actions"] == 2
        assert "login" in activity["actions"]


class TestSSOService:
    """Test SSOService."""

    def test_disabled_sso(self):
        config = SSOConfig(enabled=False)
        service = SSOService(config)

        url = service.get_auth_url("state123")
        assert url is None

    def test_oidc_auth_url(self):
        config = SSOConfig(
            enabled=True,
            provider="oidc",
            client_id="client123",
            redirect_url="https://example.com/callback",
            discovery_url="https://auth.example.com",
        )
        service = SSOService(config)

        url = service.get_auth_url("state123")
        assert url is not None
        assert "client_id=client123" in url
        assert "state=state123" in url

    def test_domain_allowed(self):
        config = SSOConfig(allowed_domains=["example.com", "company.org"])
        service = SSOService(config)

        assert service.check_domain_allowed("user@example.com") is True
        assert service.check_domain_allowed("user@other.com") is False

    def test_domain_allowed_empty(self):
        config = SSOConfig(allowed_domains=[])
        service = SSOService(config)

        assert service.check_domain_allowed("user@any.com") is True


class TestAuditAction:
    """Test AuditAction enum."""

    def test_actions(self):
        assert AuditAction.LOGIN.value == "login"
        assert AuditAction.MEMORY_CREATED.value == "memory_created"
        assert AuditAction.CRAWL_COMPLETED.value == "crawl_completed"


class TestAuditSeverity:
    """Test AuditSeverity enum."""

    def test_severities(self):
        assert AuditSeverity.LOW.value == "low"
        assert AuditSeverity.MEDIUM.value == "medium"
        assert AuditSeverity.HIGH.value == "high"
        assert AuditSeverity.CRITICAL.value == "critical"
