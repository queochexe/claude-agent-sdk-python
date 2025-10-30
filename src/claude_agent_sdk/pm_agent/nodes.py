"""Workflow nodes for Project Manager Agent."""

import json
import re
from typing import Any

from ..query import query as claude_query
from ..types import AssistantMessage, ClaudeAgentOptions, TextBlock
from . import prompts
from .types import (
    DependencyList,
    RiskList,
    Schedule,
    TaskAllocationList,
    TaskList,
    Team,
)


class WorkflowNodeError(Exception):
    """Exception raised when a workflow node fails."""

    pass


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract JSON from Claude's response, handling markdown code blocks."""
    # Try to find JSON in markdown code blocks first
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    # Clean up the text
    text = text.strip()

    # Find the first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise WorkflowNodeError(f"No valid JSON found in response: {text[:200]}")

    json_str = text[start : end + 1]

    try:
        return json.loads(json_str)  # type: ignore[no-any-return]
    except json.JSONDecodeError as e:
        raise WorkflowNodeError(
            f"Failed to parse JSON: {e}\nText: {json_str[:200]}"
        ) from e


async def call_claude(prompt: str, options: ClaudeAgentOptions | None = None) -> str:
    """Call Claude and extract text response."""
    if options is None:
        options = ClaudeAgentOptions()

    response_text = ""

    async for message in claude_query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text

    if not response_text:
        raise WorkflowNodeError("No response received from Claude")

    return response_text


async def task_generation_node(
    project_description: str, options: ClaudeAgentOptions | None = None
) -> TaskList:
    """Extract tasks from project description."""
    prompt = prompts.task_generation_prompt(project_description)
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return TaskList(**data)
    except Exception as e:
        raise WorkflowNodeError(f"Task generation failed: {e}") from e


async def dependency_mapping_node(
    tasks: TaskList, options: ClaudeAgentOptions | None = None
) -> DependencyList:
    """Map dependencies between tasks."""
    tasks_dict = [task.model_dump() for task in tasks.tasks]
    prompt = prompts.dependency_mapping_prompt(tasks_dict)
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return DependencyList(**data)
    except Exception as e:
        raise WorkflowNodeError(f"Dependency mapping failed: {e}") from e


async def scheduling_node(
    tasks: TaskList,
    dependencies: DependencyList,
    insights: list[str] | None = None,
    options: ClaudeAgentOptions | None = None,
) -> Schedule:
    """Create task schedule respecting dependencies."""
    tasks_dict = [task.model_dump() for task in tasks.tasks]
    deps_dict = [dep.model_dump() for dep in dependencies.dependencies]
    prompt = prompts.scheduling_prompt(tasks_dict, deps_dict, insights)
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return Schedule(**data)
    except Exception as e:
        raise WorkflowNodeError(f"Scheduling failed: {e}") from e


async def allocation_node(
    tasks: TaskList,
    schedule: Schedule,
    team: Team,
    options: ClaudeAgentOptions | None = None,
) -> TaskAllocationList:
    """Allocate tasks to team members."""
    tasks_dict = [task.model_dump() for task in tasks.tasks]
    schedule_dict = [s.model_dump() for s in schedule.schedule]
    team_dict = [member.model_dump() for member in team.members]
    prompt = prompts.allocation_prompt(tasks_dict, schedule_dict, team_dict)
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return TaskAllocationList(**data)
    except Exception as e:
        raise WorkflowNodeError(f"Task allocation failed: {e}") from e


async def risk_assessment_node(
    tasks: TaskList,
    schedule: Schedule,
    allocations: TaskAllocationList,
    options: ClaudeAgentOptions | None = None,
) -> RiskList:
    """Assess risks for each task."""
    tasks_dict = [task.model_dump() for task in tasks.tasks]
    schedule_dict = [s.model_dump() for s in schedule.schedule]
    allocations_dict = [a.model_dump() for a in allocations.allocations]
    prompt = prompts.risk_assessment_prompt(tasks_dict, schedule_dict, allocations_dict)
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return RiskList(**data)
    except Exception as e:
        raise WorkflowNodeError(f"Risk assessment failed: {e}") from e


async def insights_generation_node(
    schedule: Schedule,
    allocations: TaskAllocationList,
    risks: RiskList,
    options: ClaudeAgentOptions | None = None,
) -> list[str]:
    """Generate insights for optimization."""
    schedule_dict = [s.model_dump() for s in schedule.schedule]
    allocations_dict = [a.model_dump() for a in allocations.allocations]
    risks_dict = [r.model_dump() for r in risks.risks]
    prompt = prompts.insights_generation_prompt(
        schedule_dict, allocations_dict, risks_dict
    )
    response = await call_claude(prompt, options)

    try:
        data = extract_json_from_response(response)
        return data.get("insights", [])  # type: ignore[no-any-return]
    except Exception as e:
        raise WorkflowNodeError(f"Insights generation failed: {e}") from e
