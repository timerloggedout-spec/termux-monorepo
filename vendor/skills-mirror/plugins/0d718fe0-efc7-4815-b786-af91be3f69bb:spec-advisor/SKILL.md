---
name: spec-advisor
description: "Detect whether a software project lacks a spec-driven development system and, if so, advise which one fits (GitHub Spec Kit, OpenSpec, BMAD-METHOD, Agent OS, Taskmaster, AWS Kiro, ADR tooling) and delegate setup to that system's own installer. Use when setting up a project's spec or planning process, when asked which spec system or SDD framework a project should use, when adopting spec-driven development, or when harness-setup detects a software project with no spec system. Scans first for any existing spec or ADR registry and stays out if one is present. Does NOT author specs itself (the installed system owns that), does NOT build the .claude/ agent harness (that is harness-setup), does NOT create Claude Code components (that is plugin-dev or skill-creator), and does NOT choose an issue or bug tracker (that is tracker-advisor)."
model: inherit
---

# Spec advisor — choose and set up a spec-driven development system

When a software project has no spec-driven development (SDD) system, this skill helps the user
**choose** a fitting one and **delegates setup to that system's own installer**. It never authors
specs, PRDs, or ADRs — the installed system owns its workflow. The skill advises; it writes
nothing of its own except by running the chosen system's installer, and only after explicit
approval.

It is offline-first. Everything needed to scan, recommend, and name an install command is in the
curated reference and the shared detection signatures; the network is reached only with the user's
say-so (see the online policy in `references/spec-systems.md`).

## What this skill is not — and which skill to use instead

The "no duplication" boundary is the point of this skill, so it is worth stating as hard limits.
This skill does **not**:

| Does NOT | Use instead |
|---|---|
| Author specs, PRDs, or ADRs | the **installed system** — it owns its workflow |
| Choose or set up an issue tracker | **tracker-advisor** |
| Build the `.claude/` agent harness (agents, skills, orchestrator) | **harness-setup** |
| Assess how well a harness is used | **harness-review** |
| Create Claude Code components (skills, agents, plugins) | **plugin-dev / skill-creator** |
| Give one-shot Claude Code automation recommendations | **claude-code-setup** |
| Push a spec system when one is already present | nothing — the scan reports and stops |
| Write to `CLAUDE.md` | nothing — the chosen system's on-disk artifacts are self-evident |

A spec system is a *project process*, not a role-tool that agents call — so it is also kept out
of the harness `tools.md` registry. If the request is to build or change the agent harness, that
is `harness-setup`; if it is to assess one, that is `harness-review`. This skill is only about
the project's spec/planning process.

## The flow

Run these in order. Each gate is an off-ramp: the skill is advisory, not coercive, so a "no"
anywhere ends the run cleanly.

### Step 0 — Scope check: is this a software project?

SDD systems are for building software. Confirm the project is software before going further —
look for a manifest or source: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
`pom.xml`, a `*.csproj`, `Gemfile`, and the like. If the project is not software (docs, content,
data, ops config with no codebase), explain briefly that an SDD system is not the right tool and
**stop**. Recommending one here would be pushing a process the project has no use for.

### Step 1 — Scan first: is a spec system already present?

Using `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md`, scan for any existing spec system **or** ADR registry.
**If one is found, report what is present and where, then stop.** Do not push a second system on
top of one already in use — an existing process is the user's decision, and stacking a second SDD
system creates exactly the duplication this skill exists to avoid. This is a read-only report; the
scan writes nothing. The disambiguation rules (the shared `requirements/design/tasks` triple
resolved by parent directory; BMAD v4 vs v6; ADR signals) are in that reference — apply them
before concluding.

### Step 2 — Opt-in gate: offer a recommendation

If no system is found, offer to recommend one. This is the opt-in gate: a "no" ends the run
cleanly. Offering is the default; nothing past this point happens without the user's yes.

### Step 3 — Profile for fit

A good recommendation depends on the project's shape, so gather a few quick signals — by asking,
or by inferring from what Step 0 already saw:

- **Greenfield or brownfield** — a fresh repo tolerates a heavier pipeline; an existing codebase
  usually wants lighter, change-scoped specs.
- **Solo or team** — team workflows benefit from approval steps and named roles; a solo dev
  rarely wants the ceremony.
- **Process appetite** — anywhere from lightweight decision records (ADRs) to a full agile
  pipeline with personas.
- **Agent or IDE already in use** — an IDE/AWS commitment points one way (Kiro); a Claude
  Code-centric flow points another.

### Step 4 — Recommend (offline)

From the curated shortlist and the **selection decision tree** in `references/spec-systems.md`,
present **2–3 best-fit candidates** with rationale — not a single verdict. Before finalizing,
**offer** the opt-in discovery search (a broad "is there anything newer than the shortlist?" web
search); run it **only on an explicit yes**, and if it stalls or the environment is offline, fall
back silently to the curated data. Then the **user picks one explicitly**. Do not choose on their
behalf.

### Step 5 — Delegate setup

For the selected system:

1. **Optionally fetch current setup details** from that system's **official repository** (the URL
   in its profile) — install command and docs. This is the authoritative fetch (online form b),
   a precise pull from the canonical source, not a broad search. Skip it offline and use the
   curated install command.
2. **Present the install command and get explicit approval before executing it.** An install is
   an exec-and-write — it changes the user's repo and environment — so it is gated exactly like
   harness-setup's change manifest. State the command, what it will create, and where.
3. **Run or guide the system's own installer.** Then **confirm what was created and where**.
4. **Never author specs.** Once the system is installed, its own workflow takes over. The skill's
   job ends at a working, confirmed install.

**IDE special case — AWS Kiro.** Kiro is an IDE, not a repo package. A skill cannot install an
IDE into a repository, so for Kiro this is **detect-and-advise only**: explain what it is, point
the user at the official source (kiro.dev), and stop. Do not run an installer or hand-scaffold
`.kiro/`. The Kiro caveat in `references/spec-systems.md` has the detail.

## Error handling and graceful degradation

- **Offline, or a search stalls** — fall back to the curated data; never block on the network. The
  offline path is complete on its own.
- **Detection ambiguity** — resolve the shared `requirements/design/tasks` triple by parent
  directory first (per `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md`); if still ambiguous,
  report exactly what was found and ask, rather than guessing the system.
- **Installer failure** — apply the failure contract:
  1. **Report plainly** — the command run, the error, and the system's official troubleshooting
     source. Do not partially hand-roll the setup; a half-installed system is worse than a clean
     failure the user can retry.
  2. **Record nothing** — a failed install leaves no coordination context; the project still
     counts as having no spec system.
  3. **Leave a clean retry path** — name any artifacts the failed installer left behind so the
     user can remove them and retry; do not delete them without the user's say-so.
  4. **Tell the caller** — when invoked from `harness-setup`, state the outcome explicitly:
     "install failed — proceed as if no system is present," so nothing downstream assumes the
     system exists.
- **User declines at any gate** — stop cleanly. The skill is advisory; an off-ramp taken is a
  valid outcome, not a failure.

## References

- `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md` — the scan-first knowledge: the
  consolidated path→system table and the disambiguation rules (triple-by-parent-dir, BMAD v4/v6,
  ADR signals). Shared with `harness-setup`, which reads it to detect an installed system.
- `references/spec-systems.md` — the per-system profiles (official repo/docs URL, install command,
  philosophy, Claude Code affinity, maturity, best-fit), the selection decision tree, the Kiro/IDE
  caveat, and the online policy.
