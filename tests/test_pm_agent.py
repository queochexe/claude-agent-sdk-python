"""Tests for Project Manager Agent."""

from claude_agent_sdk.pm_agent import (
    ProjectManager,
    Risk,
    RiskList,
    Schedule,
    Task,
    TaskDependency,
    TaskList,
    TaskSchedule,
    Team,
    TeamMember,
)
from claude_agent_sdk.pm_agent.nodes import extract_json_from_response


class TestPMAgentTypes:
    """Test PM Agent data types."""

    def test_task_creation(self):
        """Test Task model creation."""
        task = Task(
            task_name="Setup database",
            task_description="Initialize PostgreSQL database",
            estimated_days=2,
        )
        assert task.task_name == "Setup database"
        assert task.estimated_days == 2
        assert task.id  # Should have auto-generated UUID

    def test_task_list(self):
        """Test TaskList container."""
        tasks = TaskList(
            tasks=[
                Task(
                    task_name="Task 1",
                    task_description="Description 1",
                    estimated_days=1,
                ),
                Task(
                    task_name="Task 2",
                    task_description="Description 2",
                    estimated_days=2,
                ),
            ]
        )
        assert len(tasks.tasks) == 2

    def test_team_member(self):
        """Test TeamMember model."""
        member = TeamMember(name="Alice", profile="Senior Developer")
        assert str(member) == "Alice - Senior Developer"

    def test_team(self):
        """Test Team container."""
        team = Team(
            members=[
                TeamMember(name="Alice", profile="Backend"),
                TeamMember(name="Bob", profile="Frontend"),
            ]
        )
        assert len(team.members) == 2

    def test_task_dependency(self):
        """Test TaskDependency model."""
        dep = TaskDependency(task_id="task-1", dependent_task_ids=["task-2", "task-3"])
        assert dep.task_id == "task-1"
        assert len(dep.dependent_task_ids) == 2

    def test_schedule(self):
        """Test Schedule and project duration calculation."""
        schedule = Schedule(
            schedule=[
                TaskSchedule(task_id="task-1", start_day=0, end_day=3),
                TaskSchedule(task_id="task-2", start_day=3, end_day=7),
            ]
        )
        assert schedule.get_project_duration() == 7

    def test_risk_list(self):
        """Test RiskList and total risk calculation."""
        risks = RiskList(
            risks=[
                Risk(task_id="task-1", risk_score=5, risk_description="Medium risk"),
                Risk(task_id="task-2", risk_score=8, risk_description="High risk"),
            ]
        )
        assert risks.get_total_risk() == 13


class TestJSONExtraction:
    """Test JSON extraction from Claude responses."""

    def test_extract_plain_json(self):
        """Test extracting plain JSON."""
        response = '{"tasks": [{"name": "Task 1"}]}'
        result = extract_json_from_response(response)
        assert result == {"tasks": [{"name": "Task 1"}]}

    def test_extract_json_with_markdown(self):
        """Test extracting JSON from markdown code blocks."""
        response = """
        Here's the result:
        ```json
        {"tasks": [{"name": "Task 1"}]}
        ```
        """
        result = extract_json_from_response(response)
        assert result == {"tasks": [{"name": "Task 1"}]}

    def test_extract_json_with_extra_text(self):
        """Test extracting JSON with extra text around it."""
        response = 'Some text before {"tasks": [{"name": "Task 1"}]} some text after'
        result = extract_json_from_response(response)
        assert result == {"tasks": [{"name": "Task 1"}]}

    def test_extract_json_with_code_block_no_lang(self):
        """Test extracting JSON from code block without language."""
        response = """
        ```
        {"tasks": [{"name": "Task 1"}]}
        ```
        """
        result = extract_json_from_response(response)
        assert result == {"tasks": [{"name": "Task 1"}]}


class TestPromptGeneration:
    """Test prompt generation functions."""

    def test_task_generation_prompt(self):
        """Test task generation prompt creation."""
        from claude_agent_sdk.pm_agent.prompts import task_generation_prompt

        prompt = task_generation_prompt("Build a web app")
        assert "Build a web app" in prompt
        assert "JSON" in prompt
        assert "task_name" in prompt

    def test_dependency_mapping_prompt(self):
        """Test dependency mapping prompt creation."""
        from claude_agent_sdk.pm_agent.prompts import dependency_mapping_prompt

        tasks = [
            {
                "id": "1",
                "task_name": "Setup DB",
                "task_description": "Initialize database",
            }
        ]
        prompt = dependency_mapping_prompt(tasks)
        assert "Setup DB" in prompt
        assert "dependencies" in prompt

    def test_scheduling_prompt(self):
        """Test scheduling prompt creation."""
        from claude_agent_sdk.pm_agent.prompts import scheduling_prompt

        tasks = [{"id": "1", "task_name": "Task 1", "estimated_days": 3}]
        deps = [{"task_id": "1", "dependent_task_ids": []}]
        prompt = scheduling_prompt(tasks, deps)
        assert "Task 1" in prompt
        assert "schedule" in prompt

    def test_scheduling_prompt_with_insights(self):
        """Test scheduling prompt with optimization insights."""
        from claude_agent_sdk.pm_agent.prompts import scheduling_prompt

        tasks = [{"id": "1", "task_name": "Task 1", "estimated_days": 3}]
        deps = [{"task_id": "1", "dependent_task_ids": []}]
        insights = ["Parallelize independent tasks", "Reduce critical path"]
        prompt = scheduling_prompt(tasks, deps, insights)
        assert "Parallelize independent tasks" in prompt
        assert "Previous Optimization Insights" in prompt


class TestProjectManager:
    """Test ProjectManager class."""

    def test_project_manager_init(self):
        """Test ProjectManager initialization."""
        pm = ProjectManager()
        assert pm.options is None

    def test_project_manager_init_with_options(self):
        """Test ProjectManager initialization with options."""
        from claude_agent_sdk import ClaudeAgentOptions

        options = ClaudeAgentOptions(model="claude-opus-4")
        pm = ProjectManager(options=options)
        assert pm.options == options


# Integration tests that actually call Claude would go here
# but are commented out to avoid requiring API credentials in tests

"""
@pytest.mark.asyncio
async def test_full_workflow_integration():
    # This would test the full workflow end-to-end
    # Requires Claude API access
    pm = ProjectManager()
    team = Team(members=[
        TeamMember(name="Alice", profile="Backend Developer"),
    ])

    plan = await pm.generate_plan(
        project_description="Simple test project",
        team=team,
        max_iterations=1
    )

    assert len(plan.tasks.tasks) > 0
    assert plan.schedule.get_project_duration() > 0
"""
