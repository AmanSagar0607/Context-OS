# agents/knowledge_agent.py
"""
Knowledge Agent — Entity extraction, relationship extraction, knowledge graph updates, source linking.

Responsibilities:
- Extract entities (Person, Company, Product, Technology, etc.)
- Extract relationships between entities
- Update knowledge graph
- Link new information to existing entities
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from services.openrouter import stream_chat_completion
from app.config import get_settings
from .planner import PlanStep, TaskAction
from .router import AgentResult, RouteContext

logger = logging.getLogger(__name__)

# Entity type patterns
ENTITY_PATTERNS = {
    "person": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
    "email": r'\b[\w.-]+@[\w.-]+\.\w+\b',
    "url": r'https?://[^\s]+',
    "technology": r'\b(Python|JavaScript|TypeScript|Rust|Go|Docker|Kubernetes|React|Next\.js|FastAPI|PostgreSQL|Redis|MongoDB|Milvus|Zilliz|OpenAI|Anthropic|CrewAI|LangChain|LlamaIndex)\b',
    "company": r'\b(OpenAI|Google|Microsoft|Amazon|Meta|Apple|Anthropic|Firecrawl|Vercel|Supabase|Neon)\b',
}

EXTRACTION_PROMPT = """Extract structured information from the following content.

Content:
{content}

Task: {instruction}

Return a JSON object with:
- "entities": list of {{ "type": str, "name": str, "properties": dict }}
- "relationships": list of {{ "source": str, "target": str, "type": str, "properties": dict }}
- "summary": str
- "key_facts": list of str

Return ONLY valid JSON, no markdown."""


async def knowledge_executor(step: PlanStep, context: RouteContext) -> AgentResult:
    """Execute knowledge extraction steps."""
    if step.action == TaskAction.EXTRACT:
        return await _extract_knowledge(context)
    elif step.action == TaskAction.ANSWER:
        return await _present_knowledge(context)
    return AgentResult(agent="knowledge", action=step.action.value, data=None)


async def _extract_knowledge(context: RouteContext) -> AgentResult:
    """Extract entities and relationships from content."""
    start = time.time()
    entities = []
    relationships = []
    sources = []
    
    # Gather content from context
    content = context.scraped_content
    if not content and context.retrieved_chunks:
        content = "\n".join(c.get("text", "") for c in context.retrieved_chunks[:3])
    if not content:
        content = context.query
    
    # Pattern-based extraction first
    for etype, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, content)
        for match in set(matches):
            entities.append({
                "type": etype,
                "name": match,
                "properties": {},
            })
    
    # LLM-based extraction for richer understanding
    try:
        settings = get_settings()
        if settings.openrouter_api_key:
            prompt = EXTRACTION_PROMPT.format(
                content=content[:3000],
                instruction=context.query,
            )
            
            response = ""
            async for chunk in stream_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-4o-mini",
                api_key=settings.openrouter_api_key,
            ):
                response += chunk
            
            # Parse JSON response
            parsed = _parse_json(response)
            if parsed:
                llm_entities = parsed.get("entities", [])
                llm_relationships = parsed.get("relationships", [])
                
                # Merge with pattern-based entities
                existing_names = {e["name"].lower() for e in entities}
                for ent in llm_entities:
                    if ent.get("name", "").lower() not in existing_names:
                        entities.append(ent)
                        existing_names.add(ent["name"].lower())
                
                relationships.extend(llm_relationships)
                
                # Add summary as citation
                summary = parsed.get("summary", "")
                if summary:
                    sources.append({
                        "type": "knowledge_extraction",
                        "summary": summary,
                    })
    except Exception as e:
        logger.warning(f"LLM extraction failed, using pattern-based only: {e}")
    
    context.extracted_entities = entities
    context.extracted_relationships = relationships
    
    return AgentResult(
        agent="knowledge",
        action="extract",
        data={
            "entity_count": len(entities),
            "relationship_count": len(relationships),
        },
        confidence=min(len(entities) / 3, 1.0),
        entities=entities,
        relationships=relationships,
        sources=sources,
        elapsed_ms=(time.time() - start) * 1000,
    )


async def _present_knowledge(context: RouteContext) -> AgentResult:
    """Present extracted knowledge in structured format."""
    entities_by_type = {}
    for ent in context.extracted_entities:
        etype = ent.get("type", "unknown")
        if etype not in entities_by_type:
            entities_by_type[etype] = []
        entities_by_type[etype].append(ent)
    
    return AgentResult(
        agent="knowledge",
        action="present",
        data={
            "entities_by_type": entities_by_type,
            "relationships": context.extracted_relationships,
            "total_entities": len(context.extracted_entities),
            "total_relationships": len(context.extracted_relationships),
        },
        entities=context.extracted_entities,
        relationships=context.extracted_relationships,
    )


def _parse_json(text: str) -> dict | None:
    """Extract JSON from LLM response."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from code blocks
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try finding JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None
