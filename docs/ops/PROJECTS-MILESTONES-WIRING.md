# Projects & Milestones Wiring (SSOT)

**Session:** 2026-09-21 15:14 PDT  
**Agent-Identity:** Grok (Administrator)  
**Priority hub:** Issue #175

## Surfaces

| Surface | Role | Status |
|---------|------|--------|
| **Stepie goal 2087** | Production planning utility — ordered milestones, criteria, RECON notes | LIVE (8 steps) |
| **Linear P-TER-1** `termux-monorepo hardening` | Execution track + product milestones | LIVE |
| **GitHub Projects v2** | Repo board for issues/PRs | **BLOCKED** — connector 403 Projects scope |
| **GitHub classic milestones** | Repo milestone tags on issues/PRs | Not wired this session (no gh CLI; REST not exposed) |
| **LANE-MATRIX.md** | Tip-first PR classification | LIVE SSOT |
| **dual-gate CI** | Promote authority | Contract unchanged |

## Stepie ↔ Linear map

| Stepie (2087) | Linear milestone |
|---------------|------------------|
| RECON + LANE-MATRIX pulse, Dual-gate #713, Stay-busy SSOT, Ancient HOLD, EXTRACT #630 | **M5: Operator Matrix + Stepie Planning Surface** |
| Help-wanted evidence sustain, Credential inventory notes-only (#184) | **M6: Help-wanted + Credential Hygiene** |
| (infra / hub / templates / skyhook) | M1–M4 existing |

Stepie owns *operator session plan*. Linear owns *product/execution track*. Neither merges PRs.

## GitHub Projects (when unblocked)

Required connector permissions: Projects read/write (Projects v2).

Intended board: **termux-monorepo — Operator Matrix (#175)**

Suggested fields / views:

- Status: Backlog · Ready · In progress · WAIT (dual-gate) · Done
- Lane: PROMOTE · WAIT · HOLD · EXTRACT · OBSERVE · SUPERSEDE (mirror LANE-MATRIX)
- Priority hub: #175 always linked

Seed items (once Projects accessible):

- Issue #175 (hub)
- PR #713 (slim ML extract)
- PR #714 (stepie-stepwise-ops skill)
- PR #682 (mega — EXTRACT only)
- Issue #184 (credentials notes-only)

Associated events (Automations / GHA):

- `pull_request` opened/synchronized → add to Project + set Lane from labels or LANE-MATRIX comment
- dual-gate SUCCESS → allow Status → Ready for promote (human or agent with dual-gate evidence)
- help-wanted receipt → optional Project item under M6-equivalent column

Existing Linear docs already describe Jules GHA Projects sync patterns — reuse, do not invent a second sync plane until Projects scope is granted.

## Events policy

- Unposted chat is not consensus (CLAUDE.md).
- Age alone does not promote.
- Vercel rate-limit is non-gate.
- No HITL YOLO YEET AUTOAPPROVE.

## Links

- Linear project: https://linear.app/termux-monorepo-linear/project/termux-monorepo-hardening-dbbb30646612
- Issue #175: https://github.com/timerloggedout-spec/termux-monorepo/issues/175
- PR #714: https://github.com/timerloggedout-spec/termux-monorepo/pull/714
- Skill: `.agents/skills/stepie-stepwise-ops/SKILL.md`
