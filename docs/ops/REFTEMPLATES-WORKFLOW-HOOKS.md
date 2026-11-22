# refTemplates → Actions / Workflows hooks

## Required visibility

| Surface | How refTemplates participates |
|---------|------------------------------|
| Dual-gate | All metadata + gitlink changes on this PR ride the existing dual-gate |
| evidence-led-monorepo-ops | Inventory `refTemplates/00_Index/SOURCE-MAP.md` + `smods/` vs `.gitmodules` |
| adaptive-wait | Submodule sparse-checkout / integrity jobs stay behind dual gates |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router + live-catalog | Research agents use free-first routing only |
| Codespace agent lane | Preferred smoke for any new `smods/` pin |
| ecc-tools overflow | Large template PRs thin-track if comment volume warrants |

## Integrity checklist (for CI / scripts)

1. Every slot under `15_Research_Repo_Templates/*` has `README.md` + `SOURCE.txt`
2. Every child under `19_Provider_Inference_Catalogs/*` has `README.md` + `SOURCE.txt` and pinned metadata
3. Every `smods/*` path appears in `.gitmodules` with `shallow = true` when present
4. Preferred SOURCE URLs are resolvable (HEAD or public)
5. Template metadata uses named secret references and contains zero API-key values

## Follow-up implementation

- Evidence-led inventory validates slot 15 research children and slot 19 provider-reference children.
- Keep Vultr Python/TypeScript sources metadata-only; compare repository-owned Incumbent and VultrInspired catalogue variants.
- Optional: thin GHA job on path `refTemplates/**` that asserts SOURCE.txt presence.
