"""
CrewAI Integration — CrewAI-based orchestration for ContextOS.

Provides specialized crews for complex multi-agent tasks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from crewai import Agent, Task, Crew
    _crewai_available = True
except ImportError:
    _crewai_available = False
    Agent = None
    Task = None
    Crew = None


@dataclass
class CrewConfig:
    """Configuration for a ContextOS crew."""
    name: str
    description: str
    agents: list[dict] = field(default_factory=list)
    tasks: list[dict] = field(default_factory=list)
    verbose: bool = True
    memory: bool = True


# Predefined agent roles
AGENT_ROLES = {
    "researcher": {
        "role": "Senior Research Analyst",
        "goal": "Conduct thorough research on the given topic",
        "backstory": "Expert at finding and synthesizing information from multiple sources",
    },
    "writer": {
        "role": "Technical Writer",
        "goal": "Create clear, comprehensive documentation and reports",
        "backstory": "Skilled at explaining complex concepts in accessible ways",
    },
    "analyst": {
        "role": "Data Analyst",
        "goal": "Analyze data patterns and extract meaningful insights",
        "backstory": "Expert at statistical analysis and data interpretation",
    },
    "coder": {
        "role": "Software Developer",
        "goal": "Write clean, efficient code to solve problems",
        "backstory": "Full-stack developer with expertise in multiple languages",
    },
    "reviewer": {
        "role": "Quality Reviewer",
        "goal": "Ensure work meets high quality standards",
        "backstory": "Detail-oriented reviewer with strong critical thinking skills",
    },
}

# Predefined crew templates
CREW_TEMPLATES = {
    "research_crew": CrewConfig(
        name="Research Crew",
        description="Conducts comprehensive research on topics",
        agents=[AGENT_ROLES["researcher"], AGENT_ROLES["analyst"]],
    ),
    "documentation_crew": CrewConfig(
        name="Documentation Crew",
        description="Creates technical documentation",
        agents=[AGENT_ROLES["writer"], AGENT_ROLES["reviewer"]],
    ),
    "development_crew": CrewConfig(
        name="Development Crew",
        description="Full software development workflow",
        agents=[AGENT_ROLES["coder"], AGENT_ROLES["reviewer"]],
    ),
    "content_crew": CrewConfig(
        name="Content Crew",
        description="Content creation and optimization",
        agents=[AGENT_ROLES["researcher"], AGENT_ROLES["writer"], AGENT_ROLES["reviewer"]],
    ),
}


class ContextOSCrew:
    """A CrewAI crew powered by ContextOS memory."""

    def __init__(
        self,
        config: CrewConfig,
        memory_service=None,
        knowledge_service=None,
    ):
        self.config = config
        self.memory_service = memory_service
        self.knowledge_service = knowledge_service
        self.crew = None

        if not _crewai_available:
            logger.warning("CrewAI not available. Install with: pip install crewai")
            return

        self._build_crew()

    def _build_crew(self):
        """Build the CrewAI crew from config."""
        if not _crewai_available:
            return

        agents = []
        for agent_config in self.config.agents:
            agent = Agent(
                role=agent_config.get("role", "Agent"),
                goal=agent_config.get("goal", "Complete the task"),
                backstory=agent_config.get("backstory", ""),
                verbose=self.config.verbose,
                allow_delegation=False,
            )
            agents.append(agent)

        self.agents = agents

    async def create_task(
        self,
        description: str,
        expected_output: str,
        agent_index: int = 0,
    ) -> Optional[object]:
        """Create a CrewAI task."""
        if not _crewai_available or not self.agents:
            return None

        if agent_index >= len(self.agents):
            agent_index = 0

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=self.agents[agent_index],
        )
        return task

    async def run(self, tasks: list) -> dict:
        """Run the crew with tasks."""
        if not _crewai_available or not self.agents:
            return {"error": "CrewAI not available"}

        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            memory=self.config.memory,
        )

        result = crew.kickoff()

        # Store results in memory if available
        if self.memory_service:
            try:
                await self.memory_service.add_memory(
                    content=f"Crew '{self.config.name}' completed with result: {str(result)[:500]}",
                    metadata={"crew": self.config.name, "type": "crew_result"},
                )
            except Exception as e:
                logger.warning(f"Failed to store crew result: {e}")

        return {"result": str(result), "crew": self.config.name}


def create_crew(
    template: str = "research_crew",
    memory_service=None,
    knowledge_service=None,
) -> Optional[ContextOSCrew]:
    """
    Create a predefined crew from template.

    Args:
        template: Template name (research_crew, documentation_crew, development_crew, content_crew)
        memory_service: Optional ContextOS memory service
        knowledge_service: Optional ContextOS knowledge service

    Returns:
        ContextOSCrew or None if CrewAI not available
    """
    if template not in CREW_TEMPLATES:
        logger.error(f"Unknown crew template: {template}")
        return None

    config = CREW_TEMPLATES[template]
    return ContextOSCrew(config, memory_service, knowledge_service)


def is_crewai_available() -> bool:
    """Check if CrewAI is available."""
    return _crewai_available
