"""
Knowledge Auto-Extract — Extract entities and relationships from text.

Uses LLM to automatically extract entities and relationships from
crawled content, documents, or any text.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    PROJECT = "project"
    REPOSITORY = "repository"
    WEBSITE = "website"
    DOCUMENT = "document"
    API = "api"
    ORGANIZATION = "organization"


class RelationshipType(str, Enum):
    CREATED_BY = "created_by"
    OWNED_BY = "owned_by"
    DEPENDS_ON = "depends_on"
    INTEGRATES_WITH = "integrates_with"
    REFERENCES = "references"
    RELATED_TO = "related_to"
    COMPETITOR_OF = "competitor_of"
    MENTIONED_IN = "mentioned_in"


@dataclass
class ExtractedEntity:
    """An extracted entity."""
    name: str
    entity_type: EntityType
    properties: dict = field(default_factory=dict)
    confidence: float = 0.8


@dataclass
class ExtractedRelationship:
    """An extracted relationship."""
    source_name: str
    target_name: str
    relationship_type: RelationshipType
    properties: dict = field(default_factory=dict)
    confidence: float = 0.8


@dataclass
class ExtractionResult:
    """Result of knowledge extraction."""
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)
    source_text_length: int = 0
    extraction_time_ms: float = 0.0


@dataclass
class ExtractionConfig:
    """Configuration for knowledge extraction."""
    enabled: bool = True
    max_entities: int = 20
    max_relationships: int = 30
    min_confidence: float = 0.5
    extract_entities: bool = True
    extract_relationships: bool = True


# System prompt for extraction
EXTRACTION_PROMPT = """You are a knowledge extraction assistant. Extract entities and relationships from the given text.

Entity types: person, company, product, technology, project, repository, website, document, api, organization

Relationship types: created_by, owned_by, depends_on, integrates_with, references, related_to, competitor_of, mentioned_in

Text to analyze:
{text}

Extract entities and relationships in JSON format:
{{
  "entities": [
    {{
      "name": "<entity name>",
      "type": "<entity type>",
      "properties": {{"<key>": "<value>"}},
      "confidence": <0.0-1.0>
    }}
  ],
  "relationships": [
    {{
      "source": "<source entity name>",
      "target": "<target entity name>",
      "type": "<relationship type>",
      "properties": {{"<key>": "<value>"}},
      "confidence": <0.0-1.0>
    }}
  ]
}}

Rules:
1. Extract only clearly stated entities and relationships
2. Use the exact entity and relationship types provided
3. Include confidence scores based on how certain you are
4. Keep properties minimal and relevant
5. Maximum {max_entities} entities and {max_relationships} relationships"""


class KnowledgeAutoExtract:
    """Knowledge auto-extraction service."""

    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()

    async def extract(
        self,
        text: str,
        api_key: str,
        model: str,
    ) -> ExtractionResult:
        """
        Extract entities and relationships from text.

        Args:
            text: Text to extract from
            api_key: LLM API key
            model: LLM model name

        Returns:
            ExtractionResult with entities and relationships
        """
        import time
        start = time.time()

        result = ExtractionResult(source_text_length=len(text))

        if not self.config.enabled or not text.strip():
            return result

        # Truncate text if too long
        max_chars = 8000  # Limit to avoid token overflow
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated...]"

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "ContextOS Extraction",
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a knowledge extraction assistant."},
                    {
                        "role": "user",
                        "content": EXTRACTION_PROMPT.format(
                            text=text,
                            max_entities=self.config.max_entities,
                            max_relationships=self.config.max_relationships,
                        ),
                    },
                ],
                "temperature": 0.2,
                "max_tokens": 2000,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.warning(f"Extraction LLM failed: {response.status_code}")
                    result.extraction_time_ms = (time.time() - start) * 1000
                    return result

                llm_result = response.json()
                content = llm_result["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                data = json.loads(content)

                # Parse entities
                if self.config.extract_entities:
                    for entity_data in data.get("entities", [])[:self.config.max_entities]:
                        try:
                            entity_type = EntityType(entity_data.get("type", "organization"))
                            confidence = float(entity_data.get("confidence", 0.8))

                            if confidence >= self.config.min_confidence:
                                result.entities.append(ExtractedEntity(
                                    name=entity_data["name"],
                                    entity_type=entity_type,
                                    properties=entity_data.get("properties", {}),
                                    confidence=confidence,
                                ))
                        except (ValueError, KeyError) as e:
                            logger.debug(f"Failed to parse entity: {e}")

                # Parse relationships
                if self.config.extract_relationships:
                    for rel_data in data.get("relationships", [])[:self.config.max_relationships]:
                        try:
                            rel_type = RelationshipType(rel_data.get("type", "related_to"))
                            confidence = float(rel_data.get("confidence", 0.8))

                            if confidence >= self.config.min_confidence:
                                result.relationships.append(ExtractedRelationship(
                                    source_name=rel_data["source"],
                                    target_name=rel_data["target"],
                                    relationship_type=rel_type,
                                    properties=rel_data.get("properties", {}),
                                    confidence=confidence,
                                ))
                        except (ValueError, KeyError) as e:
                            logger.debug(f"Failed to parse relationship: {e}")

        except Exception as e:
            logger.warning(f"Knowledge extraction error: {e}")

        result.extraction_time_ms = (time.time() - start) * 1000
        return result

    def extract_simple(self, text: str) -> ExtractionResult:
        """
        Simple regex-based extraction without LLM.

        Useful as fallback when LLM is unavailable.
        """
        import re
        result = ExtractionResult(source_text_length=len(text))

        # Simple patterns for common entities
        patterns = {
            EntityType.PERSON: r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            EntityType.COMPANY: r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Co)\b',
            EntityType.WEBSITE: r'https?://[^\s]+',
        }

        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in set(matches):
                if len(match) > 3:  # Skip very short matches
                    result.entities.append(ExtractedEntity(
                        name=match,
                        entity_type=entity_type,
                        confidence=0.6,
                    ))

        return result


async def extract_and_store(
    text: str,
    user_id: str,
    knowledge_service,
    api_key: str,
    model: str,
    config: Optional[ExtractionConfig] = None,
) -> ExtractionResult:
    """
    Extract knowledge from text and store in knowledge graph.

    Args:
        text: Text to extract from
        user_id: User ID for storage
        knowledge_service: Knowledge graph service
        api_key: LLM API key
        model: LLM model name
        config: Extraction configuration

    Returns:
        ExtractionResult
    """
    extractor = KnowledgeAutoExtract(config)
    result = await extractor.extract(text, api_key, model)

    # Store entities
    stored_entities = {}
    for entity in result.entities:
        try:
            stored = await knowledge_service.create_entity(
                user_id=user_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                properties=entity.properties,
            )
            stored_entities[entity.name] = stored.id
        except Exception as e:
            logger.debug(f"Failed to store entity {entity.name}: {e}")

    # Store relationships
    for rel in result.relationships:
        source_id = stored_entities.get(rel.source_name)
        target_id = stored_entities.get(rel.target_name)

        if source_id and target_id:
            try:
                await knowledge_service.create_relationship(
                    user_id=user_id,
                    source_entity_id=source_id,
                    target_entity_id=target_id,
                    relationship_type=rel.relationship_type.value,
                    properties=rel.properties,
                    confidence=rel.confidence,
                )
            except Exception as e:
                logger.debug(f"Failed to store relationship: {e}")

    return result
