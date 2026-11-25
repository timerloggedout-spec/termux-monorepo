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

The Skills CLI (`npx @agentic/skills@latest`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `python3 scripts/capabilities/discover.py find "<query>" --skills-sh` - Optional authenticated fuzzy/semantic catalog search through the repository index
- `python3 scripts/capabilities/discover.py find "<query>" --skills-sh-curated` - Search the official curated first-party catalog
- `npx skills --help` - Inspect subcommands supported by the installed CLI version
- `npx skills add <owner/repo>` - Officially documented install command; select only reviewed skills

**Installation guidance:** When installing skills globally, avoid defaulting to `-g -y`; instead require explicit user confirmation for global installs and verify scope and target before proceeding.

**Browse skills at:** https://skills.sh/\n\nThe skills.sh API provides paginated, curated, detail and audit endpoints. Search uses `GET /api/v1/skills/search?q=<query>&limit=<1-200>`; multi-word queries use semantic search. API access uses a Vercel OIDC bearer token. Detail responses include a content hash and file tree; hydrate files only for selected candidates. The CLI collects anonymous telemetry containing skill name, skill files and timestamp by default; set `DISABLE_TELEMETRY=1` to opt out.

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

**Before installing any skill:**
1. Review the skill's source code, contents, and requested permissions
2. Check source reputation (official sources are more trustworthy)
3. Default to project-local installation rather than global
4. Require explicit human approval for global or non-interactive installation
5. Defer any first-time permission grant to a human (never auto-grant permissions on first install)

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command:

```bash
npx @agentic/skills@latest find [query] [--owner <owner>]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Stable identity and provenance** — record the skills.sh ID, source repository, skill slug, immutable commit/tag where available, and content hash.
2. **Security audit** — inspect the skills.sh partner audit when available. Interpret `pass`, `warn`, and `fail` with their audit timestamp; an HTTP 404 marks audit status as unavailable; retain an unknown state.
3. **Source and permissions** — inspect SKILL.md, scripts, assets, network calls, requested tools and license. Vendor publication establishes provenance; evaluate correctness and safety independently.
4. **Popularity** — use install counts and GitHub stars as discovery signals; assess quality and security separately.
5. **Duplicates** — inspect the catalog's duplicate flag and compare forks before recommending a copy.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The install command they can run
4. A link to learn more at skills.sh

Example response:

```text
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed, confirm the install scope with the user first, then install:

```bash
npx @agentic/skills@latest add <owner/repo@skill>
```

By default this installs to the project locally. Only add the `-g` flag (global, user-level install) if the user explicitly requests a global install, and never pass `-y` to skip confirmation prompts — the user should confirm the source and scope before installation proceeds.

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
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx @agentic/skills@latest init`

Example:

```text
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx @agentic/skills@latest init my-xyz-skill
```
