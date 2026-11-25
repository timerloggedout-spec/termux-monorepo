# DoE source control-plane contract

## Authority

`timerloggedout-spec/termux-monorepo` is the authoritative DoE control plane for the related organization repositories. The source repository owns the canonical tournament definitions, factor and treatment specifications, test-suite revisions, acceptance criteria, adjudication rules, and version history.

The repositories owned by `Research-Astute` and `search-astute-ly` are execution replicas. They are intended to provide organization-local workflow adapters and runner capacity. They consume version-pinned instructions from the source control plane and return attributable evidence.

The authority chain is:

1. **Define** — source DoE Tournaments records the tournament, suite revision, factors, treatments, input data revision, metric definitions, and acceptance contract.
2. **Approve** — source control-plane validation checks schema, provenance, security preflight, and immutable revision pins.
3. **Dispatch** — the source control plane sends the approved run contract to each selected organization repository.
4. **Execute** — organization workflows run the exact approved contract on their assigned lane: Blacksmith managed runners or the separate personal self-hosted comparator.
5. **Attest** — each organization returns a signed or hash-addressed run receipt and immutable evidence artifacts.
6. **Adjudicate** — source DoE Tournaments evaluates the returned evidence against the source-owned acceptance contract and records the verdict.

Runner completion is execution telemetry. The source DoE adjudication is the acceptance decision.

## Version-pinned run contract

Every dispatched run carries the following fields:

| Field | Source of authority | Purpose |
|---|---|---|
| `tournament_id` | Source DoE Tournaments | Stable experiment identity |
| `suite_id` / `suite_revision` | Source repository | Exact test definition |
| `control_plane_sha` | Source repository | Immutable control-plane revision |
| `source_baseline_sha` | Source repository | Immutable Termux baseline |
| `target_repository` | Source dispatch manifest | Organization execution destination |
| `incumbent_version` | Tournament manifest | Established system under comparison |
| `candidate_version` | Tournament manifest | Candidate system under comparison |
| `input_revision` | Tournament manifest | Reproducible input/data set |
| `runner_lane` / `runner_image` | Execution receipt | Compute provenance |
| `workflow_run_id` / `attempt` | GitHub Actions | Execution trace |
| `started_at` / `completed_at` | Execution receipt | Timing and resource accounting |
| `outcome` / `metrics` / `artifact_digests` | Execution receipt | Evidence returned for adjudication |

The source control plane pins `control_plane_sha`, `source_baseline_sha`, `suite_revision`, and `input_revision` before dispatch. Official comparisons use full 40-character commit SHAs. Branch names support exploratory refreshes.

## Dispatch and execution boundary

Reuse the existing [Receiver Mesh](../../../docs/ops/RECEIVER-MESH.md) envelope, HMAC verification, dedupe, allowlist, dead-letter, and replay discipline as the design reference. Its documented state is PROTOTYPE: the Worker `RECEIVER_REPO` points to the source repository, and `RECEIVER_DISPATCH_TOKEN` is scoped to that repository alone. The source GitHub App inventory also records one source-repository installation with read-only permissions. These existing credentials do not authorize organization dispatch. Treat cross-organization dispatch as a separate capability: provision a narrowly scoped GitHub App installation for the selected target repositories, grant only the permissions required by the receiver workflow, and obtain approval from each installation owner. Keep the source receiver credentials separate and preserve their source-only scope. Store the new installation credential in a protected source Actions environment. The source dispatch payload contains identifiers, immutable SHAs, and non-secret run parameters.

When deployed, each selected organization repository provides a thin receiver workflow:

- Accept the approved tournament event and validate its payload schema.
- Verify the source repository, allowed suite identifier, immutable source SHA, and target repository identity.
- Check out the source baseline at the supplied SHA with full history and submodule hydration disabled by default.
- Execute only the approved suite revision and selected treatment.
- Record the local workflow run, runner image, resource use, and artifact digests.
- Return a machine-readable receipt to the source evidence intake.

Organization adapters provide execution mechanics. The source repository remains authoritative for test definitions and adjudication. Organization-local edits to a suite or acceptance rule create a proposed source change and a new versioned comparison.

## Matched infrastructure lanes

Run the same approved input, suite revision, source SHA, candidate version, and output schema across:

- **Incumbent lane:** the established personal self-hosted runner and its pinned configuration.
- **Blacksmith lane:** the organization-managed runner and pinned image.
- **Optional independent lanes:** only independently attributable OS, architecture, or treatment partitions.

Keep credentials, caches, and artifacts scoped to their execution lane. Start with one Blacksmith job per organization per comparison. Expand concurrency when the suite partitioning and evidence model justify it.

## Evidence integrity and security gates

Run repository hygiene and secret scanning before executing organization-controlled code. Review tracked shell histories, session files, workflow scripts, package hooks, and credential-bearing configuration. Rotate or revoke exposed credentials and remove sensitive artifacts from repository history as indicated by the scan.

Use read-only checkout permissions for baseline acquisition. Scope dispatch credentials to the intended repositories and event. Keep secrets out of pull-request and fork execution paths. Store receipts and artifacts with content digests and source revision metadata.

A source adjudication requires a complete receipt, matching immutable pins, and all acceptance metrics. Missing evidence is recorded as pending or incomplete according to the source-owned contract. Preserve incumbent and candidate observations as separate versioned records.

## Rollout sequence

1. Identify the authoritative DoE repository in each organization and record its repository ID and default branch.
2. Compare all candidate replicas by complete Git tree and commit ancestry.
3. Complete the security preflight and record remediation evidence.
4. Validate the source-owned tournament and run-contract schemas.
5. Extend the Receiver Mesh through a separately scoped, owner-approved dispatch installation for the selected organization repositories.
6. Install the thin receiver workflow in each selected organization repository.
7. Dispatch one controlled smoke tournament per organization on Blacksmith.
8. Run the same smoke cohort on the incumbent self-hosted lane.
9. Return receipts to source DoE Tournaments and verify source-side adjudication.
10. Expand to the approved benchmark matrix after the first matched comparison passes.

## Operational status

The source PR documents the architecture and reusable execution pattern. Organization workflow deployment, dispatch credentials, live runner execution, and first tournament adjudication remain separate rollout milestones. Record each milestone against its actual repository commit and workflow evidence.


## Source-owned DoE records

The control plane is grounded in the existing DoE records and implementation in `timerloggedout-spec/termux-monorepo`:

- [DoE Family](../../../docs/ops/DOE-FAMILY.md) defines the DoE family, campaign membership, and ownership boundaries.
- [DoE Taxonomy](../../../docs/ops/DOE-TAXONOMY.md) defines design classes and terminology.
- [DoE Methods of the Epoch](../../../docs/ops/DOE-METHODS-EPOCH-2026-11-03.md) records implemented methods, design discipline, and verdict criteria.
- [DoE Scoring Intake](../../../docs/ops/DOE-SCORING-INTAKE.md) defines the evidence consumed by DoE scoring.
- [DoE Proof Coverage](../../../docs/ops/DOE-PROOF-COVERAGE.md) points to the canonical [proof index](../../../experiments/doe/proofs/INDEX.md) and [proof manifest](../../../experiments/doe/proofs/MANIFEST.json).
- [Manager Tournament Contract](../../../docs/research/MANAGER-TOURNAMENT-CONTRACT.md) defines the manager-policy comparison protocol.
- [Receiver Mesh](../../../docs/ops/RECEIVER-MESH.md) defines the current prototype's HMAC, dedupe, allowlist, dead-letter, and repository-dispatch envelope.
- [GitHub App Process](../../../docs/ops/GITHUB-APP-PROCESS.md) and [GitHub App Credential Readiness](../../../docs/ops/GITHUB-APP-CREDENTIAL-READINESS.md) define installation scope, permission approval, and credential custody.

- `deepcli/deepcli/observatory/doe.py` provides the implemented factorial, Taguchi L9, and randomized assignment helpers; `deepcli/deepcli/observatory/tournament.py` provides campaign ranking helpers.

The manager-tournament contract applies to manager-policy cohorts. Other DoE family campaigns retain their own registered experiment contracts, schemas, and acceptance criteria.

These records remain the source authority. The organization dispatch/receipt adapter described in this document is a rollout design; its deployment and first end-to-end adjudication require separate evidence.


## Observed repository inventory — 2026-11-25

- `search-astute-ly/termux-monorepo_enterprise` and `search-astute-ly/termux-monorepo_enterprise_too` are public forks of the source repository. Their `master` heads are identical (`6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`) and their complete Git tree SHAs are identical (`9e13a7d3d3f454075c32b8018ae1df4238a3856d`). The GitHub page reports 33,369 commits behind upstream. Treat them as duplicate mirrors, not independent experimental treatments.
- The source repository and both Search-Astute forks track the same root `.Xauthority` and `.bash_history` blobs (`17aef6f21bac696605551e441295f21788ee3b1a` and `2f6af338f9bdf8a04346c2eeac2e7391d480b00a`). The history contains 501 lines; a targeted scan found no common GitHub token, AWS key, bearer token, password-assignment, or private-key patterns. This bounded pattern scan does not establish complete secret clearance. The 57-byte binary `.Xauthority` artifact remains sensitive session material. Source cleanup is proposed in [PR #5866](https://github.com/timerloggedout-spec/termux-monorepo/pull/5866), which removes both files from the current tree and adds ignore rules. Historical blob removal across the source and forks, session rotation, and fork cleanup remain pending.
- The linked GitHub organization-member inventory for `Research-Astute` exposes five repositories. None is a Termux-monorepo fork or an identifiable DoE execution receiver. `glowing-rotary-phone` is a one-file repository described as Research Staging; `manus-ui-research-hub` is the Manus UI research integration hub. Treat the Research-Astute DoE target as unresolved until its repository identity is verified.
- The source GitHub App inventory records one installation limited to the source repository with read-only permissions. Organization repository writes through the current GitHub connector returned HTTP 403. The authenticated browser profile exposed repository controls, while the attempted security-remediation browser runs ended in execution failure or budget exhaustion. These attempts made no verified organization-repository changes.

This inventory is a dated observation. Refresh repository IDs, heads, tree SHAs, access, and security findings before dispatching a tournament.
