# Changelog

All notable changes to StudySprint. Process: `VERSIONING.md`.
Entries are the GitHub Release notes, verbatim.

## [0.1.0] — 2026-10-30

First versioned state: the complete D1 build on the D0 foundation.

### Added
- G2 study artifact kinds (`study_tools.py`): syllabus +
  practice_set evidence sets in the D0 stamped shape
  (provenance / freshness / sha256), plus build_study_plan,
  generate_quiz, replan_on_missed.
- G3 Strands-wired agent (`agent.py`): the D0 evidence-gate loop on
  the vendored Delphi Oracle kernel, tools registered on a
  Strands `Agent` when the SDK is present; hashed receipts
  (`studysprint-agent-receipt/v1`, now carrying `agent_version`).
- D0 foundation vendored verbatim in `foundation/`:
  oracle_kernel.py (blob 9a4a1c78), fetch_evidence.py (8442d813),
  D0-FOUNDATION.md census + reuse map.
- Demo (`demo.py`, `demo-script.md`), Builder Center article
  (`article.md`, published 2026-10-30), sample syllabus +
  practice set in `examples/`.
- `requirements.txt`: zero required dependencies;
  strands-agents optional.
- FEATURES.md (user-wanted features, UI/UX) and this process
  (VERSIONING.md + VERSION + CHANGELOG.md).

### Changed
- Polish(1): the practice_set artifact path now yields a quiz
  from the fetched set (previously only the syllabus path built
  outputs); README + article aligned to the live assets (article
  URL, demo video, D0 repo URL).

### Evidence
- Tests: 7 passed (offline suite, tests/test_studysprint.py).
- Demo decisions (evidence/demo-run.json): ABSTAIN on asserted
  evidence → ALLOW_RECOMMENDATION on the fetched syllabus
  (12-session plan + week-1 quiz + re-plan) → ESCALATE on
  credential_mutation.
- Workshop qualifier: Strands workshop completed in-window
  2026-10-30 (all 7 modules EXIT:0; gate D1-WORKSHOP cleared).
- Live assets: article on Builder Center; demo video on YouTube
  (1:10, public). Project submission: Nov 4, per owner ruling.
