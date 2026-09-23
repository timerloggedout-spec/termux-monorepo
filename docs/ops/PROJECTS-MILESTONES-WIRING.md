# Projects & Milestones Wiring (SSOT)

**Session:** 2026-09-21 15:21 PDT  
**Agent-Identity:** Grok (Administrator)  
**Priority hub:** Issue #175 · Credentials: Issue **#184** (names/scopes only)

## Decision: Option A — GitHub Actions plane

Interactive Grok connector Projects API remains 403. **Wiring is Actions-only** using Project-capable secrets by **name** (`OPERATOR_GITHUB_TOKEN` || `OPERATOR_TOKEN` || `ARCHWIZ_GITHUB_TOKEN`).

| Surface | Role | Status |
|---------|------|--------|
| **Stepie goal 2087** | Planning utility | LIVE |
| **Linear P-TER-1** | Execution track M1–M6 | LIVE |
| **GHA `ops-operator-matrix-project-sync.yml`** | Add issue/PR → Operator Matrix board | **ADDED** (this PR) |
| **GHA `dependency-phase-project-sync.yml`** | Dependency-phase Project reconcile | Existing (master-only) |
| **Grok connector Projects** | Chat-time board ops | BLOCKED 403 — non-path |

## Operator one-time setup

1. Create Projects v2 board titled **termux-monorepo — Operator Matrix (#175)** (user or org).
2. Set repo **variable** (preferred) or secret:
   - `OPERATOR_MATRIX_PROJECT_URL` = `https://github.com/users/timerloggedout-spec/projects/<N>`
3. Confirm Actions secret exists with **project** scope (names from #184 / ARCHWIZ doc):
   - `OPERATOR_GITHUB_TOKEN` or `OPERATOR_TOKEN` or `ARCHWIZ_GITHUB_TOKEN`
4. On master (after land): Actions → **Operator Matrix Project Sync** → Run workflow → seed hub.

## Workflow behavior

**Event path:** issue/PR opened|reopened|labeled|ready_for_review → `actions/add-to-project@v1.0.2`  
**Dispatch path:** resolve project node id via GraphQL → `addProjectV2ItemById` for hub set `#175` `#184` `#713` `#714` `#682` (idempotent).

No YOLO merge. No raw PAT in logs (secrets masking). Skip with notice if URL unset.

## Vendor / template references (not vendored)

| Source | Use |
|--------|-----|
| [actions/add-to-project](https://github.com/actions/add-to-project) | Official GitHub-maintained add issue/PR to Projects v2 |
| [github/docs — Automating Projects using Actions](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions) | GraphQL field updates pattern |
| [paritytech/github-issue-sync](https://github.com/paritytech/github-issue-sync) | Issue→project sync action (PROJECT_TOKEN) |
| [suzuki-shunsuke/ghproj](https://github.com/suzuki-shunsuke/ghproj) / DEV write-up | Cross-repo gather into Projects |
| shader-slang `pr-board-sync.yml` / `issue-board-onboard.yml` | JS GraphQL `addProjectV2ItemById` idempotent pattern |
| In-repo `dependency-phase-project-sync.yml` | Established OPERATOR_TOKEN chain for ProjectV2 writes |

Do not invent a second sync plane. Prefer official `actions/add-to-project` for the event path; keep GraphQL seed thin.

## Stepie ↔ Linear map

| Stepie (2087) | Linear |
|---------------|--------|
| RECON, Dual-gate #713, Stay-busy, HOLD, #630 | **M5 Operator Matrix + Stepie** |
| Help-wanted, #184 | **M6 Help-wanted + Credential Hygiene** |

## Events policy

- Unposted chat ≠ consensus.
- Age alone does not promote.
- Vercel rate-limit non-gate.
- No HITL YOLO YEET AUTOAPPROVE.

## Links

- Workflow: `.github/workflows/ops-operator-matrix-project-sync.yml`
- Token SSOT: `docs/ops/ARCHWIZ-ADMIN-TOKEN.md`
- Skill: `.agents/skills/stepie-stepwise-ops/SKILL.md`
- Linear: https://linear.app/termux-monorepo-linear/project/termux-monorepo-hardening-dbbb30646612
