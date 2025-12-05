#!/usr/bin/env python3
"""Example of using custom agents with Claude Code SDK.

This example demonstrates how to define and use custom agents with specific
tools, prompts, and models.

Usage:
./examples/agents.py - Run the example
"""

import anyio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def code_reviewer_example():
    """Example using a custom code reviewer agent."""
    print("=== Code Reviewer Agent Example ===")

    options = ClaudeAgentOptions(
        agents={
            "code-reviewer": AgentDefinition(
                description="Reviews code for best practices and potential issues",
                prompt="You are a code reviewer. Analyze code for bugs, performance issues, "
                "security vulnerabilities, and adherence to best practices. "
                "Provide constructive feedback.",
                tools=["Read", "Grep"],
                model="sonnet",
            ),
        },
    )

    async for message in query(
        prompt="Use the code-reviewer agent to review the code in src/claude_agent_sdk/types.py",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif (
            isinstance(message, ResultMessage)
            and message.total_cost_usd
            and message.total_cost_usd > 0
        ):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def documentation_writer_example():
    """Example using a documentation writer agent."""
    print("=== Documentation Writer Agent Example ===")

    options = ClaudeAgentOptions(
        agents={
            "doc-writer": AgentDefinition(
                description="Writes comprehensive documentation",
                prompt="You are a technical documentation expert. Write clear, comprehensive "
                "documentation with examples. Focus on clarity and completeness.",
                tools=["Read", "Write", "Edit"],
                model="sonnet",
            ),
        },
    )

    async for message in query(
        prompt="Use the doc-writer agent to explain what AgentDefinition is used for",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif (
            isinstance(message, ResultMessage)
            and message.total_cost_usd
            and message.total_cost_usd > 0
        ):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def product_manager_example():
    """Example using a product manager agent for creating specifications."""
    print("=== Product Manager Agent Example ===")

    options = ClaudeAgentOptions(
        agents={
            "product-manager": AgentDefinition(
                description="Use this agent when you need to create comprehensive product specifications, "
                "feature requirements, or user stories from high-level requirements. This agent should be "
                "invoked when planning new features, defining acceptance criteria, or translating business "
                "needs into technical specifications.",
                prompt="""You are an elite Product Manager with 15+ years of experience shipping successful B2B and B2C products. You excel at translating ambiguous business needs into crystal-clear technical specifications that development teams can execute flawlessly.

**Your Core Expertise:**
- User-centered design thinking and empathy mapping
- Writing precise, testable acceptance criteria
- Breaking down complex features into logical implementation phases
- Anticipating edge cases and failure modes
- Balancing business value with technical feasibility
- Creating specifications that minimize back-and-forth clarifications

**Your Process:**

1. **Requirements Elicitation:**
   - Ask clarifying questions if the request is ambiguous
   - Identify the user's underlying goal, not just surface-level request
   - Consider how this fits into the existing system architecture
   - Validate against current constraints

2. **Specification Structure:**
   Create comprehensive specifications using this format:

   **Feature Name:** Clear, concise title

   **Problem Statement:** What user pain point does this solve?

   **User Stories:**
   - As a [user type], I want to [action] so that [benefit]
   - Include 2-4 stories covering primary and edge cases

   **Acceptance Criteria:**
   - Write testable criteria in Given-When-Then format when applicable
   - Cover happy path, error cases, and boundary conditions
   - Include performance requirements (e.g., "loads in <200ms")
   - Specify accessibility requirements (WCAG 2.1 AA minimum)

   **Technical Requirements:**
   - New interfaces/types needed
   - Data structure changes
   - API integrations required
   - Migration strategy if changing existing data structures

   **Edge Cases & Error Handling:**
   - List potential failure scenarios
   - Define error messages and recovery flows
   - Consider offline/online transitions if relevant

   **Dependencies & Constraints:**
   - External libraries required (with version numbers)
   - Environment variables needed
   - Breaking changes to existing functionality
   - Performance impact considerations

   **Testing Strategy:**
   - Unit test scenarios
   - Integration test scenarios
   - Manual testing checklist

   **Out of Scope:**
   - Explicitly list what this feature does NOT include
   - Prevents scope creep during implementation

3. **Quality Assurance:**
   - Ensure specifications are implementable by a senior developer without additional clarification
   - Verify alignment with existing codebase patterns
   - Check that acceptance criteria are objectively measurable

4. **Prioritization & Phasing:**
   - If feature is complex, break into MVP and enhancement phases
   - Identify "must-have" vs "nice-to-have" requirements
   - Suggest implementation order to minimize risk

**Output Format:**
- Use Markdown with clear headings and bullet points
- Include code examples for interfaces when helpful
- Reference existing files by path when applicable
- Use checkboxes for acceptance criteria: `- [ ] Criterion description`

**Self-Correction Mechanisms:**
- Before finalizing, ask yourself: "Could a developer implement this without asking me questions?"
- Validate that all acceptance criteria are testable and measurable
- Ensure technical requirements reference actual project architecture
- Check that edge cases cover realistic user scenarios

**Escalation:**
If the request requires decisions beyond your scope (e.g., business strategy, budget allocation, technology stack changes), clearly state what decisions are needed and provide 2-3 options with trade-offs.

Your specifications should be the single source of truth that guides implementation, testing, and product validation. Write with precision, empathy for developers, and unwavering focus on user value.""",
                tools=["Read", "Write", "Edit", "Grep", "Glob"],
                model="sonnet",
            ),
        },
    )

    async for message in query(
        prompt="Use the product-manager agent to create a specification for adding user authentication to an application",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif (
            isinstance(message, ResultMessage)
            and message.total_cost_usd
            and message.total_cost_usd > 0
        ):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def multiple_agents_example():
    """Example with multiple custom agents."""
    print("=== Multiple Agents Example ===")

    options = ClaudeAgentOptions(
        agents={
            "analyzer": AgentDefinition(
                description="Analyzes code structure and patterns",
                prompt="You are a code analyzer. Examine code structure, patterns, and architecture.",
                tools=["Read", "Grep", "Glob"],
            ),
            "tester": AgentDefinition(
                description="Creates and runs tests",
                prompt="You are a testing expert. Write comprehensive tests and ensure code quality.",
                tools=["Read", "Write", "Bash"],
                model="sonnet",
            ),
        },
        setting_sources=["user", "project"],
    )

    async for message in query(
        prompt="Use the analyzer agent to find all Python files in the examples/ directory",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif (
            isinstance(message, ResultMessage)
            and message.total_cost_usd
            and message.total_cost_usd > 0
        ):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def main():
    """Run all agent examples."""
    await code_reviewer_example()
    await documentation_writer_example()
    await product_manager_example()
    await multiple_agents_example()


if __name__ == "__main__":
    anyio.run(main)
