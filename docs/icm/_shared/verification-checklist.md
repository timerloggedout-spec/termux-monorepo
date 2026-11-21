# ICM Map Verification Checklist

Use this checklist in `maintenance/03_verify/`. Record results in that stage's `output/verification-record.md`; keep run-specific results in stage output and maintain this file as a stable reference.

## Structure

- [ ] Verify each declared `CLAUDE.md` / `AGENTS.md` relationship from its mapping ledger. Enforce byte identity only for explicit alias pairs; record compatibility, historical-rename, and independent-entry relationships separately. Verify `routing.md` under its own contract.
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
- [ ] The design proposal is explicit, source-backed, and within the registered scope; advance ordinary map edits through deterministic evidence and repository validation.
- [ ] Keep application code, Python files, generated indexes, credential artifacts, and device state in their owning scopes; ICM maintenance changes documentation and approved templates.
- [ ] The effect index gives only first-order change routing.
- [ ] The root map plus one stage/card answers where the editor is, what to read, what to change, and where to stop.
- [ ] The diff is documentation-only and `git diff --check` passes.
- [ ] Local map-specific checks and worktree preflight are recorded in verification; exact-head `repo_gate` and `termux_smoke` results are recorded in the promotion stage.
- [ ] Verify the task outcome independently of commit/workflow completion; classify queued, in-progress, and cancelled states as pending or non-passing.

## Promotion

- [ ] The proposal item and `Implements: <ITEM-ID>` reference are present.
- [ ] Resolve critical PR threads and classify every required-check result before promotion.
- [ ] Both required gates are green on the current head and the promotion state is re-fetched.
- [ ] Auto-promotion follows root `CLAUDE.md`; stop for human authorization only at an explicitly listed human-only permission boundary.
