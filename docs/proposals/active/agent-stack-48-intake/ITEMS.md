# ITEMS — agent-stack-48-intake

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| ASI-001 | P1 | executing | Add Agent Stack 48 as an unregistered LabLab event candidate in the canonical challenge coordinator and discovery log. | C13 record carries official URL, source-backed dates/tracks/submission requirements, receipt date, and explicit unknowns; candidate log agrees; registration/submission remain unclaimed. |
| ASI-002 | P1 | queued | Verify automatic Challenge OSINT ingestion after coordinator promotion. | `challenge-osint-watch` runs from the coordinator change; page fetch succeeds; a dated SHA-256 snapshot for C13 is appended; coverage reports C13; no manual snapshot fabrication. |

## Validation

- Parse `ops/challenge/coordinator.json` as JSON.
- Run `python3 scripts/challenge/osint_watch.py --no-fetch` and verify C13 appears in generated coverage.
- Run `python3 -m unittest discover -s tests` for relevant challenge/coordinator fixtures.
- Run `python3 scripts/proposals/validate_registry.py`.
- Run repository gates: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`.

GitHub API file operations are available in this session; local shell execution is unavailable. CI and the post-promotion OSINT workflow provide executable validation evidence.
