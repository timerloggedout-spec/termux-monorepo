# Dispatch observation — issue-open provider listener

## Observation identity

- Target issue: #5195 (project-task intake for this proposal)
- Event: `issues.opened`
- Workflow: `🔀 Gemini Dispatch (free-tier agentic)`
- Run: [43149913718](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43149913718)
- Execution SHA: `a9652b3fa779bbe11765caaf4c563b8f30c20476` (master at the time of run)
- Subworkflow: `.github/workflows/gemini-triage.yml`
- Job: `triage / triage`
- Job ID: `130958031538`

## Evidence observed

1. `.github/workflows/gemini-dispatch.yml` is triggered by issue `opened` and `reopened`.
2. Its top-level `dispatch` job accepts every issue-open event and explicitly sets its command to `triage` at lines 87–88; it does not require a `project-task`, provider label, `@gemini-cli` mention or QUE `swarm-admitted` label for this event branch.
3. The triage subworkflow ran the existing model router and selected provider `openrouter`, requested model `google/gemma-4-31b-it:free`.
4. The `OpenRouter triage (peer)` step was invoked. The request telemetry reported `HTTP_STATUS=429`, curl exit 0, 671 response bytes and provider error/rate-limit classification. The step logged “invocation not complete”; no response/comment was posted.
5. The Gemini model step was skipped; the separate `invoke` and `review` jobs were skipped.
6. The admission workflow for #5195 independently deferred the filing because the queue picture could not be collected (GitHub API 403 rate limit). It did not admit the task, and the task dispatch receipt remains queued/not owned.

## Classification

- **Workflow behavior:** actual outbound model request attempt occurred.
- **Provider outcome:** HTTP 429; no successful model completion evidenced.
- **Inference accounting:** one request attempt; no successful answer and no token usage evidence. Do not call it a successful inference run, quota observation, endpoint health signal or DoE trial.
- **Relationship to task:** incidental issue-open listener behavior, not an approved worker claim or DPLC execution.
- **Admission result:** swarm-admission = DEFERRED; provider task not dispatched to a worker.

## Control gap

The generic issue-open path in `gemini-dispatch.yml` is inconsistent with the intended “on-demand only” comment in that workflow and with the repository's QUE → provider-admission contract. A project-task filing (or another issue type) can trigger model selection and an external provider request before the task's dispatch marker is admitted.

## Required remediation (separate owner-governed workflow change)

- Gate generic issue-open triage behind the relevant explicit intake/label policy; do not treat every issue-open as a provider command.
- Require `swarm-admitted` or another documented provider-admission receipt before provider-bearing issue automation, except for a separately approved explicit user-triggered command with its own authorization.
- Keep `project-task-dispatch` as receipt/queue only; do not let it become a second model router.
- Reconcile the Gemini workflow's event conditions, router input and provider invocation with #5134 → #5160 and the exact model/account/route entitlement gate.
- Add regression tests for generic issue open, project-task open, deferred intake, explicit authorized command, provider unavailable, and queue picture outage.
- Verify that a skipped or deferred task produces no outbound model request.
- Workflow YAML changes must use the repository's approved privileged workflow-edit path and receive independent review. This proposal does not patch the workflow.

## Source/log references

- [gemini-dispatch.yml on master](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/gemini-dispatch.yml)
- [gemini-triage.yml on master](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/gemini-triage.yml)
- [Gemini dispatch run 43149913718](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43149913718)
- [Swarm admission run 43149913816](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43149913816)
- [Task intake run 43149913698](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43149913698)
