# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
5. [`docs/ops/PR-SCOPE-DISCIPLINE.md`](docs/ops/PR-SCOPE-DISCIPLINE.md) — **one intent per PR** (PR #42 / `src/db.py` lesson)
6. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
7. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
8. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — Operator-only edges
9. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict
10. [`docs/ops/POSITIVE-LANGUAGE.md`](docs/ops/POSITIVE-LANGUAGE.md) — preferred phrasing for agent-facing rules

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Language (agent-facing rules)

Prefer **positive directed** phrasing: state the desired action first.

| Prefer | Avoid |
|--------|--------|
| Target `master-staging` for code | “Do not push to master” as the only line |
| Keep secrets out of git | “Do not commit secrets” alone (recency still echoes the forbidden act) |
| Preserve agent shell / `gh` in trusted ADE runs | “Don’t remove agent shell access” |

Full guide: `docs/ops/POSITIVE-LANGUAGE.md`.  
**Todo:** integrate Operator’s Gemini Gem (positive-language) from Google Drive when connected.

## Hard rules

- **Code integration base:** `master-staging`.
- **Docs-only / default-branch workflows:** may target `master` so `issue_comment` events fire; keep those diffs minimal.
- **Before merge of code onto `master-staging`:** both gates green:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
  - Gate scripts live primarily on `master-staging`; run them from a staging checkout.
- **Work tracking:** every change cites an existing `docs/proposals/active/<id>/ITEMS.md` row (`Implements: <ITEM-ID>`). Add the row in the same PR or earlier.
- **One intent per PR** — workflows, app perf, Sentinel, and dashboard UX stay on separate PRs. See `docs/ops/PR-SCOPE-DISCIPLINE.md`.
- **Parked / dispositioned PRs:** treat PR #6 (TER-9) and PR #2 (Rust CI) per disposition comments only (no wholesale merge).
- **Git contents:** keep Class 3/4 artifacts (session stores, browser profiles, tokens) out of the tree.
- **Consensus:** write Review log or DEBATE.md; unposted chat stays non-binding.
- **PR body rewrites:** follow `docs/PR-SUMMARY-PROCESS.md` roster (shared multi-agent edit rights).
- **Coordination:** scan open agent PRs; prefer disjoint files; post `<!-- agent-claim -->` when claiming work.

## Agentic command surface (ADE — intentional)

Agents **run** shell, `gh`, and tools inside **trusted** CI runs. That capability is core product behavior for an Automated Agentic Development Environment.

**Keep** association gates (OWNER / MEMBER / COLLABORATOR), fork exclusion, and GEMINI.md rules.  
**Security scanners** (e.g. Aikido) that flag “agent passes commands”: treat as in-scope ADE surface — **whitelist / exclude** with that understanding.  
**Preferred path:** preserve agent command access; tighten trust boundaries rather than stripping tools.

See `docs/AGENTIC-CICD-FREE-TIER.md`.

## Agent git / GitHub identity

Commits today often show the **Operator PAT account** (`timerloggedout-spec`) as the GitHub actor even when the semantic author is an agent.

**Preferred direction (CE-23 candidate):**

| Layer | Approach |
|-------|----------|
| **Git author** | Per-agent `user.name` / `user.email` on commits (`Grok <grok@x.ai>`, `Jules <jules@google.com>`, …) — already used in trailers |
| **GitHub actor** | Separate machine users or GitHub Apps per agent so the UI shows agent identity; Operator remains committer only when required by branch protection |
| **Trailers** | Keep `Signed-off-by:` + `Agent:` / Summary-Editor fields on every PR body |

Operator may paste existing research into `docs/ops/AGENT-IDENTITY.md` when ready. Until then: set **git author** to the agent on every agent-produced commit; leave **pusher** as the authorized PAT/App.

## Authority, bypass, and delegation

| Role | May |
|------|-----|
| **Operator (human)** | Bypass proposal process for emergency / security; authorize credential rotation; merge under branch protection; resolve review conversations; delegate time-boxed authority to a named agent in writing on the issue/PR |
| **Summary-Editor / lead agent (named on PR)** | Decide scope disposition, close superseded PRs, land docs-only process fixes when user has granted “decide and do everything” for that thread |
| **Builder agents (Jules, etc.)** | Implement ITEMS rows; open focused PRs; reply on threads |
| **Review agents (Gemini, CodeRabbit, Devin)** | Flag issues; **prefer** resolving threads after a fix commit matches the finding |

**Proposal bypass** stays rare: Operator (or explicit written delegation) + short justification on the PR. Default path remains registry → ITEMS → PR.

## Debate & close

- Debate: MANIFEST Review log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
- Full rules: `docs/proposals/PROCESS.md` §§ consensus / closing.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master-staging
  → implement (minimal, single-intent diff) → PR with Implements: ID
  → gates green → merge → update ITEMS.md status
```

## Security

Credential rotation and history rewrite require **Operator** authorization.  
See `docs/SECURITY-REMEDIATION.md`.

## Review-thread resolution (human-in-the-loop → automation)

Today GitHub branch protection may require **Resolve conversation** clicks before merge. Agents can reply and fix code; **resolving** the thread often stays Operator-gated.

**Preferred automation (todo — CE-24):** a workflow that:

1. Watches `pull_request_review_comment` + push to the PR head
2. Detects agent reply + fix commit referencing the thread
3. **Waits** through bot cooldowns (CodeRabbit ~1h, etc.) via `repository_dispatch` / scheduled re-check
4. Marks the thread resolved via GraphQL when criteria match (or posts a ready-to-resolve checklist for Operator)
5. Optional: Termux/`curl_cffi` page actions only where API is insufficient (separate todo)

Design notes: `docs/ops/REVIEW-THREAD-AUTO-RESOLVE.md`.
