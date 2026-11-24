# Review Log — delphi-oracle-harmonious-intake

## 2026-11-24 — Operator design authorization

- Disposition: executing
- VOTE: accept
- term: 2026-11-24
- Voter: timerloggedout-spec
- Scope: separate general-purpose Delphi Oracle intake, research selection, Harmonious Reconciliation, and immutable selection catalogue.
- Evidence: operator instruction to build a separate version and continue through merge to master; confirmed Question Matrix design decision.

## Binding design decisions

- Preserve the quota/provider Delphi RFP form as a separate intake path.
- Use dropdown menus for single-select choices and checkboxes for multi-select choices.
- Expose research selection modes: DoE Decides, All, Specific selection, and Prior default.
- Preserve the 12-participant baseline default; keep project references independently selectable.
- Require one Question Matrix strategy selection and allow an optional per-round schedule.
- Use Termux-monorepo as panel context; WebView human oversight remains optional.
- Fix execution to false throughout deliberation and selection records.
- Support Selection Review, Registry Catalogue, Both, and Deliberation only dispositions.
- Preserve DoE candidates separately from confirmed reconciliation targets.

## 2026-11-24 — Independent review

- Reviewer: Devin Review
- Initial result: 8 actionable findings on PR #5848.
- Resolution: YAML scalar quoting; ordered Markdown/fence-aware parsing; rendered-text normalization; DoE candidate/target separation; disposition-synchronized review labels; actionable validation comments; dual catalogue gate dispatch; proposal-local gate registration.
- Regression coverage: 32 intake contract tests, including registry locality, Markdown, nested fences, DoE pending targets, review-label cleanup, and validation workflow contracts.
- Status: all eight findings resolved on feat/delphi-oracle-harmonious-intake-v2; exact-head verification and independent re-review pending on promotion PR #5849.
- Evidence: PR #5848 review comments and branch test suite; promotion PR records final verification.

## Evidence rule

Each review finding receives source-level verification and a regression test where applicable. Catalogue records preserve source issue, normalized record hash, methodology, matrix version, round profile, disposition, and execution state.