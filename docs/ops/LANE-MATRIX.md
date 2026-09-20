# OPERATOR Lane Matrix — LIVE SSOT

**Canonical living issue:** [#175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)  
**Updated:** 2026-09-20 14:22 PDT  
**Master tip at write:** `0570db31`  
**Agent-Identity:** Grok (Administrator)

> **Continuous production rule:** Every admin session MUST re-write this file (or a dated pulse under `docs/ops/generated/`) so Actions, dashboards, and peer agents read the same lanes. Comments alone are not SSOT.

## Promote path (only)

1. `mergeable_state=clean` (or equivalent after required reviews)
2. **Dual-gate green:** `agentic termux smoke` + repo/hygiene gate (`repo_gate.py` / `hygiene + portability gate`)
3. No Class 3/4 secrets in diff
4. Operator (not peer bot) authorizes merge

Vercel hobby 429, GitLab mirror fail, Mintlify skip → **non-gate**.

## Peer review routing (NOT primary operator)

| Role | Actor | Primary? |
|------|--------|----------|
| **Operator / promote authority** | Grok Administrator + dual-gate evidence | **YES** |
| Peer autofix / review volume | **CodeRabbit** (`.coderabbit.yaml`) | peer |
| Optional peer | Qodo, Devin, Jules (continue-only) | peer |
| Optional peer | GitHub **Copilot** review | **peer / optional only** |
| B3 AIC inference path | `copilot-requests: write` in agentic workflows | **inference quota, not operator route** |

**Hard rule:** Do not hardcode Copilot as the primary review or promote route.  
Requesting `request_copilot_review` is optional hygiene, never a gate substitute.  
`AGENT_AUTO_RESOLVE.md` lists CodeRabbit / Devin / Copilot as *event sources that summon Jules* — not as promote authorities.

## Lane definitions

| Lane | Meaning |
|------|---------|
| **promote** | clean + dual-gate green → merge |
| **wait** | checks in flight / unstable / missing dual-gate |
| **hold** | dirty base, stale skills-record, security-sensitive until rebase |
| **extract** | prefer thin slice when intent is mixed OR minesweeper overlap |
| **observe** | bot PRs (Jules/Bolt/Sentinel); do not force-merge |

### Size ≠ quality (operator correction 2026-09-20)

**Wholesale merge of large / mega PRs is allowed when they check out.**  
File count is not a reject criterion. Prefer extract only when:

- base is dirty against moved master and rebase is cheaper than conflict resolution, or
- multiple agents overlap the same paths (minesweeper), or
- Class 3/4 / secret risk is present.

Otherwise: dual-gate green → **promote** regardless of size.

## Live matrix pulse — 2026-09-20 14:22 PDT

| Item | Lane | Notes |
|------|------|-------|
| Master `0570db31` | LIVE | help-wanted 19:04Z refresh |
| #682 ML keep-alive | WAIT→promote candidate | validate-registry SUCCESS after `579dc2c0`; smoke SUCCESS; still `mergeable_state=unstable` |
| #686 session record | WAIT | smoke SUCCESS; unstable |
| #684 cadence unify | HOLD | prior registry/PR validate fail |
| #685 arrhythmic search | OBSERVE | dual-gate incomplete |
| #432 / #601 / #549 ML | EXTRACT or promote-if-green | size OK if dual-gate; prefer keep-alive already on #682 |
| #630 Jules 89-file | OBSERVE/EXTRACT | dirty minesweeper |
| #679 / #680 Jules | OBSERVE | unstable |
| #648 / #641 / #672 / #673 | HOLD / WAIT rebase | skills-record stack |

## Help-wanted / foreign-repo continuous eval

Surface: `docs/ops/generated/help-wanted-status.md` + dashboard deploy.  
Foreign open PRs need **continuous evaluation**, not one-shot comments:

1. **Redirect** — if work belongs in termux-monorepo or a governed fork, say so with link.
2. **Contribution rules** — dual-gate, no secrets, small green preferred when conflict risk high.
3. **Diverged builds** — intentionally separate repos (e.g. `gh-aw_fork`, `termux-mcp`, research hubs) stay alternate; do not force-merge upstream into monorepo without an extract PR.
4. **Feedback upgrade** — each help-wanted cycle should re-score foreign PRs (open/closed/stale) and record outcomes in generated status (already: tributes + foreign_open counts).

See `docs/ops/HELP-WANTED-FOREIGN-REPO.md`.

## Actions integration hooks

- Issue #175 is the human pulse target (one matrix comment per session max).
- This file is the **machine-readable ops SSOT** for agents and future matrix-cycle jobs.
- Skills that must load this: `evidence-led-monorepo-ops`, `adaptive-wait`, `operator-priority-matrix`, `recon-cycle`.

Agent-Identity: Grok (Administrator) · BIUDL
