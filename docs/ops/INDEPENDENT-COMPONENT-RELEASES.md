# Independent component releases and ArchW12.9y integration train

**Status:** release-governance contract  
**Parent:** [BIUDL Integrated Steering and Evidence Plan](../architecture/BIUDL-INTEGRATED-STEERING-AND-EVIDENCE-PLAN.md)

## 1. Why independent releases

Each substantial component/lane must be independently identifiable, testable, comparable and promotable. A single repository-wide version hides which implementation changed and prevents meaningful parallel evaluation.

The integration train is a compatibility/pinset release. It does not replace individual component releases.

## 2. Release families

Use independent version lines, subject to existing repository naming conventions:

- `foresight-vX.Y.Z`
- `chronomancer-vX.Y.Z`
- `hyperforge-vX.Y.Z`
- `workflow-controls-vX.Y.Z`
- `admin-web-vX.Y.Z`
- `admin-graph-vX.Y.Z`
- `collaborator-management-vX.Y.Z`
- `firesight-vX.Y.Z`
- `termux-cockpit-vX.Y.Z`

A release may be a code tag, signed artifact, or documented release record according to the component's packaging. Do not mint a release solely to create an appearance of progress.

## 3. Component release manifest

Every release must declare:

- component ID and semantic version;
- source repository, ref and immutable 40-hex SHA;
- release timestamp and release owner;
- API/schema/contract versions;
- dependencies and compatibility ranges;
- build/runtime environment and dependency lock state;
- test suites, exact candidate SHA, run IDs and results;
- security review and permissions changes;
- artifacts and cryptographic digests;
- known limitations, deferred tests and unresolved risks;
- promotion decision and approver reference.

A test result is only valid for the SHA and environment it actually tested. A later commit invalidates any claim that the later SHA has passed unless the checks ran again.

## 4. Compatibility contract

Compatibility is explicit between component pairs and contract versions. Use:
- `compatible`: tested together on the declared fixture/cohort;
- `conditionally_compatible`: only with named feature/configuration constraints;
- `incompatible`: known break or unsupported pairing;
- `untested`: no evidence; never infer compatibility from successful imports or a shared repository.

The integration train pins exact component versions, SHAs, contract versions, configuration digests and required evidence. It should also declare intentionally omitted/degraded components.

## 5. ArchW12.9y integration release

ArchW12.9y is the integration release train. Its manifest joins independently released components into a tested system baseline.

Minimum pinset:

```yaml
integration_id: "ArchW12.9y"
integration_version: "<version>"
created_at: "<UTC>"
source_repository: "timerloggedout-spec/termux-monorepo"
components:
  - component_id: "foresight"
    version: "<semver>"
    sha: "<40-hex>"
    contract_versions: []
    compatibility: "tested"
  - component_id: "workflow-controls"
    version: "<semver>"
    sha: "<40-hex>"
    contract_versions: []
    compatibility: "untested"
validation:
  required_contract_suites: []
  run_refs: []
  result: "not_run"
promotion:
  state: "not_promoted"
  approver_ref: null
```

This is an example shape, not an existing manifest or claim that any component is released.

## 6. Comparative parallel releases

Compare alternatives only when they use:
- the same frozen task fixtures/cohort;
- the same source baseline or declared equivalent baseline;
- the same environment/runtime/dependency lock;
- the same acceptance criteria and test protocol;
- the same evidence schema and attribution policy;
- repeated runs sufficient to report variance.

Keep all attempts, including failures, cancellations and culls. Promote the best validated implementation, not the most active branch or highest volume of generated code. Cherry-pick only the accepted bounded change and retain source lineage.

## 7. Promotion gates

The repository's current LANE-MATRIX dual gate remains authoritative for promotion to master:
1. required repo gate / hygiene + portability success on the candidate SHA;
2. required Termux smoke success on the candidate SHA;
3. exact candidate SHA must be mergeable and not dirty;
4. advisory reviews do not replace required gates;
5. Vercel rate limits remain non-gating where policy specifies;
6. explicit operator promotion and any additional domain approvals remain required.

The current device hold means physical-device validation is not available. A hosted Termux smoke workflow, if present, is evidence only for its actual runner and must not be described as a physical-device test.

## 8. Acceptance criteria

- Every release is traceable to a component SHA and contract set.
- Compatibility claims cite tests that ran against the pinned pair.
- Integration train pins exact component releases and SHAs.
- Parallel comparisons use matched cohorts and retain all outcomes.
- No component inherits a release state from another component.
- Promotion uses exact-SHA repository gates and explicit authority.
- Deferred device checks remain visible and unfulfilled while the device hold is active.
