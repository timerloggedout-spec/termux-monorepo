# Agent Substrate — activation runbook

Wiring home: `ops/agent_substrate/README.md`. Comparison home:
`docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md`.
Doctrine: freemium-prep — everything wireable is wired in-repo
before any account exists; activation is a session, not a project.

## Route 0 — evaluation on GitHub runners (LIVE, no account needed)

This is the only route open today, and it needs nothing from the
owner: dispatch `.github/workflows/agent-substrate-eval.yml`. It
builds a kind cluster on the runner, installs Substrate at the
pinned upstream commit (`ops/agent_substrate/README.md`), creates
the counter demo actor, and increments it through the substrate
proxy. Run evidence = the workflow run log; a green run is the
fleet's firsthand proof the pinned commit installs and serves.
Re-run on every deliberate pin bump.

## Route A — GKE (CLOSED today; owner items, in order)

Substrate on GKE is open to all Google Cloud customers for
evaluation / non-production use (production = allowlist, limited
GA). It installs on GKE **Standard** (Autopilot unsupported) via
`ai-on-gke/substrate-gke`. Substrate itself has no product charge;
the GKE resources incur normal charges — which is exactly why this
route is closed under the owner's card rule until each item clears:

1. **GCP project exists** — the shared fleet item (same project step
   as Data Agent Kit Route A: create WITHOUT billing, plus the
   gcloud sign-in session; prompts land on the broken-screen B160V).
2. **Billing decision** — GKE cannot run on the billing-less Route A
   project. Enabling billing is a separate owner call (card rule).
3. **Install session** — run the substrate-gke installer against the
   project, deploy the control plane, re-run the Route 0 counter
   proof inside GKE, and record run evidence here by PR.
4. **Credential grants stay default-deny** — the bundled credential
   provider starts with an empty, default-deny namespace policy.
   Any atespace grant is a named, per-namespace owner-visible act in
   a follow-up PR — never a silent installer default.

## Exit

Delete the GKE cluster (or the kind eval simply never runs). No
fleet lane depends on Substrate; removing `ops/agent_substrate/`,
the eval workflow, and this doc is the whole exit. One session.

## Status

`wired_for_evaluation` — Route 0 wired, Route A documented and
gated. Status flips only on run evidence, per route.
