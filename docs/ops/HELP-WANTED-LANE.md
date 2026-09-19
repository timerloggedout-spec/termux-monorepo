# Help-Wanted Lane (Production) — EXECUTE

**Status:** LIVE + **adaptive cadence** + **neighbor-safe** (idempotent claims, skip closed).
**Parallel / adaptive:** `docs/ops/HELP-WANTED-PARALLEL.md`
**Living board:** `docs/ops/HELP-WANTED-STATUS.md` → generated `docs/ops/generated/help-wanted-status.md`

## Why

Scan FOSS → CPPH rank → claim **once** → **upstream PR into the author's repo**. Feed evidence into workbench benchmarks. Predecessor to bug & bounty hunter. 2017 React UI is predecessor only.

## Working well with others

| Rule | Behavior |
|------|----------|
| Claim idempotent | Re-runs do **not** re-post claim marker |
| Closed issues | Default **skip** (claim + contribute) |
| Maintainer routing | Respect “fix upstream / use feature fork” (e.g. codex-termux parity vs [codex-vl](https://github.com/DioNanos/codex-vl)) |
| Stake ≠ final fix | Replace stake with real patch or close |
| No spam | Prefer mutual threads still **open** and needing code |

## Cadence (adaptive)

| Piece | Frequency |
|-------|-----------|
| Scout | **Every 2h** + dispatch |
| Execute | **Every 4h** + dispatch; daily budget gate |
| Safe parallel writes | **2–3** concurrent (token pool) |

## Delivery hierarchy

1. **PRIMARY — upstream-pr** — author's repo.
2. **FALLBACK — fork-offer / notice** — only if primary blocked.
3. **PARALLEL NOTICE** — optional alongside primary.

## Components

| Path | Role |
|------|------|
| `.agents/skills/help-wanted-lane/SKILL.md` | Agent load |
| `docs/ops/HELP-WANTED-PARALLEL.md` | Roster + limits |
| `docs/ops/HELP-WANTED-STATUS.md` | Living human-review surface |
| `scripts/ci/help_wanted_scout.py` | CPPH |
| `scripts/ci/help_wanted_claim.py` | Idempotent claim |
| `scripts/ci/help_wanted_contribute.py` | Upstream PR + fallback |
| `scripts/ci/help_wanted_evidence.py` | JSONL receipts |
| `scripts/ci/help_wanted_status.py` | Board generator |
| `.github/workflows/help-wanted-execute.yml` | Budgeted LIVE execute |

## Token order

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN`.

BIUDL. Agent-Identity: Grok (Administrator)
