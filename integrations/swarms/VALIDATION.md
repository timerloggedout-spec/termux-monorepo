# Swarms integration validation

The optional adapter is implemented locally on `cue/swarms-synthesis-20261021`. It does not replace the existing orchestrator, enable tools, or configure a provider. The base checkout is commit `2452bcd1`; at inspection it was 423 commits behind its already-fetched `origin/master`. No broad pull, remote push, PR, merge, or production deployment was performed. Unrelated existing working-tree edits were preserved.

## Checks that passed

The focused offline suite passed **35 tests**, with **1 optional SDK test skipped** in the base Python environment. It covers the new adapter/reference contracts and existing hub privilege, hub server, and orchestration contracts:

```sh
python3 -m pytest -q tests/test_swarms_adapter.py tests/test_swarms_reference.py tests/test_swarms_sdk.py tests/test_hub_mcp_privileges.py tests/test_llm_api_hub_server.py tests/test_orchestration_contracts.py
```

Both required local gates passed after the source pin and implementation were staged:

```sh
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

`python3 scripts/ci/submodule_integrity.py` passed its governed-fork checks. It reported one existing, non-required drift warning: `refTemplates/smods/lego_fork` is listed in `.gitmodules` without a gitlink. That unrelated warning was not repaired by this change. The new Swarms gitlink, shallow configuration, and source hashes passed their own offline checks.

The CLI dry-run returned valid JSON without the SDK installed in the base environment and without network calls.

## Real SDK execution

The exact source-pinned Swarms package built and installed in a dedicated virtual environment, using a credential-free process environment. Installed distribution metadata reports `swarms==16.0.2`. The probe ran on Python 3.12.3, Linux x86_64/glibc, not Android.

The retained [`test_swarms_sdk.py`](../../tests/test_swarms_sdk.py) passed with that interpreter. It exercises real upstream `Agent` and `SequentialWorkflow` twice in a fresh subprocess. The model-hub function is a deterministic stub, socket connections are forbidden, and no provider credentials are supplied. Four stub requests completed; output contained the deterministic response; temporary state was removed and cwd/environment were restored. SDK diagnostics did not contaminate the subprocess's JSON stdout.

A stricter payload assertion initially found a real compatibility defect: pinned Swarms calls custom `llm.run(task=None, messages=...)`. A text-only wrapper would have discarded the conversation and sent null content. The adapter now forwards validated structured messages, preserving system/user roles, and rejects missing or invalid payloads before contacting the hub. This behavior is covered by dedicated offline tests and the successful real-SDK rerun.

The SDK validation environment is `/tmp/swarms-validation-20261021`; it is a local test aid, not a required runtime path or a portable dependency lock. To reproduce, install the optional requirements into a clean environment and run `python -m unittest discover -s tests -p 'test_swarms_sdk.py' -v` with that environment's interpreter.

## What these checks do not prove

No live provider or production hub HTTP request was made. No inference charge was incurred. There is no measured task-quality, throughput, latency, or token-cost improvement claim. Actual provider availability and route policy must be checked when execution is deliberately enabled.

Native Termux installation and Android/Bionic dependencies remain unverified. The upstream source is pinned, but its dependency resolution is not frozen. The complete inventory covers public GitHub repository metadata only: 676 repositories and 241 matching leads, not source audits of all projects or visibility into private repositories.

This is a locally tested, reviewable integration slice. Because the checkout is stale and has unrelated user edits, it must be reconciled against the current target branch and pass remote checks before production promotion.
