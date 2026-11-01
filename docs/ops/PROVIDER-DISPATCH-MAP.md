# Provider dispatch map — complete catalog

**Owner order 2026-11-01 (fix seat `5f3a3217`): Desk dispatch resolution = COMPLETE catalog.**
Machine-readable source of record: `ops/challenge/desk-feed.json` → `dispatch.provider_catalog`
(schema `desk-feed/v1.3`). This doc is the human mirror; the feed wins on any drift.

## Why

Desk dispatch was a 4-lane funnel {Jules, Gemini, DeepSeek, command-dispatch} against a bench of
164 registry services (91 model records / 89 distinct model providers / 110 distinct providers
across all lanes, `ops/quota/registry.json` blob `0f892261` @master `ff76abef`, census
2026-11-01T11:22Z) and 18 provider workflows in-repo. Already-triggered surfaces (DeepAgent
bridge, provider-batch, CodeRabbit, Devin, Qodo, …) completed work the funnel never routed to.
The funnel is retired: every dispatch-capable surface is a named lane below, honestly classed.

## Classes

- **proven** — triggered ∧ completed, evidence cited per lane (run id / PR / session).
- **wired-unproven** — wired in-repo, no successful run yet. Gets bounded, DoE-stamped proof
  dispatches instead of permanent exile; a first success promotes it at the next feed refresh.
- **triggerable** — a live trigger exists (workflow_dispatch / schedule / event) but the surface
  is support-class or has never fired.
- **inference-only** — registry model records with no build-dispatch wiring of their own.
  Reachable for inference/eval tasks via a named arm (`provider-batch`, `provider-availability`,
  `openrouter-free-counter-batch-probe`); promotion path = `cadence-provider-onboarding` + one
  stamped proof dispatch. The full 91 record ids + 89 distinct providers are enumerated in the
  feed's `dispatch.provider_catalog.inference_only` — nothing is silently dropped from the bench.

## Proven lanes (census 2026-11-01T11:22Z, PAT API firsthand)

| Lane | Task classes | Surface | Evidence |
|---|---|---|---|
| Jules | build, fix | `agent-jules-on-issues.yml` + handoff + review-auto | sessions 17326020844735872479 (PR #2635) + 7007935780300107338 (PR #2731); last success 41296280415 |
| Gemini dispatch | build, feature, invoke | `gemini-dispatch.yml` | D1 SR run 41301369671 ✓ (issue #3050); last success 41301486059 |
| Gemini after-peers | review (2nd pass) | `gemini-after-peers.yml` | 1,269 runs; last success 41299982052 |
| DeepSeek termux-agent | fix, build | `deepseek-termux-agent.yml` | D1 fix-pass run 41301295882 ✓ |
| DeepSeek CI | invoke, review | `deepseek-ci.yml` | last success 41301485914 |
| DeepAgent bridge | device, task | `deepcli-agent-bridge.yml` | 158 runs; last success 39989289180 (2026-10-23). Greens incl. skip-exits ⇒ verify at PR level |
| DeepAgent task | task, build | `deepagent-task.yml` | first success 41301564332 in the widening window (was 0 runs) |
| provider-batch | inference, batch, eval | `provider-batch.yml` | 250 runs; last success 40710434190 (2026-10-28); latest-100 mixed ⇒ verify per dispatch |
| provider-availability | probe, catalog | `provider-availability.yml` | 93 runs; last success 40704824602 |
| provider-command-dispatch | fix, review | `provider-command-dispatch.yml` + command library | 1 run ✓ 39170909023 (2026-10-18, n=1 stale — re-proof on next use) |
| CodeRabbit | review, fix | command library + peer-review-orchestrator | default required reviewer; triggered today (Swarm census) |
| Qodo | review | command library + peer-review-orchestrator | opt-in; triggered today (Swarm census) |
| Devin | review, fix, wiki | `reconcile-devin-wiki-access.yml` + command library | wiki 778 runs, last success 41301566618; review-trigger today NOT_ESTABLISHED (Swarm census) |
| CellCog | review | `cellcog-review.yml` | 30,220 runs; last success 41301485944 |
| Peer-review orchestrator | review routing | `peer-review-orchestrator.yml` | last success 41301622846 |
| ECC Tools | review, audit ops | `agent-ecc-tools-ops.yml` | last success 41301536037 |
| Scout / Delphi | build, verify | owner-named lane route | D0 of record (PR #1702; delphi-oracle @393e1f4b) |

## Wired-unproven

| Lane | Surface | State |
|---|---|---|
| gemini-invoke | `gemini-invoke.yml` | `workflow_call` only, 0 runs |
| gemini-triage | `gemini-triage.yml` | `workflow_call` only, 0 runs |
| gemini-review | `gemini-review.yml` | 26 runs, 0 successes, last failure 2026-08-20 |

## Triggerable (support / never fired)

`gemini-interactions-smoke` (dispatch, 0 runs) · `openrouter-free-counter-batch-probe`
(dispatch, 0 runs) · `cadence-provider-onboarding` (dispatch+schedule, 8 runs, last success
2026-10-30 — the promotion arm) · `provider-recon-compound` (57 runs, last success 2026-10-27) ·
`quota-dispatch-tree` (51 runs, last success 2026-11-01 — routing support, not a build lane).

## Rotation rule (bench-wide)

No provider takes 2 consecutive dispatches for the same entry, across **all** catalog lanes
(supersedes the 2026-10-31 rule, which capped repeats inside the 4-lane funnel only).
Selection = task-fit across the full catalog: proven lanes carry production work;
wired-unproven / triggerable surfaces get bounded proof dispatches; inference-only providers
are selectable via their named arm. Every dispatch stamps provider + surface + selection
reason + session/run id — no stamp ⇒ no dispatch (telemetry gate, 2026-10-30).

**D1 re-selection (2026-11-01):** DeepSeek fix-pass (run 41301295882 ✓) ∧ Gemini SR
(issue #3050, run 41301369671 ✓) stand — distinct providers, rotation-valid, already fired.
Next D1 dispatch ⇒ a proven lane outside {DeepSeek, Gemini} for its task class, reason stamped.

## Refresh

Desk single-writer refresh pattern (feed PR). Re-census registry + workflow runs at each
refresh; a lane's class changes only on cited run/PR evidence, never on wiring alone.
