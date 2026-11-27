# refTemplates → Actions / Workflows hooks

## Required visibility

| Surface | How refTemplates participates |
|---|---|
| Dual-gate | All metadata + gitlink changes ride the same green path |
| evidence-led-monorepo-ops | Inventory SOURCE-MAP, reference metadata, and smods vs .gitmodules |
| adaptive-wait | Submodule sparse-checkout / integrity jobs stay behind dual gates |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router + live-catalog | Research agents use free-first routing only |
| Codespace agent lane | Preferred smoke for any new smods pin |
| ecc-tools overflow | Large template PRs thin-track when comment volume warrants |

## Integrity contract

1. Every directory under 05_Safety_Observability/, 11_Evaluation_Quality/, and 15_Research_Repo_Templates/ has README.md + SOURCE.txt.
2. Every smods path appears in .gitmodules with shallow configuration when present.
3. Preferred SOURCE URLs are resolvable and canonical.
4. Metadata contains no credentials or API keys.
5. License labels identify provisional research posture and exact-revision review requirements.

## Follow-up implementation

- scripts/ci/refTemplates_inventory.py --strict validates metadata contracts for categories 05, 11, and 15.
- Evidence-led inventory compares 00_Index/SOURCE-MAP.md with category entries and .gitmodules.
- Optional thin GHA job runs the strict inventory on refTemplates/**.
