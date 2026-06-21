"""
Analytics Dashboard — Usage visualization and metrics.

Provides API endpoints for usage statistics and analytics.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    MEMORY_ADD = "memory_add"
    MEMORY_SEARCH = "memory_search"
    MEMORY_DELETE = "memory_delete"
    SEARCH_QUERY = "search_query"
    CRAWL_PAGE = "crawl_page"
    CRAWL_MAP = "crawl_map"
    KNOWLEDGE_EXTRACT = "knowledge_extract"
    API_REQUEST = "api_request"


class TimeGranularity(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class MetricDataPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    count: int = 0


@dataclass
class UsageSummary:
    """Usage summary for a metric."""
    metric: str
    total: int
    period_start: datetime
    period_end: datetime
    data_points: list[MetricDataPoint] = field(default_factory=list)
    growth_rate: float = 0.0


@dataclass
class AnalyticsSnapshot:
    """Complete analytics snapshot."""
    user_id: str
    period_start: datetime
    period_end: datetime
    metrics: dict[str, UsageSummary] = field(default_factory=dict)
    top_queries: list[dict] = field(default_factory=list)
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0


@dataclass
class AnalyticsConfig:
    """Analytics configuration."""
    retention_days: int = 90
    enabled: bool = True


class AnalyticsService:
    """Analytics service for usage tracking and visualization."""

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        self.config = config or AnalyticsConfig()
        self._metrics: dict[str, list[dict]] = defaultdict(list)

    def record_metric(
        self,
        user_id: str,
        metric: MetricType,
        value: float = 1.0,
        metadata: Optional[dict] = None,
    ):
        """Record a metric data point."""
        if not self.config.enabled:
            return

        record = {
            "user_id": user_id,
            "metric": metric.value,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self._metrics[metric.value].append(record)

        # Cleanup old records
        self._cleanup_old_records()

    def _cleanup_old_records(self):
        """Remove records older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.config.retention_days)

        for metric_name in list(self._metrics.keys()):
            self._metrics[metric_name] = [
                r for r in self._metrics[metric_name]
                if datetime.fromisoformat(r["timestamp"]) > cutoff
            ]

    def get_usage_summary(
        self,
        user_id: str,
        metric: MetricType,
        period_start: datetime,
        period_end: datetime,
        granularity: TimeGranularity = TimeGranularity.DAILY,
    ) -> UsageSummary:
        """Get usage summary for a metric."""
        records = [
            r for r in self._metrics.get(metric.value, [])
            if r["user_id"] == user_id
            and period_start <= datetime.fromisoformat(r["timestamp"]) <= period_end
        ]

        total = sum(r["value"] for r in records)

        # Group by granularity
        data_points = self._aggregate_by_granularity(records, granularity)

        # Calculate growth rate
        growth_rate = self._calculate_growth_rate(data_points)

        return UsageSummary(
            metric=metric.value,
            total=int(total),
            period_start=period_start,
            period_end=period_end,
            data_points=data_points,
            growth_rate=growth_rate,
        )

    def _aggregate_by_granularity(
        self,
        records: list[dict],
        granularity: TimeGranularity,
    ) -> list[MetricDataPoint]:
        """Aggregate records by time granularity."""
        buckets: dict[str, list[float]] = defaultdict(list)

        for record in records:
            ts = datetime.fromisoformat(record["timestamp"])

            if granularity == TimeGranularity.HOURLY:
                key = ts.strftime("%Y-%m-%d %H:00")
            elif granularity == TimeGranularity.DAILY:
                key = ts.strftime("%Y-%m-%d")
            elif granularity == TimeGranularity.WEEKLY:
                # Get start of week
                start_of_week = ts - timedelta(days=ts.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
            else:  # Monthly
                key = ts.strftime("%Y-%m")

            buckets[key].append(record["value"])

        data_points = []
        for key in sorted(buckets.keys()):
            values = buckets[key]
            data_points.append(MetricDataPoint(
                timestamp=datetime.fromisoformat(key) if " " in key else datetime.strptime(key, "%Y-%m-%d"),
                value=sum(values),
                count=len(values),
            ))

        return data_points

    def _calculate_growth_rate(self, data_points: list[MetricDataPoint]) -> float:
        """Calculate growth rate from data points."""
        if len(data_points) < 2:
            return 0.0

        # Compare last period to previous period
        mid = len(data_points) // 2
        first_half = sum(dp.value for dp in data_points[:mid])
        second_half = sum(dp.value for dp in data_points[mid:])

        if first_half == 0:
            return 1.0 if second_half > 0 else 0.0

        return (second_half - first_half) / first_half

    def get_analytics_snapshot(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> AnalyticsSnapshot:
        """Get complete analytics snapshot."""
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        metrics = {}
        for metric_type in MetricType:
            summary = self.get_usage_summary(
                user_id=user_id,
                metric=metric_type,
                period_start=period_start,
                period_end=period_end,
            )
            if summary.total > 0:
                metrics[metric_type.value] = summary

        # Get top queries (placeholder - would need query logging)
        top_queries = []

        # Calculate error rate (placeholder)
        error_rate = 0.0

        # Calculate avg response time (placeholder)
        avg_response_time_ms = 0.0

        return AnalyticsSnapshot(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            top_queries=top_queries,
            error_rate=error_rate,
            avg_response_time_ms=avg_response_time_ms,
        )

    def get_daily_usage_chart(
        self,
        user_id: str,
        metric: MetricType,
        days: int = 30,
    ) -> list[dict]:
        """Get data for daily usage chart."""
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        summary = self.get_usage_summary(
            user_id=user_id,
            metric=metric,
            period_start=period_start,
            period_end=period_end,
            granularity=TimeGranularity.DAILY,
        )

        return [
            {
                "date": dp.timestamp.strftime("%Y-%m-%d"),
                "value": dp.value,
                "count": dp.count,
            }
            for dp in summary.data_points
        ]

    def get_usage_by_type(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> dict[str, int]:
        """Get usage breakdown by metric type."""
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        usage = {}
        for metric_type in MetricType:
            records = [
                r for r in self._metrics.get(metric_type.value, [])
                if r["user_id"] == user_id
                and period_start <= datetime.fromisoformat(r["timestamp"]) <= period_end
            ]
            total = sum(r["value"] for r in records)
            if total > 0:
                usage[metric_type.value] = int(total)

        return usage

    def export_analytics(
        self,
        user_id: str,
        format: str = "json",
    ) -> str:
        """Export analytics data."""
        snapshot = self.get_analytics_snapshot(user_id)

        if format == "json":
            return json.dumps({
                "user_id": snapshot.user_id,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "metrics": {
                    k: {
                        "total": v.total,
                        "growth_rate": v.growth_rate,
                    }
                    for k, v in snapshot.metrics.items()
                },
                "error_rate": snapshot.error_rate,
                "avg_response_time_ms": snapshot.avg_response_time_ms,
            }, indent=2)

        return str(snapshot)
