# Skill source fidelity and transformation experiments

## Purpose

Preserve imported vendor skills in their original form as immutable DoE controls. Evaluate normalized and selectively enhanced copies as independently versioned treatments.

## Content lanes

- **Original:** exact source bytes, original metadata, path, provenance, checksum state, and SHA-256. Immutable.
- **Candidate:** separate file with a source ID, parent source SHA-256, candidate SHA-256, transformation identifier, rationale, and reviewable diff.
- **Evaluation:** task-suite observations linked to exact source and candidate hashes.

Original vendor wording, structure, metadata, examples, and formatting remain intact. DO Statement Style and other repository conventions apply to repository-authored documentation and candidate transformations. Imported originals remain faithful source evidence.

## Manifest contract

`manifest.json` contains independent `sources[]` and `candidates[]` collections. Source records exist before any derivative exists. Multiple candidates may reference one source. Candidate paths resolve to distinct files and carry their own hashes.

The workflow compares existing source pins with the target branch's trusted manifest. Existing source IDs, paths, and SHA-256 pins remain stable across updates. New source entries record provenance and upstream checksum coverage as `verified`, `partial`, or `unverified`. A locally computed SHA-256 establishes the imported file's identity; it does not upgrade unverified upstream archive provenance.

## DoE

CMP-7 is registered in `experiments/doe/cmp-register/DESIGN.json`. The control is the original skill. Candidate arms are normalized and selectively enhanced copies. Compare task correctness, instruction fidelity, safety, discovery/load success, token/latency cost, and repair incidents under pinned, matched runtime conditions.

Retain every outcome, including failed, skipped, blocked, and inconclusive observations. Require paired observations across multiple skills before an interim review. A winner requires evidence; `no_selection` remains valid.

## Run locally

```sh
python scripts/ci/verify_skill_lineage.py --manifest experiments/doe/skill-content-preservation/manifest.json
python -m unittest tests.test_skill_lineage -v
```

The verifier is read-only and uses only the Python standard library.
