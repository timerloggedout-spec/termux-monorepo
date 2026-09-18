---
name: help-wanted-lane
description: Select AND EXECUTE external help-wanted / good-first-issue / mutual-thread tasks. Auto-claim + fork + upstream PR is primary. CPPH ranking. Parallel roster. fork-offer is FALLBACK or parallel notice only. Triggers on help-wanted, external contribution, auto-PR, bounty-hunter precursor, or /continue. Load with evidence-led-monorepo-ops + adaptive-wait.
---

# Skill: help-wanted-lane

**Owner:** Grok Administrator / Oversight Scout + Evaluation population.

**Canonical paths:**
- `.agents/skills/help-wanted-lane/SKILL.md`
- `docs/ops/HELP-WANTED-LANE.md`
- `docs/ops/HELP-WANTED-PARALLEL.md`
- `scripts/ci/help_wanted_scout.py`
- `scripts/ci/help_wanted_claim.py`
- `.github/workflows/help-wanted-scout.yml`
- `.github/workflows/help-wanted-execute.yml`

## INTENT

- AUTO-PRs on **other repos** ARE the point.
- **PRIMARY delivery = upstream PR into the author's repository.**
- External issues = evaluation lanes + real help.
- Predecessor to bug & bounty hunter.

## Live evidence (2026-09-18)

- Lane merged: monorepo #609.
- First upstream PR: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81) (`docs(layout): refresh stale ponytail comments`).
- Cadence on master: scout 2h / execute 4h + daily budget (see `docs/ops/HELP-WANTED-LANE.md`).

## Delivery hierarchy

1. **PRIMARY:** `upstream-pr`
2. **FALLBACK:** `fork-offer`
3. **PARALLEL NOTICE:** optional; never a substitute for primary.

## Operating loop

1. Scout → CPPH catalog
2. Select top-N
3. Claim
4. **upstream-pr**
5. Evidence → ledger / dashboard

Do not comment-storm our monorepo PRs to wake CI.

BIUDL. Agent-Identity: Grok (Administrator)
