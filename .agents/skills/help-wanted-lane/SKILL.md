---
name: help-wanted-lane
description: Select AND EXECUTE external help-wanted / good-first-issue / mutual-thread tasks. Auto-claim + fork + PR on other repos is in scope. CPPH ranking. Parallel roster + fork-offer. Triggers on help-wanted, external contribution, auto-PR, bounty-hunter precursor, or /continue. Load with evidence-led-monorepo-ops + adaptive-wait.
---

# Skill: help-wanted-lane

**Owner:** Grok Administrator / Oversight Scout + Evaluation population.

**Canonical paths:**
- `.agents/skills/help-wanted-lane/SKILL.md`
- `docs/ops/HELP-WANTED-LANE.md`
- `docs/ops/HELP-WANTED-PARALLEL.md` ← cadence, roster, parallel caps, fork-offer
- `docs/ops/AGENT-MONIKERS.md` ← display vs live `@`
- `scripts/ci/help_wanted_scout.py`
- `scripts/ci/help_wanted_claim.py`
- `.github/workflows/help-wanted-scout.yml` (every 6h)
- `.github/workflows/help-wanted-execute.yml` (dispatch + OPERATOR PAT)

## INTENT

- AUTO-PRs / other repos ARE the point.
- External issues = evaluation lanes + real help.
- Predecessor to bug & bounty hunter.
- Modes: **upstream-pr** | **fork-offer** (commit on our fork + issue comment with SHA link).

## Cadence / parallel (see PARALLEL.md)

- Scout: **every 6 hours**.
- Execute: **dispatch only** until auto-batch.
- Safe concurrent external writes: **2–3** (OPERATOR token pool).
- Soft cap: **3 upstream PRs / token / day**.

## Operating loop

1. Scout → CPPH catalog
2. Select top-N
3. Claim
4. upstream-pr **or** fork-offer
5. Evidence → ledger / dashboard

## Monikers

Display only (`archW1z`, `opsSweep`, `heyVern`, …). Live pings stay `@jules` / `@gemini-cli` / etc. Never `@` monikers that might be real users.

## BIUDL

Agent-Identity: Grok (Administrator)
