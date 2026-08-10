# Jules Session Management

> **Status:** ACTIVE
> **Orchestrator:** Grok (OPERATOR)
> **Related Issues:** [#118](https://github.com/timerloggedout-spec/termux-monorepo/issues/118), [PR #120](https://github.com/timerloggedout-spec/termux-monorepo/pull/120)

This document defines the policy, durable context keys, and workflow contracts that govern how Jules is invoked, debounced, gated, and tracked across various GitHub Actions runners in the monorepo.

---

## 1. Key Principles

To maintain high efficiency, safeguard free-tier limits, and prevent mixed feedback during multi-agent collaboration, Jules operates under strict orchestration rules:

1. **Session Identity**: Every pull request has a stable `context_key` formatted as `pr-<pr_number>-<branch_name>`. This context key is loaded and saved via the `agent-context-store` action.
2. **Continue-only Default**: If a recent comment marker (`<!-- agent-auto-jules -->` or `<!-- continuous-agent-ops -->`) or context record exists for a key, the workflow prefers **continuing** the existing session rather than spawning a new, separate task from scratch.
3. **Quota Gating**: Free-tier limits are enforced directly inside the workflow. When limits are exceeded, Jules skips or queues the invoke rather than performing a silent spawn.
4. **Skip-Reason Reporting**: When an invoke step is skipped (due to debounce, missing keys, `JULES_AUTO_INVOKE=0`, or capacity limits), a visible comment is posted to the PR outlining the exact reason.
5. **Operator Token (PAT) Path**: Write-path comments that require @jules or @coderabbitai attention utilize the operator token (`OPERATOR_GITHUB_TOKEN` or `OPERATOR_TOKEN`) to ensure downstream workflow triggers are correctly invoked.

---

## 2. Quota & Capacity Limits

The workflow enforces a dual-quota mechanism:
* **Concurrency Limit**: Maximum of **3 concurrent active** Jules runs.
* **Rolling Daily Limit**: Maximum of **15 runs per rolling 24-hour period**.

If either limit is breached, the execution is gated (skipped) with an on-PR explanation comment.

---

## 3. Workflow Contracts

### 3.1. `agent-review-auto-jules.yml`
Fires automatically on external bot feedback (CodeRabbit reviews, Devin comments, etc.).
* Uses `agent-context-store` to load work context.
* Dynamically evaluates `mode` (either `spawn` or `continue`).
* Enforces the quota limits via GitHub Actions API checks.
* Executes the actual `google-labs-code/jules-invoke` call using the stable context key when eligible.
* Persists the active session state back to `agent-context-store` at completion.

### 3.2. `agent-continuous-ops.yml`
Runs on a cron schedule to periodically advance PRs that have gone dirty, quiet, or have unresolved comments.
* Evaluates open PRs and maps them to stable `pr-<pr_number>-<branch_name>` context keys.
* Determines continue-vs-spawn states based on existing PR comments.
* Respects global concurrency/daily quotas before prompting/nudging.
* Employs comment bookmarks `<!-- agent-ctx:<key> -->` to associate work contexts.

---

## 4. Troubleshooting and Manual Invocation

Operators can trigger a dry-run or manual evaluation of the gating and continue-vs-spawn logic via the GitHub Actions UI:
1. Navigate to **Actions** -> **Agent review → auto Jules**.
2. Click **Run workflow**.
3. Provide a test PR number and its head branch ref to verify how the workflow evaluates state, checks quotas, and determines whether to continue or spawn.
