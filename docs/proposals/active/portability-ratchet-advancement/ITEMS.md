# ITEMS — portability-ratchet-advancement

| ID | Item | State | Evidence / exit condition |
|----|------|-------|---------------------------|
| PORT-001 | Register proposal in docs/proposals/registry.yaml | posted | This directory + registry row |
| PORT-002 | Retire remaining tracked .bak/.old files (target ∔20) | posted | git rm --cached on Class D; baseline.json counters decrease; dual-gate green |
| PORT-003 | Untrack Class B process-runtime junk (browser Singleton*, pulse runtime, .termux/shell) | posted | git rm --cached; counters decrease |
| PORT-004 | Convert high-value Class A device links to relative or vendored form (archwiz entrypoints first) | posted | relative links or vendored copies under workspace/llm_map/; link_local.sh still works |
| PORT-005 | Untrack Class E session-store artifacts after credential hygiene confirmed (names-only #184) | posted | git rm --cached; session_artifacts and paths_with_spaces counters fall |
| PORT-006 | Update docs/PORTABILITY.md measured counts after each landed PR | posted | Document reflects live baseline |

All implementation PRs must cite Implements: PORT-00x and pass dual-gate on the candidate SHA.
