#!/usr/bin/env python3
"""Advanced examples for Project Manager Agent.

This demonstrates error handling, different project types, and advanced usage patterns.

Usage:
    python examples/pm_agent_advanced.py
"""

import anyio

from claude_agent_sdk import ClaudeAgentOptions
from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember
from claude_agent_sdk.pm_agent.nodes import WorkflowNodeError


async def error_handling_example():
    """Example showing proper error handling."""
    print("=" * 80)
    print("ERROR HANDLING EXAMPLE")
    print("=" * 80)

    pm = ProjectManager()

    team = Team(
        members=[
            TeamMember(name="Alice", profile="Full-stack Developer"),
        ]
    )

    try:
        print("\n📋 Attempting to generate plan...")
        plan = await pm.generate_plan(
            project_description="Build a simple todo app",
            team=team,
            max_iterations=1,
            verbose=True,
        )
        print(f"\n✅ Success! Generated plan with {len(plan.tasks.tasks)} tasks")

    except WorkflowNodeError as e:
        print(f"\n❌ Workflow failed: {e}")
        print("This can happen if Claude's response is not properly formatted.")
        print("Suggestion: Try again or simplify your project description.")

    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")


async def different_project_types_example():
    """Examples of different project types."""
    print("\n\n" + "=" * 80)
    print("DIFFERENT PROJECT TYPES")
    print("=" * 80)

    pm = ProjectManager()

    # Software Project
    print("\n--- Software Development Project ---")
    Team(
        members=[
            TeamMember(name="Alice", profile="Backend Developer - Python/Django"),
            TeamMember(name="Bob", profile="Frontend Developer - Vue.js"),
            TeamMember(name="Carol", profile="QA Engineer - Automated Testing"),
        ]
    )

    tasks = await pm.extract_tasks(
        project_description="""
        Create a web-based inventory management system.
        Features: product catalog, stock tracking, order management,
        reporting dashboard, user authentication.
        """
    )
    print(f"✓ Extracted {len(tasks.tasks)} tasks for software project")

    # Research Project
    print("\n--- Research Project ---")
    Team(
        members=[
            TeamMember(
                name="Dr. Smith", profile="Principal Researcher - Machine Learning"
            ),
            TeamMember(name="Jane", profile="Data Scientist - NLP"),
            TeamMember(name="Mike", profile="Research Engineer - MLOps"),
        ]
    )

    tasks = await pm.extract_tasks(
        project_description="""
        Investigate the effectiveness of transformer models for code generation.
        Steps: literature review, dataset collection, model training,
        evaluation benchmarks, paper writing.
        """
    )
    print(f"✓ Extracted {len(tasks.tasks)} tasks for research project")

    # Marketing Campaign
    print("\n--- Marketing Campaign ---")
    Team(
        members=[
            TeamMember(name="Sarah", profile="Marketing Manager - Digital Strategy"),
            TeamMember(name="Tom", profile="Content Creator - Social Media"),
            TeamMember(name="Lisa", profile="Graphic Designer - Visual Assets"),
        ]
    )

    tasks = await pm.extract_tasks(
        project_description="""
        Launch a Q4 product awareness campaign.
        Channels: social media, email, blog posts, webinars.
        Goal: 50% increase in product signups.
        """
    )
    print(f"✓ Extracted {len(tasks.tasks)} tasks for marketing campaign")


async def custom_configuration_example():
    """Example with custom Claude configuration."""
    print("\n\n" + "=" * 80)
    print("CUSTOM CONFIGURATION EXAMPLE")
    print("=" * 80)

    # Use specific Claude model and settings
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",  # Specific model
        permission_mode="acceptEdits",  # Auto-accept edits
    )

    pm = ProjectManager(options=options)

    Team(
        members=[
            TeamMember(name="Alex", profile="DevOps Engineer"),
        ]
    )

    print("\n📋 Using custom Claude configuration...")
    print(f"   Model: {options.model}")
    print(f"   Permission Mode: {options.permission_mode}")

    tasks = await pm.extract_tasks(
        project_description="""
        Set up CI/CD pipeline for a Python web application.
        Include: automated testing, code quality checks, staging deployment,
        production deployment with rollback capability.
        """
    )
    print(f"\n✓ Extracted {len(tasks.tasks)} tasks")
    for task in tasks.tasks:
        print(f"   • {task.task_name} ({task.estimated_days}d)")


async def iterative_planning_example():
    """Example showing how the iterative optimization works."""
    print("\n\n" + "=" * 80)
    print("ITERATIVE OPTIMIZATION EXAMPLE")
    print("=" * 80)

    pm = ProjectManager()

    team = Team(
        members=[
            TeamMember(name="Alice", profile="Senior Developer - Full-stack"),
            TeamMember(name="Bob", profile="Junior Developer - Backend"),
        ]
    )

    print("\n🔄 Demonstrating iterative optimization...")
    print("The PM agent will refine the plan multiple times to reduce risk.\n")

    plan = await pm.generate_plan(
        project_description="""
        Build a real-time chat application with WebSocket support.
        Features: user authentication, private messages, group chats,
        file sharing, emoji reactions, online status indicators.
        """,
        team=team,
        max_iterations=3,  # Allow up to 3 optimization iterations
        verbose=True,
    )

    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)
    print(f"Iterations performed: {plan.iterations}")
    print(f"Final risk score: {plan.risks.get_total_risk()}")

    if plan.insights:
        print("\nOptimization insights generated:")
        for i, insight in enumerate(plan.insights, 1):
            print(f"{i}. {insight}")


async def standalone_operations_example():
    """Example using standalone operations for more control."""
    print("\n\n" + "=" * 80)
    print("STANDALONE OPERATIONS EXAMPLE")
    print("=" * 80)

    pm = ProjectManager()

    Team(
        members=[
            TeamMember(name="Alice", profile="Backend Developer"),
            TeamMember(name="Bob", profile="Frontend Developer"),
        ]
    )

    # Step 1: Extract tasks
    print("\n📋 Step 1: Extracting tasks...")
    tasks = await pm.extract_tasks(
        project_description="""
        Create a blog platform.
        Features: post creation, comments, user profiles, search.
        """
    )
    print(f"✓ Found {len(tasks.tasks)} tasks")

    # Step 2: Map dependencies
    print("\n🔗 Step 2: Mapping dependencies...")
    dependencies = await pm.map_dependencies(tasks)
    print(f"✓ Mapped {len(dependencies.dependencies)} dependency relationships")

    # Analyze dependencies
    for dep in dependencies.dependencies:
        task = next(t for t in tasks.tasks if t.id == dep.task_id)
        if dep.dependent_task_ids:
            dep_tasks = [
                next(t for t in tasks.tasks if t.id == did)
                for did in dep.dependent_task_ids
            ]
            print(
                f"   • {task.task_name} depends on: {', '.join(t.task_name for t in dep_tasks)}"
            )

    # Step 3: Create schedule
    print("\n📅 Step 3: Creating schedule...")
    schedule = await pm.create_schedule(tasks, dependencies)
    print(f"✓ Project duration: {schedule.get_project_duration()} days")

    # Show timeline
    task_map = {task.id: task for task in tasks.tasks}
    print("\nTimeline:")
    for sched in sorted(schedule.schedule, key=lambda s: s.start_day):
        task = task_map[sched.task_id]
        print(f"   Days {sched.start_day:2d}-{sched.end_day:2d}: {task.task_name}")


async def risk_analysis_example():
    """Example focusing on risk analysis."""
    print("\n\n" + "=" * 80)
    print("RISK ANALYSIS EXAMPLE")
    print("=" * 80)

    pm = ProjectManager()

    team = Team(
        members=[
            TeamMember(
                name="Alice", profile="Senior Developer with 10 years experience"
            ),
            TeamMember(name="Bob", profile="Junior Developer, fresh graduate"),
        ]
    )

    print("\n⚠️  Analyzing project risks...")
    plan = await pm.generate_plan(
        project_description="""
        Migrate legacy monolithic application to microservices architecture.
        Challenges: zero downtime requirement, data consistency,
        service discovery, distributed tracing.
        Must maintain backward compatibility during transition.
        """,
        team=team,
        max_iterations=2,
        verbose=True,
    )

    print("\n" + "=" * 80)
    print("RISK BREAKDOWN")
    print("=" * 80)

    # Categorize risks
    critical = [r for r in plan.risks.risks if r.risk_score >= 8]
    high = [r for r in plan.risks.risks if 6 <= r.risk_score < 8]
    medium = [r for r in plan.risks.risks if 4 <= r.risk_score < 6]
    low = [r for r in plan.risks.risks if r.risk_score < 4]

    task_map = {task.id: task for task in plan.tasks.tasks}

    if critical:
        print(f"\n🔴 CRITICAL RISK ({len(critical)} tasks):")
        for risk in critical:
            task = task_map[risk.task_id]
            print(f"   • {task.task_name}")
            print(f"     Score: {risk.risk_score}/10")
            print(f"     {risk.risk_description}")

    if high:
        print(f"\n🟠 HIGH RISK ({len(high)} tasks):")
        for risk in high:
            task = task_map[risk.task_id]
            print(f"   • {task.task_name} (Score: {risk.risk_score}/10)")

    if medium:
        print(f"\n🟡 MEDIUM RISK ({len(medium)} tasks)")

    if low:
        print(f"\n🟢 LOW RISK ({len(low)} tasks)")

    print(f"\n📊 Total Risk Score: {plan.risks.get_total_risk()}")


async def main():
    """Run all advanced examples."""
    await error_handling_example()
    await different_project_types_example()
    await custom_configuration_example()
    await iterative_planning_example()
    await standalone_operations_example()
    await risk_analysis_example()

    print("\n\n" + "=" * 80)
    print("✅ All advanced examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    anyio.run(main)
