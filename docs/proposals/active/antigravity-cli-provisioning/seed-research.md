<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Awesome Google Antigravity CLI: setup, applications, agents, skills, and remote orchestration

The strongest architecture for your setup is to use Antigravity CLI as the local execution harness, Manus’ Cue as a remote operator/coordinator, custom agents as bounded workers, skills as reusable procedures, and hooks plus permissions as execution controls. Google documents these as distinct capabilities; a remote connection is not itself a custom-agent definition or an MCP integration.[^1][^2][^3][^4]

Below are my own curated “Awesome” tables—not a reproduction of an existing list—with direct source URLs, practical applications, and a proposed architecture for your environment.

**Scope:** Three screenshots are available here. They show the hooks panel, quota panel, and agent-discovery paths; your pasted help output supplies the broader command inventory. I treat the successful Manus connection as your reported result, not something independently established by those screenshots.[^5][^6][^7]

## 1. Awesome official documentation and reference sources

Start with these sources before installing third-party customization bundles.


| Resource | What it answers | Why it belongs in your reference library | Direct URL / source |
| :-- | :-- | :-- | :-- |
| Official CLI repository | What is the CLI? Where are public project resources? | Primary project entry point; describes the terminal-oriented execution harness. | [https://github.com/google-antigravity/antigravity-cli](https://github.com/google-antigravity/antigravity-cli) [^8] |
| Installation and quickstart | How do I install, verify, launch, and trust a workspace? | Includes platform installers, `agy --version`, first-launch configuration, and initial project workflow. | [https://antigravity.google/docs/getting-started/](https://antigravity.google/docs/getting-started/) [^9] |
| CLI command and settings reference | What do slash commands and settings actually do? | Best central reference for command syntax, JSON keys, defaults, and keyboard shortcuts. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| CLI settings and tips | How does `/config` interact with settings files and flags? | Explains persistent settings, launch-time overrides, rendering modes, editor integration, and keybindings. | [https://antigravity.google/docs/cli/using/](https://antigravity.google/docs/cli/using/) [^11] |
| CLI features | How do plugins, permissions, subagents, and background work fit together? | Strongest operational overview for your roles/skills architecture. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| Agent skills | How do I create and discover `SKILL.md` procedures? | Defines metadata, directory layout, progressive loading, and CLI-specific discovery paths. | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| Lifecycle hooks | How can execution be checked, logged, or gated? | Documents events, matching, input/output contracts, and approval decisions. | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| Plugins | How do I distribute agents, skills, rules, tools, and hooks together? | Defines the bundle format and component directories. | [https://antigravity.google/docs/plugins/](https://antigravity.google/docs/plugins/) [^12] |
| MCP integration | How do I connect external tools and services? | Covers local `stdio` and remote connections; remote configurations use `serverUrl`. | [https://antigravity.google/docs/mcp/](https://antigravity.google/docs/mcp/) [^13] |
| Remote Control | How do I control a local CLI instance from another device? | Distinguishes session-scoped tunnels from an always-on background instance. | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Authentication | How does login work on remote/SSH machines? | Describes the manual browser authorization flow used when a local browser cannot launch. | [https://antigravity.google/docs/install/](https://antigravity.google/docs/install/) [^14] |
| CLI releases | What changed between builds? | Use alongside your installed `/changelog` before adopting newer commands or behavior. | [https://github.com/google-antigravity/antigravity-cli/releases](https://github.com/google-antigravity/antigravity-cli/releases) [^15] |
| Product changelog | What changed across Antigravity surfaces? | Particularly useful for Remote Control lifecycle and compatibility changes. | [https://antigravity.google/docs/changelog/](https://antigravity.google/docs/changelog/) [^16] |
| Google skills codelab | How do I learn skill authoring through an exercise? | Guided implementation rather than reference-only documentation. | [https://codelabs.developers.google.com/antigravity/how-to-create-agent-skills-for-antigravity-cli](https://codelabs.developers.google.com/antigravity/how-to-create-agent-skills-for-antigravity-cli) [^17] |

### Version discipline matters here

Your installed command list is the authority for what your particular session exposes. Current public documentation includes commands not present in your pasted menu, such as `/boost` and `/teamwork-preview`; your menu includes `/plan`, while the current reference also documents `/planning`. Do not assume these are interchangeable or available in your build.[^10]

Similarly, Google documents `/remote-control`, not `/remote`, as the canonical session command. Preserve the working connection you already have, but use the documented name in reusable runbooks unless your local help explicitly confirms an alias.[^4][^10]

## 2. Awesome setup and configuration checklist

The following is my recommended implementation order, using the documented controls.


| Priority | Setup item | Command or location | Recommended use | Direct source |
| :-- | :-- | :-- | :-- | :-- |
| P0 | Record installed version | `agy --version` | Capture the version in every architecture/runbook snapshot. | [https://antigravity.google/docs/getting-started/](https://antigravity.google/docs/getting-started/) [^9] |
| P0 | Establish project boundary | Launch `agy` inside the intended project directory | Prefer a dedicated project over a broad home-directory workspace. | [https://antigravity.google/docs/getting-started/](https://antigravity.google/docs/getting-started/) [^9] |
| P0 | Add necessary directories explicitly | `/add-dir <path>` | Add only the additional repository/document folders required by the task. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| P0 | Inspect persistent configuration | `/config`; `~/.gemini/antigravity-cli/settings.json` | Establish a reproducible baseline before granting remote operation. | [https://antigravity.google/docs/cli/using/](https://antigravity.google/docs/cli/using/) [^11] |
| P0 | Set global approval posture | `toolPermission` | Begin with `request-review` or `strict`, rather than unrestricted execution. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| P0 | Set granular permissions | `/permissions` | Separate allowed, denied, and approval-required tools/resources. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| P0 | Evaluate execution sandbox | `enableTerminalSandbox` | Enable where supported and verify behavior on the actual host before trusting it. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| P1 | Preserve workspace boundaries | `allowNonWorkspaceAccess: false` | Keep access scoped unless a task has a specific reason to expand it. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| P1 | Configure review policy | `artifactReviewPolicy` | Use reviewable changes during architecture development and connector setup. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| P1 | Inspect custom agents | `/agents` | Confirm the expected role exists and inspect active workers and approvals. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| P1 | Add focused skills | `.agents/skills/<name>/SKILL.md` | Version project procedures alongside the project. | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| P1 | Refresh skill discovery | `/skills reload` | Reload after creating or updating skills, then verify their presence. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| P1 | Audit connected tools | `/mcp` | Begin with the minimum tool servers and credentials needed. | [https://antigravity.google/docs/mcp/](https://antigravity.google/docs/mcp/) [^13] |
| P1 | Audit execution hooks | `/hooks` | Confirm that intended checks are loaded, enabled, and targeting the right tool names. | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| P2 | Improve mobile ergonomics | `/keybindings`, rendering configuration | Tune navigation, approval, and multiline input for your terminal client. | [https://antigravity.google/docs/cli/using/](https://antigravity.google/docs/cli/using/) [^11] |
| P2 | Observe workload and context | `/tasks`, `/context`, `/usage` | Monitor background execution, context growth, and quota consumption. | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |
| P2 | Package a stable environment | `/plugin`; `agy plugin` | Turn tested customizations into a reusable bundle rather than manually copying scattered files. | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |

Your screenshot’s `/add-dir` error is consistent with invoking it without the required path argument: the documented syntax is `/add-dir <path>`.[^7][^10]

### Suggested conservative configuration baseline

Merge selected keys into the existing file; do not replace the whole configuration blindly. These keys and values are documented, but compatibility should still be checked against your installed build.[^10]

```json
{
  "toolPermission": "request-review",
  "artifactReviewPolicy": "asks-for-review",
  "allowNonWorkspaceAccess": false,
  "notifications": true,
  "verbosity": "high"
}
```

Evaluate `"enableTerminalSandbox": true` separately. Google documents native sandbox mechanisms for Linux, macOS, and Windows, but the installation material reviewed here does not establish equivalent support for native Android/Termux. Your screenshots show a Termux-style filesystem; a functioning CLI does not, by itself, establish functioning sandbox isolation.[^9][^1][^7]

## 3. Awesome architecture: roles versus skills versus tools

The central distinction is: agents own delegated work; skills describe how to do work; MCP exposes tools; hooks intervene in execution; plugins distribute these components.[^2][^3][^12][^1]


| Layer | Responsibility | Antigravity mechanism | What I would put there | Direct source |
| :-- | :-- | :-- | :-- | :-- |
| External coordinator | Translate your goals into bounded assignments and review results | Manus operating through your existing Remote Control connection | Task dispatch, progress checks, approval routing, handoff summaries—not an assumed native agent registration | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Primary session | Maintain the project objective and delegate subtasks | Main CLI conversation | Plan, task dependencies, acceptance criteria, integration decisions | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| Worker identity | Define a specialized background role | Custom agents/subagents; `/agents` | Researcher, implementer, verifier, documentation maintainer | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| Reusable procedure | Provide a repeatable workflow | `SKILL.md`; `/skills`; generated slash commands | Source verification, connector audit, test-driven fix, documentation synchronization | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| Behavioral constraints | Express conventions and operating rules | Plugin `rules/` | Evidence requirements, naming conventions, handoff format | [https://antigravity.google/docs/plugins/](https://antigravity.google/docs/plugins/) [^12] |
| External capability | Access services and data | MCP servers | Repository inspection, documentation tools, database reads | [https://antigravity.google/docs/mcp/](https://antigravity.google/docs/mcp/) [^13] |
| Execution intervention | Apply checks at defined lifecycle events | Hooks | Preflight checks, policy decisions, formatting, audit records | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| Authorization boundary | Decide which operations are permitted | `/permissions`, settings, sandbox | Read/write scope, command approval, access restrictions | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| Distribution unit | Ship a coherent operating package | Plugin | Versioned agents + skills + rules + hooks + MCP definitions | [https://antigravity.google/docs/plugins/](https://antigravity.google/docs/plugins/) [^12] |
| Observation and review | Inspect work before accepting it | `/tasks`, `/agents`, `/diff`, `/artifact`, `/context` | Worker monitoring, evidence inspection, change review | [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/) [^10] |

Rules and skill instructions should not be treated as substitutes for permission enforcement. Google exposes explicit authorization controls and hook decisions—including `deny` and `force_ask`—for execution gating.[^3][^1]

### Proposed role roster for your environment

These are my proposed roles, not claims that these named agents ship with Antigravity. The documented subagent framework supports delegation and allows the primary agent to control worker capabilities, including MCP and write access.[^1]


| Proposed role | Primary assignment | Suggested access posture | Reusable skills to author | Required handoff |
| :-- | :-- | :-- | :-- | :-- |
| Coordinator | Decompose objectives; assign work; reconcile results | Delegation enabled; restricted direct publishing | Task decomposition, dependency planning | Plan, owners, dependencies, acceptance criteria |
| Source researcher | Find primary documentation and validate claims | Read/search only where practical | Source verification, evidence extraction | Claim/source matrix with uncertainties |
| Repository cartographer | Map repositories, components, dependencies, and interfaces | Read-only filesystem and repository tools | Architecture inventory, dependency mapping | Component map and relevant file paths |
| Implementer | Make a bounded change | Write access limited to assigned workspace | Minimal patch, migration procedure | Patch summary and executed checks |
| Independent verifier | Test the implementation against acceptance criteria | Test execution; avoid silently rewriting the implementation | Regression testing, adversarial review | Pass/fail evidence and unresolved defects |
| Connector architect | Define MCP integration and authentication boundaries | Configuration reads; approved configuration writes | Connector audit, tool inventory | Tool schema, scopes, authentication and failure matrix |
| Documentation maintainer | Update reference tables and project documentation | Documentation-only writes initially | Documentation synchronization, terminology audit | Updated docs with evidence and change summary |
| Release steward | Prepare an approved deliverable | Publishing/deployment approval required | Release checklist, rollback planning | Release notes, verification record, rollback instructions |

A useful default is one coordinator, one implementer, and one independent verifier. Add specialists when the task justifies them rather than constructing a large swarm before the handoff contracts work.

## 4. Awesome filesystem and packaging reference

Be especially careful with the distinction between App/IDE paths and CLI paths.


| Component | Documented or observed location | Status / caution | Direct source |
| :-- | :-- | :-- | :-- |
| CLI settings | `~/.gemini/antigravity-cli/settings.json` | Official CLI configuration location | [https://antigravity.google/docs/cli/using/](https://antigravity.google/docs/cli/using/) [^11] |
| CLI keybindings | `~/.gemini/antigravity-cli/keybindings.json` | Official custom keybinding location | [https://antigravity.google/docs/cli/using/](https://antigravity.google/docs/cli/using/) [^11] |
| Project skills | `<workspace>/.agents/skills/<skill>/SKILL.md` | Official workspace location | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| Global CLI skills | `~/.gemini/antigravity-cli/skills/<skill>/SKILL.md` | Use the CLI-specific section of the documentation | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| Global App/IDE skills | `~/.gemini/config/skills/<skill>/SKILL.md` | Different surface; do not assume this is the documented global CLI path | [https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/) [^2] |
| Project hooks | `.agents/hooks.json` | Official workspace location | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| Global hooks | `~/.gemini/config/hooks.json`, or hooks inside CLI settings | Official documented alternatives | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| Installed CLI plugins | `~/.gemini/antigravity-cli/plugins/<plugin>/` | Staged plugin components | [https://antigravity.google/docs/cli/features/](https://antigravity.google/docs/cli/features/) [^1] |
| Plugin agent definitions | `<plugin>/agents/<agent-name>.md` | Official plugin layout; do not assume it uses the same schema as standalone agent files | [https://antigravity.google/docs/plugins/](https://antigravity.google/docs/plugins/) [^12] |
| Standalone workspace agents | `<workspace>/.agents/agents/<agent-name>/agent.md` | Shown by your installed `/agents` panel; verify against your build before templating | Your screenshot [^7] |
| Standalone global agents | `~/.gemini/config/agents/<agent-name>/agent.md` | Shown by your installed panel; keep separate from CLI global skill paths | Your screenshot [^7] |

A proposed plugin layout, following Google’s documented bundle structure, would be:[^12]

```text
research-operations/
├── plugin.json
├── mcp_config.json
├── hooks.json
├── agents/
│   ├── source-researcher.md
│   ├── implementer.md
│   └── independent-verifier.md
├── skills/
│   ├── source-audit/
│   │   └── SKILL.md
│   ├── connector-audit/
│   │   └── SKILL.md
│   └── verify-deliverable/
│       └── SKILL.md
└── rules/
    ├── evidence-policy.md
    └── handoff-contract.md
```

This is a layout proposal, not a complete installable plugin: the manifest and agent definitions still need valid contents for the target build.

## 5. Awesome skills to build first

Google recommends focused skills with clear descriptions. The CLI exposes discovered skills as slash commands, and the agent can also select relevant skills from their descriptions.[^2]


| Proposed skill | Best application | Expected output | Evaluation criterion | Supporting mechanism |
| :-- | :-- | :-- | :-- | :-- |
| `source-audit` | Technical research and documentation validation | Claim/source table with exact URLs and uncertainty labels | Every material claim has evidence or is marked unverified | Skills instructions and resources [^2] |
| `workspace-map` | Understanding an unfamiliar repository | Component inventory, entry points, dependencies | Another worker can locate the relevant implementation without repeating discovery | Skills plus code-search tools [^2][^1] |
| `connector-audit` | MCP and external-service integration | Server inventory, tool schemas, scopes, authentication requirements | Read/write boundaries and failure modes are explicit | Skills plus MCP [^2][^13] |
| `bounded-implementation` | Controlled engineering changes | Minimal patch tied to an approved objective | No unrelated modifications; checks recorded | Skills plus diff review [^2][^10] |
| `verify-deliverable` | Independent quality assurance | Acceptance-test matrix and reproducible commands | Conclusions reference actual execution or inspected artifacts | Skills plus task/artifact inspection [^2][^10] |
| `documentation-sync` | Maintaining knowledge bases alongside code | Updated docs and a change/evidence summary | Public interfaces and documentation agree | Skills with optional scripts/resources [^2] |
| `agent-handoff` | Manus-to-CLI and worker-to-worker coordination | Structured task/result record | A new worker can continue without reconstructing the entire conversation | Skills and subagent coordination [^2][^3] |
| `release-readiness` | Preparing approved delivery | Test results, change summary, known risks, rollback notes | Missing gates block the recommendation to release | Skills, hooks, permissions [^2][^3][^1] |

### Minimal skill example

Place this in `.agents/skills/source-audit/SKILL.md`. Its frontmatter follows Google’s documented skill format; the workflow below is my proposed research procedure.[^2]

```markdown
---
name: source-audit
description: Audits technical claims against primary documentation and produces a claim-to-source evidence table. Use when validating CLI behavior, configuration paths, integration capabilities, or architecture documentation.
---

# Source Audit

1. Record the installed product version and the question being verified.
2. Separate observed local behavior from publicly documented behavior.
3. Prefer official documentation and release notes.
4. Record a direct source URL for each material claim.
5. Mark conflicts, version differences, and unverified assumptions.
6. Do not infer native integrations from successful browser access.
7. Return:
   - Claim
   - Evidence
   - Direct URL
   - Applicable version or surface
   - Confidence
   - Unresolved question
```

After creation, run `/skills reload` and inspect `/skills`. The skill should then be available through the CLI’s skill-to-slash-command mechanism.[^1][^2]

## 6. Awesome hooks and execution controls

Your screenshot shows five hook types. Current documentation lists those events plus `SessionStart`, which is another reason to distinguish your installed build from the latest reference.[^3][^5]


| Event | Useful application | Important implementation detail | Direct source |
| :-- | :-- | :-- | :-- |
| `SessionStart` | Inject environment identity, project instructions, and startup diagnostics | Runs once at conversation start; verify availability in your build | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| `PreToolUse` | Gate risky commands, file changes, or external operations | Can return decisions such as `deny`, `ask`, or `force_ask` | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| `PostToolUse` | Record tool outcomes or run narrowly targeted formatting | Receives tool details and an optional error field | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| `PreInvocation` | Inject brief reminders or current task constraints | Runs before a model call; keep injected context focused | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| `PostInvocation` | Inspect execution progress or influence continuation | Supports injected steps and termination behavior | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |
| `Stop` | Check completion requirements before ending | `fullyIdle` distinguishes a finished agent from one with active background work; `continue` can restart the loop | [https://antigravity.google/docs/hooks/](https://antigravity.google/docs/hooks/) [^3] |

My recommended control stack is:

1. Permissions define the authorization baseline.
2. Sandbox containment limits execution where supported.
3. Hooks add targeted checks and audit records.
4. Independent verification checks the deliverable.
5. Human approval remains required for publishing, deployment, credential changes, and other consequential external writes.

The first three are separate documented mechanisms; the final two are my proposed operating policy for your environment.[^3][^1]

Avoid an unconditional `Stop → continue` hook. Since that response re-enters the execution loop, your own completion hook should have bounded retries and a clear failure outcome rather than perpetually demanding more work.[^3]

## 7. Awesome Manus/Cue + Remote Control operating patterns

The documented Remote Control model keeps execution on the host machine and exposes a browser interface for interacting with the session. It does not, by itself, establish a native Manus integration, structured inter-agent messaging contract, or MCP connection.[^13][^4]


| Pattern | Command / mechanism | Best fit | Limitation or boundary | Direct source |
| :-- | :-- | :-- | :-- | :-- |
| Attach to the current interactive session | `/remote-control` or `/remote-control on` | Your existing live terminal workflow | Tunnel lasts only as long as that CLI instance | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Start an interactive session already connected | `agy --remote-control` | Repeatable project startup | Each process has a session-specific instance identity | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Disconnect remote access but retain local session | `/remote-control off` | End a remote operating window | Remote tunnel closes; terminal remains running | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Maintain a background remote instance | `agy remote-control start` | Longer-lived host availability | Host must remain on; verify daemon support and behavior on your environment | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Inspect background instance | `agy remote-control status` | Connection diagnostics | Reports daemon status and instance identity, not task correctness | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Stop background remote instance | `agy remote-control stop` | Explicit teardown | Stops and unregisters the daemon | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Separate work by session | Multiple project sessions with remote control | Different projects or independent workstreams | Separate sessions are not automatically a coordinated agent team | [https://antigravity.google/docs/remote-control/](https://antigravity.google/docs/remote-control/) [^4] |
| Connect external systems structurally | MCP configuration | Tool-based data and service integration | Separate from browser Remote Control | [https://antigravity.google/docs/mcp/](https://antigravity.google/docs/mcp/) [^13] |

Google’s documented browser access flow uses the same Google Account as the host instance. For Cue’s access, document the actual authentication arrangement and approval authority rather than treating the printed URL as a complete authorization model. Do not distribute session URLs or account credentials as general project documentation.[^4]

### Proposed task contract for Cue

Use a structured handoff even if Cue currently communicates through the browser interface. This is my proposed coordination format, not a native Antigravity API:

```yaml
task_id: AGY-001
objective: Audit and document the project's MCP configuration.
workspace: /absolute/path/to/project

allowed_actions:
  - inspect project files
  - inspect configured MCP servers
  - draft documentation

approval_required:
  - installing plugins or packages
  - modifying credentials
  - changing tool permissions
  - publishing or deploying
  - writing to external services

acceptance_criteria:
  - inventory every configured server
  - distinguish read tools from write tools
  - identify authentication requirements
  - record direct documentation URLs
  - mark unverified assumptions

handoff:
  - summary
  - files_changed
  - checks_executed
  - evidence
  - unresolved_questions
  - approval_requests
```


## 8. Awesome applications: where this setup is most useful

These are my use-case rankings for your research, connector, and agent-development work—not benchmark claims.


| Application | Fit | Suggested workflow | Why the documented capabilities support it |
| :-- | :-- | :-- | :-- |
| Repository architecture discovery | High | Cartographer → researcher → architecture summary | Workspace code search, subagents, and background tasks support parallel investigation. [^1] |
| Connector and MCP engineering | High | Inventory → schema/scopes audit → bounded configuration change → verification | MCP connections and permission controls provide the necessary tool and access layers. [^13][^1] |
| Documentation and knowledge-base maintenance | High | Source audit → implementation/documentation comparison → reviewable update | Skills can package repeatable procedures; diff and artifact panels support review. [^2][^10] |
| Test-backed code maintenance | High | Implementer → independent verifier → diff review | Asynchronous workers can run builds/tests while the primary session coordinates changes. [^1] |
| Mobile supervision of host-based work | High | Host executes; remote browser monitors and approves | Remote Control retains the host environment while exposing live interaction remotely. [^4] |
| Reusable research operations | High, with explicit evidence rules | Researcher → claim/source matrix → verifier | Skills can include procedures, schemas, scripts, and reference resources. [^2] |
| Recurring maintenance checks | Conditional | `/schedule` → bounded inspection → report | Scheduling can wake the agent with a one-time or recurring instruction; host/runtime availability still needs operational testing. [^10] |
| Long-running autonomous engineering | Conditional | Explicit goal → bounded workers → tests → completion review | `/goal` and subagent capabilities support extended work, but do not replace acceptance criteria or authorization boundaries. [^10][^1] |
| Production deployment or external publishing | Approval-gated | Prepare → verify → request approval → execute | Permission controls and hook gates can separate preparation from consequential execution. [^1][^3] |

## 9. Awesome community collections—use as raw material, not automatic trust

These are useful discovery sources, but community claims of “battle-tested” quality or cross-client compatibility are not equivalent to validation on Antigravity CLI 1.4.4.


| Collection | Useful material | My recommended treatment | Direct URL / source |
| :-- | :-- | :-- | :-- |
| Agentic Awesome Skills / AAS Core | Broad skill library, bundles, ordered workflow playbooks | Select a small subset; inspect instructions, scripts, permissions, and licensing before use | [https://github.com/sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) [^18] |
| Antigravity Awesome Skills fork | Role bundles and workflow metadata | Compare provenance with upstream; avoid installing duplicated or stale variants | [https://github.com/benjaminasterA/antigravity-awesome-skills](https://github.com/benjaminasterA/antigravity-awesome-skills) [^19] |
| Antigravity Skills | Skills ported from another coding-agent ecosystem | Treat ports as adaptation candidates; validate paths and tool assumptions | [https://github.com/rmyndharis/antigravity-skills](https://github.com/rmyndharis/antigravity-skills) [^20] |

For a valid plugin package, Google documents installation from an official marketplace, local directory, or GitHub repository. A repository containing loose `SKILL.md` files is not automatically a valid plugin: inspect its structure before choosing the installation method.[^12][^1]

## 10. Recommended first implementation

For your current setup, I would build a small, versioned “research operations” environment before expanding to a large agent library:


| Stage | Deliverable | Acceptance check |
| :-- | :-- | :-- |
| 1. Baseline | Version record, settings snapshot, project boundary, connection mode | Reproduce the same workspace and approval posture in a new session |
| 2. Skills | `source-audit`, `connector-audit`, `agent-handoff`, `verify-deliverable` | Each appears in `/skills` and succeeds on a small test assignment |
| 3. Roles | Coordinator, researcher, implementer, independent verifier | Each role produces the agreed handoff without exceeding its assigned scope |
| 4. Controls | Permission rules, tested preflight checks, audit logging | A deliberately disallowed action is actually blocked or routed for approval |
| 5. Remote operation | Cue task contract and reconnect/teardown runbook | Cue can resume the correct session and distinguish “finished,” “blocked,” and “awaiting approval” |
| 6. Packaging | Versioned plugin containing the validated components | Reinstall in a separate test workspace and reproduce behavior |

This sequence builds on Antigravity’s documented skill discovery, plugin packaging, subagent monitoring, permissions, and Remote Control lifecycle, while keeping your proposed Manus coordination layer explicit and independently testable.[^4][^12][^1][^2]

<span style="display:none">[^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33]</span>

<div align="center">⁂</div>

[^1]: https://antigravity.google/docs/cli/features/

[^2]: https://antigravity.google/docs/skills/

[^3]: https://antigravity.google/docs/hooks/

[^4]: https://antigravity.google/docs/remote-control/

[^5]: 1000011642.jpeg

[^6]: 1000011641.jpeg

[^7]: 1000011640.jpeg

[^8]: https://github.com/google-antigravity/antigravity-cli

[^9]: https://antigravity.google/docs/getting-started/

[^10]: https://antigravity.google/docs/cli/reference/

[^11]: https://antigravity.google/docs/cli/using/

[^12]: https://antigravity.google/docs/plugins/

[^13]: https://antigravity.google/docs/mcp/

[^14]: https://antigravity.google/docs/install/

[^15]: https://github.com/google-antigravity/antigravity-cli/releases

[^16]: https://antigravity.google/docs/changelog/

[^17]: https://codelabs.developers.google.com/antigravity/how-to-create-agent-skills-for-antigravity-cli

[^18]: https://github.com/sickn33/agentic-awesome-skills

[^19]: https://github.com/benjaminasterA/antigravity-awesome-skills

[^20]: https://github.com/rmyndharis/antigravity-skills

[^21]: https://antigravity.google/product/antigravity-cli/

[^22]: https://www.oreilly.com/live-events/agentic-coding-with-google-antigravity-cli/0642572224547/

[^23]: https://github.com/google-gemini/gemini-cli/issues/27304

[^24]: https://github.com/google-gemini/gemini-cli/discussions/27274

[^25]: https://github.com/google/agents-cli/issues/26

[^26]: https://dev.to/gde/google-antigravity-gemini-4-argon-how-to-load-your-global-agents-skills-2cek

[^27]: https://antigravity.google/docs/features/

[^28]: https://antigravity.google/docs/overview/

[^29]: https://www.reddit.com/r/google_antigravity/comments/1qcuc8u/i_aggregated_58_skills_for_antigravity_into_one/

[^30]: https://skillsllm.com/skill/antigravity-awesome-skills

[^31]: https://www.cloudvyn.com/blog/best-github-repos-antigravity-skills-2026

[^32]: https://daily.dev/posts/iwmwvjy5z

[^33]: https://lobehub.com/skills/aradotso-trending-skills-antigravity-awesome-skills

