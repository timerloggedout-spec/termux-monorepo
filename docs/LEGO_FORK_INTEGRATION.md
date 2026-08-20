# LEGO Fork — Customizable Template Reference (smod)

## Purpose

`timerloggedout-spec/lego_fork` is pinned as a **shallow reference submodule** at `refTemplates/smods/lego_fork`. It is a **customizable template** for composition thinking: given a inventory of pieces (capabilities), decide which complete *sets* (team compositions / deliverable shapes) can be assembled — and which cannot — without forcing a merge of incomplete work.

> **Boundary:** Reference only. Not an automatic runtime. Customizations belong in the user-owned fork. Pin advances require an explicit PR. Do not copy third-party source into monorepo application paths.

| Property | Value |
|---|---|
| Submodule path | `refTemplates/smods/lego_fork` |
| Fork remote | `https://github.com/timerloggedout-spec/lego_fork.git` |
| Tracking branch | `main` |
| Initial pinned revision | `074f334b71f47552b01d07b78fb6c01fd2c47c0e` |
| Checkout policy | Shallow, intentionally pinned through the Gitlink |
| Related roster work | Issues #129 / #175; MoneyBall routing; Lane 4 in `docs/ops/LANE_CONSOLIDATION_SSOT.md` |

## What the template encodes

From the fork’s domain model (`pkg/brick`):

- **Piece** — atomic capability (skill, tool, role fragment).
- **User inventory** — which pieces an agent (or the team pool) currently holds.
- **Set** — a complete build recipe (a target composition / deliverable).
- **AvailableSets** — sets that can be built *now* because every required piece is present in sufficient quantity.
- **FiftyPercent** — pieces common enough across the pool to treat as stable shared foundation.

Mapped to Teams / Rosters / MoneyBall (complementary, not a replacement):

| LEGO concept | Team machine concept |
|---|---|
| Piece | Skill, tool, connector, or specialist capability on a roster candidate |
| Inventory | Active roster members + their skills/tools after MoneyBall cull/clone |
| Set | A job shape that needs a specific combination (e.g. review+security+build) |
| AvailableSets | Jobs the current roster can complete without inventing missing roles |
| Selection adjust | Wait for pieces / promote specialists / re-rank via ELO before claiming the set |

**Production quality bar** (from the fork README — keep this bar for trunk merges):

- Intentions described clearly
- Straightforward, boring code
- Integration tested
- Conscious of complexity
- Reviewed or pair-programmed
- Formatted + linted
- Errors logged

Latency while agents are `<Thinking>` is secondary: **wait and see**; prefer correct, efficient trunk commits over speed.

## Initialize

```bash
git submodule update --init --depth 1 refTemplates/smods/lego_fork
```

If the Gitlink is not yet present on the branch, add once:

```bash
git submodule add -f --depth 1 -b main https://github.com/timerloggedout-spec/lego_fork.git refTemplates/smods/lego_fork
```

Read `refTemplates/smods/lego_fork/README.md` and `pkg/brick/service.go` before inventing roster composition rules. Do not execute the Go service as a monorepo dependency unless a separate, reviewed integration PR lands.

## Customize in the fork

```bash
cd refTemplates/smods/lego_fork
git switch main
# intentional template changes only
git add <files>
git commit -m "feat(template): describe customization"
git push origin main
cd ../../..
git add refTemplates/smods/lego_fork
git commit -m "chore(submodule): advance lego_fork pin"
```

## Team machine sync (wait · select · trunk)

Goal: agents operate as one machine — **in sync**, waiting when pieces are incomplete, adjusting selection, merging only **perfect trunk** slices.

1. **Triage / claim** — one clear scope; post `<!-- agent-claim -->` when claiming files.
2. **Compose** — check AvailableSets analogue: does the active roster have the required pieces for this set?
3. **Wait** — if pieces are missing, do not open a half-built PR; hire/specialist or wait for parallel work.
4. **Select** — MoneyBall / model matrix ranks who and which model runs the role.
5. **Build** — Jules (or designated builder) implements on a single fat branch when possible.
6. **Review** — Gemini primary + peers; synthesize; fix.
7. **Trunk** — merge only when dual-gate green (`repo_gate` + `termux_smoke`) and disposition not 🔴.

## PR sprawl isolation & cherry-pick

See `docs/ops/PR_SPRAWL_CHERRY_PICK.md`.

## Review checklist

| Check | Expected |
|---|---|
| `git submodule status refTemplates/smods/lego_fork` | Non-prefixed SHA on `main` |
| `.gitmodules` entry | path, URL, `branch = main`, `shallow = true` |
| Pin advance | Own PR; `git diff --submodule=log` shows intended range only |
| Gates | `python3 scripts/ci/repo_gate.py` and `termux_smoke.py` green |

## References

- Fork: https://github.com/timerloggedout-spec/lego_fork
- Roster / MoneyBall: issue #129, PR #131 track
- Operator matrix: issue #175
- Lane SSOT: `docs/ops/LANE_CONSOLIDATION_SSOT.md`
- smod convention: `docs/ICM-ARCHITECT-INTEGRATION.md`
