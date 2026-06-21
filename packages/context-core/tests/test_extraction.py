"""
Tests for knowledge auto-extraction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch

from knowledge.extraction import (
    ExtractionConfig,
    ExtractionResult,
    KnowledgeAutoExtract,
    EntityType,
    RelationshipType,
    ExtractedEntity,
    ExtractedRelationship,
)


class TestExtractionConfig:
    """Test ExtractionConfig."""

    def test_default_config(self):
        config = ExtractionConfig()
        assert config.enabled is True
        assert config.max_entities == 20
        assert config.max_relationships == 30
        assert config.min_confidence == 0.5

    def test_custom_config(self):
        config = ExtractionConfig(
            enabled=False,
            max_entities=10,
            min_confidence=0.8,
        )
        assert config.enabled is False
        assert config.max_entities == 10
        assert config.min_confidence == 0.8


class TestExtractionResult:
    """Test ExtractionResult."""

    def test_result_creation(self):
        result = ExtractionResult()
        assert result.entities == []
        assert result.relationships == []
        assert result.source_text_length == 0


class TestKnowledgeAutoExtract:
    """Test KnowledgeAutoExtract."""

    def test_disabled_extraction(self):
        config = ExtractionConfig(enabled=False)
        extractor = KnowledgeAutoExtract(config)

        result = extractor.extract_simple("test text")
        assert result.entities == []

    def test_simple_extraction_urls(self):
        extractor = KnowledgeAutoExtract()
        result = extractor.extract_simple("Visit https://example.com for more info")

        # Should extract URLs
        url_entities = [e for e in result.entities if e.entity_type == EntityType.WEBSITE]
        assert len(url_entities) > 0

    def test_simple_extraction_empty(self):
        extractor = KnowledgeAutoExtract()
        result = extractor.extract_simple("no entities here")
        # Simple extraction may or may not find anything
        assert isinstance(result.entities, list)

    def test_empty_text(self):
        extractor = KnowledgeAutoExtract()
        result = extractor.extract_simple("")
        assert result.entities == []


class TestEntityType:
    """Test EntityType enum."""

    def test_entity_types(self):
        assert EntityType.PERSON.value == "person"
        assert EntityType.COMPANY.value == "company"
        assert EntityType.TECHNOLOGY.value == "technology"


class TestRelationshipType:
    """Test RelationshipType enum."""

    def test_relationship_types(self):
        assert RelationshipType.CREATED_BY.value == "created_by"
        assert RelationshipType.DEPENDS_ON.value == "depends_on"
