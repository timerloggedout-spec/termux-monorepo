# ICM Architect Custom-Fork Integration

## Purpose

The monorepo applies ICM to **itself**: its `docs/icm/` catalog, contracts, cards, process definitions, and maintenance Pipeline are the operative workspace. It includes **ICM Architect** as a shallow Git reference submodule at `refTemplates/smods/icm-architect_fork`. ICM Architect is a skill for designing or restructuring a process, repository, or workspace around the Interpretable Context Methodology (ICM), where navigable folders and Markdown artifacts carry the system’s operational context.[1]

> **Boundary:** The monorepo pins a reviewed revision; all intentional changes to ICM Architect belong in the user-owned fork, `timerloggedout-spec/icm-architect_fork`. This keeps local extensions reviewable without copying third-party source into the monorepo.

| Property | Value |
|---|---|
| Submodule path | `refTemplates/smods/icm-architect_fork` |
| Fork remote | `https://github.com/timerloggedout-spec/icm-architect_fork.git` |
| Upstream project | `https://github.com/RinDig/ICM-Architect` |
| Tracking branch | `main` |
| Initial pinned revision | `b20fb45063a564cf607b03526e206f519d174def` |
| Checkout policy | Shallow, intentionally pinned through the Gitlink |
| Governing work item | `ICM-01` |

## Reference Inputs

The monorepo maintains a bounded reference-input layer under `refTemplates/smods/`. These forks are pinned examples and customization surfaces; they are **not** a second monorepo, an automatic runtime, or permission to copy external source into repository-native ICM contracts.

| Reference | Submodule path | Repository-native use |
|---|---|---|
| ICM Architect | `refTemplates/smods/icm-architect_fork` | Select the smallest ICM form and audit maps. |
| Full methodology | `refTemplates/smods/interpretable-context-methodology_fork` | Consult detailed conventions, examples, and workspace-builder patterns. |
| Promptbase | `refTemplates/smods/content-agent-routing-promptbase_fork` | Consult Layer 0–3 routing, canonical-source, and one-way-dependency patterns. |
| ICM CCTV | `refTemplates/smods/icm-cctv_fork` | Consult optional visual stage mirrors and human-checkpoint patterns; keep the native Pipeline output canonical. |

The user-declared BLU B160V/free-services envelope is documented in the repository-native [`docs/icm/` platform card](icm/objects/platform/blu-b160v-free-services.md). It is a design constraint only; this integration neither accesses the Termux MCP nor configures the device.[1]

## Companion Methodology Reference

The user-owned **Interpretable Context Methodology** companion fork is pinned beside ICM Architect. It provides the full convention set, example workspaces, and workspace-builder; ICM Architect remains the compact selection and restructuring skill. Read Architect first to choose the smallest form, then consult the methodology reference only for detailed Pipeline conventions or a concrete recurring-workspace example.[1] [2]

| Property | Value |
|---|---|
| Submodule path | `refTemplates/smods/interpretable-context-methodology_fork` |
| Fork remote | `https://github.com/timerloggedout-spec/interpretable-context-methodology_fork.git` |
| Upstream project | `https://github.com/RinDig/Interpretable-Context-Methodology` |
| Tracking branch | `main` |
| Initial pinned revision | `02ba5d85c7871b75c7c702a2d8da6524723d53d4` |
| Checkout policy | Shallow, intentionally pinned through the Gitlink |
| Governing work item | `ICM-04` |

## Initialize a Clone

After cloning the monorepo, initialize only the reference needed for the work. The commands keep setup scoped and avoid fetching unrelated submodules.

```bash
git submodule update --init --depth 1 refTemplates/smods/icm-architect_fork
git submodule update --init --depth 1 refTemplates/smods/interpretable-context-methodology_fork
git submodule update --init --depth 1 refTemplates/smods/content-agent-routing-promptbase_fork
git submodule update --init --depth 1 refTemplates/smods/icm-cctv_fork
```

ICM Architect provides `SKILL.md`, reference notes, and starter templates. The methodology fork provides the complete conventions and example workspaces. Neither is automatically executed or copied into an agent runtime. A consuming agent or developer should read the relevant reference before selecting a destination workspace.[1] [2]

## Make a Local Customization

A customization is made in the fork, not by copying files beside the Gitlink. Start in the checked-out submodule and record the upstream remote if it is not already present.

```bash
cd refTemplates/smods/icm-architect_fork
git remote get-url upstream >/dev/null 2>&1 || \
  git remote add upstream https://github.com/RinDig/ICM-Architect.git
git fetch upstream main
git switch main
# Make and test the intended change.
git add <files>
git commit -m "feat: describe the ICM customization"
git push origin main
```

Then update the monorepo’s Gitlink to the resulting fork revision and commit that pointer change with the related documentation or integration update.

```bash
cd ../../..
git add refTemplates/smods/icm-architect_fork
git commit -m "chore(submodule): advance ICM Architect fork"
```

## Incorporate Upstream Changes

Upstream changes must be reviewed in the fork before they are pinned in the monorepo. The following sequence makes the merge point explicit and preserves the fork as the only customization surface.

```bash
cd refTemplates/smods/icm-architect_fork
git fetch upstream main
git switch main
git merge --ff-only upstream/main
# If a fast-forward is not possible, review and resolve the merge deliberately.
git push origin main

cd ../../..
git add refTemplates/smods/icm-architect_fork
git commit -m "chore(submodule): sync ICM Architect upstream"
```

Run `git diff --submodule=log` before committing the monorepo pointer. The output identifies the precise submodule commit range being introduced. The standard repository gates still apply before a merge to `master-staging`.

## Review Checklist

| Check | Expected outcome |
|---|---|
| `git submodule status refTemplates/smods/icm-architect_fork` | A non-prefixed SHA and the expected `main` branch label. |
| `git config -f .gitmodules --get-regexp '^submodule\.refTemplates/smods/icm-architect_fork\.'` | Path, fork URL, `main` branch, and `shallow=true` are present. |
| `git diff --submodule=log` | Only the intended Gitlink revision changes. |
| `python3 scripts/ci/repo_gate.py` | The repository gate completes successfully. |
| `python3 scripts/ci/termux_smoke.py` | The Termux smoke gate completes successfully. |

## Applied System Map

The monorepo now applies the ICM Architect **System map** form at [`docs/icm/CLAUDE.md`](icm/CLAUDE.md). It is a linked edit map rather than a duplicate specification: its object cards cite existing architecture, navigation, tool, governance, full-methodology, and workspace-artifact sources; its process cards record the actual change-and-validation, structured-Termux-job, and workspace-artifact-triage movements; and its effect index provides only first-order routing. Start at the root `AGENTS.md` governance sequence, then open the ICM catalog and one matching card before loading deeper sources.[1] [2]

No source files, generated indexes, recovery artifacts, device state, or application code were moved or refactored to make this map. The map’s purpose is to reduce context loading while preserving the existing source of truth and human approval boundaries.

The method is completed as a composition of a **System map** for repository editing and a nested, documentation-only **maintenance Pipeline** at [`docs/icm/maintenance/CLAUDE.md`](icm/maintenance/CLAUDE.md). The pipeline separates stable rules/templates from per-update artifacts, requires a human design gate, verifies links and canonical sources, and records `master-staging` validation before a later `master` merge. See [`docs/icm/_meta/method-coverage.md`](icm/_meta/method-coverage.md) for the exact method-to-file coverage.

Historical and pending PRs are not silently absorbed into this implementation. [`docs/icm/_meta/related-pull-requests.md`](icm/_meta/related-pull-requests.md) reconciles the merged reconnaissance precursor (#4), the open metadata-recovery skeleton (#47), the pending CAVEMAN workspace (#103), and this direct implementation (#232).

## References

[1]: https://github.com/RinDig/ICM-Architect "RinDig/icm-architect — upstream project and usage overview"
[2]: https://github.com/RinDig/Interpretable-Context-Methodology "RinDig/Interpretable-Context-Methodology — full conventions and reference workspaces"
[3]: https://github.com/RinDig/Content-Agent-Routing-Promptbase "RinDig/Content-Agent-Routing-Promptbase — layered context-routing precedent"
[4]: https://github.com/timerloggedout-spec/icm-cctv_fork "timerloggedout-spec/icm-cctv_fork — optional file-backed visual review reference"
