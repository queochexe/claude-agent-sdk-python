# Project Manager Agent

An AI-powered project management agent for the Claude SDK that automates comprehensive project planning.

Based on the [GenAI_Agents repository](https://github.com/NirDiamant/GenAI_Agents) by NirDiamant (11.2k+ stars).

## Features

- 📋 **Task Extraction** - Automatically breaks down project descriptions into actionable tasks
- 🔗 **Dependency Mapping** - Identifies task relationships and blocking dependencies
- 📅 **Optimized Scheduling** - Creates timelines that respect dependencies and parallelize independent tasks
- 👥 **Team Allocation** - Assigns tasks to team members based on their expertise
- ⚠️ **Risk Assessment** - Evaluates and scores risks for each task and the overall project
- 🔄 **Iterative Optimization** - Self-reflects and refines the plan to minimize project risk

## Installation

The PM Agent is included with the Claude SDK. Just install the SDK with:

```bash
pip install claude-agent-sdk
```

Or if you're developing locally:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import anyio
from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember

async def main():
    # Initialize the Project Manager
    pm = ProjectManager()

    # Define your team
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

    # Generate a project plan
    plan = await pm.generate_plan(
        project_description="""
        Build a 24/7 customer support chatbot with AI capabilities.
        The system should handle common customer queries, escalate complex
        issues to human agents, and integrate with our existing CRM system.
        """,
        team=team,
        max_iterations=3,  # Number of optimization iterations
        verbose=True       # Print progress updates
    )

    # Access the results
    print(f"Total Tasks: {len(plan.tasks.tasks)}")
    print(f"Project Duration: {plan.schedule.get_project_duration()} days")
    print(f"Total Risk Score: {plan.risks.get_total_risk()}")

anyio.run(main)
```

## API Reference

### `ProjectManager`

Main class for generating project plans.

**Constructor:**
```python
pm = ProjectManager(options: ClaudeAgentOptions | None = None)
```

**Methods:**

#### `generate_plan()`
Generate a comprehensive project plan from a project description.

```python
plan = await pm.generate_plan(
    project_description: str,      # Detailed project description
    team: Team,                    # Team members with their expertise
    max_iterations: int = 3,       # Max optimization iterations
    verbose: bool = False          # Print progress updates
) -> ProjectPlan
```

#### `extract_tasks()`
Extract tasks only (standalone operation).

```python
tasks = await pm.extract_tasks(
    project_description: str
) -> TaskList
```

#### `map_dependencies()`
Map dependencies between tasks (standalone operation).

```python
dependencies = await pm.map_dependencies(
    tasks: TaskList
) -> DependencyList
```

#### `create_schedule()`
Create a schedule for tasks (standalone operation).

```python
schedule = await pm.create_schedule(
    tasks: TaskList,
    dependencies: DependencyList
) -> Schedule
```

### Data Models

#### `Team` and `TeamMember`

```python
team = Team(members=[
    TeamMember(
        name="Alice",
        profile="Skills and experience description"
    ),
])
```

#### `ProjectPlan`

The complete project plan returned by `generate_plan()`:

```python
plan = ProjectPlan(
    tasks: TaskList,                    # All extracted tasks
    dependencies: DependencyList,       # Task dependencies
    schedule: Schedule,                 # Task timeline
    allocations: TaskAllocationList,    # Task assignments
    risks: RiskList,                    # Risk assessments
    insights: list[str],                # Optimization insights
    iterations: int                     # Optimization iterations performed
)
```

**Helper Methods:**
- `plan.get_summary()` - Returns dict with project statistics
- `plan.schedule.get_project_duration()` - Total project duration in days
- `plan.risks.get_total_risk()` - Sum of all risk scores

## Examples

### Basic Usage

See `examples/pm_agent_example.py` for comprehensive examples including:
- Full project planning workflow
- Standalone operations (task extraction only)
- Accessing and analyzing plan components

Run the example:
```bash
python examples/pm_agent_example.py
```

### Custom Claude Configuration

```python
from claude_agent_sdk import ClaudeAgentOptions
from claude_agent_sdk.pm_agent import ProjectManager

# Use a specific Claude model
options = ClaudeAgentOptions(
    model="claude-opus-4",
    permission_mode="acceptEdits"
)

pm = ProjectManager(options=options)
```

### Error Handling

```python
from claude_agent_sdk.pm_agent.nodes import WorkflowNodeError

try:
    plan = await pm.generate_plan(
        project_description="...",
        team=team,
        max_iterations=3
    )
except WorkflowNodeError as e:
    print(f"Planning failed: {e}")
```

### Analyzing the Plan

```python
# Get summary statistics
summary = plan.get_summary()
print(f"Tasks: {summary['total_tasks']}")
print(f"Duration: {summary['project_duration_days']} days")
print(f"Risk: {summary['total_risk_score']}")

# Inspect tasks
for task in plan.tasks.tasks:
    print(f"{task.task_name}: {task.estimated_days} days")

# View schedule
task_map = {task.id: task for task in plan.tasks.tasks}
for sched in sorted(plan.schedule.schedule, key=lambda s: s.start_day):
    task = task_map[sched.task_id]
    print(f"Days {sched.start_day}-{sched.end_day}: {task.task_name}")

# Check allocations
for allocation in plan.allocations.allocations:
    task = task_map[allocation.task_id]
    print(f"{task.task_name} → {allocation.team_member_name}")

# Analyze risks
high_risks = [r for r in plan.risks.risks if r.risk_score >= 7]
for risk in high_risks:
    task = task_map[risk.task_id]
    print(f"⚠️ {task.task_name}: {risk.risk_description}")
```

## Architecture

The PM Agent uses a multi-stage workflow:

```
Project Description + Team
          ↓
    Task Generation (extract actionable tasks)
          ↓
    Dependency Mapping (identify blockers)
          ↓
    ┌─────────────────────────────────┐
    │  Optimization Loop              │
    │  (up to max_iterations)         │
    │                                 │
    │  1. Schedule Creation           │
    │  2. Team Allocation             │
    │  3. Risk Assessment             │
    │  4. Insight Generation          │
    │  5. Repeat if risk not reduced  │
    └─────────────────────────────────┘
          ↓
    Final Project Plan
```

### Components

- **types.py** - Pydantic models for type-safe data structures
- **prompts.py** - LLM prompt templates for each workflow stage
- **nodes.py** - Individual workflow step implementations
- **workflow.py** - Main orchestrator that connects all stages

### Key Design Decisions

1. **No LangGraph** - Uses simple async Python instead of external graph frameworks
2. **Claude SDK Native** - Leverages `query()` for all LLM interactions
3. **Type Safety** - Pydantic v2 models ensure data validation
4. **Modular** - Each workflow stage can be used independently
5. **Minimal Dependencies** - Only adds pydantic>=2.0.0

## Testing

Run the test suite:

```bash
# Run PM agent tests only
python -m pytest tests/test_pm_agent.py -v

# Run with coverage
python -m pytest tests/test_pm_agent.py --cov=claude_agent_sdk.pm_agent
```

The test suite includes:
- Unit tests for all data models
- JSON extraction and parsing tests
- Prompt generation tests
- ProjectManager initialization tests

## Performance Considerations

- Each workflow stage makes one LLM call
- Full workflow makes 5-15 calls depending on iterations
- Typical execution time: 30-120 seconds for complex projects
- Cost: ~$0.01-0.05 per plan with Claude Sonnet

### Optimization Tips

1. **Limit iterations** - Set `max_iterations=1` for faster results
2. **Simplify descriptions** - More concise descriptions = faster processing
3. **Use Haiku** - Configure `model="claude-haiku"` for speed over quality
4. **Cache results** - Save and reuse plans for similar projects

## Troubleshooting

### Common Issues

**"No valid JSON found in response"**
- Claude's response wasn't properly formatted JSON
- Try again, as LLM responses can vary
- Check your project description is clear and not too ambiguous

**"Task generation failed"**
- Project description might be too vague
- Ensure description includes concrete deliverables
- Try breaking down very large projects

**WorkflowNodeError during scheduling**
- Circular dependencies detected
- Review task relationships in your description

### Debug Mode

Enable verbose output to see what's happening:

```python
plan = await pm.generate_plan(
    project_description="...",
    team=team,
    verbose=True  # Prints progress for each stage
)
```

## Contributing

The PM Agent is part of the Claude SDK. To contribute:

1. Make changes in `src/claude_agent_sdk/pm_agent/`
2. Add tests in `tests/test_pm_agent.py`
3. Run linting: `python -m ruff check src/claude_agent_sdk/pm_agent --fix`
4. Run tests: `python -m pytest tests/test_pm_agent.py`
5. Type check: `python -m mypy src/claude_agent_sdk/pm_agent`

## License

MIT License - Same as the Claude SDK

## Credits

Based on the Project Manager Assistant Agent from [GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) by [NirDiamant](https://github.com/NirDiamant).

Adapted for the Claude SDK with:
- Simplified architecture (no LangGraph dependency)
- Integration with Claude SDK's native capabilities
- Enhanced error handling and type safety
- Comprehensive documentation and examples
