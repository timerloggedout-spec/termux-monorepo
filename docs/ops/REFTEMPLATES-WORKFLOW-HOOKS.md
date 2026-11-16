# refTemplates → Actions / Workflows hooks

## Required visibility

| Surface | How refTemplates participates |
|---------|------------------------------|
| Dual-gate | All metadata + gitlink changes on this PR ride dual-gate; no special path |
| evidence-led-monorepo-ops | Inventory `refTemplates/00_Index/SOURCE-MAP.md` + `smods/` vs `.gitmodules` |
| adaptive-wait | Submodule sparse-checkout / integrity jobs stay behind dual gates |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router + live-catalog | Research agents use free-first routing only |
| Codespace agent lane | Preferred smoke for any new `smods/` pin |
| ecc-tools overflow | Large template PRs thin-track if comment volume warrants |

## Enforced template contract

1. Every reusable template child under numbered categories (excluding the index and papers/citation shelves) has nonempty regular `README.md` and `SOURCE.txt`.
2. Every child under `01_Agent_Runtime/` additionally has a regular, valid object-root `integration.json`.
3. Every `refTemplates/smods/*` path has exactly one `.gitmodules` entry and one mode-160000 gitlink; orphan entries and orphan gitlinks fail.
4. Every sMods pin uses a credential-free HTTPS GitHub URL, `shallow = true`, and a 40-character immutable gitlink SHA.
5. Symlinked slot roots, template directories, and metadata files fail closed.
6. CI reads Git metadata only. It does not initialize, fetch, or recursively update submodules.

The executable contract is `scripts/ci/refTemplates_inventory.py --strict`; focused regression tests run in `.github/workflows/refTemplates-eval.yml`.

## Operating rule

Select and adapt an existing reference template before introducing a new integration-specific structure. A new runtime integration must carry its own `integration.json`, source record, and README. A new sMods fork must be an intentional shallow custom fork pinned by a gitlink SHA; a floating branch name is not a pin.
