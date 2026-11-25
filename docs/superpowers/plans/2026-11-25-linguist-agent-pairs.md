# Plan — Agent-specific Linguist pairs and safe projection

**Item:** NSE-024 (pair-mapping extension for PR #5889)
**Branch:** `cue/linguist-rule-mapping-20261125`
**State:** implementation plan; PR remains open and unmerged.

## Outcome

Register each active Agent machine surface with its sibling `*.hum.md` source in the existing Linguist projection script. Render deterministic, lossless `agent-surface-v1` outputs; retain ICM's byte-identical Claude/AGENTS aliases. Keep SG001–SG008 meanings and candidate dispositions unchanged.

## Bounded tasks

1. Extend `docs/proposals/active/notation-sets/ITEMS.md` with the pair-mapping acceptance under NSE-024.
2. Add RED tests in `tests/test_contact_projections.py` for the seven exact source/target pairs, uniqueness, parity, stale `--check`, containment, symlink rejection, credential-like source rejection before writes, and atomic failure preservation.
3. Port the historical `scripts/cedrlang/render_contact_projections.py` into this branch as the sole mapper. Replace implicit discovery and unregistered dictionary codes with an explicit seven-pair registry, path preflight, source/output screening, and same-directory atomic replacement.
4. Align the seven human sidecars and generate their machine counterparts through the mapper. Keep each ICM Claude/AGENTS pair byte-identical; remove active root `AGENTS.md` routes and retain historical references with clear labels.
5. Update active NSE-020 and round-trip pointers, and wire the focused mapper test plus `--check` into `.github/workflows/repo-gate.yml`.
6. Run focused tests, Siglary tests/validator, `repo_gate.py`, `termux_smoke.py`, link and diff checks; inspect the final diff and the PR's exact-head review/check state.

## Acceptance and boundaries

- Registry contains exactly seven active machine surfaces, each with one unique sibling `.hum.md` source.
- `--check` proves exact deterministic output parity without writing files.
- Path traversal, out-of-root targets, symlink components, and credential-like values fail during preflight; a write failure preserves the prior target.
- Keep generated docs free of the user-excluded channel reference and aligned with the current surfaces policy.
- Preserve existing PR history with ordinary commits. Keep PR #5889 open and unmerged; keep PR #5887, the original checkout, and overlay-loader refs unchanged.
- Commit context cites `Implements: NSE-024`.
