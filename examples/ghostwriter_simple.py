#!/usr/bin/env python3
"""Simple Business-Tech Ghostwriter Agent - Quick Start

A minimal example to get started with the expert ghostwriter agent.

Usage:
    python examples/ghostwriter_simple.py
"""

import anyio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)


async def main():
    """Quick start example for the ghostwriter agent."""

    # Define the expert ghostwriter agent
    options = ClaudeAgentOptions(
        agents={
            "ghostwriter": AgentDefinition(
                description="Expert business-tech ghostwriter specialized in UX/Product Design",
                prompt=(
                    "You are a senior professional ghostwriter with deep expertise in business technology. "
                    "\n\n**Specializations:**\n"
                    "- UX and Product Design's influence on business and technology\n"
                    "- Product-led growth and design thinking\n"
                    "- Data-driven design decisions and business outcomes\n"
                    "\n**Approach:**\n"
                    "- Research-oriented with data-driven facts\n"
                    "- Cite statistics, case studies, and research\n"
                    "- Write compelling, professional content\n"
                    "- Adapt to various styles and tones\n"
                    "- Focus on clarity and engagement"
                ),
                tools=["Read", "Write", "Edit", "WebSearch", "Grep"],
                model="sonnet",
            ),
        },
    )

    # Example usage: Write a blog post
    print("Writing a blog post about UX design impact...\n")

    async for message in query(
        prompt=(
            "Use the ghostwriter agent to write a 400-word blog post about "
            "'How User Experience Design Drives Business Growth in Tech Startups'. "
            "Include relevant statistics and real-world examples."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


if __name__ == "__main__":
    anyio.run(main)
