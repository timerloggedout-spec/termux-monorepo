# Reverse Engineering — research kept for comparison

Owner order 2026-10-28: keep any research completed for comparison.
This is the durable archive (not scratch) for this lane's completed
research/check work. Repo landings are the record of the builds
themselves (PRs #2143, #2145); this archive keeps the *evidence and
inputs* those builds and checks ran on, so future comparisons
(v2 taxonomy, template-set merges, wave findings) diff against the
originals, not reconstructions.

## apk-xref/ (PR #2143, merged a732d509d0)

- `pr2140-template-set/` — the research-triggers template set as read
  at seam-lock time (forms, `apk_xref_intake.py`, APK-XREF-TEMPLATES.md;
  PR #2140, later merged 3add283f). The toolkit's findings format was
  built and round-trip-verified against this parser.
- `demo-findings/` — synthetic in-test APK + the findings.md generated
  from it; fed through the #2140 parser, all findings fields round-tripped
  losslessly.
- `live-proof-fdroid/` — real-artifact proof: F-Droid client
  `org.fdroid.fdroid_2000052.apk` (2.0.2, build 2000052, 12,569,951 B,
  sha256 19d51fad482239f6df6a99120e34513667e9a86d136dafdc4a211a68c3327b52)
  + its `--no-corpus` extraction (31 permissions, 36 components,
  3 DEX, 69 hosts, 339 endpoints). The generic `segment` tracker-marker
  false positive was found on this artifact and tightened.
- `wave-briefs/` — the three wave briefs read at build time
  (#2064 aihub, #2121 wraith, #2123 relagent) as filed.
- `publish-spec-2143.json` — the exact pat_publish spec for PR #2143.

## re-taxonomy/ (PR #2145, merged 6e8e955ad1; research issue #2146)

- `gen_taxonomy.py` — the generator that produced taxonomy.json v1.
- `publish-spec-2145.json`, `research-request-2146.json` — exact
  publish spec + the filed [research:service] issue body.
- `pr2148-template-set/` — research-triggers' RE template set at the
  head vocab-checked (0f27f06f04): forms, intake workflow,
  `re_taxonomy_intake.py`, doc, tests.
- `test-tree/` — the reconstructed tree the #2148 suite was re-run in
  (parser + tests + master taxonomy.json): 6/6 pass.
- `VOCAB-CHECK-2148.md` — the check of record: embedded vocab identical
  to taxonomy.json (8 axes + stages, 0 deltas), example-record
  end-to-end OK, negatives refused, verdict PASS (PR comment 6477797743).

## Input of record

Collaborator example (Perplexity export) the taxonomy v1 adapts:
`user-supplied upload (owner files)/A_hierarchical_matrice_tagged_overlapping_nested_t_0_oe2v.md`
(owner-supplied, stays in user files).
