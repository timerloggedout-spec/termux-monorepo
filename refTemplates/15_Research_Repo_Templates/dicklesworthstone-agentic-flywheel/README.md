# Dicklesworthstone Agentic Coding Flywheel — Integration Profile

**Status:** RESEARCHED · METADATA-ONLY · INTEGRATION PR IN PROGRESS
**Upstream:** https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup
**Methodology:** https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/docs/methodology/THE_FLYWHEEL_CORE_LOOP.md
**Integration contract:** docs/ops/DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md
**Machine-readable stack:** stack.json

## Why this slot exists

Track the Flywheel as a stack of composable capabilities, not as a one-line installer dependency. Upstream ACFS is a broad Ubuntu/Arch-oriented bootstrap that installs and configures 30+ tools; it is not a Termux-native install contract and must not be run wholesale inside this monorepo or CI.

The upstream core loop identifies three primary operating capabilities:

1. **Agent Mail** — coordination, claims, reservations, and handoffs.
2. **Beads Rust (br)** — explicit dependency-aware task graph.
3. **Beads Viewer (bv)** — graph-aware triage and next-task selection.

Supporting layers include command safety (DCG/SLB), multi-agent terminal orchestration (NTM), session search/memory (CASS/CASS Memory), and reproducible bootstrap (ACFS). These are separate capabilities and should be integrated incrementally.

## Adoption posture

- Metadata-first; no recursive clone or installer execution.
- Reuse existing monorepo capabilities before introducing duplicate daemons, schedulers, task ledgers, or mail buses.
- Keep upstream as the source of truth; project-specific patches belong in a maintained timerloggedout-spec/*_fork repository and a shallow gitlink under refTemplates/smods/ only after that fork exists.
- Pin a reviewed tag or commit SHA for any executable dependency; never follow mutable main from production automation.
- Test in a disposable Linux container first. Termux/Android support is a separate compatibility result, not implied by Linux support.
- Do not enable upstream “vibe” defaults, passwordless sudo, destructive-command bypasses, or agent-wide unsafe flags in project-controlled environments.
- No secrets, session stores, provider credentials, or user configuration snapshots in this reference slot.

## Existing repository flywheels and cadence controls

This integration is explicitly **not** a greenfield flywheel implementation. The repository already has:

- A Delphi outcome-feedback flywheel in `scripts/delphi/gate.py` and `.github/workflows/delphi-gate.yml`, which updates role weights from confirmed/missed outcomes using the append-only weights ledger.
- The Delphi lane/event contract for shadow trials, real-run feedback, HindSight misses, and re-scoring pending candidates.
- Camshaft/Flywheel, Cadence, and Gantt scheduling/control surfaces with current-SHA, cooldown, idempotency, and provider-evidence boundaries.

ACFS capabilities must be evaluated as candidate adapters to these control planes. Do not add a second scheduler, task ledger, or scoring/weights ledger. See the repository-wide audit in `docs/ops/DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md`.

## Relationship to the project

This profile is a reference and integration map, not a new runtime control plane. Existing GitHub Actions, task tracking, agent telemetry, and current refTemplates/smods/ pins remain authoritative until a capability passes its own compatibility, security, and dual-gate checks.

See the integration matrix and staged acceptance criteria in the linked contract.
