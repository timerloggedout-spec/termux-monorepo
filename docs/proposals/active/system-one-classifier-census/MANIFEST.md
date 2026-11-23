---
id: system-one-classifier-census
title: "System One classifier census — the full decision-model ecosystem as the Tier-1 extension backlog"
author: Perplexity
posted_at: 2026-10-27
source: "Perplexity research answer (inventory as of 2026-10-21), uploaded by the owner 2026-10-27; full text preserved in CENSUS.md. Registered by the Tier 1 Classifiers steward at the owner's direction."
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: []
related_prs: [1754, 1782, 1786]
gates_required: [proposal-lifecycle, repo-gate]
---

# MANIFEST — system-one-classifier-census

## Why this is a proposal

This census was referenced as the basis for an implementation said to have begun. The 2026-10-27 repository audit found a passing source mention (the Awesome Decision Models directory) in `docs/architecture/INFRASTRUCTURE-CMDB-P0-INVENTORY.md`; a tracked proposal, package and code entry remained unregistered at that point. The owner's direction registered this work as a proposal and extended every census entry into a tracked item in ITEMS.md.

## Summary

- The census inventories the **System One** ecosystem — typed decision
  models that take application state plus caller-defined questions and
  return choices, scores, or probabilities (Choice / Score / Noul)
  instead of open-ended text: 88 model families, adapters, runtimes,
  and directories, each with source URLs (CENSUS.md).
- The local observatory names are role labels, while the similarly
  named catalog entries are independently maintained external
  candidates. Keep four identities separate: role contract, local
  implementation, external project/model, and protocol adapter.
  Local Mev captures text-generation output; local Jev scores against
  a rubric; local Kev performs exact/token-F1 reference comparison;
  local Laya reduces aligned Jev/Kev evidence. External Jev, Kev, Laya
  and both Mev entries retain their own model/service identity and
  provenance. The names alone establish neither code lineage nor
  capability equivalence.
- The observatory dispatch provides a local baseline trial. External
  System One-compatible services also have a distinct typed-decision
  route through `decide(state, questions)`. That adapter exposes typed `decide(state, questions)`; generic `ask(prompt)` requires a separate adapter. Role mapping remains candidate-specific and requires explicit producer/critic adapters plus matched trials.
  Compare these candidates through capability-specific adapters and
  matched cohorts. This proposal supplies the external candidate
  inventory for those comparisons.

## Workstreams

- **W1 — Census → catalog integration.** Fold the census entries into
  the fleet's Tier-1 classifier map and provider catalogs
  (`scripts/provider_model_catalog.py`, hub providers), each entry
  carrying its census state (hosted / open weights / adapter /
  runtime) and source URL. Each entry maps to one declared model, adapter, runtime or directory layer.
- **W2 — Counterpart evaluation.** The self-hostable namesakes and
  near-peers (Kev, Laya + ports, Lev, Tev1, Strands Decider 2B,
  Nimble, Open-Jev, jev-style, Ollaya-served models) are candidates
  for observatory trials via `classifier-trial-dispatch` where a
  free route exists. Hosted/paid entries (Jev via TypeSafe, Clef,
  pplx-decider, and similar) stay `referenced` until the owner
  allows a paid route (`free_only=false` is owner-gated).
- **W3 — Adapters, runtimes, directories tracking.** The technique
  and runtime layer (SemIf, AnyJev/Tacit, simple-jev, Ollaya,
  laya.cpp, sys1, classifier.dev, the directories) is tracked as
  infrastructure options in their own layer and count.

## Honesty notes (carried from the source)

- Many entries use directory-level evidence; ITEMS.md states remain `referenced` until a workstream verifies each entry against primary sources.
- Treat source coverage as a dated snapshot; variants, quantizations and new checkpoints form an open-ended set.
- Track API compatibility and capability equivalence as separate evidence dimensions (question types, context and calibration differ). Cross-model performance ranking requires matched trials.

## Tranche-1 trials (2026-10-27)

Executed under the owner's "Get them in our comparisons!" order with the
free_only gate standing; records in TRIALS.md. Laya **evaluated** via a
self-hosted simple-jev server calling the fleet's typed-decision stage
(quality 0.7139 / grounding 0.7692 on the trial state); simple-jev
**evaluated** as the serving adapter (its hosted demo refuses datacenter
egress — 403 from both the sandbox and GitHub Actions, run 40517046438).
Kev is a LoRA-adapter + head family; trial admission requires its compatible serving stack. mev (Mellow AI) is a full
merged model — trial_candidate; local serve blocked on this host
(9 GB weights vs timing-out egress + 7 GB RAM; see TRIALS.md T1-MEV). Jev (TypeSafe)
and the other paid-route rows are on the blocked-paid list in TRIALS.md
for an owner ruling (SC-004).
