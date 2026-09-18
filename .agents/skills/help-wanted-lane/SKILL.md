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
- `docs/ops/AGENT-MONIKERS.md`
- `scripts/ci/help_wanted_scout.py`
- `scripts/ci/help_wanted_claim.py`
- `.github/workflows/help-wanted-scout.yml` (every 6h)
- `.github/workflows/help-wanted-execute.yml` (dispatch + OPERATOR PAT)

## INTENT

- AUTO-PRs on **other repos** ARE the point.
- **PRIMARY delivery = upstream PR into the author's repository.**
- External issues = evaluation lanes + real help.
- Predecessor to bug & bounty hunter.

## Delivery hierarchy (non-negotiable)

1. **PRIMARY:** `upstream-pr` — open PR on the target/author repo.
2. **FALLBACK:** `fork-offer` — only if upstream PR blocked/not allowed/failed.
3. **PARALLEL NOTICE:** optional issue comment with commit URL **with** primary (or with fallback) — never a replacement for primary when primary works.

## Cadence / parallel

- Scout: **every 6 hours**.
- Execute: **dispatch only** until auto-batch.
- Safe concurrent external writes: **2–3** (OPERATOR token pool).
- Soft cap: **3 upstream PRs / token / day**.

## Operating loop

1. Scout → CPPH catalog
2. Select top-N
3. Claim
4. **upstream-pr** (fallback/notice only if needed)
5. Evidence → ledger / dashboard

## Monikers

Display only (`archW1z`, `opsSweep`, `heyVern`, …). Live pings stay `@jules` / `@gemini-cli` / etc.

## BIUDL

Agent-Identity: Grok (Administrator)
