# Rust Zero-Drift Evolution — DoE Campaign Candidate

**Status: proposed / not admitted.** This directory records a candidate experiment design. It is not an active campaign, an executed benchmark, an admitted dependency or evidence of a completed experiment.

## Subject

- Repository: https://github.com/timerloggedout-spec/rust-zero-drift_fork
- Pinned revision: `2f1cac93142b4ce392d57371e5d590a56d13f5ad`
- Candidate themes: compiler guardrails, validated Newtypes and Typestate, Sans-IO architecture, property/mutation verification and deterministic systems patterns.
- Intake classification: restricted-use external reference.

The inspected LICENSE states **All Rights Reserved** and permits public viewing/portfolio inspection only. It grants no general right to redistribute or republish derivative work. The campaign therefore tests independently authored patterns and uses the repository as a reference for hypotheses; source code and protected skill text remain outside the experiment corpus unless written permission is obtained.

The fork's `Cargo.toml` repository field points to `PNWcoastie/rust-zero-drift`, rather than this fork. Provenance requires clarification before further admission.

## Proposed comparison

A 2^4 full-factorial candidate compares four treatment dimensions:

1. Compiler guardrails: repository-native baseline vs unsafe prohibition and strict Clippy.
2. Domain modeling: repository-native types vs validated Newtypes and Typestate.
3. Verification: unit/integration tests vs property, mutation and compile-fail checks.
4. Core boundary: repository-native architecture vs Sans-IO core with explicit adapters.

The intended cohort is authorized, project-owned Rust development work. The design holds task contract, base SHA, Rust toolchain, target, runner and independent evaluator constant, with task-family and difficulty blocking. Outcomes prioritize verified invariants and regressions; build time, mutation sensitivity, binary size, dependency count and maintenance burden are secondary.

## Admission requirements

Before designed dispatch:

1. DoE oversight reviews and admits `DESIGN.json`.
2. The task cohort, factor levels, sample plan, effect threshold, uncertainty method, stopping rule and resource cap are locked.
3. License/provenance boundaries and independent implementation rules are approved.
4. The automated runner is verified for Rust/Cargo execution and evidence emission.
5. Each run emits one record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`.

No run records are present. No pattern has been promoted or culled. Manual exploratory work is observational and remains separate from designed results.

## Record layout

- `DESIGN.json`: preregistered hypothesis, factors, blocks, outcomes, constraints and decision rule.
- `records/`: append-only one-record-per-executed-observation evidence, created when the runner is admitted.
- `SUMMARY.json`: generated only after observations exist.
- `README.md`: source classification and operating notes.
