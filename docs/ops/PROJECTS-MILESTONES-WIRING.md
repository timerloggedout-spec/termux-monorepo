# Projects & Milestones Wiring (SSOT)

**Session:** 2026-09-21 15:19 PDT  
**Agent-Identity:** Grok (Administrator)  
**Priority hub:** Issue #175 · Credential inventory: Issue **#184** (names/scopes only)

## Surfaces

| Surface | Role | Status |
|---------|------|--------|
| **Stepie goal 2087** | Production planning utility — ordered milestones, criteria, RECON notes | LIVE (8 steps) |
| **Linear P-TER-1** `termux-monorepo hardening` | Execution track + product milestones (M1–M6) | LIVE |
| **GitHub Projects v2** (interactive connector) | Repo board for issues/PRs via Grok GitHub App | **BLOCKED** — 403 Resource not accessible by integration |
| **GitHub Projects v2** (Actions / PAT plane) | GHA or CLI using secrets with `project` scope | **AUTHORIZED at account** — wire by secret **name** only |
| **GitHub classic milestones** | Repo milestone tags on issues/PRs | Not wired this session |
| **LANE-MATRIX.md** | Tip-first PR classification | LIVE SSOT |
| **dual-gate CI** | Promote authority | Contract unchanged |

## Two auth planes (do not conflate)

### Plane A — Account credentials (#184 inventory)

Issue **#184** lists classic PATs whose scopes include **`project`** (among others). Names only in agent context:

| Secret / token name (inventory) | Notes |
|----------------------------------|-------|
| `Gh_actions` | classic; includes `project` |
| `timers-full+accessPAT` | classic; includes `project` |
| `DEEPSEEK_API_KEY` (classic PAT row) | misnamed inventory row — treat as GH PAT family only if confirmed; never as model auth |
| `ARCHWIZ_GITHUB_TOKEN` | fine-grained preferred per `ARCHWIZ-ADMIN-TOKEN.md` |
| `OPERATOR_GITHUB_TOKEN` / `OPERATOR_TOKEN` | primary GHA admin lane |

These authorize **Actions jobs** and owner CLI when injected as secrets. They are **not** automatically the Grok chat connector token.

### Plane B — Grok GitHub App connector (this session)

`github___projects_list` / `github___projects_write` call the **GitHub App** installation for Grok (xAI). Current response:

```text
403 Resource not accessible by integration
```

So **Projects v2 is not on the App installation permissions** for this connector, even when account PATs have `project`. Fix is Operator UI: expand the Grok GitHub App permissions (Projects read/write), or re-authorize the connector — not pasting a PAT into chat.

Policy: **raw PATs never enter agent context**. Route by secret name in workflows only.

## Stepie ↔ Linear map

| Stepie (2087) | Linear milestone |
|---------------|------------------|
| RECON + LANE-MATRIX pulse, Dual-gate #713, Stay-busy SSOT, Ancient HOLD, EXTRACT #630 | **M5: Operator Matrix + Stepie Planning Surface** |
| Help-wanted evidence sustain, Credential inventory notes-only (#184) | **M6: Help-wanted + Credential Hygiene** |
| (infra / hub / templates / skyhook) | M1–M4 existing |

Stepie owns *operator session plan*. Linear owns *product/execution track*. Neither merges PRs.

## GitHub Projects — unblock paths

1. **Interactive (preferred for this agent):** Grant Projects on the Grok GitHub App installation → retry `projects_list` / `create_project`.
2. **Actions path (authorized by #184 names):** Workflow uses `secrets.OPERATOR_GITHUB_TOKEN` or `secrets.ARCHWIZ_GITHUB_TOKEN` (or named PAT secret with `project`) to create/update Project items via GraphQL. Reuse Jules GHA Projects-sync patterns already linked in Linear docs.
3. **Never:** put classic PAT values into Stepie notes, issues, or chat.

Intended board once either path works: **termux-monorepo — Operator Matrix (#175)**

Suggested fields / views:

- Status: Backlog · Ready · In progress · WAIT (dual-gate) · Done
- Lane: PROMOTE · WAIT · HOLD · EXTRACT · OBSERVE · SUPERSEDE (mirror LANE-MATRIX)
- Priority hub: #175 always linked

Seed items:

- Issue #175 (hub)
- PR #713 (slim ML extract)
- PR #714 (stepie-stepwise-ops skill)
- PR #682 (mega — EXTRACT only)
- Issue #184 (credentials notes-only)

## Associated events

- `pull_request` opened/synchronized → add to Project + set Lane from labels or LANE-MATRIX
- dual-gate SUCCESS → Status → Ready (still no auto-merge)
- help-wanted receipt → M6-equivalent column
- GHA only: use secret **names** from #184 / ARCHWIZ doc — not values

## Events policy

- Unposted chat is not consensus (CLAUDE.md).
- Age alone does not promote.
- Vercel rate-limit is non-gate.
- No HITL YOLO YEET AUTOAPPROVE.

## Links

- Linear: https://linear.app/termux-monorepo-linear/project/termux-monorepo-hardening-dbbb30646612
- Issue #175 · Issue #184 · PR #714
- Token SSOT: `docs/ops/ARCHWIZ-ADMIN-TOKEN.md`
- Skill: `.agents/skills/stepie-stepwise-ops/SKILL.md`
