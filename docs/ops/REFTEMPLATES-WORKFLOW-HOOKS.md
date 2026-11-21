# refTemplates → Actions / Workflows hooks

## Required visibility

| Surface | How refTemplates participates |
|---------|------------------------------|
| Dual-gate | All metadata + gitlink changes on this PR follow the standard dual-gate |
| evidence-led-monorepo-ops | Inventory `refTemplates/00_Index/SOURCE-MAP.md` + `smods/` vs `.gitmodules` |
| adaptive-wait | Submodule sparse-checkout / integrity jobs stay behind dual gates |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router + live-catalog | Research agents use free-first routing only |
| Codespace agent lane | Preferred smoke for any new `smods/` pin |
| ecc-tools overflow | Large template PRs thin-track if comment volume warrants |

## Integrity checklist (for CI / scripts)

1. Every reference child under `15_Research_Repo_Templates/*`, `18_Vector_Databases/*` and `19_Provider_Inference_Catalogs/*` has `README.md` + `SOURCE.txt`
2. Every `smods/*` path appears in `.gitmodules` with `shallow = true` when present
3. Preferred SOURCE URLs are resolvable (HEAD or public)
4. Template metadata contains source names and public URLs; credential values stay in their authorized stores

## Follow-up implementation

- Inventory script validates `README.md` + `SOURCE.txt` for child references in slots 15, 18 and 19.
- Follow-up: diff `smods/` vs `.gitmodules` and add a thin GHA job on `refTemplates/**` for source-path integrity.

Provider catalog SDKs under slot 19 remain metadata-only. Runtime adoption requires a separate accepted item, provider-specific adapter contract, tests and dual-gate evidence.
