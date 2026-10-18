# Review Log / Debate — agent-contributor-provenance

**Status:** in review; no merge/promotion decision recorded here until the current SHA's gates and review disposition are re-fetched.  
**Parent:** [issue #1241](https://github.com/timerloggedout-spec/termux-monorepo/issues/1241)  
**Implementation:** [PR #1244](https://github.com/timerloggedout-spec/termux-monorepo/pull/1244)

## Binding decisions

| Decision | Rationale | Evidence / status |
|---|---|---|
| Extend ATES and the Agent Evidence Substrate; do not add a parallel telemetry store. | Reuse canonical schemas, reducer, run linkage, and read-only observer. | [ATES event schema](../../../ops/AGENT-THROUGHPUT-EVENT.schema.json); PR #1244 |
| Keep GitHub actor/triggering actor separate from author/provider/model. | PAT-mediated commits cannot prove which agent or model produced a change. | [Orchestration contract](../../../ops/AGENT-TEAM-ORCHESTRATION.md); PR #1244 |
| Record settings/context as SHA-256 fingerprints only; leave missing values null. | Preserve provenance without retaining prompts, completions, secrets, or raw context. | [Author provenance schema](../../../ops/AGENT-THROUGHPUT-EVENT.schema.json) |
| Keep Pinggy/tunnel health outside ATES agent-task throughput. | Infrastructure liveness is not an agent task or evidence of model authorship. | [Live bridge contract](../../../ops/TERMUX-LIVE-BRIDGE.md); [bridge redundancy](../../../ops/BRIDGE-REDUNDANCY.md) |
| Exclude the generated citation index and output ledger from their own source corpus. | Prevent recursive self-citation and inflated citation counts. | Current curator tests; [resolved Codex finding](https://github.com/timerloggedout-spec/termux-monorepo/pull/1244#discussion_r4305963425) |
| Treat citation extraction as provenance preservation, not truth verification. | A valid URL/reference does not independently verify the associated claim. | [Daily Digest Specification](../../../briefing/DAILY-DIGEST-SPEC.md); source-curation tests |
| Promote only after current-head repo-gate and termux-smoke success plus outcome verification. | Repo governance defines these as the dual gates; third-party review and Vercel are advisory/non-gating. | [Dual-gate contract](../../../ARCHW1Z-GATE.md); [lane matrix](../../../ops/LANE-MATRIX.md) |

## Collaborator and review ledger

- **Codex:** found a P2 workflow-summary defect ("identity[1]" after changing the identity map to objects). Fixed to "identity.agentId" on the feature branch and resolved the now-outdated thread. The original review references an earlier SHA, so it is not treated as current-head review approval.
- **Gemini:** the requested review workflow completed, but no concrete findings/comment were published; completion of a workflow is not equivalent to an affirmative review.
- **CodeRabbit:** a current-head full-review trigger was requested. The peer-response state reported "pending_operator_action" for a provider-owned control; no completed CodeRabbit review is claimed. Do not simulate the provider UI action or fabricate an acknowledgement.
- **Jules:** a read-only audit was requested on issue #1241. The Jules API lane reported that it could not create a session and asked to verify its connected source. This is a failed/unavailable delegation attempt, not a review.
- **DeepSeek CI:** workflow run was cancelled during rapid PR synchronization; cancelled is not success.
- **Vercel:** deployment checks reported the account daily deployment limit; this is not application test evidence and is non-gating per the lane-matrix policy.
- **ECC Tools:** hosted promotion readiness, PR config audit, and harness audit reported success for the observed SHA; check-publication permission was unavailable. Treat the report as advisory evidence, not a replacement for GitHub checks.

## Current validation snapshot

On commit "ef0d08a15ad4dc67a174d2b23430dd50eecf2b1b":

- repo gate: success
- termux smoke: success
- proposal lifecycle registry validation: success
- briefing registry validation: success
- research registry validation: success
- Agent Quality Lane: success
- Orchestration Regression Guard: success
- Advisory GitHub Actions lint: success at last terminal observation
- CodeQL: queued/pending at the last observation
- Citation ledger: 102 citation instances from 18 source documents; artifact "source-citations-39103273114" is linked from the PR.

This is a timestamped snapshot, not a claim about a later head. Any additional commit requires re-fetching the current head and rerunning the dual gates before promotion.
