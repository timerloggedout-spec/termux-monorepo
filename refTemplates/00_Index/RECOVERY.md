# refTemplates recovery — narrow slice of environment reconstruction

## Fact

`refTemplates/*` is a **narrow slice** of the full environment reconstruction.

During the original git initialization of termux-monorepo, files under the original refTemplates tree were removed with plain `rm` instead of `git rm`. That produced the recovery path that still governs this tree.

## Recovery SSOT

- Branch `recreate/refTemplates-skeleton` — full categorical map (01–14 + Haven + Interpreted-Context-Methdology_fork + README_RECOVERY)
- Restore commits on early master lineage (`65c9f811`, `b104890`, `8a53ffb`, …)
- Live master posture: thin `01_Agent_Runtime/` metadata + `smods/` shallow gitlinks
- Full recursive submodule materialization is **rare and explicit**

## Current consolidation

See `docs/ops/REFTEMPLATES-CONSOLIDATION.md`:

- `15_Research_Repo_Templates/` — consolidated research scaffolds (Jogyo primary)
- `smods/` — live custom-adapted gitlink lane
- `16_Org_Phased/` — complementary orgs / Enterprise until self-sustaining

Do not treat the current master tree as the complete historical inventory.
