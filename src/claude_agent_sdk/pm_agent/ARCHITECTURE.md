# Project Manager Agent - Architecture Documentation

This document describes the internal architecture and design decisions for the PM Agent module.

## Overview

The PM Agent is a multi-stage AI workflow that transforms project descriptions into comprehensive, optimized project plans. It's designed to integrate seamlessly with the Claude SDK while remaining modular and testable.

## Design Philosophy

1. **Simplicity over Complexity** - No external graph frameworks (LangGraph), just Python async/await
2. **Type Safety** - Pydantic v2 models ensure data validation at every step
3. **Modularity** - Each workflow stage can be used independently
4. **SDK Native** - Leverages Claude SDK's built-in capabilities
5. **Testability** - Clear separation between logic and LLM calls

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ProjectManager                              │
│                    (workflow.py)                                │
│                                                                 │
│  Orchestrates the entire workflow and manages state            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────┐
                              ▼                         ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │   Workflow Nodes │    │  Prompt Templates│
                    │    (nodes.py)    │◄───┤  (prompts.py)    │
                    └──────────────────┘    └──────────────────┘
                              │
                              ├─► task_generation_node()
                              ├─► dependency_mapping_node()
                              ├─► scheduling_node()
                              ├─► allocation_node()
                              ├─► risk_assessment_node()
                              └─► insights_generation_node()
                              │
                              ▼
                    ┌──────────────────┐
                    │  Claude SDK      │
                    │  query()         │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Data Models     │
                    │  (types.py)      │
                    │                  │
                    │  • Task          │
                    │  • Team          │
                    │  • Schedule      │
                    │  • Risk          │
                    │  • ProjectPlan   │
                    └──────────────────┘
```

## Module Structure

### 1. `types.py` - Data Models

**Purpose:** Define all data structures using Pydantic v2 for type safety and validation.

**Key Models:**
- `Task` - Single actionable work item
- `TaskList` - Container for multiple tasks
- `TeamMember` - Individual with skills/expertise
- `Team` - Group of team members
- `TaskDependency` - Relationships between tasks
- `DependencyList` - Container for dependencies
- `TaskSchedule` - Timeline for a task
- `Schedule` - Complete project timeline
- `TaskAllocation` - Assignment of task to team member
- `TaskAllocationList` - All task assignments
- `Risk` - Risk assessment for a task
- `RiskList` - All project risks
- `ProjectPlan` - Complete final output

**Design Decisions:**
- Use Pydantic for automatic validation
- Separate "item" models from "list" models for clarity
- Include helper methods (`get_summary()`, `get_project_duration()`, etc.)
- Use UUID for task IDs to ensure uniqueness

### 2. `prompts.py` - Prompt Templates

**Purpose:** Generate structured prompts for each workflow stage.

**Functions:**
- `task_generation_prompt()` - Extract tasks from description
- `dependency_mapping_prompt()` - Identify task relationships
- `scheduling_prompt()` - Create optimized timeline
- `allocation_prompt()` - Assign tasks to team
- `risk_assessment_prompt()` - Evaluate risks
- `insights_generation_prompt()` - Generate optimization suggestions

**Design Decisions:**
- All prompts request JSON-only responses for reliable parsing
- Include specific instructions about data format
- Provide context from previous stages
- Support optional insights for iterative improvement

### 3. `nodes.py` - Workflow Nodes

**Purpose:** Implement individual workflow steps that call Claude and process responses.

**Key Functions:**
- `call_claude()` - Wrapper around SDK's `query()` function
- `extract_json_from_response()` - Parse JSON from Claude's response (handles markdown, extra text)
- `task_generation_node()` - Generate `TaskList`
- `dependency_mapping_node()` - Generate `DependencyList`
- `scheduling_node()` - Generate `Schedule`
- `allocation_node()` - Generate `TaskAllocationList`
- `risk_assessment_node()` - Generate `RiskList`
- `insights_generation_node()` - Generate optimization insights

**Design Decisions:**
- Each node is an async function for concurrency
- Nodes are pure functions (no side effects)
- Clear error messages with `WorkflowNodeError`
- JSON extraction handles multiple response formats
- All nodes return typed Pydantic models

### 4. `workflow.py` - Orchestrator

**Purpose:** Main `ProjectManager` class that coordinates the entire workflow.

**Class Structure:**

```python
class ProjectManager:
    def __init__(self, options: ClaudeAgentOptions | None = None)

    async def generate_plan(...) -> ProjectPlan
    async def extract_tasks(...) -> TaskList
    async def map_dependencies(...) -> DependencyList
    async def create_schedule(...) -> Schedule
```

**Workflow Execution:**

```
1. Task Generation
   ├─► Call task_generation_node()
   └─► Returns: TaskList

2. Dependency Mapping
   ├─► Call dependency_mapping_node(tasks)
   └─► Returns: DependencyList

3. Iterative Optimization Loop (up to max_iterations)
   │
   ├─► 3a. Scheduling
   │   ├─► Call scheduling_node(tasks, deps, insights)
   │   └─► Returns: Schedule
   │
   ├─► 3b. Allocation
   │   ├─► Call allocation_node(tasks, schedule, team)
   │   └─► Returns: TaskAllocationList
   │
   ├─► 3c. Risk Assessment
   │   ├─► Call risk_assessment_node(tasks, schedule, allocations)
   │   └─► Returns: RiskList
   │
   ├─► 3d. Check Stopping Condition
   │   ├─► If risk decreased from previous iteration → STOP
   │   └─► If max_iterations reached → STOP
   │
   └─► 3e. Generate Insights (if continuing)
       ├─► Call insights_generation_node(schedule, allocations, risks)
       ├─► Returns: list[str] of insights
       └─► Loop back to 3a with new insights

4. Return Final ProjectPlan
   └─► Contains all components + optimization history
```

**Design Decisions:**
- Simple async/await, no complex state machines
- Each iteration stores results for history tracking
- Stopping condition: risk score improvement
- Verbose mode for debugging
- Standalone methods for individual operations

## Data Flow

### Input → Output for Each Stage

```
Stage 1: Task Generation
Input:  project_description (str)
Output: TaskList (tasks with estimates)

Stage 2: Dependency Mapping
Input:  TaskList
Output: DependencyList (which tasks block which)

Stage 3a: Scheduling
Input:  TaskList + DependencyList + Optional[insights]
Output: Schedule (start/end days for each task)

Stage 3b: Allocation
Input:  TaskList + Schedule + Team
Output: TaskAllocationList (task → team member)

Stage 3c: Risk Assessment
Input:  TaskList + Schedule + TaskAllocationList
Output: RiskList (risk scores + descriptions)

Stage 3d: Insights (if iterating)
Input:  Schedule + TaskAllocationList + RiskList
Output: list[str] (optimization recommendations)
```

## Optimization Loop

The iterative optimization is the core innovation:

1. **Initial Plan** - First schedule/allocation/risk assessment
2. **Evaluate** - Calculate total risk score
3. **Reflect** - Generate insights about what could improve
4. **Refine** - Re-plan with insights incorporated
5. **Compare** - Did risk decrease?
   - ✅ Yes → Success, stop iterating
   - ❌ No → Continue (up to max_iterations)

**Why this works:**
- Claude learns from its own output
- Insights guide specific improvements
- Risk score provides objective metric
- Prevents infinite loops with max_iterations

## Error Handling

### Exception Hierarchy

```
Exception
└── WorkflowNodeError (custom)
    ├── Raised when LLM response is invalid
    ├── Raised when JSON parsing fails
    └── Raised when data validation fails
```

### Failure Points and Mitigations

1. **JSON Parsing Failure**
   - **Cause:** Claude returns non-JSON or malformed JSON
   - **Mitigation:** `extract_json_from_response()` handles multiple formats
   - **Fallback:** Clear error message with text sample

2. **Pydantic Validation Failure**
   - **Cause:** Returned data doesn't match schema
   - **Mitigation:** Strict prompts requesting specific format
   - **Fallback:** Re-try with clearer prompt

3. **LLM API Errors**
   - **Cause:** Network issues, rate limits, service errors
   - **Mitigation:** Propagate errors from SDK
   - **Fallback:** User should retry

## Testing Strategy

### Unit Tests (`tests/test_pm_agent.py`)

- ✅ Data model creation and validation
- ✅ JSON extraction from various formats
- ✅ Prompt generation with different inputs
- ✅ ProjectManager initialization

### Integration Tests (TODO)

- Mock Claude responses for full workflow
- Test error paths and recovery
- Performance benchmarks

### Manual Testing

- Run `examples/pm_agent_example.py`
- Run `examples/pm_agent_advanced.py`
- Test with real Claude API

## Performance Characteristics

### Time Complexity

- Task Generation: O(1) LLM call
- Dependency Mapping: O(1) LLM call
- Each Iteration: O(3) LLM calls (schedule + allocate + assess)
- Insights: O(1) LLM call
- **Total:** 2 + (3 × iterations) + (iterations - 1) calls

Example: 3 iterations = 2 + 9 + 2 = **13 LLM calls**

### Space Complexity

- Stores all iteration history
- O(iterations × tasks) memory
- Typical: ~1-10 MB for large projects

### Typical Execution Time

- Simple project (5 tasks): 20-40 seconds
- Medium project (15 tasks): 40-80 seconds
- Complex project (30+ tasks): 80-150 seconds

## Comparison with Original Implementation

### NirDiamant/GenAI_Agents (Original)

**Stack:**
- LangGraph for state management
- LangChain for LLM calls
- OpenAI GPT-4o-mini
- Jupyter notebook format

**Pros:**
- Visual graph representation
- Battle-tested framework
- Rich LangChain ecosystem

**Cons:**
- Heavy dependencies (LangGraph + LangChain)
- Complex setup
- OpenAI-specific

### Our Implementation

**Stack:**
- Native Python async/await
- Claude SDK query()
- Anthropic Claude
- Installable Python package

**Pros:**
- Minimal dependencies (just pydantic)
- Simpler architecture
- Native Claude SDK integration
- Production-ready packaging

**Cons:**
- No visual graph editor
- Manual state management

## Extension Points

### Adding New Workflow Stages

1. Create prompt in `prompts.py`
2. Create data model in `types.py`
3. Create node function in `nodes.py`
4. Call from workflow in `workflow.py`

Example: Add "Cost Estimation" stage:

```python
# types.py
class CostEstimate(BaseModel):
    task_id: str
    estimated_cost: float

# prompts.py
def cost_estimation_prompt(...) -> str:
    ...

# nodes.py
async def cost_estimation_node(...) -> CostEstimateList:
    ...

# workflow.py (in generate_plan)
costs = await nodes.cost_estimation_node(tasks, schedule)
```

### Custom LLM Providers

Pass custom options to ProjectManager:

```python
options = ClaudeAgentOptions(
    model="custom-model",
    # other options
)
pm = ProjectManager(options=options)
```

### Custom Prompts

Subclass and override prompt functions:

```python
import claude_agent_sdk.pm_agent.prompts as prompts

def my_task_prompt(desc: str) -> str:
    return f"Custom instruction: {desc}"

# Monkey-patch (not ideal but works)
prompts.task_generation_prompt = my_task_prompt
```

## Future Enhancements

### Potential Improvements

1. **Caching** - Cache task extraction for similar projects
2. **Parallel Execution** - Run independent stages concurrently
3. **Streaming** - Stream partial results as they're generated
4. **Custom Metrics** - Allow user-defined success metrics beyond risk
5. **Constraint Handling** - Explicit budget/time constraints
6. **Resource Leveling** - Balance workload across time
7. **Gantt Chart Export** - Visual timeline generation
8. **Version Control** - Track plan changes over iterations

### API Additions

```python
# Possible future APIs
pm.save_plan(plan, "plan.json")
pm.load_plan("plan.json")
pm.export_gantt(plan, "timeline.png")
pm.compare_plans(plan1, plan2)
```

## References

- Original Implementation: [GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents)
- Claude SDK: [Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk)
- Pydantic: [Documentation](https://docs.pydantic.dev/)

---

*This architecture is designed to be simple, maintainable, and extensible while providing powerful AI-driven project planning capabilities.*
