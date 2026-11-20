# B6 — Advisory OpenSSF Scorecard

**Status:** Implemented on `fix/ar01-automation-baseline`; pending first manual/scheduled GitHub-hosted execution.  
**Ledger item:** X-03 / B6  
**Workflow:** `.github/workflows/scorecard-advisory.yml`

This public test-and-build integration adopts **controlled updateability**, rather than an unconditional mutable-container exception. The outer Scorecard action remains pinned to an immutable repository commit. Its upstream Docker-image tag is allowed only because a separate read-only preflight job resolves that tag from GitHub Container Registry and fails before the publishing job if the observed manifest digest differs from the reviewed digest recorded in the workflow.

| Control surface | Boundary |
|---|---|
| Outer action | `ossf/scorecard-action` is pinned to immutable commit `2d1146689b8cda280b9bc96326124645441f03bc` (v2.4.4; Apache-2.0). |
| Updateable transitive dependency | Upstream’s `v2.4.4` container tag is accepted only while it resolves to reviewed manifest digest `sha256:ae5104dd3cc28466ebeb11144354be4cac4b7ff829654f9fab89021d71c46670`. |
| Preflight | A dedicated `contents: read` job fetches a registry pull token, resolves the tag manifest with registry `HEAD`, records both digests in its summary, and fails closed on mismatch. |
| Publisher | The Scorecard job cannot start without the preflight through `needs: verify-scorecard-image`. It holds only `contents: read`, `id-token: write`, and `security-events: write`. |
| Publication | `id-token: write` authenticates Scorecard’s public-result publication; `security-events: write` is limited to Scorecard SARIF upload through the pinned CodeQL uploader. |
| Non-authority | No repository-content, pull-request, issue, comment, action, attestation, secret, or direct-push permission is granted. Checkout disables credential persistence. |
| Trigger | Scheduled weekly Monday 03:41 UTC and controlled manual dispatch only. Pull requests, issues, comments, pushes, dispatches, and external event inputs cannot trigger the workflow. |
| Promotion | Advisory only. The workflow does not alter required checks or merge policy. |

## Controlled Update Protocol

A Scorecard update is a reviewable three-part change: the upstream action commit, its declared container tag, and the tag’s expected registry manifest digest. The updater must resolve the candidate manifest digest directly from GitHub Container Registry, update all three values and the deterministic test together, run local validations, and submit the change through a normal reviewed PR. The preflight then checks that the tag still resolves to the reviewed digest at runtime. A mismatch is a safe failure that publishes no Scorecard result and requires a new review; it is not automatically accepted.

> This exception is deliberately narrow. It does **not** permit mutable tags for arbitrary actions, images, scripts, or remote downloads. It applies only to this immutable outer action’s currently unavoidable transitive container reference and is bounded by a reviewed registry-digest assertion.

## Acceptance Evidence

The policy test verifies scheduled/manual-only triggering, immutable outer action pins, the exact reviewed tag/digest pair, the fail-closed comparison, job dependency, least-privilege separation, explicit Scorecard/SARIF publication, and absence of repository mutation or comment paths. The workflow is lint-clean under checksum-verified actionlint v1.7.12. A manually dispatched first run is required before considering required-check promotion.

## Rollback

Delete `scorecard-advisory.yml` to remove both the weekly schedule and the publication path. The workflow owns no repository state, branch state, PR state, or retained artifacts.

## References

[1]: [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
[2]: [OpenSSF Scorecard Action repository](https://github.com/ossf/scorecard-action)
[3]: [Scorecard Action v2.4.4 revision](https://github.com/ossf/scorecard-action/commit/2d1146689b8cda280b9bc96326124645441f03bc)
[4]: [GitHub CodeQL Action v4 revision](https://github.com/github/codeql-action/commit/ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd)
