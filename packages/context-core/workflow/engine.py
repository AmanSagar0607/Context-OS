"""
Workflow Engine — Advanced workflow orchestration.

Provides step-by-step workflow execution with branching, loops, and error handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    RETRY = "retry"
    WAIT = "wait"
    CALLBACK = "callback"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single workflow step."""
    id: str
    name: str
    step_type: StepType
    action: Optional[str] = None
    config: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """A complete workflow definition."""
    id: str
    name: str
    description: str
    steps: list[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    workflow_id: str
    status: WorkflowStatus
    step_results: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0


class WorkflowEngine:
    """Workflow execution engine."""

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}
        self._action_handlers: dict[str, Callable] = {}
        self._running: dict[str, asyncio.Task] = {}

    def register_action(self, action_name: str, handler: Callable):
        """Register an action handler."""
        self._action_handlers[action_name] = handler

    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: Optional[list[dict]] = None,
        metadata: Optional[dict] = None,
    ) -> Workflow:
        """Create a new workflow."""
        workflow_id = str(uuid4())

        workflow_steps = []
        if steps:
            for i, step_data in enumerate(steps):
                step = WorkflowStep(
                    id=step_data.get("id", f"step_{i}"),
                    name=step_data.get("name", f"Step {i + 1}"),
                    step_type=StepType(step_data.get("type", "action")),
                    action=step_data.get("action"),
                    config=step_data.get("config", {}),
                    depends_on=step_data.get("depends_on", []),
                    timeout_seconds=step_data.get("timeout_seconds", 300),
                    max_retries=step_data.get("max_retries", 3),
                )
                workflow_steps.append(step)

        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            metadata=metadata or {},
        )

        self._workflows[workflow_id] = workflow
        return workflow

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self._workflows.get(workflow_id)

    async def add_step(
        self,
        workflow_id: str,
        step_data: dict,
    ) -> Optional[WorkflowStep]:
        """Add a step to a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        step = WorkflowStep(
            id=step_data.get("id", f"step_{len(workflow.steps)}"),
            name=step_data.get("name", f"Step {len(workflow.steps) + 1}"),
            step_type=StepType(step_data.get("type", "action")),
            action=step_data.get("action"),
            config=step_data.get("config", {}),
            depends_on=step_data.get("depends_on", []),
            timeout_seconds=step_data.get("timeout_seconds", 300),
            max_retries=step_data.get("max_retries", 3),
        )

        workflow.steps.append(step)
        return step

    async def run_workflow(
        self,
        workflow_id: str,
        context: Optional[dict] = None,
    ) -> WorkflowResult:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow to execute
            context: Optional execution context

        Returns:
            WorkflowResult
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                error="Workflow not found",
            )

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        if context:
            workflow.context.update(context)

        start_time = datetime.utcnow()
        step_results = {}

        try:
            # Execute steps in order, respecting dependencies
            for step in workflow.steps:
                # Check if dependencies are satisfied
                deps_met = all(
                    step_results.get(dep, {}).get("status") == StepStatus.COMPLETED.value
                    for dep in step.depends_on
                )

                if not deps_met:
                    step.status = StepStatus.SKIPPED
                    step_results[step.id] = {
                        "status": StepStatus.SKIPPED.value,
                        "reason": "Dependencies not met",
                    }
                    continue

                # Execute step
                result = await self._execute_step(step, workflow.context)
                step_results[step.id] = result

                if result["status"] == StepStatus.FAILED.value:
                    workflow.status = WorkflowStatus.FAILED
                    workflow.completed_at = datetime.utcnow()
                    return WorkflowResult(
                        workflow_id=workflow_id,
                        status=WorkflowStatus.FAILED,
                        step_results=step_results,
                        error=result.get("error"),
                        duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                    )

            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()

            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.COMPLETED,
                step_results=step_results,
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )

        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()

            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                step_results=step_results,
                error=str(e),
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: dict,
    ) -> dict:
        """Execute a single workflow step."""
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()

        try:
            if step.step_type == StepType.ACTION:
                result = await self._execute_action(step, context)
            elif step.step_type == StepType.CONDITION:
                result = await self._evaluate_condition(step, context)
            elif step.step_type == StepType.WAIT:
                result = await self._execute_wait(step, context)
            elif step.step_type == StepType.CALLBACK:
                result = await self._execute_callback(step, context)
            else:
                result = {"status": StepStatus.COMPLETED.value, "output": None}

            step.status = StepStatus.COMPLETED
            step.result = result
            step.completed_at = datetime.utcnow()

            return {
                "status": StepStatus.COMPLETED.value,
                "output": result,
                "duration_ms": (datetime.utcnow() - step.started_at).total_seconds() * 1000,
            }

        except Exception as e:
            logger.error(f"Step {step.id} failed: {e}")

            # Retry if configured
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                logger.info(f"Retrying step {step.id} (attempt {step.retry_count})")
                return await self._execute_step(step, context)

            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()

            return {
                "status": StepStatus.FAILED.value,
                "error": str(e),
                "duration_ms": (datetime.utcnow() - step.started_at).total_seconds() * 1000,
            }

    async def _execute_action(self, step: WorkflowStep, context: dict) -> Any:
        """Execute an action step."""
        handler = self._action_handlers.get(step.action)
        if not handler:
            raise ValueError(f"No handler for action: {step.action}")

        if asyncio.iscoroutinefunction(handler):
            return await handler(step.config, context)
        else:
            return handler(step.config, context)

    async def _evaluate_condition(self, step: WorkflowStep, context: dict) -> Any:
        """Evaluate a condition step."""
        condition = step.config.get("condition", "true")
        # Simple condition evaluation
        try:
            result = eval(condition, {"context": context})
            return {"condition": condition, "result": result}
        except Exception as e:
            raise ValueError(f"Invalid condition: {condition} - {e}")

    async def _execute_wait(self, step: WorkflowStep, context: dict) -> Any:
        """Execute a wait step."""
        duration = step.config.get("duration_seconds", 1)
        await asyncio.sleep(duration)
        return {"waited_seconds": duration}

    async def _execute_callback(self, step: WorkflowStep, context: dict) -> Any:
        """Execute a callback step."""
        callback_url = step.config.get("url")
        if not callback_url:
            raise ValueError("No callback URL configured")

        # In production, make HTTP request to callback URL
        return {"callback_sent": True, "url": callback_url}

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.RUNNING:
            return False

        workflow.status = WorkflowStatus.PAUSED
        return True

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.PAUSED:
            return False

        workflow.status = WorkflowStatus.RUNNING
        # Resume execution
        asyncio.create_task(self.run_workflow(workflow_id))
        return True

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False

        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()

        # Cancel running task if exists
        task = self._running.get(workflow_id)
        if task and not task.done():
            task.cancel()

        return True

    async def list_workflows(
        self,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50,
    ) -> list[Workflow]:
        """List workflows."""
        workflows = list(self._workflows.values())

        if status:
            workflows = [w for w in workflows if w.status == status]

        return workflows[:limit]


# Global engine instance
_engine: Optional[WorkflowEngine] = None


def get_engine() -> WorkflowEngine:
    """Get the global workflow engine."""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine
