# BOINC — the distributed-compute TEMPLATE of record

Owner ruling 2026-11-18: in fleet architecture, **BOINC names the template** for distributed compute BETWEEN our own surfaces — work distribution across the VMs and devices, shared-RAM-style pooling, volunteer-host work units. The donations lane (idle compute to public science projects) is a SEPARATE, already-noted program and never the referent of "BOINC" in architecture text.

## The template (what we copy)

- **Work units**: compute ships as small, self-describing, independently verifiable units; any surface can take any unit.
- **Volunteer hosts**: surfaces join/leave freely; the scheduler assumes churn (a capped seat never blocks the pool).
- **Shared state via the server**: hosts hold no peer state; work + results flow through one registry of record.
- **Credit accounting**: every completed unit earns a recorded credit — the participation ledger (same shape as the pool's transacting fraction).
- **Redundant validation**: a unit's result is trusted after independent corroboration (the fleet's receipt discipline).

## Fleet mapping

- Surfaces = hosts {Muse VM - Hark VM - devices when the device law lifts}.
- Work units = the compute backlog registry items (ops/compute/BACKLOG.md), sliced to the capacity card.
- Server/registry = the staging index + the export store; results land as exports, never chat text.
- Shared RAM = pooled working sets via the store + Relate-class in-process stores per surface.

## Status

Template of record from 2026-11-18. First adoption target: the registry cadence jobs (pool refresh - endpoints-db - BRR delta) expressed as work units any surface can execute.
