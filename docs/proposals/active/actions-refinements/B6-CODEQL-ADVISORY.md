# B6 — Advisory CodeQL Analysis

**Status:** Implemented on `fix/ar01-automation-baseline`; pending first GitHub-hosted execution and review.  
**Ledger item:** X-04 / B6  
**Workflow:** `.github/workflows/codeql-advisory.yml`

The public test-and-build environment’s enabled administrative control surface authorizes this narrowly scoped Code Scanning pilot. The workflow has no repository-content write path. Its only write capability is `security-events: write`, isolated to the CodeQL job so that the official action can upload SARIF findings to GitHub Code Scanning.

| Candidate-review criterion | Result |
|---|---|
| Action | GitHub’s official `github/codeql-action` v4, pinned to commit `ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd`. |
| License and use | MIT-licensed action. The CodeQL project permits use on open-source repositories hosted on GitHub. |
| Trigger | Pull requests changing Python, JavaScript/TypeScript, or GitHub Actions sources; a weekly Monday 03:23 UTC baseline; and controlled manual dispatch. |
| Language/build scope | `actions`, `javascript-typescript`, and `python`, each with `build-mode: none`. The control does not claim coverage of the repository’s Rust trees or introduce an unreliable multi-project compiled-language autobuild. |
| Permission boundary | Workflow scope is `permissions: {}`. The analysis job receives only `contents: read` and `security-events: write`. Checkout disables persisted credentials. |
| Publication boundary | `security-events: write` is used solely by `analyze` to upload CodeQL SARIF. No issue, pull-request, contents, actions, identity-token, or secret write scope is granted. |
| Findings policy | `security-extended` results are visible in GitHub Code Scanning but are **advisory** in this batch; no branch-protection required-check policy is changed. |
| Rollback | Delete `codeql-advisory.yml`. This removes scheduled execution but does not alter existing source, PR, issue, or token state. |

## Scorecard Evaluation and Deferral

`ossf/scorecard-action` v2.4.4 was evaluated as X-03. Its published action manifest is a Docker action that references `docker://ghcr.io/ossf/scorecard-action:v2.4.4`. Although the outer action repository commit can be SHA-pinned, the container reference remains a mutable tag inside the action manifest. That fails this program’s immutable-dependency rule until the maintainer supplies a digest-pinned container route or a separately reviewed wrapper can verify the image digest. Scorecard’s SARIF publication also needs `security-events: write` and `id-token: write`; this CodeQL pilot deliberately does not reuse either permission outside its isolated job.

> CodeQL advanced setup requires `security-events: write` to upload findings. That permission is explicitly approved only for this isolated CodeQL analysis job in the public test environment.

## Acceptance Evidence

The deterministic policy test checks the exact three immutable action references, source and schedule triggers, explicit language matrix, `build-mode: none`, `security-extended` suite, `contents: read` plus isolated `security-events: write`, disabled persisted credentials, and absence of code/PR/issue/comment/dispatch mutation paths. The workflow is lint-clean under checksum-verified actionlint v1.7.12. The first GitHub-hosted run will establish runtime, result volume, and operational compatibility before any required-check promotion is considered.

## References

[1]: [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
[2]: [CodeQL Action repository](https://github.com/github/codeql-action)
[3]: [CodeQL Action v4 revision](https://github.com/github/codeql-action/commit/ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd)
[4]: [CodeQL Action configuration guidance](https://github.com/github/codeql-action)
[5]: [Scorecard Action repository](https://github.com/ossf/scorecard-action)
[6]: [Scorecard Action v2.4.4 revision](https://github.com/ossf/scorecard-action/commit/2d1146689b8cda280b9bc96326124645441f03bc)
