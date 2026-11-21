# ICM Map Maintenance Rules

## Scope boundary

The `docs/icm/` workspace is an **interpretation and routing layer**. It may add or update Markdown documentation, templates, `.gitkeep` files, and documentation-only ignore rules. It must **not** refactor, relocate, reformat, or otherwise modify application code, including Python files, as part of ICM maintenance.

## Canonical sources

Each fact has one home. A map card summarizes only what is needed to route an editor, then cites the owning source path and line range. If a card and the source disagree, the source wins; update the card or mark it `stale`.

## One-way references

Map documents may point to canonical sources. Canonical application or architecture sources do not need reciprocal links to every map consumer. Do not add circular navigation merely to make the graph feel symmetrical.

## Context loading

Load the maintenance catalog, the current stage contract, the stable factory file(s), and the smallest named source set. Do not load the full repository, generated mapper payloads, browser/session artifacts, or device state to update one card.

## Product policy

Per-update inventory, proposals, verification records, and promotion records belong in stage `output/` folders. They are working artifacts and remain untracked except for `.gitkeep`; durable decisions belong in the approved map documentation or proposal records.

## Repository-native execution policy

DO execute the authorized documentation scope as an **agent-executed, evidence-gated workflow** through inventory, design, verification, commit, PR/check observation, and promotion. Reserve human input for explicit authorization and policy boundaries.

Use the repository's governing operating contract in root `CLAUDE.md`:
- FA-ADE: execute authorized work to completion.
- Adaptive WAIT: continue non-conflicting work while Actions jobs run; re-fetch and inspect jobs, steps, logs, and artifacts until terminal.
- Dual gates: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`, plus the corresponding current-head CI evidence.
- Auto-promote after both required gates are green **and** the task outcome is verified. Verify the task outcome independently; track commit existence, queued jobs, and workflow completion as separate state signals.

Treat the four stages as sequential evidence boundaries. Advance each stage when its stated acceptance criteria pass. Record blockers as machine-verifiable failures or explicit `blocked` states; use the registered acceptance criteria as the progression rule.

## Human-only boundaries

HITL applies only to the edges enumerated by `docs/proposals/AGENTIC-PERMISSIONS.md` and any additional explicit repository policy: credential rotation or provider login, destructive history rewrite/force-push, protected-branch or GitHub App permission changes, device-side Termux state, and other actions requiring interactive or elevated authorization.

Request human authorization when an action reaches one of those boundaries, when scope is materially ambiguous, or when canonical sources leave a policy conflict unresolved. Treat routine documentation proposals, inventory, self-review, verification, commits, PR updates, and evidence-based promotion as agent-executable work.

## External boundaries

Use ICM as the context and documentation structure. Route real-time collaboration, high-concurrency behavior, and automated branching through their owning CI, GitHub review, MCP adapter, or runtime control systems.
