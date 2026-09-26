---
id: ops-hitl-control-plane
title: "OPS-EVENT HITL Control Plane"
author: timerloggedout-spec
status: proposed
source: source.md
---

# OPS-EVENT HITL Control Plane

This proposal extends the existing Gource/Core + SeekLog work into a maintainer-facing human-in-the-loop control surface.

The key boundary is intentional:
- OPS-EVENT / SeekLog is the canonical event/replay substrate.
- Gource is a compatible renderer/replay reference and optional parallel visualization consumer.
- The dashboard is the HITL command surface.
- GitHub remains authoritative for repository state and review state.
- n8n-like orchestration is a workflow topology/reference, not a new source of truth.

The control plane may propose, queue, dispatch, observe, validate, and reconcile actions, but every mutating action must produce an evidence envelope and preserve an explicit human approval boundary where repository policy requires it.
