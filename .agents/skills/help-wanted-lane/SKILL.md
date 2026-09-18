---
name: help-wanted-lane
description: Select AND EXECUTE external help-wanted / good-first-issue / mutual-thread tasks. Auto-claim + fork + PR on other repos is in scope. CPPH ranking. Oversight + evaluation lane. Triggers on help-wanted, external contribution, auto-PR, bounty-hunter precursor, or /continue. Load with evidence-led-monorepo-ops + adaptive-wait.
---

# Skill: help-wanted-lane

**Owner:** Grok Administrator / Oversight Scout + Evaluation population.

**Canonical paths:**
- `.agents/skills/help-wanted-lane/SKILL.md`
- `docs/ops/HELP-WANTED-LANE.md`
- `scripts/ci/help_wanted_scout.py`
- `scripts/ci/help_wanted_claim.py` ← claim + fork scaffold
- `.github/workflows/help-wanted-scout.yml`
- `.github/workflows/help-wanted-execute.yml` ← dispatch execution

## INTENT (non-negotiable)

- **AUTO-PRs and working on other repos ARE the point.**
- Other projects' Issues are **evaluation lanes** while we get real work done and help where wanted.
- 2017 React UI (mac-s-g/github-help-wanted) is a **predecessor / superfluous** search surface — we scan FOSS to accelerate development, not rebuild that UI.
- This lane is a **predecessor to bug & bounty hunter lanes** (already noted in monorepo issues).
- Public Vercel / dashboard surfaces will show contribution stats and graphs.

## Operating loop (YOLO)

1. **Scout** → ranked catalog (CPPH).
2. **Select** top-N by score + language + evaluation value.
3. **Claim** → public comment on target issue (attribution).
4. **Fork** (if needed) → branch → implement → **open PR on target repo**.
5. **Evidence** → monorepo ledger / ACTION-EFFECTIVENESS + dashboard feed.
6. Dual-gate remains for *our* monorepo changes only; external PRs follow target norms.

## Mutual-thread anchors (user ↔ maintainer already engaged)

| Repo / Issue | Note |
|--------------|------|
| [DioNanos/codex-termux#14](https://github.com/DioNanos/codex-termux/issues/14) | Extensive mutual comments; AGENTS.md /status; Termux Codex parity |
| [GlassHaven/Haven#273](https://github.com/GlassHaven/Haven/issues/273) | Termux SAF / folder upload; long mutual thread |
| [Kilo-Org/agentic-path#25](https://github.com/Kilo-Org/agentic-path/issues/25) | User comment: Path.kilo.ai + repeated integration failures |
| [PubDeer/astro-loop#42](https://github.com/PubDeer/astro-loop/issues/42) | User bug/enhancement; maintainer replied |
| [IBM/ibm-bob#2968](https://github.com/IBM/ibm-bob/issues/2968) | Mutual with IBM support on AGENTS.md init |
| mac-s-g/github-help-wanted + `github-help-wanted_fork` | Label-search predecessor |

Prefer continuing threads we already touched when they still need code.

## CPPH (unchanged core)

Label tier · unassigned · body clarity · freshness · comments · repo health · language · no competing PR → 0–100.

## Execution guards

- Rate limits + abuse avoidance: max N external PRs per day (config).
- Claim comment required before heavy work.
- Never force-merge external; never force-push others' default branches.
- Secrets stay in Actions / Codespace secrets — never in issue text.

## BIUDL

Agent-Identity: Grok (Administrator)
