---
name: help-wanted-lane
description: Select AND EXECUTE external help-wanted / good-first-issue / mutual-thread tasks. Auto-claim + fork + upstream PR is primary. CPPH ranking. Neighbor-safe (idempotent claims, skip closed). Oversight + evaluation. Triggers on help-wanted, external contribution, auto-PR, bounty-hunter precursor, or /continue. Load with evidence-led-monorepo-ops + adaptive-wait.
---

# Skill: help-wanted-lane

**Owner:** Grok Administrator / Oversight Scout + Evaluation population.

**Canonical paths (in-repo — collaborator parity):**
- `.agents/skills/help-wanted-lane/SKILL.md` ← this file
- `docs/ops/HELP-WANTED-LANE.md`
- `docs/ops/HELP-WANTED-PARALLEL.md`
- `docs/ops/HELP-WANTED-STATUS.md` ← living human-review surface
- `docs/ops/HELP-WANTED-EVIDENCE-FEED.md`
- `docs/ops/SKILLS-INVENTORY.md` · root `SKILLS.md`
- `scripts/ci/help_wanted_scout.py`
- `scripts/ci/help_wanted_claim.py` ← idempotent claim
- `scripts/ci/help_wanted_contribute.py` ← upstream PR + fallback
- `scripts/ci/help_wanted_evidence.py` · `help_wanted_status.py`
- `.github/workflows/help-wanted-scout.yml` (~2h)
- `.github/workflows/help-wanted-execute.yml` (~4h + dispatch)

## INTENT

- AUTO-PRs on **other repos** ARE the point.
- **PRIMARY delivery = upstream PR into the author's repository.**
- External issues = evaluation lanes + real help.
- Predecessor to bug & bounty hunter.
- **Work well with others** — no claim spam, respect closed + maintainer routing.

## Delivery hierarchy (non-negotiable)

1. **PRIMARY:** `upstream-pr` — open PR on the target/author repo.
2. **FALLBACK:** `fork-offer` / issue notice — only if upstream PR blocked.
3. **PARALLEL NOTICE:** optional with primary — never a substitute when primary works.

## Neighbor rules

| Rule | Behavior |
|------|----------|
| Claim idempotent | One claim marker; re-runs skip post |
| Closed issues | Default **skip** (`--allow-closed` / `HELP_WANTED_ALLOW_CLOSED=1` to override) |
| Maintainer routing | Parity forks ≠ upstream logic fixes (e.g. codex-termux vs openai/codex vs codex-vl) |
| Stake ≠ final fix | Replace stake or close |

## Cadence / parallel

- Scout: **~every 2 hours** + dispatch.
- Execute: **~every 4 hours** + dispatch; daily budget gate.
- Safe concurrent external writes: **2–3** (OPERATOR token pool).
- Soft cap: tunable upstream actions / UTC day.

## Operating loop

1. Scout → CPPH catalog
2. Select top-N (prefer **open** mutual threads)
3. Claim **once**
4. **upstream-pr** (fallback/notice only if needed)
5. Evidence JSONL → status board → optional dashboard

## Mutual-thread anchors

Prefer continuing **open** threads we already touched when they still need code.

| Repo / Issue | Note |
|--------------|------|
| DioNanos/codex-termux#14 | **Closed** — do not re-claim; maintainer: logic → upstream; features → codex-vl |
| GlassHaven/Haven#273 | Mutual SAF / folder upload; stake PR may already exist |
| Kilo-Org/agentic-path#25 | Integration failures thread |
| PubDeer/astro-loop#42 | User bug/enhancement |

## BIUDL

Agent-Identity: Grok (Administrator)
