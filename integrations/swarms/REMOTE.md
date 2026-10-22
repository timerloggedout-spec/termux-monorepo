# Remote offline validation (THUB-016)

This workflow lets you use GitHub-hosted runners as a remote **offline contract-test** environment when controlling the repository from Termux. It does not execute a user task, call a model/provider, install the optional Swarms SDK, write or merge a PR, or deploy anything. The manual run uses fixed synthetic workflow and source-planning fixtures only.

## Before dispatching

The workflow must already exist on the repository's default branch for GitHub to offer its `workflow_dispatch` trigger. Make a PR containing this workflow and merge it through the repository's normal process first; this workflow itself does not merge PRs. Once merged, dispatch it on the default branch:

```sh
gh workflow run swarms-validation.yml --ref master
gh run list --workflow swarms-validation.yml --limit 5
gh run watch
```

The repository default branch is `master`. Check run logs with `gh run view RUN_ID --log`. Termux needs the GitHub CLI authenticated with permission to dispatch workflows; do not put credentials or task text in command arguments.

## What runs automatically

Pull requests and pushes that change Swarms source, scripts, integration files, matching tests, or this workflow trigger path-filtered checks. PR runs validate the PR commit through GitHub Actions; they are **not** the same as manually dispatching the workflow on the default branch. CI installs only pinned pytest, PyYAML and uvicorn for tests, runs `tests/test_swarms*.py`, and invokes the fixed offline CLI dry-run and research-plan fixture. The existing optional SDK test skips when the SDK is absent; this CI intentionally does not install it, so a skip is not evidence of SDK execution. A separate bounded Rust job runs `cargo test --locked` and may download Cargo dependencies; it makes no model calls.

## WorkSpaces / Codespaces

In a GitHub Codespace, check out the repository branch containing the workflow and use the same `gh workflow run` / `gh run` commands in the terminal. GitHub Actions jobs run on GitHub-hosted runners, not inside the Workspace/Codespace itself. The workflow is an Actions remote runner option; no Workspace CLI feature, scheduler, always-on process, or remote Swarms service is configured here. Local validation from a checked-out repository is:

```sh
python3 -m pytest -q tests/test_swarms*.py
python3 scripts/swarms/run.py --task 'Synthetic offline validation fixture'
```

Neither Actions nor Codespaces free availability is promised; quotas, billing, organization policy, and repository settings determine access. The workflow grants only `contents: read`, persists no checkout credentials, has bounded timeouts, and has no user-defined dispatch inputs. It validates contracts only; it does not authorize, promote, merge, or deploy changes.
