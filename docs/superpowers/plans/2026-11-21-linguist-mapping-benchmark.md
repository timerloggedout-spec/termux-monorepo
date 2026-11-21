# Linguist Mapping Benchmark — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-11-21-linguist-mapping-benchmark-design.md`
**Proposal:** NSE-024
**Execution:** inline, bounded to benchmark corpus, feed adapter, tests, and documentation

## Global constraints

- Keep `linguist-panel-feed/v1` authoritative.
- Preserve all source grades, relations, provenance, and feed timestamps.
- Keep codec round-trip evidence separate from semantic mapping grade.
- Keep count-only families out of enumerated records.
- Report ranking quality only when ranked outputs are supplied.
- Keep dashboard rendering changes outside this plan.
- Use imperative commit subjects and action-first PR text.

## Task 1 — Establish fixture and regression contract

**Files:** `experiments/linguist/mapping-benchmarks/fixtures/fleet-lean-mappings.json`, `tests/test_linguist_mapping_benchmark.py`

- Preserve the 30-row sourced fixture.
- Correct the test import syntax.
- Assert 522 distinct records from the 523-entry snapshot, with one duplicate occurrence retained as metadata.
- Assert unique IDs for reused nomenclature label IDs and deterministic disambiguation for conflicting source IDs.
- Assert exact duplicate rows collapse with `feed_duplicate_count`.

**Expected:** focused tests describe deterministic generation, evidence-state retention, feed identity, duplicate accounting, count-only exclusion, and ranking metrics.

## Task 2 — Implement stable feed identity

**File:** `scripts/linguist/mapping_benchmark.py`

- Prefer feed `mapping_id`, then `label_id`, then `id`.
- Scope identity by family and append a digest of the canonical source entry.
- Collapse exact duplicate entries while preserving occurrence count.
- Mark identity-collision groups and retain the original feed entry ID.
- Emit feed entry, projected mapping, duplicate, collision, and timestamp metadata.

**Expected:** every projected record has a unique benchmark ID and provenance; exact duplicates are counted once.

## Task 3 — Record proposal and evidence contract

**Files:** `docs/proposals/active/notation-sets/ITEMS.md`, `docs/linguist/MAPPING-BENCHMARKS.md`, this design and plan.

- Register NSE-024 before implementation review.
- Document the 523 → 522 projection and stable identity rules.
- Keep the page-rendering integration as a separate future item.

**Expected:** documentation matches the implementation and preserves the proposal's posted lifecycle until its review disposition changes.

## Verification

Run in the repository checkout or CI:

```sh
python -m pytest tests/test_linguist_mapping_benchmark.py -q
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py --base origin/master
python3 scripts/ci/termux_smoke.py
```

**Expected:** focused tests pass; registry is consistent; repo-gate and Termux smoke pass on the same PR head.

## Stop conditions

- `success`: all focused tests and required gates pass on the same immutable head.
- `blocked`: a required permission or source contract is unavailable.
- `approval-required`: a protected-history or other operator-only action is needed.
- `stagnated`: repeated verification yields no new evidence or improvement.


## Execution ledger

- **2026-11-21 — Task 1:** Preserved the 30-row sourced fixture; added 15 focused tests and corrected the escaped-newline import. The malformed import reproduced a Python `SyntaxError`; the corrected import snippet passed `py_compile`.
- **2026-11-21 — Task 2:** Audited the canonical feed: 523 enumerated rows, 522 distinct mapping identities, one verbatim duplicate, and reused display IDs resolved through native `label_id` / `mapping_id` identity. Added snapshot-scoped record IDs, exact-duplicate counts, and identity-collision metadata. Synthetic identity and duplicate checks passed. Round-trip evidence is independent from semantic grade; pair-scoped candidates, explicit hard negatives, and out-of-pool ranking rejection are covered.
- **2026-11-21 — Task 3:** Registered NSE-024, added the design and plan, and linked the implementation branch to the proposal manifest and registry. Proposal status remains `posted` with operator review requested.
- **Review state:** PR #5752 is ready for review from the final2 branch, based on the current `master` head, with nine scoped files and four imperative commits. Earlier drafts #5738 and #5751 remain open pending replacement validation.
- **Verification state:** Full focused pytest, repo-gate, and Termux smoke remain pending CI evidence on the final PR head. The local runtime has no repository checkout and outbound GitHub access is unavailable; GitHub Actions is the authoritative repository validation surface.

- **2026-11-21 — Review transition:** PR #5752 moved to ready-for-review. The following synchronization commit requests the repository's standard pull-request validation workflows.
