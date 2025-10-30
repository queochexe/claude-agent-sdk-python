"""Prompt templates for Project Manager Agent workflow."""

from typing import Any


def task_generation_prompt(project_description: str) -> str:
    """Generate prompt for extracting tasks from project description."""
    return f"""You are a project manager analyzing a project description to extract actionable tasks.

Project Description:
{project_description}

Extract all actionable tasks from this project. For each task:
1. Create a clear, specific task name
2. Write a detailed description of what needs to be done
3. Estimate the number of days needed (be realistic)
4. Break down any task that would take more than 5 days into smaller subtasks

Return your response as a JSON object with this exact structure:
{{
  "tasks": [
    {{
      "task_name": "Task name here",
      "task_description": "Detailed description here",
      "estimated_days": 3
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""


def dependency_mapping_prompt(tasks: list[dict[str, Any]]) -> str:
    """Generate prompt for identifying task dependencies."""
    tasks_str = "\n".join(
        [
            f"- ID: {t['id']}, Name: {t['task_name']}, Description: {t['task_description']}"
            for t in tasks
        ]
    )

    return f"""You are a project manager identifying task dependencies and blocking relationships.

Tasks:
{tasks_str}

For each task, identify which other tasks must be completed before it can start (dependencies/blockers).
Consider:
- Technical dependencies (e.g., backend API must exist before frontend can integrate)
- Logical sequence (e.g., planning before implementation)
- Resource dependencies

Return your response as a JSON object with this exact structure:
{{
  "dependencies": [
    {{
      "task_id": "task-uuid-here",
      "dependent_task_ids": ["uuid-of-task-that-must-complete-first", "another-uuid"]
    }}
  ]
}}

If a task has no dependencies, use an empty list for dependent_task_ids.

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""


def scheduling_prompt(
    tasks: list[dict[str, Any]],
    dependencies: list[dict[str, Any]],
    insights: list[str] | None = None,
) -> str:
    """Generate prompt for creating task schedules."""
    tasks_str = "\n".join(
        [
            f"- ID: {t['id']}, Name: {t['task_name']}, Estimated days: {t['estimated_days']}"
            for t in tasks
        ]
    )

    deps_str = "\n".join(
        [
            f"- Task {d['task_id']} depends on: {', '.join(d['dependent_task_ids']) if d['dependent_task_ids'] else 'None'}"
            for d in dependencies
        ]
    )

    insights_section = ""
    if insights:
        insights_section = f"""
Previous Optimization Insights:
{chr(10).join(f"- {insight}" for insight in insights)}

Apply these insights to improve the schedule.
"""

    return f"""You are a project manager creating an optimized project schedule.

Tasks:
{tasks_str}

Dependencies:
{deps_str}
{insights_section}

Create a schedule that:
1. Respects all task dependencies (dependent tasks must complete before blocked tasks start)
2. Parallelizes independent tasks when possible
3. Accounts for the estimated days for each task
4. Minimizes overall project duration

For each task, specify start_day and end_day where:
- Day 0 is the project start
- end_day = start_day + estimated_days
- Tasks with no dependencies can start on day 0
- Tasks with dependencies must start after all dependent tasks complete

Return your response as a JSON object with this exact structure:
{{
  "schedule": [
    {{
      "task_id": "task-uuid-here",
      "start_day": 0,
      "end_day": 3
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""


def allocation_prompt(
    tasks: list[dict[str, Any]],
    schedule: list[dict[str, Any]],
    team: list[dict[str, str]],
) -> str:
    """Generate prompt for allocating tasks to team members."""
    tasks_str = "\n".join(
        [
            f"- ID: {t['id']}, Name: {t['task_name']}, Description: {t['task_description']}"
            for t in tasks
        ]
    )

    schedule_str = "\n".join(
        [
            f"- Task {s['task_id']}: days {s['start_day']}-{s['end_day']}"
            for s in schedule
        ]
    )

    team_str = "\n".join([f"- {m['name']}: {m['profile']}" for m in team])

    return f"""You are a project manager assigning tasks to team members based on their expertise.

Tasks:
{tasks_str}

Schedule:
{schedule_str}

Team Members:
{team_str}

Allocate each task to the most suitable team member considering:
1. Match task requirements to team member expertise
2. Balance workload across team members
3. Consider task timing (overlapping tasks need different people)
4. Leverage specialized skills appropriately

Return your response as a JSON object with this exact structure:
{{
  "allocations": [
    {{
      "task_id": "task-uuid-here",
      "team_member_name": "Team member name here"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""


def risk_assessment_prompt(
    tasks: list[dict[str, Any]],
    schedule: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
) -> str:
    """Generate prompt for assessing project risks."""
    tasks_str = "\n".join(
        [
            f"- ID: {t['id']}, Name: {t['task_name']}, Description: {t['task_description']}"
            for t in tasks
        ]
    )

    schedule_str = "\n".join(
        [
            f"- Task {s['task_id']}: days {s['start_day']}-{s['end_day']}"
            for s in schedule
        ]
    )

    allocations_str = "\n".join(
        [
            f"- Task {a['task_id']}: assigned to {a['team_member_name']}"
            for a in allocations
        ]
    )

    return f"""You are a project manager assessing risks for each task in the project.

Tasks:
{tasks_str}

Schedule:
{schedule_str}

Task Allocations:
{allocations_str}

Assess the risk for each task considering:
1. Task complexity and uncertainty
2. Resource availability and skill match
3. Dependencies and potential bottlenecks
4. Timeline constraints
5. Technical challenges

For each task, assign a risk score from 0 (no risk) to 10 (critical risk).

Return your response as a JSON object with this exact structure:
{{
  "risks": [
    {{
      "task_id": "task-uuid-here",
      "risk_score": 5,
      "risk_description": "Brief description of the risk factors"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""


def insights_generation_prompt(
    schedule: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    risks: list[dict[str, Any]],
) -> str:
    """Generate prompt for creating optimization insights."""
    schedule_str = "\n".join(
        [
            f"- Task {s['task_id']}: days {s['start_day']}-{s['end_day']}"
            for s in schedule
        ]
    )

    allocations_str = "\n".join(
        [
            f"- Task {a['task_id']}: assigned to {a['team_member_name']}"
            for a in allocations
        ]
    )

    risks_str = "\n".join(
        [
            f"- Task {r['task_id']}: Risk {r['risk_score']}/10 - {r['risk_description']}"
            for r in risks
        ]
    )

    total_risk = sum(r["risk_score"] for r in risks)

    return f"""You are a project manager analyzing the current project plan to generate improvement insights.

Current Schedule:
{schedule_str}

Current Task Allocations:
{allocations_str}

Current Risks (Total Risk Score: {total_risk}):
{risks_str}

Analyze the current plan and generate 3-5 actionable insights to reduce risk and improve the schedule:
1. Identify high-risk tasks that need attention
2. Suggest schedule optimizations (parallelization, reordering)
3. Recommend workload rebalancing
4. Highlight resource constraints or bottlenecks
5. Propose risk mitigation strategies

Return your response as a JSON object with this exact structure:
{{
  "insights": [
    "Specific actionable insight 1",
    "Specific actionable insight 2",
    "Specific actionable insight 3"
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""
