# Help-Wanted Lane — INTENDED PURPOSE

**Status:** LIVE  
**One sentence:** Scan FOSS help-wanted → rank → claim once → open **upstream PR** into the author’s repo → follow maintainer feedback → show evidence on the dashboard.

This is **not** a place for one-off hard-coded PR patch jobs. Those are noise.

## Pipeline (only this)

```text
scout (2h)          rank help-wanted / good-first-issue (CPPH)
       │
       ▼
execute (4h)        claim (idempotent) → fork/patch → PRIMARY upstream PR
       │              FALLBACK notice only if primary blocked
       ▼
followup (2h)       poll OUR open PRs with CHANGES_REQUESTED → notify + evidence
       │
       ▼
dashboard           /help-wanted/ KPIs from evidence receipts
```

| Workflow | Does |
|----------|------|
| `help-wanted-scout` | Rank candidates. Optional chain → execute |
| `help-wanted-execute` | LIVE claim + upstream PR. Always dispatches followup after contribute |
| `help-wanted-followup` | **Only** poll CHANGES_REQUESTED on PRs we authored |
| `help-wanted-dashboard-deploy` | Publish status UI |

## Working with others

| Rule | Behavior |
|------|----------|
| Claim once | Marker; no spam re-claims |
| Skip closed | Default |
| PRIMARY | PR into **author’s** repo |
| FALLBACK | Notice/link only if upstream PR blocked |
| Follow-up | Generic poll — not per-repo special modes |
| Mutual threads | Prefer still-open issues needing code |

## Scripts

| Path | Role |
|------|------|
| `scripts/ci/help_wanted_scout.py` | CPPH rank |
| `scripts/ci/help_wanted_claim.py` | Idempotent claim |
| `scripts/ci/help_wanted_contribute.py` | Upstream PR + fallback |
| `scripts/ci/help_wanted_followup.py` | CHANGES_REQUESTED poll |
| `scripts/ci/help_wanted_evidence.py` | JSONL receipts |
| `scripts/ci/help_wanted_status.py` | Board generator |

## Tokens

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN`

## Foreign signals

`repository_dispatch` into **this** monorepo (`help-wanted-execute`, `help-wanted-followup`, …).  
True webhooks *from* foreign repos need an App install there; until then schedule + dispatch is the path.

See `HELP-WANTED-PARALLEL.md`, `HELP-WANTED-STATUS.md`, `HELP-WANTED-FOREIGN-HOOKS.md`.

Agent-Identity: Grok (Administrator)
