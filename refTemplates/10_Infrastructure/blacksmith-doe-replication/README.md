# Blacksmith DoE replication pattern

## Authority and topology

- **Control-plane authority:** `timerloggedout-spec/termux-monorepo` owns DoE Tournaments, canonical test definitions, factor/treatment specifications, suite revisions, acceptance criteria, adjudication rules, and version history.
- **Execution owners:** the DoE repositories owned by `Research-Astute` and `search-astute-ly` provide organization-local receiver workflows and runner capacity.
- **Dispatch:** the source control plane sends approved, immutable run contracts to each selected organization repository.
- **Evidence return:** organization workflows return run receipts and content-addressed artifacts to the source control plane for adjudication.
- **Compute:** Blacksmith managed runners execute eligible organization-repository jobs. Personal self-hosted infrastructure remains a separate execution lane and competitor.
- **Comparison:** every result records the control-plane SHA, source baseline SHA, suite revision, input revision, candidate/incumbent versions, workflow run, and runner lane.

The organization repositories are execution replicas, not independent DoE authorities. They consume source-owned specifications at immutable revisions and return evidence to source DoE Tournaments. See [CONTROL-PLANE.md](CONTROL-PLANE.md) for the dispatch, receipt, security, and rollout contract. The personal source repository remains the canonical baseline and retains its portable gate.

## Blacksmith eligibility and current public setup

Blacksmith's Quickstart states that managed runners are available to GitHub organizations, not personal repositories. Install and authorize the Blacksmith GitHub App on each organization, then use the current runner label documented by Blacksmith:

```yaml
runs-on: blacksmith-2vcpu-ubuntu-2604
```

Verify the label and organization eligibility in the selected organization workspace before enabling this template. Dashboard inspection confirmed both `Research-Astute` and `search-astute-ly` organization workspaces are accessible through the account selector. The personal `timerloggedout-spec` account context is distinct from an organization workspace; Blacksmith's managed-runner eligibility applies to organization repositories.

Blacksmith documents transparent acceleration for official GitHub cache actions, including `actions/cache`, and advertises 25 GB of cache storage per repository per week. Treat this as a vendor-published allowance; confirm the live account quota and usage in the dashboard.

## Full-history baseline clone

Copy the following workflow into each organization-controlled DoE repository as `.github/workflows/doe-baseline-clone.yml`. It checks out the complete source-repository history and records immutable provenance. The checkout is deliberately scoped to the root repository first; submodule hydration is a separate, opt-in cost.

```yaml
name: DoE full-history baseline clone

on:
  workflow_dispatch:
    inputs:
      source_ref:
        description: Immutable source commit SHA or reviewed ref
        required: true
        default: master
        type: string
      hydrate_submodules:
        description: Materialize pinned submodules for dependency-sensitive suites
        required: false
        default: false
        type: boolean
  push:
    paths:
      - ".github/workflows/doe-baseline-clone.yml"
      - "doe/**"

permissions:
  contents: read

concurrency:
  group: doe-baseline-${{ github.repository }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  baseline:
    name: Clone and attest source baseline
    runs-on: blacksmith-2vcpu-ubuntu-2604
    timeout-minutes: 30
    steps:
      - name: Checkout source repository with full history
        uses: actions/checkout@v4
        with:
          repository: timerloggedout-spec/termux-monorepo
          ref: ${{ inputs.source_ref || 'master' }}
          path: baseline/termux-monorepo
          fetch-depth: 0
          submodules: false
          persist-credentials: false

      - name: Record baseline provenance
        id: provenance
        shell: bash
        run: |
          set -euo pipefail
          cd baseline/termux-monorepo
          echo "source_sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
          echo "source_ref=$(git describe --always --dirty)" >> "$GITHUB_OUTPUT"
          git status --short
          git log -1 --format='%H%n%P%n%an%n%aI%n%s' > ../../baseline-commit.txt
          git submodule status --recursive > ../../submodule-pins.txt

      - name: Hydrate pinned submodules when required
        if: inputs.hydrate_submodules == true
        shell: bash
        run: |
          set -euo pipefail
          git -C baseline/termux-monorepo submodule update --init --recursive --depth 1
          git -C baseline/termux-monorepo submodule status --recursive > submodule-materialized.txt

      - name: Upload versioned baseline evidence
        uses: actions/upload-artifact@v4
        with:
          name: doe-baseline-${{ steps.provenance.outputs.source_sha }}
          path: |
            baseline-commit.txt
            submodule-pins.txt
            submodule-materialized.txt
          if-no-files-found: warn
          retention-days: 30
```

For reproducible tournament runs, pass a reviewed 40-character commit SHA as `source_ref`. Use a branch name only for exploratory refreshes. The workflow's default `master` value is a convenience for manual discovery, not an immutable comparison pin.

## Clone and compute lanes

Use the following lane model in each organization DoE repository:

| Lane | Purpose | Clone policy | Cadence |
|---|---|---|---|
| Baseline attestation | Record complete source history and pinned submodule SHAs | One full-history root clone | Every comparison |
| Dependency-sensitive suite | Exercise code requiring submodule contents | Hydrate pinned submodules only when the suite needs them | On demand / selected tournament rounds |
| Incumbent benchmark | Measure the established self-hosted system | Run on the incumbent's own controlled runner | Matched test inputs |
| Blacksmith competitor benchmark | Measure the managed-runner candidate | Run on Blacksmith | Matched test inputs |
| Regression / matrix lanes | Independent OS, architecture, or suite partitions | Separate clones only where work is genuinely independent | Change-triggered |

Each organization runs its own baseline and benchmark record. Keep the same source SHA, candidate version, suite revision, test inputs, and output schema across the two organizations.

## Free-tier and cache leverage

1. Start with one Blacksmith job per organization per comparison. Add parallel clones only when the suites can run independently and produce separately attributable evidence.
2. Use Blacksmith's transparent Git checkout and Actions cache. Cache package/build outputs with keys that include OS/architecture and lockfile hashes; keep cache namespaces repository-local.
3. Avoid caching mutable source trees or credentials. Cache deterministic dependencies and build products; store test results as versioned artifacts.
4. Keep the root full-history clone separate from submodule hydration. The root clone records every gitlink SHA; hydrate the submodules only for suites that execute those dependencies.
5. Coalesce pull-request runs by PR and cancel superseded runs. Run broad tournament suites on explicit dispatch or a deliberate schedule.
6. Set workflow timeouts and artifact retention. Track minutes, cache storage, cache hit rate, queue time, and wall-clock duration by organization and lane.
7. Preserve the portable `repo-gate.yml` on GitHub-hosted `ubuntu-latest`; use Blacksmith selectively for organization-owned DoE workloads.

Blacksmith currently advertises 3,000 free runner minutes per month and 25 GB of cache storage per repository per week. Dashboard inspection for both `Research-Astute` and `search-astute-ly` showed 0 / 3,000 2-vCPU Linux runner minutes, $0.00 usage, 0 jobs, and 0 GB sticky-disk usage against a 1 GB allowance for the November 1–23, 2026 reporting period. The reset date and exact cache entitlement were not visible. Recheck live values before increasing concurrency.

## Comparison record

Every DoE result should carry:

- `tournament_id` and test-suite revision
- organization and DoE repository commit
- source baseline commit SHA
- incumbent system version / configuration identifier
- candidate system version / configuration identifier
- runner lane and runner image label
- workflow run ID and attempt
- test input/data revision
- start/end timestamps and measured resource use
- pass/fail outcome, metric values, and evidence artifact references

The DoE Tournaments authority adjudicates acceptance. Runner success alone is not acceptance.

## Security and operational boundaries

- Run a repository hygiene and secret scan before enabling any workflow that executes cloned repository content. The public `search-astute-ly/termux-monorepo_enterprise` snapshot contains tracked `.Xauthority` and `.bash_history` files; treat these as sensitive artifacts and resolve their exposure, history contents, and any related credential/session rotation before executing repository code. The paired `_too` repository exposes matching workflow blob SHAs for the inspected workflow set, so treat it as a replicated copy until a versioned diff establishes divergence.
- Use `contents: read` for clone-only workflows.
- Keep organization runner groups scoped to the DoE repositories that need them.
- Keep secrets out of fork and pull-request execution paths.
- Use immutable commit SHAs for official tournament evidence.
- Keep personal self-hosted runners isolated from Blacksmith jobs and their caches.
- Keep baseline and candidate artifacts separately named and attributable.
- Review any workflow that executes repository-controlled scripts before granting write permissions.

## Source references

- Blacksmith Quickstart: https://docs.blacksmith.sh/introduction/quickstart
- Blacksmith security model: https://www.blacksmith.sh/security
- GitHub Actions billing: https://docs.github.com/en/actions/concepts/billing-and-usage
- GitHub Actions limits: https://docs.github.com/en/actions/reference/limits
