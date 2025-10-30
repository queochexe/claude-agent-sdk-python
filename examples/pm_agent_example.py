#!/usr/bin/env python3
"""Example of using the Project Manager Agent with Claude SDK.

This example demonstrates how to use the PM Agent to generate comprehensive
project plans from project descriptions, including task extraction, dependency
mapping, scheduling, team allocation, and risk assessment.

Based on the GenAI_Agents project manager implementation:
https://github.com/NirDiamant/GenAI_Agents

Usage:
    python examples/pm_agent_example.py
"""

import anyio

from claude_agent_sdk.pm_agent import ProjectManager, Team, TeamMember


async def basic_example():
    """Basic example: Generate a project plan for a chatbot project."""
    print("=" * 80)
    print("BASIC EXAMPLE: Customer Support Chatbot")
    print("=" * 80)

    # Initialize the Project Manager
    pm = ProjectManager()

    # Define the team
    team = Team(
        members=[
            TeamMember(
                name="Alice",
                profile="Senior Backend Developer with 5 years Python/FastAPI experience, "
                "expert in API design and database optimization",
            ),
            TeamMember(
                name="Bob",
                profile="Frontend Developer specializing in React and TypeScript, "
                "3 years experience building responsive web applications",
            ),
            TeamMember(
                name="Carol",
                profile="DevOps Engineer with AWS, Docker, and Kubernetes expertise, "
                "experienced in CI/CD pipelines and infrastructure automation",
            ),
            TeamMember(
                name="David",
                profile="ML Engineer with NLP background, experienced in training and "
                "deploying language models and chatbot systems",
            ),
        ]
    )

    # Generate project plan
    plan = await pm.generate_plan(
        project_description="""
        Build a 24/7 customer support chatbot with AI capabilities.
        The system should:
        - Handle common customer queries automatically using NLP
        - Escalate complex issues to human agents
        - Integrate with existing CRM system (Salesforce)
        - Provide real-time analytics dashboard for support managers
        - Support multiple languages (English, Spanish, French)
        - Include A/B testing framework for response optimization
        - Ensure GDPR compliance for customer data
        """,
        team=team,
        max_iterations=3,
        verbose=True,
    )

    # Display results
    print("\n" + "=" * 80)
    print("PROJECT PLAN SUMMARY")
    print("=" * 80)

    summary = plan.get_summary()
    print(f"📊 Total Tasks: {summary['total_tasks']}")
    print(f"⏱️  Project Duration: {summary['project_duration_days']} days")
    print(f"⚠️  Total Risk Score: {summary['total_risk_score']}")
    print(f"👥 Team Size: {summary['team_size']}")
    print(f"🔄 Optimization Iterations: {summary['optimization_iterations']}")

    print("\n" + "-" * 80)
    print("TASKS")
    print("-" * 80)
    for i, task in enumerate(plan.tasks.tasks, 1):
        print(f"{i}. {task.task_name}")
        print(f"   Duration: {task.estimated_days} days")
        print(f"   Description: {task.task_description}")
        print()

    print("-" * 80)
    print("SCHEDULE")
    print("-" * 80)
    # Create task lookup
    task_map = {task.id: task for task in plan.tasks.tasks}
    for sched in sorted(plan.schedule.schedule, key=lambda s: s.start_day):
        task = task_map.get(sched.task_id)
        if task:
            print(f"Days {sched.start_day}-{sched.end_day}: {task.task_name}")

    print("\n" + "-" * 80)
    print("TEAM ALLOCATIONS")
    print("-" * 80)
    for allocation in plan.allocations.allocations:
        task = task_map.get(allocation.task_id)
        if task:
            print(f"• {task.task_name} → {allocation.team_member_name}")

    print("\n" + "-" * 80)
    print("RISK ASSESSMENT")
    print("-" * 80)
    high_risk_tasks = [r for r in plan.risks.risks if r.risk_score >= 7]
    medium_risk_tasks = [r for r in plan.risks.risks if 4 <= r.risk_score < 7]
    low_risk_tasks = [r for r in plan.risks.risks if r.risk_score < 4]

    print(f"🔴 High Risk ({len(high_risk_tasks)} tasks):")
    for risk in high_risk_tasks:
        task = task_map.get(risk.task_id)
        if task:
            print(f"   • {task.task_name} (Score: {risk.risk_score}/10)")
            print(f"     {risk.risk_description}")

    print(f"\n🟡 Medium Risk ({len(medium_risk_tasks)} tasks):")
    for risk in medium_risk_tasks:
        task = task_map.get(risk.task_id)
        if task:
            print(f"   • {task.task_name} (Score: {risk.risk_score}/10)")

    print(f"\n🟢 Low Risk ({len(low_risk_tasks)} tasks)")

    if plan.insights:
        print("\n" + "-" * 80)
        print("OPTIMIZATION INSIGHTS")
        print("-" * 80)
        for i, insight in enumerate(plan.insights, 1):
            print(f"{i}. {insight}")

    print("\n" + "=" * 80)


async def standalone_operations_example():
    """Example showing standalone operations (task extraction only)."""
    print("\n\n" + "=" * 80)
    print("STANDALONE OPERATIONS EXAMPLE")
    print("=" * 80)

    pm = ProjectManager()

    # Just extract tasks without full planning
    print("\n📋 Extracting tasks from project description...")
    tasks = await pm.extract_tasks(
        project_description="""
        Create a mobile fitness tracking app.
        Features: workout logging, progress charts, social sharing, meal planning.
        """
    )

    print(f"\n✓ Extracted {len(tasks.tasks)} tasks:")
    for i, task in enumerate(tasks.tasks, 1):
        print(f"{i}. {task.task_name} ({task.estimated_days} days)")
        print(f"   {task.task_description}")
        print()

    # Map dependencies
    print("🔗 Mapping task dependencies...")
    dependencies = await pm.map_dependencies(tasks)
    print(f"\n✓ Mapped {len(dependencies.dependencies)} dependency relationships")

    # Create schedule
    print("\n📅 Creating schedule...")
    schedule = await pm.create_schedule(tasks, dependencies)
    print(f"\n✓ Project duration: {schedule.get_project_duration()} days")


async def main():
    """Run all examples."""
    await basic_example()
    await standalone_operations_example()


if __name__ == "__main__":
    anyio.run(main)
