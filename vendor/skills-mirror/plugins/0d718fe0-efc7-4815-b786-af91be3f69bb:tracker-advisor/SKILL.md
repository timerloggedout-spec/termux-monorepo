---
name: tracker-advisor
description: "Detect whether a software project lacks an issue tracker suited to agentic work and, if so, advise which one fits (Beads, Backlog.md, git-bug, git-issues, Beans, or GitHub Issues, Linear, Jira via their official access paths) and delegate setup to that system's own installer. Use when choosing or setting up a project's issue, bug, or work tracker, when asked how agents should pull ready work or record work state, or when harness-setup detects a software project with no tracker. Scans first and stays out if a tracker is already present. Does NOT author, triage, or groom issues (the installed tracker owns that), does NOT choose a spec system or spec-derived task decomposition such as Taskmaster (that is spec-advisor), does NOT build the .claude/ agent harness (that is harness-setup), and does NOT sync two trackers with each other (harness-setup generates that, via its dual-tracker sync sub-step)."
model: inherit
---

# Tracker advisor — choose and set up an agent-suited issue tracker

When a software project has no issue tracker that agents can work — no place to pull ready work
from or write work state back to — this skill helps the user **choose** a fitting one and
**delegates setup to that system's own installer**. It never authors, triages, or grooms issues —
the installed tracker owns its workflow. The skill advises; it writes nothing of its own except
by running the chosen system's installer, and only after explicit approval.

It is offline-first. Everything needed to scan, recommend, and name an install command is in the
curated reference and the shared detection signatures; the network is reached only with the
user's say-so (see the online policy in `references/tracker-systems.md`).

## What this skill is not — and which skill to use instead

The "no duplication" boundary is the point of this skill, so it is worth stating as hard limits.
This skill does **not**:

| Does NOT | Use instead |
|---|---|
| Author, triage, or groom issues | the **installed tracker** — it owns its workflow |
| Choose a spec system, or spec-derived task decomposition (Taskmaster) | **spec-advisor** |
| Build the `.claude/` agent harness (agents, skills, orchestrator) | **harness-setup** |
| Assess how well a harness is used | **harness-review** |
| Create Claude Code components (skills, agents, plugins) | **plugin-dev / skill-creator** |
| Keep two trackers in sync (repo-native ⇄ Jira/Linear/GitHub Issues) | **harness-setup** — its dual-tracker sync sub-step generates the project's `tracker-sync` skill |
| Push a tracker when one is already present | nothing — the scan reports and stops |
| Write to `CLAUDE.md` | nothing — the chosen system's on-disk artifacts are self-evident |

A tracker is a *project process*, not a role-tool that agents call ad hoc — so, like a spec
system, it is kept out of the harness `tools.md` registry. If the request is to build or change
the agent harness, that is `harness-setup`; if it is to assess one, that is `harness-review`.
This skill is only about choosing and standing up the project's issue-tracking process.

## The flow

Run these in order. Each gate is an off-ramp: the skill is advisory, not coercive, so a "no"
anywhere ends the run cleanly.

### Step 0 — Scope check: is this a software project?

These trackers are built for software work. Confirm the project is software before going
further — look for a manifest or source: `package.json`, `pyproject.toml`, `go.mod`,
`Cargo.toml`, `pom.xml`, a `*.csproj`, `Gemfile`, and the like. If the project is not software
(docs, content, data, ops config with no codebase), explain briefly that an agent-oriented issue
tracker is not the right tool and **stop**.

### Step 1 — Scan first: is a tracker already present?

Using `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md` (the issue-trackers table), scan
for any existing tracker. **If one is found, report what is present and where, then stop.** Do
not push a second tracker on top of one already in use — stacking trackers splits the work
state, exactly the duplication this skill exists to avoid. This is a read-only report; the scan
writes nothing. Three signals need their rules from that reference before concluding:

- **git-bug is not a path** — check `git for-each-ref refs/bugs` (rule: issue trackers table).
- **`.github/ISSUE_TEMPLATE/` is a weak signal** — report "GitHub Issues appears to be in use"
  and **ask** whether it is the active tracker; if yes, stop (it is agent-reachable via `gh`);
  if no, continue (rule 5).
- **Taskmaster is spec-derived, not a general tracker** — report that spec-derived task
  tracking is covered, and continue only if the user explicitly wants a general issue tracker
  alongside it (rule 6).

### Step 2 — Opt-in gate: offer a recommendation

If no tracker is found, offer to recommend one. This is the opt-in gate: a "no" ends the run
cleanly. Offering is the default; nothing past this point happens without the user's yes.

### Step 3 — Profile for fit

A good recommendation depends on how the work runs, so gather a few quick signals — by asking,
or by inferring from what Step 0 already saw:

- **Single agent or concurrent agents** — concurrent work needs collision-safe IDs and a
  ready-work queue (Beads's home ground); a single agent tolerates anything.
- **Dependency-graph need** — does work block other work in ways agents must query, or is a
  flat list enough?
- **Human surface** — do humans want a kanban/board view (Backlog.md), or is the CLI enough?
- **Existing SaaS commitment** — a team already living in GitHub Issues, Linear, or Jira points
  at the advise-only profiles, not a new tool.
- **Git-purist vs MCP appetite** — issues as git objects (git-bug) vs markdown files vs an MCP
  surface.

### Step 4 — Recommend (offline)

From the curated shortlist and the **selection decision tree** in
`references/tracker-systems.md`, present **2–3 best-fit candidates** with rationale — not a
single verdict. Flag the early-stage entries (git-issues, Beans) as such. Before finalizing,
**offer** the opt-in discovery search (a broad "is there anything newer than the shortlist?" web
search); run it **only on an explicit yes**, and if it stalls or the environment is offline,
fall back silently to the curated data. Then the **user picks one explicitly**. Do not choose on
their behalf.

### Step 5 — Delegate setup

For the selected system:

1. **Optionally fetch current setup details** from that system's **official repository** (the
   URL in its profile) — install command and docs. This is the authoritative fetch (online form
   b), a precise pull from the canonical source, not a broad search. Skip it offline and use the
   curated install command. For the early-stage entries it is strongly recommended.
2. **Present the install command and get explicit approval before executing it.** An install is
   an exec-and-write — it changes the user's repo and environment — so it is gated exactly like
   harness-setup's change manifest. State the command, what it will create, and where.
3. **Run or guide the system's own installer.** Then **confirm what was created and where**.
4. **Never author issues.** Once the tracker is installed, its own workflow takes over. The
   skill's job ends at a working, confirmed install.

**SaaS special case — GitHub Issues, Linear, Jira.** These are services, not repo packages, so
they are **detect-and-advise only**: explain the option, name the official access path (`gh`;
the vendor MCP servers), and stop — configuring credentials is the user's call. For Linear,
Jira, and GitHub Issues, note that a repo-native tracker can be kept in sync with them:
`harness-setup` generates that (its dual-tracker sync sub-step, model in
`${CLAUDE_PLUGIN_ROOT}/shared/tracker-sync-protocol.md`) — name it and stop; this skill does
not set it up. The SaaS/MCP caveat in `references/tracker-systems.md` has the detail.

## Error handling and graceful degradation

- **Offline, or a search stalls** — fall back to the curated data; never block on the network.
  The offline path is complete on its own.
- **Detection ambiguity** — apply the disambiguation rules in
  `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md` (bare `backlog/`, the ISSUE_TEMPLATE
  weak signal, Taskmaster); if still ambiguous, report exactly what was found and ask, rather
  than guessing the system.
- **Installer failure** — apply the failure contract:
  1. **Report plainly** — the command run, the error, and the system's official troubleshooting
     source. Do not partially hand-roll the setup; a half-installed system is worse than a clean
     failure the user can retry.
  2. **Record nothing** — a failed install leaves no coordination context; the project still
     counts as having no tracker.
  3. **Leave a clean retry path** — name any artifacts the failed installer left behind so the
     user can remove them and retry; do not delete them without the user's say-so.
  4. **Tell the caller** — when invoked from `harness-setup`, state the outcome explicitly:
     "install failed — proceed as if no system is present," so nothing downstream assumes the
     tracker exists.
- **User declines at any gate** — stop cleanly. The skill is advisory; an off-ramp taken is a
  valid outcome, not a failure.

## References

- `${CLAUDE_PLUGIN_ROOT}/shared/detection-signatures.md` — the scan-first knowledge: the
  issue-trackers path→system table (plus the git-bug ref check) and the disambiguation rules
  (bare `backlog/`, ISSUE_TEMPLATE weak signal, Taskmaster boundary). Shared with
  `spec-advisor` and `harness-setup`.
- `references/tracker-systems.md` — the per-system profiles (official repo/docs URL, install
  command, philosophy, agent affinity, maturity, best-fit), the selection decision tree, the
  SaaS/MCP caveat, and the online policy.
