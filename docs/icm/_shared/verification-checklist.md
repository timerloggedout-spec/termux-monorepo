# ICM Map Verification Checklist

Use this checklist in `maintenance/03_verify/`. Record results in that stage's `output/verification-record.md`; do not copy run-specific results into this stable reference file.

## Structure

- [ ] `CLAUDE.md` and `AGENTS.md` are byte-identical in each ICM workspace that supplies both names. (`routing.md` is separately owned: verify its links and contract rather than treating it as a required alias.)
- [ ] Every active working folder has a `CONTEXT.md` with explicit inputs, process, outputs, and automated acceptance criteria.
- [ ] No active pipeline stage is empty; each stage has a contract and an `output/.gitkeep` placeholder.
- [ ] Factory/reference material and per-run output are structurally separate.

## Sources and references

- [ ] Every `verified` card cites an existing canonical repository source.
- [ ] Relative Markdown links resolve inside the repository.
- [ ] No routing file carries large source payload that belongs in a canonical shelf.
- [ ] References remain one-way from map documents to their sources unless a source-level reason requires otherwise.

## Scope and automated evidence

- [ ] The requested change maps to an authorized proposal item and the source inventory is complete.
- [ ] The design proposal is explicit, source-backed, and within the registered scope; no human sign-off is required for ordinary map edits.
- [ ] No application code, Python file, generated index, credential artifact, or device state was modified as ICM maintenance.
- [ ] The effect index gives only first-order change routing.
- [ ] The root map plus one stage/card answers where the editor is, what to read, what to change, and where to stop.
- [ ] The diff is documentation-only and `git diff --check` passes.
- [ ] `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` pass for the candidate, with exact-head CI evidence re-fetched and recorded.
- [ ] Task outcome is verified independently of commit/workflow completion; queued, in-progress, and cancelled states are not success.

## Promotion

- [ ] The proposal item and `Implements: <ITEM-ID>` reference are present.
- [ ] No unresolved critical PR threads or unclassified required-check failures remain.
- [ ] Both required gates are green on the current head and the promotion state is re-fetched.
- [ ] Auto-promotion follows root `CLAUDE.md`; stop for human authorization only at an explicitly listed human-only permission boundary.
