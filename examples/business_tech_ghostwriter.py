#!/usr/bin/env python3
"""Expert Business-Tech AI Ghostwriter Agent

A specialized ghostwriter agent focused on UX/Product Design's influence on
business and technology. Research-oriented and data-driven.

Usage:
    python examples/business_tech_ghostwriter.py
"""

import anyio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)


async def create_ghostwriter_agent():
    """Create and configure the business-tech ghostwriter agent."""

    options = ClaudeAgentOptions(
        agents={
            "ghostwriter": AgentDefinition(
                description="Expert business-tech ghostwriter specialized in UX/Product Design",
                prompt=(
                    "You are a senior professional ghostwriter with deep expertise in business technology. "
                    "\n\n**Core Specializations:**\n"
                    "- UX (User Experience) and Product Design principles and their business impact\n"
                    "- How design decisions influence technology adoption and business outcomes\n"
                    "- Product-led growth strategies and design thinking methodologies\n"
                    "- The intersection of human-centered design and business strategy\n"
                    "\n**Writing Approach:**\n"
                    "- Research-oriented: Always ground claims in data, case studies, and industry research\n"
                    "- Data-driven: Cite statistics, metrics, and quantifiable results when available\n"
                    "- Evidence-based: Reference real-world examples and authoritative sources\n"
                    "- Compelling narratives: Blend data with storytelling for engaging content\n"
                    "\n**Content Standards:**\n"
                    "- Write in various styles and tones (technical, executive, conversational) as needed\n"
                    "- Adapt to the client's voice and brand guidelines\n"
                    "- Focus on clarity, precision, and engagement\n"
                    "- Structure content logically with clear takeaways\n"
                    "- Include relevant data points, research findings, and industry insights\n"
                    "\n**Research Best Practices:**\n"
                    "- Verify facts before including them\n"
                    "- Cite sources appropriately\n"
                    "- Stay current with latest UX/Product Design trends and business technology news\n"
                    "- Draw insights from reputable sources (industry reports, academic research, case studies)"
                ),
                tools=["Read", "Write", "Edit", "WebSearch", "Grep", "Glob"],
                model="sonnet",
            ),
        },
        permission_mode="acceptEdits",  # Auto-accept file edits
    )

    return options


async def example_blog_post():
    """Example: Write a research-backed blog post."""
    print("=== Example 1: Research-Backed Blog Post ===\n")

    options = await create_ghostwriter_agent()

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Use the ghostwriter agent to write a 500-word blog post about "
            "'How UX Design Impacts Customer Retention Rates in SaaS Products'. "
            "Include relevant statistics and research findings. "
            "Save it to blog_post_ux_retention.md"
        )

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}\n")
            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd and msg.total_cost_usd > 0:
                    print(f"Cost: ${msg.total_cost_usd:.4f}\n")


async def example_whitepaper_section():
    """Example: Create a data-driven whitepaper section."""
    print("=== Example 2: Whitepaper Section ===\n")

    options = await create_ghostwriter_agent()

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Use the ghostwriter agent to write an executive summary for a whitepaper "
            "on 'The ROI of Investing in Product Design: A Data-Driven Analysis'. "
            "Research and include industry benchmarks and case studies. "
            "Make it compelling for C-level executives. "
            "Save to whitepaper_executive_summary.md"
        )

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}\n")
            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd and msg.total_cost_usd > 0:
                    print(f"Cost: ${msg.total_cost_usd:.4f}\n")


async def example_linkedin_article():
    """Example: LinkedIn thought leadership article."""
    print("=== Example 3: LinkedIn Thought Leadership ===\n")

    options = await create_ghostwriter_agent()

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Use the ghostwriter agent to write a LinkedIn article (800 words) "
            "about 'Why Design Systems Are a Business Strategy, Not Just a Design Tool'. "
            "Target audience: Product leaders and tech executives. "
            "Include data on efficiency gains and business impact. "
            "Save to linkedin_design_systems.md"
        )

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}\n")
            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd and msg.total_cost_usd > 0:
                    print(f"Cost: ${msg.total_cost_usd:.4f}\n")


async def example_case_study():
    """Example: Product design case study."""
    print("=== Example 4: Case Study ===\n")

    options = await create_ghostwriter_agent()

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Use the ghostwriter agent to create a case study outline "
            "for 'How Mobile-First Design Increased User Engagement by 40%'. "
            "Include sections for: Challenge, Approach, Results (with metrics), and Key Takeaways. "
            "Research similar real-world examples for inspiration. "
            "Save to case_study_mobile_first.md"
        )

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}\n")
            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd and msg.total_cost_usd > 0:
                    print(f"Cost: ${msg.total_cost_usd:.4f}\n")


async def interactive_mode():
    """Interactive mode for custom requests."""
    print("=== Interactive Ghostwriter Mode ===")
    print("Enter your writing request (or 'exit' to quit):\n")

    options = await create_ghostwriter_agent()

    async with ClaudeSDKClient(options=options) as client:
        # Example interactive session
        request = (
            "Use the ghostwriter agent to write a short email (200 words) "
            "to a product team explaining why investing time in UX research "
            "will accelerate development. Include data-backed reasoning."
        )

        print(f"Request: {request}\n")

        await client.query(request)

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}\n")
            elif isinstance(msg, ResultMessage):
                if msg.total_cost_usd and msg.total_cost_usd > 0:
                    print(f"Cost: ${msg.total_cost_usd:.4f}\n")


async def main():
    """Run all examples."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   Expert Business-Tech AI Ghostwriter Agent Examples     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # Run examples
    await example_blog_post()
    print("\n" + "="*60 + "\n")

    await example_whitepaper_section()
    print("\n" + "="*60 + "\n")

    await example_linkedin_article()
    print("\n" + "="*60 + "\n")

    await example_case_study()
    print("\n" + "="*60 + "\n")

    await interactive_mode()

    print("\n✅ All examples completed!")
    print("\nGenerated files:")
    print("- blog_post_ux_retention.md")
    print("- whitepaper_executive_summary.md")
    print("- linkedin_design_systems.md")
    print("- case_study_mobile_first.md")


if __name__ == "__main__":
    anyio.run(main)
