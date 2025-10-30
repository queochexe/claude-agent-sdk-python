"""Integration tests for Project Manager Agent with mocked Claude responses."""

from unittest.mock import patch

import pytest

from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember
from claude_agent_sdk.pm_agent.nodes import WorkflowNodeError


@pytest.fixture
def sample_team():
    """Create a sample team for testing."""
    return Team(
        members=[
            TeamMember(name="Alice", profile="Backend Developer"),
            TeamMember(name="Bob", profile="Frontend Developer"),
        ]
    )


@pytest.fixture
def mock_task_response():
    """Mock response for task generation."""
    return """
    {
      "tasks": [
        {
          "task_name": "Setup Database",
          "task_description": "Initialize PostgreSQL database",
          "estimated_days": 2
        },
        {
          "task_name": "Create API",
          "task_description": "Build REST API endpoints",
          "estimated_days": 5
        }
      ]
    }
    """


@pytest.fixture
def mock_dependency_response():
    """Mock response for dependency mapping."""

    def create_response(tasks):
        task_ids = [t["id"] for t in tasks]
        return f"""
        {{
          "dependencies": [
            {{
              "task_id": "{task_ids[0]}",
              "dependent_task_ids": []
            }},
            {{
              "task_id": "{task_ids[1]}",
              "dependent_task_ids": ["{task_ids[0]}"]
            }}
          ]
        }}
        """

    return create_response


@pytest.fixture
def mock_schedule_response():
    """Mock response for scheduling."""

    def create_response(tasks):
        task_ids = [t["id"] for t in tasks]
        return f"""
        {{
          "schedule": [
            {{
              "task_id": "{task_ids[0]}",
              "start_day": 0,
              "end_day": 2
            }},
            {{
              "task_id": "{task_ids[1]}",
              "start_day": 2,
              "end_day": 7
            }}
          ]
        }}
        """

    return create_response


@pytest.fixture
def mock_allocation_response():
    """Mock response for task allocation."""

    def create_response(tasks):
        task_ids = [t["id"] for t in tasks]
        return f"""
        {{
          "allocations": [
            {{
              "task_id": "{task_ids[0]}",
              "team_member_name": "Alice"
            }},
            {{
              "task_id": "{task_ids[1]}",
              "team_member_name": "Bob"
            }}
          ]
        }}
        """

    return create_response


@pytest.fixture
def mock_risk_response():
    """Mock response for risk assessment."""

    def create_response(tasks):
        task_ids = [t["id"] for t in tasks]
        return f"""
        {{
          "risks": [
            {{
              "task_id": "{task_ids[0]}",
              "risk_score": 3,
              "risk_description": "Low risk - standard database setup"
            }},
            {{
              "task_id": "{task_ids[1]}",
              "risk_score": 5,
              "risk_description": "Medium risk - complex API design"
            }}
          ]
        }}
        """

    return create_response


@pytest.fixture
def mock_insights_response():
    """Mock response for insights generation."""
    return """
    {
      "insights": [
        "Consider parallelizing independent tasks",
        "Add buffer time for high-risk tasks"
      ]
    }
    """


class TestIntegrationWithMocking:
    """Integration tests using mocked Claude responses."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_mocking(
        self,
        sample_team,
        mock_task_response,
        mock_dependency_response,
        mock_schedule_response,
        mock_allocation_response,
        mock_risk_response,
        mock_insights_response,
    ):
        """Test complete workflow with mocked responses."""
        pm = ProjectManager()

        # Track which stage we're in to return appropriate mocks
        call_count = [0]
        task_list = None

        async def mock_call_claude(prompt, options=None):
            """Mock the call_claude function."""
            nonlocal task_list
            call_count[0] += 1

            # Task generation
            if "Extract all actionable tasks" in prompt:
                return mock_task_response

            # Dependency mapping
            elif "identify which other tasks must be completed" in prompt:
                # Parse tasks from previous response to get IDs

                from claude_agent_sdk.pm_agent.nodes import extract_json_from_response

                if task_list is None:
                    data = extract_json_from_response(mock_task_response)
                    from claude_agent_sdk.pm_agent.types import TaskList

                    task_list = TaskList(**data)
                return mock_dependency_response(
                    [t.model_dump() for t in task_list.tasks]
                )

            # Scheduling
            elif "Create a schedule" in prompt:
                return mock_schedule_response([t.model_dump() for t in task_list.tasks])

            # Allocation
            elif "Allocate each task to the most suitable" in prompt:
                return mock_allocation_response(
                    [t.model_dump() for t in task_list.tasks]
                )

            # Risk assessment
            elif "Assess the risk for each task" in prompt:
                return mock_risk_response([t.model_dump() for t in task_list.tasks])

            # Insights
            elif "generate 3-5 actionable insights" in prompt:
                return mock_insights_response

            else:
                raise ValueError(f"Unexpected prompt: {prompt[:100]}")

        # Patch the call_claude function
        with patch(
            "claude_agent_sdk.pm_agent.nodes.call_claude",
            side_effect=mock_call_claude,
        ):
            plan = await pm.generate_plan(
                project_description="Build a simple web app",
                team=sample_team,
                max_iterations=1,
                verbose=False,
            )

        # Verify the plan structure
        assert len(plan.tasks.tasks) == 2
        assert plan.tasks.tasks[0].task_name == "Setup Database"
        assert plan.tasks.tasks[1].task_name == "Create API"

        # Verify dependencies
        assert len(plan.dependencies.dependencies) == 2

        # Verify schedule
        assert len(plan.schedule.schedule) == 2
        assert plan.schedule.get_project_duration() == 7

        # Verify allocations
        assert len(plan.allocations.allocations) == 2

        # Verify risks
        assert len(plan.risks.risks) == 2
        assert plan.risks.get_total_risk() == 8

        # Verify at least 5 calls were made (task + dep + schedule + allocate + risk)
        assert call_count[0] >= 5

    @pytest.mark.asyncio
    async def test_error_handling_invalid_json(self, sample_team):
        """Test error handling when Claude returns invalid JSON."""
        pm = ProjectManager()

        async def mock_call_claude_invalid(prompt, options=None):
            """Return invalid JSON."""
            return "This is not JSON at all!"

        with (
            patch(
                "claude_agent_sdk.pm_agent.nodes.call_claude",
                side_effect=mock_call_claude_invalid,
            ),
            pytest.raises(WorkflowNodeError, match="No valid JSON found"),
        ):
            await pm.extract_tasks("Build an app")

    @pytest.mark.asyncio
    async def test_error_handling_malformed_json(self, sample_team):
        """Test error handling with malformed JSON."""
        pm = ProjectManager()

        async def mock_call_claude_malformed(prompt, options=None):
            """Return malformed JSON."""
            return '{"tasks": [{"task_name": "Test", missing closing brace'

        with (
            patch(
                "claude_agent_sdk.pm_agent.nodes.call_claude",
                side_effect=mock_call_claude_malformed,
            ),
            pytest.raises(WorkflowNodeError, match="No valid JSON found"),
        ):
            await pm.extract_tasks("Build an app")

    @pytest.mark.asyncio
    async def test_iterative_optimization_stops_on_improvement(
        self,
        sample_team,
        mock_task_response,
        mock_dependency_response,
        mock_schedule_response,
        mock_allocation_response,
    ):
        """Test that optimization stops when risk improves."""
        pm = ProjectManager()

        call_count = [0]
        task_list = None

        async def mock_call_claude_improving(prompt, options=None):
            """Mock with improving risk scores."""
            nonlocal task_list
            call_count[0] += 1

            if "Extract all actionable tasks" in prompt:
                return mock_task_response
            elif "identify which other tasks must be completed" in prompt:
                from claude_agent_sdk.pm_agent.nodes import extract_json_from_response

                if task_list is None:
                    data = extract_json_from_response(mock_task_response)
                    from claude_agent_sdk.pm_agent.types import TaskList

                    task_list = TaskList(**data)
                return mock_dependency_response(
                    [t.model_dump() for t in task_list.tasks]
                )
            elif "Create a schedule" in prompt:
                return mock_schedule_response([t.model_dump() for t in task_list.tasks])
            elif "Allocate each task" in prompt:
                return mock_allocation_response(
                    [t.model_dump() for t in task_list.tasks]
                )
            elif "Assess the risk" in prompt:
                # Return decreasing risk scores
                task_ids = [t.id for t in task_list.tasks]
                iteration = (call_count[0] - 3) // 3  # Rough iteration count
                risk1 = max(8 - iteration * 2, 1)
                risk2 = max(6 - iteration * 2, 1)
                return f"""
                {{
                  "risks": [
                    {{"task_id": "{task_ids[0]}", "risk_score": {risk1}, "risk_description": "Risk"}},
                    {{"task_id": "{task_ids[1]}", "risk_score": {risk2}, "risk_description": "Risk"}}
                  ]
                }}
                """
            elif "generate 3-5 actionable insights" in prompt:
                return '{"insights": ["Improve scheduling"]}'
            else:
                return "{}"

        with patch(
            "claude_agent_sdk.pm_agent.nodes.call_claude",
            side_effect=mock_call_claude_improving,
        ):
            plan = await pm.generate_plan(
                project_description="Build an app",
                team=sample_team,
                max_iterations=5,  # Allow many iterations
                verbose=False,
            )

        # Should stop early due to improvement
        assert plan.iterations < 5
        assert plan.iterations >= 1


class TestStandaloneOperations:
    """Test individual operations with mocking."""

    @pytest.mark.asyncio
    async def test_extract_tasks_only(self, mock_task_response):
        """Test task extraction in isolation."""
        pm = ProjectManager()

        async def mock_call_claude(prompt, options=None):
            return mock_task_response

        with patch(
            "claude_agent_sdk.pm_agent.nodes.call_claude",
            side_effect=mock_call_claude,
        ):
            tasks = await pm.extract_tasks("Build a simple app")

        assert len(tasks.tasks) == 2
        assert tasks.tasks[0].task_name == "Setup Database"
        assert tasks.tasks[0].estimated_days == 2

    @pytest.mark.asyncio
    async def test_map_dependencies_only(
        self, mock_task_response, mock_dependency_response
    ):
        """Test dependency mapping in isolation."""
        pm = ProjectManager()

        # First extract tasks
        async def mock_call_claude_tasks(prompt, options=None):
            return mock_task_response

        with patch(
            "claude_agent_sdk.pm_agent.nodes.call_claude",
            side_effect=mock_call_claude_tasks,
        ):
            tasks = await pm.extract_tasks("Build an app")

        # Then map dependencies
        async def mock_call_claude_deps(prompt, options=None):
            return mock_dependency_response([t.model_dump() for t in tasks.tasks])

        with patch(
            "claude_agent_sdk.pm_agent.nodes.call_claude",
            side_effect=mock_call_claude_deps,
        ):
            dependencies = await pm.map_dependencies(tasks)

        assert len(dependencies.dependencies) == 2
        # Second task depends on first
        assert len(dependencies.dependencies[1].dependent_task_ids) == 1
