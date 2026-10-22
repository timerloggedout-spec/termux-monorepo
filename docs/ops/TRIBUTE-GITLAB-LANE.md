# GitLab Tribute discovery/planning lane

This is an **opt-in, read-only** surface for Tribute repositories. GitLab projects are classified explicitly as `native_gitlab` or `github_mirror`; there is no inference that every GitLab project has a GitHub twin. Nothing here changes workflows, provider configuration, credentials, repository settings, or either provider's data.

## Offline planner

Pass a JSON snapshot to the planner. Mode is mandatory. Native projects need an exact namespace path allowlist entry; unlisted projects and unproven mirrors remain observe-only.

```sh
python3 scripts/ci/tribute_gitlab_lane.py --snapshot snapshot.json \
  --project-mode native_gitlab --allowlisted-project group/tribute

python3 scripts/ci/tribute_gitlab_lane.py --snapshot mirror.json \
  --project-mode github_mirror --github-repository owner/tribute --github-sha <canonical-sha>
```

A `native_gitlab` project can produce an unassigned review candidate only when `project.path_with_namespace` exactly matches an explicitly supplied `--allowlisted-project` path. Native mode does not require or claim a GitHub twin; supplying matching canonical GitHub details does not bypass the allowlist. In `github_mirror` mode the canonical GitHub repository mapping and SHA are supplied by the caller; a review candidate requires a valid owner/repository identity and equal 40- or 64-character hexadecimal SHAs. GitHub owner and GitLab group paths can differ. Missing or unequal evidence is `unknown`/observe-only. This evidence is caller-asserted, not independently fetched or proven. Candidate plans are proposals, never actions; the write plan is always empty.

## Optional bounded collector

The same script can collect a snapshot through installed `glab`:

```sh
python3 scripts/ci/tribute_gitlab_lane.py --collect \
  --project-id 12345 --project-mode native_gitlab --allowlisted-project group/tribute
```

The project ID defaults to the explicit positive numeric ID `85129320` and can be overridden with `--project-id`. Collector calls are fixed-host `glab api --hostname gitlab.com` GET requests only, each with a 20-second subprocess timeout. It reads project metadata, default-branch head, opened issues, and opened merge requests; pagination uses 100 records per page and stops at five pages per collection. `pagination_truncated` reports when a full final page means additional records may be omitted. glab authentication is external and never inspected or emitted.

Output includes project path/URL/default branch/ID, head SHA, per-feature collection status, issue/MR identifiers, titles, state, labels, compact milestone (`id`, `title`), username-only author/assignee metadata, and MR pipeline status. Raw descriptions/bodies and user emails are deliberately discarded. GitLab approval details are not collected. A feature explicitly disabled by project metadata (`*_enabled: false` or access level `disabled`) is skipped and reported as `disabled`. Enabled or unknown features are queried normally; permission errors propagate and are not hidden. Collection never performs POST/PUT/PATCH/DELETE and does not read files or secrets from auth configuration.

GitHub mirror SHA evidence must be supplied by the caller (`--github-sha` and optionally `--github-repository`); the collector does not assume or discover a GitHub twin. Do not treat stale or caller-asserted evidence as independently verified.

## Validation

```sh
python3 -m unittest tests.test_tribute_gitlab_lane
```

Tests mock `glab` subprocesses, verify fixed host, timeout and metadata scrubbing, encoded branch refs, disabled-feature skipping, fail-closed permission behavior, bounded pagination/truncation, SHA/repository validation, explicit native allowlisting, and the empty-write-plan invariant. No live call is made by tests. Default mode is read-only planning with no writes. No workflow, provider, settings, secrets, commits, push, or mutations are in scope.
