"""Type definitions for Project Manager Agent."""

import uuid
from typing import Any

from pydantic import BaseModel, Field


class Task(BaseModel):
    """Represents a single project task."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str
    task_description: str
    estimated_days: int = Field(ge=1, description="Estimated days to complete task")

    def __str__(self) -> str:
        """String representation of task."""
        return f"{self.task_name} ({self.estimated_days}d): {self.task_description}"


class TaskList(BaseModel):
    """Container for multiple tasks."""

    tasks: list[Task]


class TaskDependency(BaseModel):
    """Represents task dependencies (blocking relationships)."""

    task_id: str = Field(description="ID of the task")
    dependent_task_ids: list[str] = Field(
        default_factory=list,
        description="IDs of tasks that must complete before this task",
    )


class DependencyList(BaseModel):
    """Container for task dependencies."""

    dependencies: list[TaskDependency]


class TeamMember(BaseModel):
    """Represents a team member with their skills/profile."""

    name: str
    profile: str = Field(description="Skills, expertise, and experience")

    def __str__(self) -> str:
        """String representation of team member."""
        return f"{self.name} - {self.profile}"


class Team(BaseModel):
    """Container for team members."""

    members: list[TeamMember]


class TaskSchedule(BaseModel):
    """Represents when a task should be executed."""

    task_id: str
    start_day: int = Field(ge=0, description="Project day when task starts")
    end_day: int = Field(ge=1, description="Project day when task ends")


class Schedule(BaseModel):
    """Container for task schedules."""

    schedule: list[TaskSchedule]

    def get_project_duration(self) -> int:
        """Calculate total project duration in days."""
        if not self.schedule:
            return 0
        return max(s.end_day for s in self.schedule)


class TaskAllocation(BaseModel):
    """Represents assignment of a task to a team member."""

    task_id: str
    team_member_name: str


class TaskAllocationList(BaseModel):
    """Container for task allocations."""

    allocations: list[TaskAllocation]


class Risk(BaseModel):
    """Represents risk assessment for a task."""

    task_id: str
    risk_score: int = Field(
        ge=0, le=10, description="Risk score from 0 (low) to 10 (high)"
    )
    risk_description: str = Field(description="Description of the risk")


class RiskList(BaseModel):
    """Container for risk assessments."""

    risks: list[Risk]

    def get_total_risk(self) -> int:
        """Calculate total project risk score."""
        return sum(r.risk_score for r in self.risks)


class ProjectPlan(BaseModel):
    """Complete project plan with all components."""

    tasks: TaskList
    dependencies: DependencyList
    schedule: Schedule
    allocations: TaskAllocationList
    risks: RiskList
    insights: list[str] = Field(default_factory=list)
    iterations: int = Field(default=1, description="Number of optimization iterations")

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the project plan."""
        return {
            "total_tasks": len(self.tasks.tasks),
            "total_risk_score": self.risks.get_total_risk(),
            "project_duration_days": self.schedule.get_project_duration(),
            "team_size": len(
                {a.team_member_name for a in self.allocations.allocations}
            ),
            "optimization_iterations": self.iterations,
        }
