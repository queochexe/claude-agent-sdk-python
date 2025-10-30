"""
Project Manager Agent for Claude SDK.

This module provides an AI-powered project management agent that can:
- Extract actionable tasks from project descriptions
- Map task dependencies and blocking relationships
- Create optimized project schedules
- Allocate tasks to team members based on expertise
- Assess risks and iteratively refine plans

Based on the GenAI_Agents project manager implementation by NirDiamant:
https://github.com/NirDiamant/GenAI_Agents

Example Usage:
    ```python
    import anyio
    from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember

    async def main():
        pm = ProjectManager()

        team = Team(members=[
            TeamMember(
                name="Alice",
                profile="Senior Backend Developer with 5 years Python/FastAPI experience"
            ),
            TeamMember(
                name="Bob",
                profile="Frontend Developer specializing in React and TypeScript"
            ),
            TeamMember(
                name="Carol",
                profile="DevOps Engineer with AWS, Docker, and Kubernetes expertise"
            ),
        ])

        plan = await pm.generate_plan(
            project_description=\"\"\"
            Build a 24/7 customer support chatbot with AI capabilities.
            The system should handle common queries, escalate complex issues,
            integrate with our CRM, and provide analytics dashboard.
            \"\"\",
            team=team,
            max_iterations=3,
            verbose=True
        )

        # Access plan components
        print(f"Tasks: {len(plan.tasks.tasks)}")
        print(f"Duration: {plan.schedule.get_project_duration()} days")
        print(f"Risk Score: {plan.risks.get_total_risk()}")

        # Inspect individual tasks
        for task in plan.tasks.tasks:
            print(f"- {task.task_name} ({task.estimated_days} days)")

    anyio.run(main)
    ```
"""

from .types import (
    DependencyList,
    ProjectPlan,
    Risk,
    RiskList,
    Schedule,
    Task,
    TaskAllocation,
    TaskAllocationList,
    TaskDependency,
    TaskList,
    TaskSchedule,
    Team,
    TeamMember,
)
from .workflow import ProjectManager

__all__ = [
    "ProjectManager",
    "Team",
    "TeamMember",
    "Task",
    "TaskList",
    "TaskDependency",
    "DependencyList",
    "TaskSchedule",
    "Schedule",
    "TaskAllocation",
    "TaskAllocationList",
    "Risk",
    "RiskList",
    "ProjectPlan",
]
