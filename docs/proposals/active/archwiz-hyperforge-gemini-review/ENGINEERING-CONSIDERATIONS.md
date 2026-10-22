# ArchWiz Hyper-Forge — Engineering Considerations

**Purpose:** this document is intentionally separate from the source-faithful Gemini plan.

The Gemini plan says **what the concept proposes**. This document says **how the repository should engineer, constrain, test, and govern it**.

## 1. Preserve composition over duplication

The strongest implementation already established by PR #937 is an adapter model:

```text
Hyper-Forge
   │
   ├── existing dispatch
   ├── existing RECON
   ├── existing Foresight
   ├── existing ChronoMancer
   ├── existing forensic tools
   └── existing validation gates
```

Do not create a second orchestration protocol merely to make the cockpit look complete.

## 2. Separate presentation from authority

The Tron layer is presentation-only.

Required invariant:

```text
UI / imagery
    ≠
canonical state
    ≠
execution authority
    ≠
validation evidence
```

README imagery, generated art, ANSI panels, and dashboards must not become sources of truth.

## 3. Treat the 20 operations as capabilities

The Gemini numbering varies across the source material. The durable contract should therefore be capability-oriented.

Each operation should eventually have:

- stable capability identifier
- command/tool entry point
- preconditions
- side effects
- evidence output
- tests
- failure classification
- authority level
- operator confirmation requirements

## 4. Make state transitions explicit

The repository already benefits from separating:

```text
COMMITTED
EXECUTED
VALIDATED
PROMOTED
```

Hyper-Forge should not collapse these into one “done” indicator.

Likewise:

- queued ≠ success
- in-progress ≠ success
- generated artifact ≠ validated artifact
- visual status ≠ canonical status

## 5. Use existing evidence infrastructure

The project already has substantial work around:

- Action → Effect
- ATES / throughput
- complexity measurements
- runtime watchers
- historical backfill
- provider/research matrices
- GitHub artifact provenance

Hyper-Forge should consume these evidence surfaces rather than inventing parallel telemetry.

ATES is an observational metric, not a universal merge-quality gate.

## 6. Native Android is a separate delivery surface

The four-tab Android concept is valuable as a product direction, but it should not be disguised as completed by the Termux TUI.

Recommended boundary:

```text
Termux Hyper-Forge
      │
      │ shared contracts
      ▼
native Android surface
```

The shared contract should be established before duplicating behavior in a GUI.

## 7. Foresight / ChronoMancer integration

A future unified loop should be evidence-bearing:

```text
RECON
 ↓
FORESIGHT
 ↓
CHRONOMANCER
 ↓
BOUNDED DISPATCH
 ↓
VALIDATION
 ↓
EVIDENCE
 ↓
RECORD
```

Every transition should preserve correlation identifiers so the resulting record can be traced back to source state and GitHub evidence.

## 8. Security and scope

The cockpit must not:

- print secrets
- persist credentials
- embed provider tokens
- bypass repository gates
- silently promote work
- treat arbitrary model output as authoritative state

Forensics and malware-research lanes should remain separately scoped; the Hyper-Forge surface may navigate to approved research tooling but should not silently expand privileges.

## 9. Acceptance-test strategy

Each capability should receive the smallest deterministic test that proves:

1. importability
2. routing correctness
3. missing-tool behavior
4. failure propagation
5. evidence emission where applicable
6. authority/promotion boundaries

The existing `tests/test_termux_cockpit.py` is the baseline for this pattern.

## 10. Research lanes

The repository's broader research architecture already distinguishes observational providers and environments. Hyper-Forge should keep those lanes composable:

- OpenTelemetry as neutral interoperability boundary
- Docker as reproducible execution substrate
- Codespaces as interactive reproduction surface
- Tree-sitter / Lizard / Radon as complexity providers
- Langfuse / Phoenix as experiment/evaluation adapters
- benchmark suites as later manager-tournament inputs

These are research/measurement surfaces, not mandatory cockpit dependencies.

## 11. Definition of done

A milestone is complete only when:

```text
implementation
 + tests
 + documentation
 + GitHub issue/PR linkage
 + authoritative CI evidence
 + explicit review state
 = promotable milestone
```

No “looks finished” state is accepted.

## 12. Open engineering decisions

- exact native Android technology and lifecycle
- shared protocol schema between Termux and Android
- canonical event envelope for Foresight/ChronoMancer/Dispatch
- capability IDs for all 20 source operations
- restore semantics and safety boundary
- evidence retention policy
- manager/orchestration experiment interface
- acceptance criteria for “full Gemini parity”
