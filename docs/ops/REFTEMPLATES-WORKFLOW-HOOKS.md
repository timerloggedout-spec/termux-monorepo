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
| Agent runtime integrations | Every new `01_Agent_Runtime/*` integration template carries `README.md`, `SOURCE.txt`, and `integration.json`; the canonical sMods disposition is recorded in `refTemplates/smods/INTEGRATIONS.json` and checked by `verify_agent_tooling_templates.py` |

## Integrity checklist (for CI / scripts)

1. Every slot under `15_Research_Repo_Templates/*` has `README.md` + `SOURCE.txt`.
2. Every new `01_Agent_Runtime/*` integration template has `README.md`, `SOURCE.txt`, and `integration.json`; all manifest-declared `required_files` must exist and be nonempty.
3. Every template sMods candidate has an explicit disposition in `refTemplates/smods/INTEGRATIONS.json`.
4. A `pinned` sMods record must match the exact `.gitmodules` URL and a 160000 gitlink; `fork_required` must not masquerade as a live pin.
5. Every live `smods/*` gitlink remains reconciled with `.gitmodules`; shallow-pin policy is validated for new pins without silently rewriting historical entries.
6. Preferred SOURCE URLs are resolvable (HEAD or public).
7. No hardcoded API keys in template metadata.

## Follow-up implementation

- Extend evidence-led inventory script to walk `15_*` and diff `smods` vs `.gitmodules`
- `refTemplates-eval.yml` runs the offline template/smods validator and its focused tests on the existing cadence.
