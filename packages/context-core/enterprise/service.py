"""
Enterprise Features — SSO and Audit Logs.

Provides SAML/OIDC SSO integration and comprehensive audit logging.
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


class AuditAction(str, Enum):
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"

    # Memory operations
    MEMORY_CREATED = "memory_created"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_DELETED = "memory_deleted"
    MEMORY_SEARCHED = "memory_searched"

    # Knowledge operations
    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_DELETED = "entity_deleted"
    RELATIONSHIP_CREATED = "relationship_created"

    # Crawl operations
    CRAWL_STARTED = "crawl_started"
    CRAWL_COMPLETED = "crawl_completed"
    CRAWL_FAILED = "crawl_failed"

    # Admin operations
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    PLAN_CHANGED = "plan_changed"

    # System operations
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    MIGRATION_RUN = "migration_run"


class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """An audit log entry."""
    id: str
    timestamp: datetime
    user_id: Optional[str]
    action: AuditAction
    severity: AuditSeverity
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: dict = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class SSOConfig:
    """SSO configuration."""
    enabled: bool = False
    provider: str = "oidc"  # oidc, saml, azure_ad, okta, google
    client_id: str = ""
    client_secret: str = ""
    discovery_url: str = ""
    redirect_url: str = ""
    scopes: list[str] = field(default_factory=lambda: ["openid", "email", "profile"])
    attribute_mapping: dict = field(default_factory=lambda: {
        "email": "email",
        "name": "name",
        "groups": "groups",
    })
    allowed_domains: list[str] = field(default_factory=list)
    auto_create_users: bool = True


@dataclass
class EnterpriseConfig:
    """Enterprise features configuration."""
    sso: SSOConfig = field(default_factory=SSOConfig)
    audit_log_enabled: bool = True
    audit_log_retention_days: int = 365
    require_audit_for: list[AuditAction] = field(default_factory=lambda: [
        AuditAction.LOGIN,
        AuditAction.LOGOUT,
        AuditAction.LOGIN_FAILED,
        AuditAction.USER_CREATED,
        AuditAction.USER_DELETED,
        AuditAction.API_KEY_CREATED,
        AuditAction.API_KEY_REVOKED,
        AuditAction.PLAN_CHANGED,
    ])


class AuditLogService:
    """Audit logging service."""

    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self._entries: list[AuditEntry] = []

    def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
    ) -> Optional[AuditEntry]:
        """
        Log an audit entry.

        Args:
            action: Action performed
            user_id: User who performed the action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action succeeded
            error_message: Error message if failed
            severity: Override severity level

        Returns:
            Created AuditEntry or None if logging disabled
        """
        if not self.config.audit_log_enabled:
            return None

        # Determine severity
        if severity is None:
            severity = self._determine_severity(action, success)

        entry = AuditEntry(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

        self._entries.append(entry)

        # Log to logger
        log_msg = f"AUDIT: {action.value} by {user_id or 'system'}"
        if resource_type:
            log_msg += f" on {resource_type}:{resource_id or 'unknown'}"

        if severity in (AuditSeverity.HIGH, AuditSeverity.CRITICAL):
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return entry

    def _determine_severity(self, action: AuditAction, success: bool) -> AuditSeverity:
        """Determine severity based on action type."""
        # Critical actions
        if action in (
            AuditAction.USER_DELETED,
            AuditAction.SYSTEM_CONFIG_CHANGED,
            AuditAction.MIGRATION_RUN,
        ):
            return AuditSeverity.CRITICAL

        # High severity actions
        if action in (
            AuditAction.LOGIN_FAILED,
            AuditAction.API_KEY_REVOKED,
            AuditAction.PLAN_CHANGED,
        ):
            return AuditSeverity.HIGH

        # Medium severity actions
        if action in (
            AuditAction.LOGIN,
            AuditAction.LOGOUT,
            AuditAction.USER_CREATED,
            AuditAction.USER_UPDATED,
            AuditAction.PASSWORD_CHANGED,
        ):
            return AuditSeverity.MEDIUM

        # Failed actions are always at least medium
        if not success:
            return AuditSeverity.MEDIUM

        return AuditSeverity.LOW

    def get_entries(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get audit entries with filters."""
        entries = self._entries

        if user_id:
            entries = [e for e in entries if e.user_id == user_id]

        if action:
            entries = [e for e in entries if e.action == action]

        if severity:
            entries = [e for e in entries if e.severity == severity]

        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]

        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]

        return entries[-limit:]

    def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
    ) -> dict:
        """Get user activity summary."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)
        entries = [e for e in self._entries if e.user_id == user_id and e.timestamp >= cutoff]

        action_counts = {}
        for entry in entries:
            action_counts[entry.action.value] = action_counts.get(entry.action.value, 0) + 1

        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(entries),
            "actions": action_counts,
            "last_activity": entries[-1].timestamp.isoformat() if entries else None,
        }

    def export_entries(
        self,
        format: str = "json",
        **filters,
    ) -> str:
        """Export audit entries."""
        entries = self.get_entries(**filters)

        if format == "json":
            return json.dumps([
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "action": e.action.value,
                    "severity": e.severity.value,
                    "resource_type": e.resource_type,
                    "resource_id": e.resource_id,
                    "details": e.details,
                    "success": e.success,
                }
                for e in entries
            ], indent=2)

        return str(entries)


class SSOService:
    """SSO authentication service."""

    def __init__(self, config: SSOConfig):
        self.config = config

    def get_auth_url(self, state: str) -> Optional[str]:
        """
        Get SSO authorization URL.

        Args:
            state: CSRF state parameter

        Returns:
            Authorization URL or None if SSO disabled
        """
        if not self.config.enabled:
            return None

        if self.config.provider == "oidc":
            return self._get_oidc_auth_url(state)
        elif self.config.provider == "saml":
            return self._get_saml_auth_url(state)

        return None

    def _get_oidc_auth_url(self, state: str) -> str:
        """Generate OIDC authorization URL."""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_url,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": state,
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.config.discovery_url}/authorize?{query_string}"

    def _get_saml_auth_url(self, state: str) -> str:
        """Generate SAML authentication URL."""
        # Simplified - real implementation would use python3-saml
        return f"{self.config.discovery_url}/sso/saml?state={state}"

    async def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate an SSO token.

        Args:
            token: SSO token to validate

        Returns:
            User info dict or None if invalid
        """
        if not self.config.enabled:
            return None

        # In production, validate with SSO provider
        # This is a placeholder
        try:
            # Decode and validate JWT
            import jwt
            payload = jwt.decode(
                token,
                self.config.client_secret,
                algorithms=["RS256"],
            )
            return payload
        except Exception as e:
            logger.warning(f"SSO token validation failed: {e}")
            return None

    def check_domain_allowed(self, email: str) -> bool:
        """Check if email domain is allowed."""
        if not self.config.allowed_domains:
            return True

        domain = email.split("@")[-1] if "@" in email else ""
        return domain in self.config.allowed_domains
