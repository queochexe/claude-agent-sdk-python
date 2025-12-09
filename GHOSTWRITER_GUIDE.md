# Expert Business-Tech Ghostwriter Agent Guide

A specialized AI ghostwriter agent for business technology content, with expertise in UX/Product Design's influence on business outcomes.

## Quick Start

### Simple Example

```bash
python examples/ghostwriter_simple.py
```

This runs a basic example that writes a blog post about UX design's business impact.

### Full Examples

```bash
python examples/business_tech_ghostwriter.py
```

This runs multiple examples including:
- Blog posts with research and statistics
- Whitepaper sections for executives
- LinkedIn thought leadership articles
- Product design case studies

## Agent Capabilities

### Core Specializations

- **UX & Product Design**: Deep understanding of how design decisions impact business
- **Product-Led Growth**: Strategies combining design and business objectives
- **Design Thinking**: Methodologies for innovation and problem-solving
- **Data-Driven Design**: Using metrics and research to guide decisions

### Writing Strengths

✅ **Research-Oriented**: Grounds all claims in data and case studies
✅ **Data-Driven**: Cites statistics and quantifiable results
✅ **Professional Quality**: Adapts to various tones (technical, executive, conversational)
✅ **Evidence-Based**: References real-world examples and authoritative sources

### Available Tools

- **Read**: Analyze existing content and research
- **Write**: Create new content files
- **Edit**: Refine and improve existing content
- **WebSearch**: Research latest trends, statistics, and case studies
- **Grep**: Search codebases and documentation
- **Glob**: Find relevant files and resources

## Usage Examples

### 1. Blog Post with Research

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    agents={
        "ghostwriter": AgentDefinition(
            description="Expert business-tech ghostwriter",
            prompt="[Your custom prompt...]",
            tools=["Read", "Write", "WebSearch"],
            model="sonnet",
        )
    }
)

async for msg in query(
    prompt="Use the ghostwriter agent to write a blog post about "
           "design systems ROI with statistics and case studies",
    options=options
):
    print(msg)
```

### 2. Executive Content

```python
await client.query(
    "Use the ghostwriter agent to write an executive summary "
    "about AI in product design. Target: C-level executives. "
    "Length: 300 words. Include business impact data."
)
```

### 3. Technical Case Study

```python
await client.query(
    "Use the ghostwriter agent to create a case study about "
    "mobile-first design improving conversion rates. "
    "Include: Challenge, Approach, Results (with metrics), Key Takeaways"
)
```

### 4. LinkedIn Article

```python
await client.query(
    "Use the ghostwriter agent to write a LinkedIn article (800 words) "
    "on 'The Business Value of UX Research'. "
    "Audience: Product managers and tech leaders. "
    "Include industry benchmarks and examples."
)
```

## Customization

### Adjusting the Writing Style

Modify the prompt to change tone and style:

```python
prompt=(
    "You are a senior ghostwriter... "
    "\n**Writing Style:**\n"
    "- Conversational yet professional\n"
    "- Use storytelling to illustrate points\n"
    "- Keep sentences concise (max 20 words)\n"
    "- Use active voice\n"
    # ... rest of prompt
)
```

### Adding Specific Expertise

```python
prompt=(
    "You are a senior ghostwriter... "
    "\n**Additional Expertise:**\n"
    "- Fintech and payment systems\n"
    "- Enterprise SaaS products\n"
    "- Mobile app monetization\n"
    # ... rest of prompt
)
```

### Brand Voice Guidelines

```python
prompt=(
    "You are a senior ghostwriter... "
    "\n**Brand Voice:**\n"
    "- Company: [Your company name]\n"
    "- Tone: [Professional/Friendly/Bold/etc.]\n"
    "- Avoid: [Jargon/Clichés/etc.]\n"
    "- Preferred phrases: [Your key messages]\n"
    # ... rest of prompt
)
```

## Content Types

The ghostwriter excels at:

| Content Type | Use Case | Typical Length |
|-------------|----------|----------------|
| **Blog Posts** | Thought leadership, education | 500-1500 words |
| **Whitepapers** | In-depth research, authority building | 2000-5000 words |
| **Case Studies** | Showcase results, build credibility | 800-1200 words |
| **LinkedIn Articles** | Professional networking, insights | 600-1000 words |
| **Email Campaigns** | Product launches, newsletters | 200-400 words |
| **Product Docs** | User guides, API documentation | Varies |
| **Press Releases** | Announcements, media outreach | 300-500 words |

## Best Practices

### 1. Provide Clear Context

❌ **Vague**: "Write about UX"
✅ **Specific**: "Write a 500-word blog post about UX accessibility in fintech apps, targeting product managers, with statistics on ROI"

### 2. Request Research When Needed

```python
"Research the latest statistics on design system adoption rates,
 then write an executive summary citing 3-5 data points"
```

### 3. Specify Target Audience

- C-level executives → focus on business outcomes, ROI
- Product managers → balance technical and business perspectives
- Designers → dive deeper into methodologies and processes
- Developers → emphasize technical implementation and benefits

### 4. Include Examples or References

```python
"Write a case study similar to how Airbnb documented their design
 system journey, but focused on a B2B SaaS context"
```

### 5. Iterate and Refine

```python
# First pass
await client.query("Write a blog post about design thinking")

# Refinement
await client.query(
    "Revise the previous blog post to add more data-driven examples
     and reduce it to 600 words"
)
```

## Advanced Usage

### Multi-Step Content Creation

```python
async with ClaudeSDKClient(options=options) as client:
    # Step 1: Research
    await client.query(
        "Use the ghostwriter to research and outline the key trends
         in UX design for 2025"
    )
    async for msg in client.receive_response():
        print(msg)

    # Step 2: Write
    await client.query(
        "Based on the research, write a 1000-word article about
         these trends and their business implications"
    )
    async for msg in client.receive_response():
        print(msg)

    # Step 3: Refine
    await client.query(
        "Edit the article to make it more suitable for a technical
         audience, adding specific implementation examples"
    )
    async for msg in client.receive_response():
        print(msg)
```

### Batch Content Generation

```python
topics = [
    "How Design Impacts Customer Retention",
    "The ROI of User Research",
    "Design Systems at Scale",
    "Mobile-First Design Strategies"
]

for topic in topics:
    await client.query(
        f"Use the ghostwriter to write a 400-word blog post about '{topic}'
          with research and examples. Save to blog_{topic.lower().replace(' ', '_')}.md"
    )
    async for msg in client.receive_response():
        print(msg)
```

## Tips for Best Results

1. **Be Specific**: The more details you provide, the better the output
2. **Request Research**: Always ask for data-backed content when accuracy matters
3. **Specify Length**: Set word count expectations upfront
4. **Define Audience**: Clarify who will read the content
5. **Provide Examples**: Reference similar content or styles you like
6. **Iterate**: Don't expect perfection on the first draft
7. **Use Context**: The agent can read existing files to match your style

## Common Use Cases

### Startup Founders
- Investor pitch decks (narrative sections)
- Product launch announcements
- Blog posts for thought leadership
- Social media content strategies

### Product Managers
- Product requirement documents (PRDs)
- Feature announcements
- User research summaries
- Roadmap communication

### Marketing Teams
- Content marketing campaigns
- SEO-optimized articles
- Email newsletters
- Social media posts

### UX/Design Teams
- Design system documentation
- Case study write-ups
- Process documentation
- Research report summaries

## Troubleshooting

### Output is too generic
**Solution**: Add more specific requirements, examples, and context

### Missing research/data
**Solution**: Explicitly request "research and include statistics from 2024-2025"

### Wrong tone
**Solution**: Specify the exact tone (conversational, formal, technical, etc.) and target audience

### Too long/short
**Solution**: Set clear word count limits in your prompt

## Resources

- [Claude Agent SDK Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)
- [Examples Directory](./examples/)
- [Agent Concepts](https://docs.anthropic.com/en/docs/claude-code/sdk/agents)

## Support

For questions or issues:
- Check the [examples/](./examples/) directory for more use cases
- Review the [Claude Agent SDK docs](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)
- Report bugs at [GitHub Issues](https://github.com/anthropics/claude-agent-sdk-python/issues)
