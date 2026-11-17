# YAML review boundaries — AR-32

Continue PR #5496 without rewriting history or changing workflow authority.
Source head: `44381a34ab5a870e3cb06b0ab8ec9814eb771ed6`.

## Evidence and design

- Review 4583420142: an indented plain-scalar continuation beginning with
  `? "unfinished` must not open multiline quoted state and hide later faults.
- Review 4583433895: an empty anchored flow node must stop its anchor name at
  flow delimiters, leaving subsequent quoted entries visible to the scanner.
- Review 4583433904: YAML standalone CR is a line break. Correct the earlier
  payload assumption; normalize CRLF and CR, but not arbitrary Unicode separators.
- The explicit flow-key report 4583433888 is already addressed; add its exact
  example to prevent regression during continuation-state changes.

Keep the gate stdlib-only and heuristic, not a replacement YAML parser. Extend
the existing line scanner with optional plain-scalar parent-indentation state.
At greater indentation, plain continuation starts with quote eligibility disabled;
real mapping/flow boundaries restore it. Preserve existing independent callers.

## Execution

1. `tests/test_repo_gate_block_scalars.py`: parser-backed continuation, anchor,
   line-break and explicit flow-key fixtures; verify failures before production edits.
2. `scripts/ci/repo_gate.py`: add continuation state, anchor token delimiters,
   and YAML line-break normalization. Preserve quote and flow state interfaces.
3. Update AR-32 in `docs/proposals/active/actions-refinements/ITEMS.md` to record
   corrected scope and review evidence; keep status in_review.
4. Run repo-gate and automation unit suites, catalog check, staged repository
   gate, Linux smoke and diff checks. Inspect diff for security/scope changes.
5. Commit and push with `Implements: AR-32`; re-fetch exact remote head,
   required checks, review dispositions; leave owner-authored merge authority intact.

## Non-goals

No workflows, generated catalogs, provider invocations, paid infrastructure,
credential/permission edits, device-side claims, or unrelated cleanup.