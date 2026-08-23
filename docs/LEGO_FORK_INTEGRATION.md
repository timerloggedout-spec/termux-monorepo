# LEGO Fork — Customizable Template Reference (smod)

## Purpose

`timerloggedout-spec/lego_fork` is registered as a **shallow reference submodule** at `refTemplates/smods/lego_fork`. It is a **customizable template** for composition thinking: given an inventory of pieces (capabilities), decide which complete *sets* (team compositions / deliverable shapes) can be assembled — and which cannot — without forcing a merge of incomplete work.

> **Boundary:** Reference only. Not an automatic runtime. Customizations belong in the user-owned fork. Pin advances require an explicit PR. Do not copy third-party source into monorepo application paths.

| Property | Value |
|---|---|
| Submodule path | `refTemplates/smods/lego_fork` |
| Fork remote | `https://github.com/timerloggedout-spec/lego_fork.git` |
| Tracking branch | `main` |
| Initial pinned revision | `074f334b71f47552b01d07b78fb6c01fd2c47c0e` |
| Checkout policy | Shallow, intentionally pinned through the Gitlink |
| Related roster work | Issues #129 / #175; MoneyBall routing |

## What the template encodes

| LEGO concept | Team machine concept |
|---|---|
| Piece | Skill, tool, connector, or specialist capability |
| Inventory | Active roster members + skills after MoneyBall cull/clone |
| Set | A job shape that needs a specific combination |
| AvailableSets | Jobs the current roster can complete without inventing roles |

## Operator policy (mega preferred)

Prefer **one coherent fat PR per lane**. Do not open parallel micro-PRs for the same stream. Dirty heads: rebase the fat branch onto current `master` rather than splintering extracts (unless the operator explicitly requests extract-only).

Dual-gate before trunk: `repo_gate` + `termux_smoke`.

## Initialize (after gitlink exists)

```bash
git submodule update --init --depth 1 refTemplates/smods/lego_fork
```

If the Gitlink is not yet present:

```bash
git submodule add -f --depth 1 -b main https://github.com/timerloggedout-spec/lego_fork.git refTemplates/smods/lego_fork
git -C refTemplates/smods/lego_fork checkout 074f334b71f47552b01d07b78fb6c01fd2c47c0e
git add refTemplates/smods/lego_fork
git commit -m "chore(submodule): gitlink lego_fork @ 074f334"
```

API/connector pushes cannot always create `mode=160000` gitlinks; local/operator step completes the pin.

## Related

- Fork inventory: `docs/submodules/fork-inventory.yaml`
- Batteries sibling smod: #309
- Operator matrix: #175
