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

Native Termux installation and Android/Bionic dependencies remain unverified. The upstream source is pinned, but its dependency resolution is not frozen. The original inventory covers public metadata for 676 `timerloggedout-spec` repositories and 241 matching leads, not Kye Gomez's listing, source audits of all projects, or visibility into private repositories. See the correction below.

This is a locally tested, reviewable integration slice. Because the checkout is stale and has unrelated user edits, it must be reconciled against the current target branch and pass remote checks before production promotion.

## THUB-012: corrected Kye Gomez scope and Rust assessment

The corrected inventory is [`swarms-kyegomez-repositories.json`](../../docs/research/swarms-kyegomez-repositories.json): owner `kyegomez`, 455 public repositories, five HTTP-200 pages, no errors or duplicates, and pagination exhausted. Its 19 Swarms/multi-agent and 197 model-research leads are name/description matches, not source-audit coverage. The original 676-repository JSON remains unchanged as historical monorepo-owner evidence.

The reproducible stdlib collector defaults to `kyegomez`, validates returned owners, and refuses to claim completeness after failed collection, duplicate records, unsafe pagination links, or loops. Eight offline tests cover those boundaries and assert the saved snapshot belongs to Kye rather than the monorepo owner.

The extended focused suite passed **43 tests**, with **one optional SDK test skipped** in base Python:

```sh
python3 -m pytest -q tests/test_swarms_inventory.py tests/test_swarms_adapter.py tests/test_swarms_reference.py tests/test_swarms_sdk.py tests/test_hub_mcp_privileges.py tests/test_llm_api_hub_server.py tests/test_orchestration_contracts.py
```

The genuine SDK test was separately rerun in `/tmp/swarms-validation-20261021` and passed again: real upstream orchestration, deterministic stub inference, four stub requests across two executions, and socket connections forbidden. No provider credential or live inference was used.

The [selected Python code review](../../docs/research/SWARMS-CODE-REVIEW.md) records immutable source links and explicitly identifies telemetry's opt-out default. The [Rust assessment](../../docs/research/SWARMS-RUST.md) inspects organization repository `swarms-rs` at `ee1e74cb6e2c94775db88dddb311f2235e3fe9e3`, including actual provider/base-URL configuration and workspace requirements. It does **not** claim a Rust build, test run, native Android support, or demonstrated Rust-to-hub interoperability. Rust and remote services are valid deployment choices; the current Python adapter is not a language constraint.

Both local gates passed with the correction staged: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`. Local research links resolve, and a byte-for-byte comparison confirms the original owner inventory is unchanged. No unrelated provider files, session state, remote branches, or deployment settings were modified by this correction.
