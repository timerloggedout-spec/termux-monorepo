# Source — provider-family-doe-observatory

## Owner direction

2026-11-11, active ChatGPT project conversation:

> Do it ALL

This is the bounded owner authorization for PFDO-001 through PFDO-004 on the feature branch. It is not authorization to bypass the repository's dual gates, merge review, or the independent safety/evidence gates of QDesk participant provisioning.

## Existing contracts used

- `docs/ops/DOE-FAMILY.md` — configured-instance identity and DoE version/settings register.
- `docs/ops/NESTED-FAMILY.md` — `nested-family/v1`, dispatch joins, provenance and the `instance_key` non-enrichment rule.
- `docs/ops/AGENT-MONIKERS.md` — moniker identity boundary.
- `scripts/doe/instance_key.py` — canonical configured-instance key.
- `scripts/tracking/nested_family.py` — existing collector and single-writer contract.
- `.github/workflows/repo-tracking-collect.yml` — Nested Family refresh workflow.
- `.github/workflows/quota-usage-series-refresh.yml` — quota and Swarm refresh workflow.
- `#5136` — Participant Identity Plane build task.
- `#5145` — QDesk Observatory / Delphi DoE proposal.

## Evidence boundary

The settings projection is derived from the documented current-of-record register. It does not assert a singular global DoE version, a participant's provisioned account, a dispatch execution, or an outcome that is absent from the source records.
