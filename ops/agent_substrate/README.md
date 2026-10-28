# Agent Substrate — fleet evaluation wiring

Agent Substrate is the open-source sibling of Google Cloud's Agent
Compute Engine: the same agent-first design (hardware-isolated
microVM or gVisor sandboxes, egress proxies that inject credentials
outside the agent's reach, idle suspend/resume) as a Kubernetes
runtime that runs on any cluster. It is the only form of the ACE
design that can be executed today; ACE itself is announced-only
(see `docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md`).

## Pins (verified live 2026-10-28)

- Upstream: https://github.com/agent-substrate/substrate
  (Apache-2.0; pinned commit `475f49b023352b47b8504ffead596953f28d7e7f`,
  2026-10-28 — bump deliberately, never track `main` implicitly)
- GKE installer (not used by the fleet eval; billing-gated, see the
  activation doc): https://github.com/ai-on-gke/substrate-gke
- Upstream docs that matter here: `docs/egress-credential-injection.md`
  (the credential-swap seam), `docs/security.md`, `docs/architecture.md`

## Fleet mapping

| Substrate concept | Fleet analogue |
|---|---|
| Actor (suspended/resumed sandbox) | One agent session — the unit ACE gives a microVM |
| Atespace | A lane's namespace: policy and credential grants are per-atespace |
| Credential provider + egress injection | Foundry `account_ref` seam / `scripts/credential_proxy/` — credential enters at egress, never inside the sandbox; the bundled provider deploys **default-deny** and grants are explicit per atespace |
| Sandbox identity (SPIFFE) | The attested-identity half Provenance/HindSight currently records by convention |
| Snapshot / suspend | Idle-cost shape: agents wait most of the time (quota/cost discipline) |

## Evaluation shape

The eval runs **only** on GitHub-hosted runners via
`.github/workflows/agent-substrate-eval.yml` (`workflow_dispatch`):
kind cluster → upstream quickstart → counter demo actor → proxy →
HTTP increment → evidence in the run log. No GCP, no card, no VM
hosting, nothing continuous. GKE activation is a separate, later,
owner-gated step: `docs/ops/AGENT-SUBSTRATE-ACTIVATION.md`.

Status: Route 0 evaluation PROVEN (run 40765289808, 2026-10-28 —
kind + pinned Substrate + counter actor + proxy increment, all on a
GitHub-hosted runner). Not deployed anywhere; no fleet workload
runs on Substrate today.
