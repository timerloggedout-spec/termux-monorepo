# ITEMS — delphi-oracle-harmonious-intake

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| DORI-001 | P1 | executing | Add the separate general-purpose Delphi Oracle Issue Form and deterministic intake normalizer using canonical research/DoE registries. | Legacy quota form remains unchanged; form uses checkboxes and dropdowns; DoE Decides / All / Specific selection / Prior default resolve deterministically; 12 research participants and four DoE components are selectable; default means the 12 baseline research participants; silo-local scoring and comparison; execution is always false. |
| DORI-002 | P1 | executing | Add event-driven selection review and registry-catalogue handoff, Question Matrix and Harmonious Reconciliation metadata, and end-to-end contract tests. | Matrix strategy and optional round schedule persist; selection review is idempotent; catalogue disposition opens a PR against master; registry records preserve source IDs/provenance; optional WebView oversight stays optional; legacy intake remains compatible; focused tests and all required repository gates pass on the exact PR head. |

## Validation

- `python3 -B -m unittest discover -s tests -p 'test_delphi_intake.py' -v`
- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- Required PR checks and proposal-lifecycle workflow on the same immutable head SHA.

## Evidence boundary

The current environment exposes GitHub repository operations. A local checkout, shell-backed Termux device, and Termux `get_device_info` action are unavailable; GitHub Actions will provide repository-gate evidence, with terminal job results fetched before promotion.
