"""
AmanAgentLab Agents — multi-agent intelligence system.

Core System:
  - Planner: Intent detection, query classification, task planning
  - Router: Intelligent agent selection and orchestration

Agents:
  - Retrieval: Vector search, RAG context building, citation collection
  - Memory: Memory extraction, preference learning, context retrieval
  - Research: Search, scrape, crawl, map, extract
  - Knowledge: Entity/relationship extraction, knowledge graph updates
  - Citation: Source verification, grounding verification, attribution
  - Security: Prompt injection detection, context validation, trust analysis
  - Workflow: Background jobs, monitoring, scheduled research

CrewAI:
  - WebIntelligenceCrew: CrewAI-based web intelligence orchestration
"""

# Core system
from agents.planner import create_plan, QueryType, TaskAction, Plan, PlanStep
from agents.router import AgentRegistry, Router, RouteContext, AgentResult

# Intelligence agents
from agents.retrieval_agent import retrieval_executor
from agents.memory_agent import memory_executor
from agents.research_agent import research_executor
from agents.knowledge_agent import knowledge_executor
from agents.citation_agent import citation_executor
from agents.security_agent import security_executor
from agents.workflow_agent import workflow_executor

# CrewAI (legacy) - optional import
try:
    from agents.crawl_agents import WebIntelligenceCrew
    from agents.tools import JinaReaderTool, Crawl4AITool, LLMScraperTool, ScrapeGraphAITool
    _crewai_available = True
except ImportError:
    _crewai_available = False
    WebIntelligenceCrew = None
    JinaReaderTool = None
    Crawl4AITool = None
    LLMScraperTool = None
    ScrapeGraphAITool = None

__all__ = [
    # Core
    "create_plan", "QueryType", "TaskAction", "Plan", "PlanStep",
    "AgentRegistry", "Router", "RouteContext", "AgentResult",
    # Agents
    "retrieval_executor",
    "memory_executor",
    "research_executor",
    "knowledge_executor",
    "citation_executor",
    "security_executor",
    "workflow_executor",
    # CrewAI
    "WebIntelligenceCrew",
    "JinaReaderTool",
    "Crawl4AITool",
    "LLMScraperTool",
    "ScrapeGraphAITool",
]
