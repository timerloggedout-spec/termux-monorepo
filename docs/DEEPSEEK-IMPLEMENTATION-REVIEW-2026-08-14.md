# Corrected DeepSeek Web-Wrapper Lineage and Integration Decision

**Date:** 2026-08-14

**Scope:** The intended reverse-engineered DeepSeek web-wrapper, WASM proof-of-work, AWS WAF browser cookie, and persistent session/caching model.

**Correction:** This supersedes the prior review artifact. The web-wrapper, PoW solver, WAF-compatible browser state, and persistence are **intentional capabilities to preserve**, not features to remove.

## Decision

The selected baseline is the **current DeepCLI lineage on `master`**, principally the runtime introduced through PR #174 and its later fixes. It is the only candidate that combines the active web-wrapper session manager, WASM PoW flow, chat-session creation, streaming CI agent, account selection, and persistent session cache. No older PR should be cherry-picked over it.

The existing recorded browser traffic establishes that the working request shape includes both `X-Ds-Pow-Response` and an `aws-waf-token` browser cookie alongside `ds_session_id`. Before this update, the active session manager preserved only `ds_session_id` when importing a JSON cookie capture; it silently discarded the WAF cookie. The focused update closes that capability gap while retaining the existing cache and PoW mechanics.

| Candidate | Capability coverage | Decision |
|---|---|---|
| PR #112 | Early workflow seed on an intermediate feature base. | Do not cherry-pick. |
| PR #134 | Closed/destructive experiment with unrelated deletions. | Do not merge or cherry-pick. |
| PR #137 | Open rebase of the superseded branch. | Do not merge or cherry-pick. |
| PR #162 | Earlier `multi-ai-cli` safe-path implementation and tests. | Retain as historical reference only; it does not supersede current DeepCLI runtime. |
| PR #174 + current `master` | Current web-wrapper, PoW, session, streaming, trigger, and cache lineage. | **Selected baseline.** Extend in place. |
| PR #210 | Closed hotfix branch overlapping the selected lineage. | No standalone cherry-pick. |

## Evidence chain

| Evidence source | Confirmed behavior | Integration consequence |
|---|---|---|
| Supplied Termux transcript | `deepcli` created a session after the reported `cookies.json` deletion. | Literal `cookies.json` restoration is unnecessary. |
| `deepseek-cli/pow-details.json` and `deepseek-cli/upload-api.json` | The captured request schema contains `authorization`, `cookie`, `x-ds-pow-response`, and browser-client headers. Redacted inspection identified cookie names `ds_session_id`, `aws-waf-token`, `ds_cookie_preference`, `.thumbcache_*`, and `smidv2`. | Preserve the browser cookie jar instead of collapsing it to only `ds_session_id`. |
| `deepcli/session_manager.py` | Retrieves a PoW challenge, runs the Node/WASM solver, creates a chat session, and persists session state under a `0700` directory with `0600` session JSON. | Keep this runtime and cache lifecycle; add full cookie-jar support. |
| `deepcli/ci_agent.py` | Computes and sends the `X-Ds-Pow-Response` header for completion requests. | No PoW rollback or alternate solver is required. |
| PR #174 discussion | Operator direction explicitly stated that session persistence is desired and the DeepSeek web-wrapper/PoW/cache path should be retained. | Cache preservation is an explicit functional requirement. |

## Implemented focused update

The feature branch `feature/deepseek-waf-persistent-session` extends the selected runtime without modifying provider endpoints, PoW algorithm, cookie values, token values, or external credentials.

| Change | Result |
|---|---|
| Full browser-cookie parser | JSON browser exports now retain all present cookies, including `aws-waf-token` and `ds_session_id`, without logging values. |
| Explicit WAF environment aliases | `DEEPSEEK_AWS_WAF_TOKEN`, `DEEPSEEK_WAF_TOKEN`, `AWS_WAF_TOKEN`, `WAF_AWS_TOKEN`, and local `WAF-AWS-TOKEN` can populate the `aws-waf-token` cookie. |
| Persistent refresh | A fresh WAF cookie supplied through the environment refreshes the persisted jar on resumed sessions; no `cookies.json` file is required. |
| Workflow injection | The DeepSeek CI workflow maps the supported GitHub Secret names into `DEEPSEEK_AWS_WAF_TOKEN` without embedding a value in source. |
| Documentation | The operational contract now identifies the WAF cookie and confirms that persistence is intentional for this web-wrapper path. |
| Offline tests | Standard-library tests cover browser-cookie import, explicit WAF injection, new-session propagation, and persisted-session refresh. |

## Validation

The focused offline test suite passed all four cases using only fixture values. Syntax compilation of the changed Python files also passed, and the diff has no whitespace errors. No live request was made and no credential, cookie value, or session blob was displayed, committed, or attached.

The documented repository gate scripts and `pytest` are absent from the current `master` checkout, so their prescribed commands could not be run here. The included tests use `unittest` specifically to remain executable without adding dependencies.

## Remaining integration rule

The current capability branch is based on the current `master` because `master-staging` predates and does not contain the current DeepCLI web-wrapper files. Before promotion, rebase or merge the branch into the then-current governed integration target; retain the selected current runtime rather than reverting to an older safe-path branch.

## References

[1]: https://github.com/timerloggedout-spec/termux-monorepo/issues/109 "DeepSeek web-wrapper initiative"
[2]: https://github.com/timerloggedout-spec/termux-monorepo/pull/174 "Current DeepSeek web-wrapper lineage"
[3]: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/deepcli/session_manager.py "DeepCLI session manager"
[4]: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/deepcli/ci_agent.py "DeepCLI PoW request agent"
[5]: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/deepseek-ci.yml "DeepSeek CI workflow"
