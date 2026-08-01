# Repository Guidelines

## Mission and Operating Model

This is a Termux-first personal monorepo of CLIs, agent orchestration,
conversation tooling, indexing, and imported reference projects. Treat it as
several deployable subprojects, not one application. Before changing code,
identify the owning directory, runtime, and dependency boundary. Prefer a
narrow fix in one project over a root-level rewrite.

## Map the Repository Before Editing

- deepcli/ and deepseek-cli/: DeepSeek CLI, sessions, and terminal UI helpers.
- cli-synthegration/: conversation branching, exports, Chronos, and indexes.
- termux-multi-agent/: agent provisioning, execution, and dashboards.
- multi-ai-cli/: provider bridges and multi-model command surfaces.
- harmonizer-prod_cli/ and synthegration-cli/: independent Rust crates.
- archwiz/ and workspace/: provenance, mapping, recovery, and automation.
- _1-Projects/, refTemplates/, and nested .git directories: imported or
  reference material; do not casually reformat, vendor, or update it.

Start with git status --short --branch, rg --files <project>, and the nearest
README or package manifest. Preserve unrelated worktree changes; stage only
explicit paths.

## Build, Test, and Development

Run the smallest relevant command first, then expand only when warranted:

    python3 -m unittest tests/test_sanitize_codex_blobs.py
    cargo fmt --check --manifest-path harmonizer-prod_cli/Cargo.toml
    cargo test --manifest-path harmonizer-prod_cli/Cargo.toml
    cargo test --manifest-path synthegration-cli/Cargo.toml

For Node projects, enter the project directory and inspect package.json before
running package scripts. Do not assume a root workspace command exists. New
shell automation should use a shebang, set -euo pipefail, quoted variables,
and explicit paths.

## Engineering Practices

Follow local style rather than imposing a global framework. Python uses four
spaces, snake_case, small functions, and standard-library dependencies unless
a project manifest declares otherwise. Rust must pass rustfmt; use snake_case
functions and CamelCase types. Name tests test_*.py and add a focused
regression test for each fix.

Use a reconnaissance loop for complex work:

1. Map callers with rg, then inspect only relevant paths.
2. State the invariant being protected, such as “session data never enters Git.”
3. Make the smallest reversible change.
4. Validate behavior and run git diff --check.
5. Review staged paths before committing.

Avoid speculative refactors, silent exception swallowing, import-time
filesystem mutations, and network-dependent tests.

## Security, Sessions, and Extracted Code

Session stores are local-only private state. Never commit:

- .deepcli/session_store/
- .pi/agent/sessions/
- cli-synthegration/conv_repo/sessions/

GitHub Actions Secrets store individual runtime values; they are not a remote
session vault. When recovering extracted code, use
tools/sanitize_codex_blobs.py against a known source revision. It redacts
high-confidence credential values while preserving surrounding code and
creates a non-secret manifest. Do not force-add ignored blob stores without
an explicit size, licensing, and security review. Never print, log, or paste
tokens, cookies, browser profiles, session contents, or private keys.

## Git and Pull Requests

Use concise conventional-style commits: fix: handle cache migration, ci: test
Rust crates, or security: keep session stores out of git. Keep one concern per
commit. Before pushing, run targeted tests, inspect git diff --cached --check,
and confirm no user-owned files are staged.

Open draft PRs for broad or security-sensitive changes. PR descriptions must
state scope, validation commands, migration/security effects, and follow-up
work. Removing an artifact from the latest commit does not erase repository
history: rotate exposed credentials and plan history rewriting separately.
