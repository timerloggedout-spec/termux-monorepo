# refTemplates → Actions / Workflows hooks

## Required visibility

| Surface | How refTemplates participates |
|---------|------------------------------|
| Dual-gate | All metadata + gitlink changes on this PR ride dual-gate; no special path |
| evidence-led-monorepo-ops | Inventory `refTemplates/00_Index/SOURCE-MAP.md`, Tier-C `13_*` pattern metadata, Tier-A `15_*` slots, and `smods/` vs `.gitmodules` |
| adaptive-wait | Submodule sparse-checkout / integrity jobs stay behind dual gates |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router + live-catalog | Research agents use free-first routing only |
| Codespace agent lane | Preferred smoke for any new `smods/` pin |
| ecc-tools overflow | Large template PRs thin-track if comment volume warrants |

## Integrity checklist (for CI / scripts)

1. Every directory child under `13_Third_Party_Refs/*` and `15_Research_Repo_Templates/*` has `README.md` + `SOURCE.txt`
2. Every `smods/*` path appears in `.gitmodules` with `shallow = true` when present
3. Preferred SOURCE URLs are resolvable (HEAD or public)
4. No hardcoded API keys in template metadata

## Follow-up implementation

- Inventory validates README + SOURCE metadata for Tier-C `13_*` pattern references and Tier-A `15_*` research slots.
- `refTemplates_score.py` scores the `15_*` research cohort; Tier-C patterns remain outside research-template ELO and Delphi participation.
- Keep `.github/workflows/refTemplates-eval.yml` path coverage on `refTemplates/**`.
