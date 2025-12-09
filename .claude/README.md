# Claude Code Configuration

This directory contains configuration for Claude Code, including custom agents, hooks, and permissions.

## 📁 Directory Structure

```
.claude/
├── agents/           # Custom agent definitions (Markdown files)
│   └── ghostwriter.md
├── settings.json     # Project settings (hooks, permissions)
└── README.md        # This file
```

## 🤖 Custom Agents

### Ghostwriter Agent

**Location**: `.claude/agents/ghostwriter.md`

Expert business-tech ghostwriter specialized in UX/Product Design's influence on business and technology.

#### How to Use in Claude Code Browser/CLI

Once this repository is connected to Claude Code, Claude will **automatically detect and use the ghostwriter agent** when appropriate. You can also explicitly request it:

**Automatic delegation** (Claude decides):
```
I need a blog post about design systems and business value
```

**Explicit request**:
```
Use the ghostwriter agent to write a 600-word blog post about
design systems ROI with statistics and case studies
```

#### Agent Capabilities

✅ Research-oriented, data-driven content creation
✅ UX and Product Design expertise
✅ Web search for latest trends and statistics
✅ Multiple content formats (blogs, whitepapers, case studies, LinkedIn)

#### Example Use Cases

**1. Blog Post:**
```
Use the ghostwriter agent to write a blog post about how
mobile UX affects conversion rates. Include recent statistics.
```

**2. Case Study:**
```
Use the ghostwriter to create a case study about improving
onboarding flow. Include before/after metrics.
```

**3. LinkedIn Article:**
```
Use the ghostwriter to write an 800-word LinkedIn article
about AI in product design for engineering leaders
```

**4. Research + Write:**
```
Use the ghostwriter to research UX accessibility trends,
then write an executive summary with ROI data
```

**5. Email Campaign:**
```
Use the ghostwriter to draft a product launch email (250 words)
highlighting our new design system for customers
```

## 🎯 How Agents Work in Claude Code

1. **Auto-Discovery**: Claude Code automatically detects agent files in `.claude/agents/`
2. **Smart Delegation**: Claude reads agent descriptions and delegates when appropriate
3. **Tool Access**: Agents can use specified tools (Read, Write, WebSearch, etc.)
4. **Model Selection**: Each agent can use a specific Claude model (sonnet, opus, haiku)

## ✏️ Creating New Agents

To add more agents, create new Markdown files in `.claude/agents/`:

```markdown
---
name: my-agent
description: >
  When to use this agent and what it's good at
tools: Read, Write, Bash
model: sonnet
---

Your agent's system prompt goes here.
Define its expertise, approach, and guidelines.
```

## ⚙️ Settings.json

The `settings.json` file contains:
- **Permissions**: Auto-approved commands (linting, testing)
- **Hooks**: Automated actions (post-edit formatting)
- **Other settings**: Project-specific configuration

Agents are NOT defined in settings.json - they're separate Markdown files in `agents/`.

## 📚 Documentation

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Settings](https://code.claude.com/docs/en/settings)
- [Python SDK Examples](../examples/)
