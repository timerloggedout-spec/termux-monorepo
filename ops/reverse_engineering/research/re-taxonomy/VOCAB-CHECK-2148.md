# RE taxonomy — vocab check of record (PR #2148)

Lane: reverse-engineering-toolkits (d573ca2b), 2026-10-28.
Target: PR #2148 (research-triggers/re-taxonomy-templates), head
`0f27f06f048c333e803d3658da7fb5e4bbe53c67` — fetched FETCH_HEAD verified
identical to the PR head at verdict time. (Announced in chat as #2147;
#2147 is an unrelated issue-lifecycle PR — number corrected on the PR.)
Verdict posted: PR #2148 comment 6477797743 — **PASS, merge cleared.**

Checks (all firsthand, against master `ops/reverse_engineering/taxonomy.json`,
re-taxonomy/v1 from PR #2145):

1. Embedded fallback vocabulary in `scripts/reverse_engineering/re_taxonomy_intake.py`
   program-diffed vs taxonomy.json: all 8 axes (target, format, architecture,
   method, objective, tool_role, environment, evidence) + workflow_stages —
   **identical, zero deltas**.
2. Live `--taxonomy ops/reverse_engineering/taxonomy.json` resolution exercised.
3. Form headings == parser-consumed fields, both forms
   (`reverse-engineering-taxonomy.yml`, `reverse-engineering-taxonomy-record.yml`);
   record node carries exactly the fields `taxonomy.py validate()` consumes
   (id, name, kind, parents, tags, toolchain).
4. Their suite reproduced in `test-tree/` (this archive): **6/6 pass**.
5. Independent end-to-end: taxonomy.json `example_record` (Android
   native-library analysis) filed through the record form → parsed +
   validated against the live taxonomy; node id
   `android-native-library-analysis`, parents preserved.
6. Negatives refused: `architecture:ARM128` (not in vocab);
   parent `no-such-node` (does not resolve).
7. Workflow pattern: issues opened/reopened/edited only, no `labeled`,
   no concurrency group, `{}` top permissions, no `pull_request_target`,
   `--taxonomy` from trusted checkout.

Kept for comparison against: any future vocab change (ping-before-merge
rule), the v2 research outcome of issue #2146, and the as-merged state
of PR #2148.
