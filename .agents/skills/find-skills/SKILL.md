---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills@1.0.0` or the version pinned in `skills-lock.json`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands (always pin the CLI version):**

- `npx skills@1.0.0 find [query] [--owner <owner>]` — Search for skills interactively or by keyword
- `npx skills@1.0.0 add <package>` — Install a skill **project-locally** by default (no global flag)
- `npx skills@1.0.0 update` — Update installed skills in the current project

**Security rules:**

- Pin every `npx skills@...` invocation to an explicit version (see `skills-lock.json` / approved release).
- Default install scope is **project-local**. Do not use `--global` / `-g` or non-interactive `--yes` / `-y` unless the user explicitly approves that scope and mode.
- Do not treat install counts, GitHub stars, or source reputation as security validation.

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) for well-known skills in the domain. Rankings can help discovery but are **not** a security signal.

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command with a pinned version:

```bash
npx skills@1.0.0 find [query] [--owner <owner>]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills@1.0.0 find react performance`
- User asks "can you help me with PR reviews?" → `npx skills@1.0.0 find pr review`
- User asks "I need to create a changelog" → `npx skills@1.0.0 find changelog`

### Step 4: Review Before Recommending

**Do not recommend a skill based solely on search results.** Review the skill source, license, and contents. Prefer official or known maintainers when possible, but always require explicit user approval before install.

### Step 5: Present Options to the User

When you find relevant skills, present them with:

1. The skill name and what it does
2. The source repository
3. The **project-local** install command (pinned version)
4. A link to learn more at skills.sh

Example response:

```text
I found a skill that might help: "react-best-practices" from vercel-labs/agent-skills.

To install it project-locally (pinned CLI):
npx skills@1.0.0 add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices

Say if you want global install or non-interactive flags — those require explicit approval.
```

### Step 6: Offer to Install (with approval)

If the user wants to proceed, install **project-locally** by default:

```bash
npx skills@1.0.0 add <owner/repo@skill>
```

Only add `--global` / `-g` or `--yes` / `-y` when the user has explicitly approved global scope or non-interactive execution.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or similar collections — still review before install

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with a pinned init command

Example:

```text
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills@1.0.0 init my-xyz-skill
```
