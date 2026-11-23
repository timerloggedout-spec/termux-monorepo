# Skill source fidelity and transformation experiments

## Purpose

Preserve imported vendor skills in their original form as immutable DoE controls. Evaluate normalized and selectively enhanced copies as independently versioned treatments.

## Content lanes

- **Original:** source bytes, original metadata, path, provenance, and source SHA-256. Immutable.
- **Candidate:** separate file with parent source SHA-256, candidate SHA-256, transformation identifier, rationale, and reviewable diff.
- **Evaluation:** task-suite observations linked to exact source and candidate hashes.

Original vendor wording, structure, metadata, examples, and formatting remain intact. DO Statement Style and other repository conventions apply to repository-authored documentation and candidate transformations. Imported originals remain faithful source evidence.

## Manifest contract

`manifest.json` records source/candidate pairs. Each source entry includes a repository-relative path and SHA-256. Each candidate references the source SHA-256 and has its own repository-relative path and SHA-256. The verifier checks source bytes and candidate lineage without modifying either file.

The initial manifest may contain an empty `pairs` array while source payload promotion is pending. Populate it from the verified vendor source manifest after source promotion. Keep checksum coverage explicitly classified as verified, partial, or unverified.

## DoE

CMP-7 is registered in `experiments/doe/cmp-register/DESIGN.json`. The control is the original skill. Candidate arms are normalized and selectively enhanced copies. Compare task correctness, instruction fidelity, safety, discovery/load success, token/latency cost, and repair incidents under pinned, matched runtime conditions.

Retain every outcome, including failed, skipped, blocked, and inconclusive observations. Require paired observations across multiple skills before an interim review. A winner requires evidence; `no_selection` remains valid.

## Run locally

```sh
python scripts/ci/verify_skill_lineage.py --manifest experiments/doe/skill-content-preservation/manifest.json
```

The verifier is read-only and uses only the Python standard library.
