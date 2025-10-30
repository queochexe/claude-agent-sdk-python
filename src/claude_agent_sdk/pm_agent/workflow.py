"""Project Manager workflow orchestrator."""

from ..types import ClaudeAgentOptions
from . import nodes
from .types import (
    DependencyList,
    ProjectPlan,
    RiskList,
    Schedule,
    TaskAllocationList,
    TaskList,
    Team,
)


class ProjectManager:
    """
    AI-powered project manager agent that generates comprehensive project plans.

    This agent automates project planning by:
    1. Extracting actionable tasks from project descriptions
    2. Mapping task dependencies and blocking relationships
    3. Creating optimized schedules that respect dependencies
    4. Allocating tasks to team members based on expertise
    5. Assessing risks for each task and the overall project
    6. Iteratively refining the plan to reduce risk

    Example:
        ```python
        import anyio
        from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember

        async def main():
            pm = ProjectManager()

            team = Team(members=[
                TeamMember(name="Alice", profile="Senior Backend Developer, Python/FastAPI expert"),
                TeamMember(name="Bob", profile="Frontend Developer, React/TypeScript specialist"),
                TeamMember(name="Carol", profile="DevOps Engineer, AWS/Docker experience"),
            ])

            plan = await pm.generate_plan(
                project_description="Build a 24/7 customer support chatbot with AI",
                team=team,
                max_iterations=3
            )

            print(f"Project Duration: {plan.schedule.get_project_duration()} days")
            print(f"Total Risk Score: {plan.risks.get_total_risk()}")
            print(f"Tasks: {len(plan.tasks.tasks)}")

        anyio.run(main)
        ```
    """

    def __init__(self, options: ClaudeAgentOptions | None = None):
        """
        Initialize the Project Manager agent.

        Args:
            options: Optional ClaudeAgentOptions to configure Claude behavior
                    (e.g., model selection, custom system prompts)
        """
        self.options = options

    async def generate_plan(
        self,
        project_description: str,
        team: Team,
        max_iterations: int = 3,
        verbose: bool = False,
    ) -> ProjectPlan:
        """
        Generate a comprehensive project plan from a project description.

        This method runs the complete workflow:
        1. Task extraction
        2. Dependency mapping
        3. Scheduling (with iterative optimization)
        4. Task allocation
        5. Risk assessment
        6. Insight generation and re-planning (if needed)

        Args:
            project_description: Detailed description of the project to plan
            team: Team object containing team members and their expertise
            max_iterations: Maximum number of optimization iterations (default: 3)
            verbose: If True, print progress updates during execution

        Returns:
            ProjectPlan: Complete project plan with tasks, schedule, allocations,
                        risks, and optimization insights

        Raises:
            WorkflowNodeError: If any workflow step fails
        """
        if verbose:
            print("🚀 Starting project planning workflow...")

        # Step 1: Extract tasks
        if verbose:
            print("📋 Extracting tasks from project description...")
        tasks = await nodes.task_generation_node(project_description, self.options)
        if verbose:
            print(f"   ✓ Extracted {len(tasks.tasks)} tasks")

        # Step 2: Map dependencies
        if verbose:
            print("🔗 Mapping task dependencies...")
        dependencies = await nodes.dependency_mapping_node(tasks, self.options)
        if verbose:
            print(
                f"   ✓ Mapped {len(dependencies.dependencies)} dependency relationships"
            )

        # Iterative optimization loop
        insights: list[str] = []
        risk_scores: list[int] = []
        schedule_history: list[Schedule] = []
        allocation_history: list[TaskAllocationList] = []
        risk_history: list[RiskList] = []

        for iteration in range(max_iterations):
            if verbose:
                print(f"\n🔄 Optimization iteration {iteration + 1}/{max_iterations}")

            # Step 3: Create schedule
            if verbose:
                print("   📅 Creating task schedule...")
            schedule = await nodes.scheduling_node(
                tasks, dependencies, insights if insights else None, self.options
            )
            schedule_history.append(schedule)
            if verbose:
                print(
                    f"      ✓ Scheduled {len(schedule.schedule)} tasks, duration: {schedule.get_project_duration()} days"
                )

            # Step 4: Allocate tasks
            if verbose:
                print("   👥 Allocating tasks to team members...")
            allocations = await nodes.allocation_node(
                tasks, schedule, team, self.options
            )
            allocation_history.append(allocations)
            if verbose:
                print(f"      ✓ Allocated {len(allocations.allocations)} tasks")

            # Step 5: Assess risks
            if verbose:
                print("   ⚠️  Assessing project risks...")
            risks = await nodes.risk_assessment_node(
                tasks, schedule, allocations, self.options
            )
            risk_history.append(risks)
            current_risk = risks.get_total_risk()
            risk_scores.append(current_risk)
            if verbose:
                print(f"      ✓ Total risk score: {current_risk}")

            # Check if we should continue optimizing
            if len(risk_scores) > 1:
                previous_risk = risk_scores[-2]
                improvement = previous_risk - current_risk

                if verbose:
                    if improvement > 0:
                        print(
                            f"      ✅ Risk improved by {improvement} points ({previous_risk} → {current_risk})"
                        )
                    else:
                        print(
                            f"      ℹ️  Risk did not improve ({previous_risk} → {current_risk})"
                        )

                # Stop if risk decreased (plan improved)
                if improvement > 0:
                    if verbose:
                        print("\n✅ Plan optimized successfully!")
                    break

            # Generate insights for next iteration (if not last iteration)
            if iteration < max_iterations - 1:
                if verbose:
                    print("   💡 Generating optimization insights...")
                new_insights = await nodes.insights_generation_node(
                    schedule, allocations, risks, self.options
                )
                insights.extend(new_insights)
                if verbose:
                    print(f"      ✓ Generated {len(new_insights)} insights")
                    for insight in new_insights:
                        print(f"        - {insight}")

        if verbose:
            print("\n🎉 Project planning complete!")
            print(f"   Total tasks: {len(tasks.tasks)}")
            print(f"   Project duration: {schedule.get_project_duration()} days")
            print(f"   Final risk score: {risks.get_total_risk()}")
            print(f"   Optimization iterations: {len(risk_scores)}")

        # Return the final plan
        return ProjectPlan(
            tasks=tasks,
            dependencies=dependencies,
            schedule=schedule,
            allocations=allocations,
            risks=risks,
            insights=insights,
            iterations=len(risk_scores),
        )

    async def extract_tasks(self, project_description: str) -> TaskList:
        """
        Extract tasks from a project description (standalone operation).

        Args:
            project_description: Project description to analyze

        Returns:
            TaskList: List of extracted tasks
        """
        return await nodes.task_generation_node(project_description, self.options)

    async def map_dependencies(self, tasks: TaskList) -> DependencyList:
        """
        Map dependencies between tasks (standalone operation).

        Args:
            tasks: List of tasks to analyze

        Returns:
            DependencyList: List of task dependencies
        """
        return await nodes.dependency_mapping_node(tasks, self.options)

    async def create_schedule(
        self, tasks: TaskList, dependencies: DependencyList
    ) -> Schedule:
        """
        Create a schedule for tasks (standalone operation).

        Args:
            tasks: List of tasks
            dependencies: Task dependencies

        Returns:
            Schedule: Task schedule
        """
        return await nodes.scheduling_node(tasks, dependencies, None, self.options)
