# 2026-10-03 Foresight Implementation Package

## Status

This is an additive implementation pass against the existing briefing/evidence spine. It does not create a second source of truth.

## Implemented

- Dated five-item snapshot: `data/briefing/briefings/2026-10-03.json`.
- Resource evidence appended for MCP 2026-07-28, agent-harness supply-chain research, AgentCompass v1.0.0, CODESTRUCT, llama.cpp b11379, and photonic AI accelerator research.
- Procurement records appended with explicit portability, offline, interoperability, reproducibility, provenance, dependency, runtime/evidence lock-in, security, cost, horizon, confidence, decision status, and unresolved questions.
- Radar signals appended for MCP statelessness, agent-harness supply chain, evaluation infrastructure, AST-native actions, Android/ARM inference, and photonic acceleration.
- Source registry expanded with the new evidence families.
- A machine-checked daily snapshot schema enforces exactly five substantive items.
- A snapshot validator is wired into the existing briefing registry workflow.

## Engineering interpretation

### MCP

Treat MCP 2026-07-28 as the compatibility baseline. Protocol-level statelessness does not prohibit application state; state should be explicit and auditable rather than hidden in transport sessions.

### Agentic security

Treat skills, hooks, MCP declarations, subagents, and agent configuration as dependency classes. The next implementation target is an admission manifest/lockfile that records immutable component identity, version/hash, requested permissions, provenance, and validation result.

### Observability

Keep OpenTelemetry GenAI/MCP conventions adapter-level while they remain Development status. The repository's closed, privacy-safe JSONL contract remains canonical; upstream conventions can be mapped in without allowing prompt/tool payloads into the evidence store.

### Evaluation

AgentCompass is a candidate open evaluation substrate. CODESTRUCT is a candidate structured-action provider. Neither becomes a merge gate by itself. Compare same cohorts, environments, tasks, and manager policies.

### Edge inference

llama.cpp b11379 is now the current evidence anchor for Android arm64 and Snapdragon CPU/GPU/NPU artifacts. The first experiment should pin runtime commit, model hash, device ABI, backend, environment fingerprint, and memory/thermal/energy observations.

### Hardware foresight

Photonic acceleration remains a research/procurement watch. The actionable software requirement is accelerator-neutral interfaces and measurement of memory/energy movement.

## Next bounded experiments

1. Audit repository MCP integrations for pre-2026-07-28 session assumptions — **initial code search found no `Mcp-Session-Id` implementation hit; re-check generated/external configuration before promotion.**
2. Drafted `schemas/agent-lock.schema.json` and `docs/security/AGENT-HARNESS-ADMISSION.md`; implement the read-only scanner next.
3. Run AgentCompass and the existing ATES reducer over one identical cohort.
4. Add one AST-native action adapter experiment and compare against text editing.
5. Benchmark llama.cpp b11379 on the first admitted Android/Termux cohort.
6. Add memory/thermal/energy receipt fields without making them mandatory when unavailable.

## Evidence discipline

Research claims remain research. Vendor claims remain attributed. H0/H1/H2/H3 describe maturity, not confidence. No aggregate procurement score is introduced.

## Loop

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`
