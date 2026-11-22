# Architecture Versioning and Automated Refresh

**Status:** canonical  
**Owner/lane:** Repository Architecture / ICM  
**Canonical for:** semantic version policy, generated architecture evidence, and refresh lifecycle

## Authority

- architecture.md is the repository-wide navigation and synthesis entry.
- Domain architecture documents under docs/architecture/ retain their domain authority.
- Editable Mermaid sources are authoritative for their diagrams.
- docs/architecture/VERSION is the current architecture release identifier.
- docs/architecture/CHANGELOG.md records the meaning of each released architecture version.
- Generated files under docs/architecture/generated/ are projections. The generator owns their contents.

The manifest indexes architecture.md, architecture Markdown and Mermaid sources, docs/ops/diagrams/*.mmd, and the SHE architecture source. The diagram inventory records the SVG renders for architecture flow modules and PNG renders for operational diagrams. SHE's mixed-format architecture document remains indexed as a source-owned document.

## Semantic version policy

Use stable MAJOR.MINOR.PATCH versions.

| Level | Use when | Examples |
|---|---|---|
| MAJOR | A breaking change alters system boundaries, authority, ownership, or a published architecture contract | Reassigning canonical ownership; replacing a cross-plane contract |
| MINOR | A backward-compatible architecture capability or relationship is added | New subsystem, plane, interface, or material data-flow edge |
| PATCH | A correction preserves architecture semantics | Clarifying text, fixing a link, correcting a label or metadata |

The change author proposes the level. Reviewers verify the classification against the actual semantic delta.

## Required change protocol

1. Update the canonical domain source and its paired Mermaid source when a diagrammed relationship changes.
2. Classify the semantic change as MAJOR, MINOR, or PATCH.
3. Increase VERSION and add a matching top-of-file changelog entry in the same pull request whenever architecture sources change.
4. Keep generated manifests and rendered assets out of manual edits.
5. Run the architecture documentation tests, the version-delta gate, Mermaid rendering, and manifest validation.
6. Review the generated manifest and rendered diagrams as derived evidence.
7. Merge only after repository policy gates pass. The trusted master refresh then commits the generated projections.
8. WAIT → WATCH → RE-FETCH the resulting master commit and confirm the manifest and renders match the merged sources.

The CI version gate compares the pull-request head with its base ref. Semantic source changes require both VERSION and CHANGELOG.md in that same change. A version-file-only change also triggers the gate, which requires the matching changelog entry and a version greater than the base version. The first governed baseline starts at 1.0.0.

## Bounded feedback loop

The architecture refresh uses the Loopy six-step contract:

1. Observe the current source tree, base SHA, version, manifest, and diagram fingerprints.
2. Choose the bounded source/diagram scope and semantic version increment.
3. Act on canonical documents, paired Mermaid sources, VERSION, and CHANGELOG.
4. Verify tests, the base-diff gate, diagram renders, and manifest consistency.
5. Record commit, run, artifact, fingerprints, outcome, and remaining work.
6. Repeat only when fresh feedback can change the next action; otherwise stop with a named terminal state.

The loop's terminal states are success, clean no-op, blocked, approval-required, exhausted, and stagnated. Failed checks remain recorded observations and enter diagnosis before another attempt.

## Deterministic manifest

Run the following commands:

    python3 scripts/ci/architecture_docs.py --write
    python3 scripts/ci/architecture_docs.py --check

The generator writes docs/architecture/generated/architecture-manifest.json with:

- manifest schema and architecture version;
- sorted source paths and per-file SHA-256 fingerprints;
- a source-set SHA-256 over ordered path/content pairs;
- diagram source and rendered-asset paths and SHA-256 fingerprints.

The manifest intentionally omits wall-clock timestamps and run-specific metadata. Identical source and render bytes produce identical manifest bytes. Git commit SHA, workflow run ID, and artifact identity remain available from the GitHub Actions execution record and uploaded validation artifact.

## Automated lifecycle

| Event | Action | Authority |
|---|---|---|
| Pull request | Run tests, validate the version bump, render Mermaid, generate and check the manifest, upload review artifacts | Read-only |
| Push to master | Re-render diagrams, regenerate and validate projections, commit changed generated files | Existing trusted refresh job |
| Generated-only follow-up commit | Preserve source version; generated files remain projections | Bot writer under existing workflow permissions |

The existing Automation Documentation Continuous Refresh workflow owns execution. The architecture pipeline adds no independent scheduler, credential, provider, or runtime dependency.

## Failure handling

- Invalid semantic version: fail the version gate.
- Missing version or changelog update: fail the version gate.
- Missing or stale diagram render: fail manifest generation.
- Stale manifest: fail --check.
- Mermaid syntax failure: preserve the failed run as evidence and repair the source.
- Generated-only drift: regenerate from canonical sources and inspect the resulting diff.

A failed run is an observation. The workflow records the failure and follows the repository's WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE loop.
