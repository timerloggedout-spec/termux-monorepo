# ICM Architect Custom-Fork Integration

## Purpose

The monorepo includes **ICM Architect** as a shallow Git submodule at `refTemplates/smods/icm-architect_fork`. ICM Architect is a skill for designing or restructuring a process, repository, or workspace around the Interpretable Context Methodology (ICM), where navigable folders and Markdown artifacts carry the system’s operational context.[1]

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

## Initialize a Clone

After cloning the monorepo, initialize only this reference skill when it is needed. The command keeps setup scoped and avoids fetching unrelated submodules.

```bash
git submodule update --init --depth 1 refTemplates/smods/icm-architect_fork
```

The submodule provides `SKILL.md`, reference notes, and starter templates. It is **not** automatically executed or copied into an agent runtime. A consuming agent or developer should read its `SKILL.md` before using the method, then deliberately select an appropriate destination workspace.[1]

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

The monorepo now applies the ICM Architect **System map** form at [`docs/icm/CLAUDE.md`](icm/CLAUDE.md). It is a linked edit map rather than a duplicate specification: its object cards cite existing architecture, navigation, tool, and governance sources; its process cards record the actual change-and-validation and structured-Termux-job movements; and its effect index provides only first-order routing. Start at the root `AGENTS.md` governance sequence, then open the ICM catalog and one matching card before loading deeper sources.[1]

No source files, generated indexes, recovery artifacts, or device state were moved to make this map. The map’s purpose is to reduce context loading while preserving the existing source of truth and human approval boundaries.

## References

[1]: https://github.com/RinDig/ICM-Architect "RinDig/icm-architect — upstream project and usage overview"
