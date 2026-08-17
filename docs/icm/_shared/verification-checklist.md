# ICM Map Verification Checklist

Use this checklist in `maintenance/03_verify/`. Record results in that stage’s `output/verification-record.md`; do not copy run-specific results into this stable reference file.

## Structure

- [ ] `CLAUDE.md`, `AGENTS.md`, and `routing.md` are byte-identical in each ICM workspace that supplies all three names.
- [ ] Every active working folder has a `CONTEXT.md` with explicit inputs, process, outputs, and human check.
- [ ] No active pipeline stage is empty; each stage has a contract and an `output/.gitkeep` placeholder.
- [ ] Factory/reference material and per-run output are structurally separate.

## Sources and references

- [ ] Every `verified` card cites an existing canonical repository source.
- [ ] Relative Markdown links resolve inside the repository.
- [ ] No routing file carries large source payload that belongs in a canonical shelf.
- [ ] References remain one-way from map documents to their sources unless a source-level reason requires otherwise.

## Scope and human oversight

- [ ] The requested change was inventoried and the design proposal received a human decision.
- [ ] No application code, Python file, generated index, credential artifact, or device state was modified as ICM maintenance.
- [ ] The effect index gives only first-order change routing.
- [ ] The root map plus one stage/card answers where the editor is, what to read, what to change, and where to stop.

## Promotion

- [ ] `git diff --check` passes.
- [ ] Required repository validation has been run and any baseline failures are recorded separately from branch changes.
- [ ] The proposal item and commit/PR reference are present.
- [ ] The change is reviewable; no automatic merge is implied.
