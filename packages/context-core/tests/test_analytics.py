"""
Tests for analytics service.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime, timedelta

from analytics.service import (
    AnalyticsConfig,
    AnalyticsService,
    MetricType,
    TimeGranularity,
    MetricDataPoint,
)


class TestAnalyticsConfig:
    """Test AnalyticsConfig."""

    def test_default_config(self):
        config = AnalyticsConfig()
        assert config.retention_days == 90
        assert config.enabled is True

    def test_custom_config(self):
        config = AnalyticsConfig(retention_days=30, enabled=False)
        assert config.retention_days == 30
        assert config.enabled is False


class TestAnalyticsService:
    """Test AnalyticsService."""

    def test_record_metric(self):
        service = AnalyticsService()
        service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)
        assert len(service._metrics["memory_add"]) == 1

    def test_disabled_analytics(self):
        config = AnalyticsConfig(enabled=False)
        service = AnalyticsService(config)
        service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)
        assert "memory_add" not in service._metrics

    def test_get_usage_summary(self):
        service = AnalyticsService()

        # Record some metrics
        for _ in range(5):
            service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)

        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=1)

        summary = service.get_usage_summary(
            user_id="user1",
            metric=MetricType.MEMORY_ADD,
            period_start=period_start,
            period_end=period_end,
        )

        assert summary.total == 5
        assert summary.metric == "memory_add"

    def test_get_analytics_snapshot(self):
        service = AnalyticsService()

        # Record metrics
        service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)
        service.record_metric("user1", MetricType.SEARCH_QUERY, 2.0)

        snapshot = service.get_analytics_snapshot("user1", period_days=30)

        assert snapshot.user_id == "user1"
        assert len(snapshot.metrics) == 2

    def test_get_daily_usage_chart(self):
        service = AnalyticsService()

        # Record metrics
        for _ in range(3):
            service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)

        chart_data = service.get_daily_usage_chart(
            user_id="user1",
            metric=MetricType.MEMORY_ADD,
            days=7,
        )

        assert isinstance(chart_data, list)
        assert len(chart_data) > 0

    def test_get_usage_by_type(self):
        service = AnalyticsService()

        service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)
        service.record_metric("user1", MetricType.SEARCH_QUERY, 2.0)

        usage = service.get_usage_by_type("user1", period_days=30)

        assert "memory_add" in usage
        assert "search_query" in usage
        assert usage["memory_add"] == 1
        assert usage["search_query"] == 2

    def test_export_analytics_json(self):
        service = AnalyticsService()
        service.record_metric("user1", MetricType.MEMORY_ADD, 1.0)

        export = service.export_analytics("user1", format="json")

        assert isinstance(export, str)
        assert "user1" in export

    def test_aggregate_by_granularity(self):
        service = AnalyticsService()

        records = [
            {"timestamp": "2026-06-20T10:00:00", "value": 1.0},
            {"timestamp": "2026-06-20T11:00:00", "value": 2.0},
            {"timestamp": "2026-06-21T10:00:00", "value": 3.0},
        ]

        data_points = service._aggregate_by_granularity(records, TimeGranularity.DAILY)

        assert len(data_points) == 2
        assert data_points[0].value == 3.0  # June 20 total
        assert data_points[1].value == 3.0  # June 21 total

    def test_growth_rate(self):
        service = AnalyticsService()

        data_points = [
            MetricDataPoint(timestamp=datetime(2026, 6, 1), value=10),
            MetricDataPoint(timestamp=datetime(2026, 6, 2), value=10),
            MetricDataPoint(timestamp=datetime(2026, 6, 3), value=20),
            MetricDataPoint(timestamp=datetime(2026, 6, 4), value=20),
        ]

        growth = service._calculate_growth_rate(data_points)
        assert growth == 1.0  # 100% growth

    def test_growth_rate_no_data(self):
        service = AnalyticsService()
        growth = service._calculate_growth_rate([])
        assert growth == 0.0


class TestMetricType:
    """Test MetricType enum."""

    def test_metric_types(self):
        assert MetricType.MEMORY_ADD.value == "memory_add"
        assert MetricType.SEARCH_QUERY.value == "search_query"
        assert MetricType.CRAWL_PAGE.value == "crawl_page"
