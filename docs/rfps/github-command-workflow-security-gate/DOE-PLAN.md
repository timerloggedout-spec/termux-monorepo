# DoE plan — command and workflow security gate

**Parent:** `security.command_workflow_gate`  
**Existing experiment lane:** issue #4015  
**Mode:** synthetic/replay only; no live attack or destructive execution.

## Pre-registration

Freeze before replay:

- baseline commit SHA and candidate policy SHA;
- parser/rule-set version;
- exact fixture corpus hash;
- treatment assignments and participant-role map;
- decision thresholds, replication floor, and stopping rules;
- provider/model catalog snapshot and eligibility evidence, if any endpoint qualifies.

The baseline is the current behavior as observed in the reviewed iOS-Termux implementation plus the current repository workflow checks. Record gaps rather than assuming absent controls are passing.

## Treatments

| Treatment | Policy | Purpose |
|---|---|---|
| A — Control | Current checks and existing Tier-1 deterministic floor | Establish current false-positive and miss baseline |
| B — Deterministic-first | Structured command plan, parser-backed normalization, protected-target and effective-config rules | Test core policy coverage |
| C — Adaptive fleet | B plus capability/adapter/availability/quota-aware participant selection | Measure whether dynamic selection improves review quality without excess dispatch |
| D — Escalated critique | B plus independent reviewer/verifier only when risk, uncertainty, or disagreement exceeds the pre-registered threshold | Measure targeted escalation value |

No treatment may use model output to override a deterministic block, grant permission, or mark an unverified operation safe.

## Fixture strata

- benign file operations, including temporary-file cleanup;
- `rm -f`, `rm -r`, `rm -rf` and mixed flag order;
- protected roots, home/storage paths, relative paths, symlinks, traversal, globbing, and ambiguous targets;
- `find -delete`, Python `unlink` / `shutil.rmtree`, and shell redirection;
- SSH client/server distinction, effective `sshd_config`, public/private binds, password/key combinations, unknown configuration;
- shell interpolation, command substitution, nested shells, untrusted issue/PR strings;
- secret-file/environment reads and attempted egress;
- downloads, redirects, archive extraction, and download-to-execute sequences;
- GitHub Actions trigger trust, fork PRs, permissions, mutable action refs, checkout persistence, and secret-bearing jobs;
- parser failure, stale catalogs, missing quota, 429/5xx, unavailable adapters, and duplicate event delivery.

Fixtures must be inert strings or mocked metadata. Never run the commands.

## Metrics

Report per stratum and overall:

- high-risk recall / missed high-risk operations;
- benign precision / false-positive review or quarantine;
- safe-admission rate;
- parse coverage and explicit unknown rate;
- policy disagreement and human-intervention rate;
- duplicate/conflicting dispatch rate;
- time-to-useful-resolution and end-to-end latency;
- provider/model failure and unavailable-route rates;
- token and quota consumption only when observed from invocation receipts;
- participant attribution completeness.

Preserve raw fixture outcomes and negative results. Do not claim significance below the pre-registered replication floor.

## Participant and endpoint admission

The five Delphi roles are the existing blind rubric panel, not a set of model APIs. For DoE execution, participant roles are task roles (builder, independent reviewer, verifier, Scout/evidence, cost auditor) assigned only to currently eligible participants.

A free inference endpoint is eligible only when its actual invoke endpoint, dispatch adapter, capability, current availability, exact no-cost terms, and live quota headroom are verified. Provider pool membership is discovery evidence only. If a route or quota check is unavailable, record the participant as unavailable/not established and run the local deterministic control. The current Delphi gate remains `DELPHI_LLM_MAX=0`.

## MoneyBall record

Fix the pass-specific weights at intake and record them in the experiment manifest. Starting proposal (subject to the pass intake, not a global constant):

- fleet-pain relevance: 0.30
- evidence maturity: 0.25
- survivability: 0.20
- inverse adoption cost: 0.15
- composability: 0.10

Store per-axis score, evidence references, weight, weighted contribution, unknowns, and composite. Report the MoneyBall profile beside the Delphi ballot aggregate; never combine the two into one score.

## Stop / promotion rules

Stop a treatment on any secret exposure, unauthorized side effect, deterministic block override, uncontrolled fan-out, quota/billing ambiguity, or evidence-integrity failure. No production promotion from this DoE alone: require exact-head CI, security review, documented false-positive review, a human owner decision, and a rollback plan.
