# Projects & Milestones Wiring (SSOT)

**Session:** 2026-09-21 15:21 PDT  
**Agent-Identity:** Grok (Administrator)  
**Legacy seed item:** Issue #175 (closed; historical only) · Credentials: Issue **#184** (names/scopes only)

**Canonical state:** `ops/tracking/tracking.json` via [REPO-TRACKING](REPO-TRACKING.md). The ProjectV2 board below is an optional visual projection, not a state authority.

## Decision: Option A — GitHub Actions plane

Interactive Grok connector Projects API remains 403. **Wiring is Actions-only** using Project-capable secrets by **name** (`OPERATOR_GITHUB_TOKEN` || `OPERATOR_TOKEN` || `ARCHWIZ_GITHUB_TOKEN`).

| Surface | Role | Status |
|---------|------|--------|
| **Stepie goal 2087** | Planning utility | LIVE |
| **Linear P-TER-1** | Execution track M1–M6 | LIVE |
| **GHA `ops-operator-matrix-project-sync.yml`** | Historical issue/PR → ProjectV2 sync | **ARCHIVED** (2026-11-02) |
| **GHA `dependency-phase-project-sync.yml`** | Dependency-phase Project reconcile | Existing (master-only) |
| **Grok connector Projects** | Chat-time board ops | BLOCKED 403 — non-path |

## Operator one-time setup

1. The existing Projects v2 board titled **termux-monorepo — Operator Matrix (#175)** may remain as a visual projection; the `#175` suffix is historical and does not make the issue a hub.
2. Set repo **variable** (preferred) or secret:
   - `OPERATOR_MATRIX_PROJECT_URL` = `https://github.com/users/timerloggedout-spec/projects/<N>`
3. Confirm Actions secret exists with **project** scope (names from #184 / ARCHWIZ doc):
   - `OPERATOR_GITHUB_TOKEN` or `OPERATOR_TOKEN` or `ARCHWIZ_GITHUB_TOKEN`
4. The former event-driven ProjectV2 membership workflow is archived. Do not expect an owning event to repair board membership; use the current generated read-only projection at `docs/ops/generated/lane-matrix-status.*` for PR disposition and `ops/tracking/tracking.json` for cross-domain lane×project state.

## Workflow behavior

**Historical event path (archived 2026-11-02):** issue/PR opened|reopened|labeled|ready_for_review → `actions/add-to-project@v1.0.2`. The former ProjectV2 membership sync is not an active repair mechanism. The board is a static visual projection, not a source of truth; use the generated repository tracking surfaces above.

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
