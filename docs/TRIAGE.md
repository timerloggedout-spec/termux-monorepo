# Triage: every open PR and branch, critically evaluated

State captured against `master` @ `320c73b`. 10 PRs (8 open, 1 draft, 2 merged),
18 remote branches, 0 issues, **0 CI workflows on `master`**.

This is a critique, not a rubber stamp. Where a PR is right, the note says so and
gives a merge order. Where it is wrong, the note says exactly what breaks.

---

## 0. The blocking structural facts

**No CI exists.** `.github/` is absent from `master`. Every "verified" claim in every
open PR is a hand-run `py_compile`/`bash -n` in an author's shell. PR #2 is the only
CI proposal and it cannot succeed (see below). This PR adds
`.github/workflows/repo-gate.yml` + `scripts/ci/repo_gate.py` as the missing floor:
stdlib-only, no toolchain, no network, ~30 s, and runnable on-device.

**`master-staging` is byte-identical to `master`** (`ahead=0 behind=0`). PR #5 and
PR #6 target it, so merging them lands nothing on `master` and silently forks the
two. Either declare `master-staging` the real integration branch and set it as the
repo default, or retarget both PRs. Right now it is neither.

**Three branches are identical to `master`** and carry no work:
`feature/ci-gate-and-docs`, `master-staging`, `termux-monorepo`. The first is
especially misleading — its name promises exactly the CI gate that does not exist.
Delete or repurpose.

**`Master_Protection` ruleset** requires review-thread resolution and runs Copilot
review, with `required_approving_review_count: 0` and merge-commits only. That is why
PR #8 and PR #9 report `BLOCKED` with all checks green: unresolved conversations, not
failing tests. Resolve the threads and they are mergeable. Also note: with 0 required
approvals, the ruleset is a conversation gate, not a quality gate — which is precisely
the hole `repo-gate.yml` fills.

**The clone is not reproducible.** 42 of 45 tracked symlinks dangle; 34 point at
`/data/data/com.termux/...`. Five of them are the archwiz entrypoints the README tells
you to start from. Full analysis and migration plan: **[docs/PORTABILITY.md](PORTABILITY.md)**.

---

## PR #10 — `fix(deepcli): optional curl_cffi → requests fallback` — **merge first**

+31/−10, 1 file, `MERGEABLE/CLEAN`, targets `master`.

Correct and minimal. Termux Python 3.14 cannot load `curl_cffi` 0.16 (missing
`_ZNSt6__ndk1...` from libc++), which hard-crashes deepcli at import — so this is the
one change that unblocks *running* anything else. Try-import, alias to stdlib
`requests`, one-line stderr warning, annotations relaxed to `Any`.

Review points, none blocking:

1. **The fallback is not behaviour-neutral.** `curl_cffi.requests` exists in this
   codebase for browser TLS impersonation (`impersonate=`). Stdlib `requests` ignores
   that kwarg's intent, so a provider that gates on TLS fingerprint will start
   failing at *request* time instead of import time — a worse failure mode to debug.
   The warning should say so explicitly: `curl_cffi unavailable — TLS impersonation
   disabled, provider may reject requests`.
2. **`except Exception` vs `BaseException`.** The observed failure is a loader error
   surfacing as `ImportError`/`OSError`; both are `Exception`, fine. But keep it as a
   bare-ish `except Exception` rather than narrowing, since the ndk symbol error has
   shown up as more than one type.
3. **The PR body flags the real risk itself:** if the live CLI is `~/deepcli/` rather
   than the monorepo tree, this fix never runs. That is Class A of
   docs/PORTABILITY.md — `harmony_hub/bin/deepcli -> ~/deepcli/deepcli.py` is a
   dangling device link, so "which deepcli is live" is currently unanswerable from the
   repo. Worth resolving before more deepcli PRs stack up.

## PR #5 — `fix(TER-5): log archwiz dispatch failures` — **merge second, retarget**

+26/−9, 3 files, `MERGEABLE/CLEAN`, targets **`master-staging`**.

Replaces `except: pass` with stderr logging in `deepcli/deepcli/core.py`,
`archwiz/dispatch_pipeline.py`, and adds the missing hook in
`multi-ai-cli/core/cache.py`. Non-blocking, no control-flow change. This is the P0
observability fix and it is right.

- **Retarget to `master`.** As merged today it lands on a branch identical to
  `master` and therefore ships nothing.
- **Overlaps PR #6.** PR #6 rewrites the same `_cache_save` dispatch hook and the same
  `dispatch_pipeline.update_all`. Land #5 first (26 lines, trivially reviewable), then
  rebase #6 on top; the reverse order makes #5 pure conflict noise.
- `print(..., file=sys.stderr)` is fine for now, but three modules now grow their own
  ad-hoc `[archwiz dispatch]` prefix. One `archwiz.log` helper would stop that from
  becoming four variants by TER-10.

## PR #6 — `fix(TER-9): vibe silent dispatch + provider-aware stores` — **split**

+6431/−56, 39 files, targets **`master-staging`**, based on the unmerged
`vibe/mistralai-vibe-code-wrapper-6055d2`.

The TER-9 content is good: provider-aware store resolution
(`explicit path → mistralai-cli → deepcli → multi-ai-cache`), and marking eight
scaffold providers `is_available() -> False` / `live = False` instead of letting them
pretend. Making non-functional providers *loudly* non-functional is exactly the right
call.

The packaging is the problem:

1. **6431 added lines is not 'a TER-9 fix'.** It is the `vibe` wrapper base plus
   TER-9. Because the base branch is unmerged, the diff conflates the two and nobody
   can review the fix. Either merge `vibe/mistralai-vibe-code-wrapper-6055d2` on its
   own first, or rebase this onto `master` and keep only the TER-9 delta.
2. **Retarget to `master`** (same reason as #5).
3. **Stacking order:** #5 → vibe base → #6.
4. `is_available() -> False` plus `send_message` raising is belt-and-braces and good;
   make sure the raise is a single shared `ProviderNotLive` so callers can catch one
   type rather than eight.
5. The author's own "**Do not merge until Termux smoke-tested**" is the correct
   posture — and is an argument for the gate in this PR, so that "smoke-tested" is not
   forever a promise in a PR body.

## PR #7 — `Termux MCP integration` — **merge, mostly independent**

+176/−0, 6 files, `MERGEABLE/CLEAN`, targets `master`.

Adds `integrations/termux-mcp/` — a transport-configurable launcher for the fork's
`FastMCP("termux-control")` server, phone-side `run.sh`, a cloudflared `tunnel.sh`, and
two prefill Devin custom-MCP configs. Placeholders only, no secrets. The
`mcp[cli]>=1.2.0,<2` pin is justified in-body (mcp 2.0 drops
`mcp.server.fastmcp`) — good, that is the kind of pin that usually goes unexplained.

Review points:

1. **`tunnel.sh` is the sharp edge.** A cloudflared quick tunnel exposes a server with
   45+ shell/`adb`/`termux-api` tools on a public URL with no authentication. Anyone
   with the URL gets arbitrary device control. This needs a bearer-token/allowlist
   check in front of the HTTP transport and a loud warning in the README, or it should
   ship disabled with `--dry-run` semantics. Recommend gating: refuse to start the
   network transport unless `TERMUX_MCP_TOKEN` is set.
2. Bind default `TERMUX_MCP_HOST=127.0.0.1` is the right default — keep it, and make
   `0.0.0.0` require an explicit opt-in env var.
3. Coordinate the `integrations/` root with PR #8 (which proposes the same root) so
   whichever lands second does not create `integrations/` twice with different
   conventions.

## PR #8 — `feat(TER-11): vendor codex-termux_fork submodule + bridge scaffold` — **unblock and merge**

+352/−0, 8 files, `BLOCKED` on unresolved threads (no failing checks).

Shallow (`--depth 1`, `shallow = true`) submodule plus a `codex_bridge` scaffold with
`doctor` / `build` / `run` / `reconcile`. The honesty is genuinely good: the PR body
states plainly that `run` does not translate deepcli turns to the Codex protocol and
that `reconcile` is not a live dispatch pipeline.

Review points:

1. **`reconcile` keyed on `sid = f.stem` is fragile here specifically.** 423 tracked
   session artifacts have filenames like
   `Add export command to save session messages_1494fde3.json` — the stem is prose,
   not a UUID, and 452 tracked paths contain spaces. Key on a parsed `id` field inside
   the JSON with the filename only as a fallback, and quote every path.
2. **`ch = sha256(session bytes)`** over a mutable, appended-to session file will churn
   on every turn. If the pointer is meant to be stable, hash an immutable subset
   (id + created_at + first message) or accept that `ch` is a change-detector, not an
   identity — and say which in the README.
3. **Submodule + CI:** `checkout` without `submodules: recursive` leaves the fork
   absent, so any Rust discovery step will not see its crates. `repo-gate.yml`
   deliberately sets `submodules: false` and reads the git index, so it is unaffected —
   but PR #2's workflow is (below).
4. The proposed `integrations/` vs `codex-termux/` split in the PR discussion is
   sound: full submodules only for forks that are actually built/run. Settle it with
   PR #7 before both land.

## PR #9 — `feat(TER-12): DeepForge — deepcli-first bridge` — **merge after #8 and #10**

+513/−0, 8 files, `BLOCKED` on unresolved threads.

Makes `python -m codex_bridge run` prefer deepcli, adds `deepcli` and `codex-native`
subcommands, and renames the product to DeepForge. Defaulting a Termux monorepo into
an OpenAI ChatGPT sign-in wall was plainly the wrong behaviour, so the intent is right.

Review points:

1. **Hard-depends on PR #10.** "Prefer deepcli when a launcher or package is present"
   is precisely the path that crashes on `curl_cffi` under Python 3.14. Merging #9
   before #10 turns an OpenAI auth wall into an import traceback — no better.
   Order: **#10 → #8 → #9**.
2. **Detection needs a liveness probe, not just presence.** A launcher existing on
   disk is not the same as deepcli importing successfully. `run` should fall back to
   `--codex-native` with a printed reason when the deepcli import fails, otherwise the
   user is stuck with no working path at all.
3. **The rename is still an open bikeshed on TER-12** while this PR already writes
   "DeepForge" into the README and CLI strings. Keep the module/entrypoint names
   neutral (`codex_bridge`) and let "DeepForge" live only in user-facing strings, so
   settling the name later is a docs change, not a refactor.

## PR #3 — `security: remove session stores from Git tracking` — **highest value, still draft**

+255/−233 175, 580 files, draft, targets `master`.

Removes 571 session-store artifacts from the index while keeping local files, blocks
future tracking, and adds a deterministic sanitizer with a unittest. This is the most
valuable open PR in the repo and it has been sitting in draft. Confirmed independently:
**423 session artifacts are still tracked on `master`**, and `.gitignore` already lists
`.deepcli/session_store/` — ignore rules do not untrack, which is exactly the trap.

Blocking items, all named by the author already:

1. **Rotate credentials before merge, not after.** Untracking the tip leaves every
   blob reachable in history. Merging first and rotating later means the window stays
   open with a public paper trail pointing at it. Rotate → merge → then a separately
   reviewed history rewrite.
2. **The pre-commit hook is broken and dangerous:** the author reports it scanned
   deleted files and echoed their contents to stdout during this very commit. That is
   a secret-leak vector inside the tool meant to prevent leaks. Fix the hook in its own
   PR first.
3. **CodeRabbit skipped the review** (580 files > 100 limit). Split into
   `git rm --cached` of the artifacts (mechanical, reviewable by counter) and the
   sanitizer + policy docs (small, worth real review). `repo_gate.py`'s
   `tracked_session_artifacts` counter gives a one-number check on the mechanical half.
4. History rewrite interacts with `Master_Protection`'s `non_fast_forward` rule — plan
   the ruleset exception explicitly rather than discovering it mid-force-push.

## PR #2 — `Add GitHub Actions workflow for Rust build and test` — **do not merge as-is**

+131/−0, 1 file, targets `master`. The stated constraint is
*"Limit local, Android Termux, device, resources, usage."*

**This workflow fails 100% of the time, on the first job.** Lines 31–35:

```yaml
python3 - <<'PY'
import json,sys
crates = ${crates:+""}
PY
```

The heredoc is **quoted** (`<<'PY'`), so bash performs no expansion. Python receives
the literal text `crates = ${crates:+""}` and raises `SyntaxError`. With
`set -euo pipefail` the step exits non-zero, `discover` fails, and `build`/`skip`
never run. The block is also dead by the author's own adjacent comment. Delete it.

Further defects:

| # | Issue | Fix |
|---|---|---|
| 1 | `base_ref=${{ github.event.pull_request.base.ref }}` interpolated straight into the shell body — branch-name script injection | pass through `env:` and reference `"$BASE_REF"` |
| 2 | `actions-rs/toolchain@v1` is archived/unmaintained | `dtolnay/rust-toolchain@stable` |
| 3 | `echo "Changed files:\n$changed"` — `echo` does not interpret `\n` | `printf '%s\n'` |
| 4 | Cache `path: target` at repo root, but builds run in `working-directory: ${{ matrix.crate }}` → the cache never covers the real `target/` dirs | cache `${{ matrix.crate }}/target` |
| 5 | `checkout` without `submodules` → PR #8's vendored `codex-termux_fork` crates are invisible to `find` | `submodules: recursive` once #8 lands, or scope explicitly |
| 6 | `on: push: branches: [master]` builds **all 4** crates with `cargo build --verbose` + `cargo test --verbose` | this is the "limit resource usage" violation |

There are exactly 4 tracked `Cargo.toml`s (`appliedSxi/maxc`, `harmonizer-prod_cli`,
`synthegration-cli`, `workspace/maxc` — note `maxc` appears twice, likely a stale
duplicate worth resolving separately). Recommendation: keep the affected-crate matrix
idea, fix the six defects, and move the trigger to `workflow_dispatch` +
`pull_request: paths: ['**/Cargo.toml', '**/*.rs']` so Rust minutes are spent only when
Rust changes. Merge `repo-gate.yml` as the always-on floor; Rust stays opt-in.

## PR #4, PR #1 — merged

`docs: deep RECON intel` and `Critical Evaluation` are on `master`. Note that
`critical-proposal` is still 8 ahead of `master` after PR #1 merged — there is
unmerged follow-on work there (`archwiz/config.py`, `docs/proposals/`, `.replit`,
`skills-lock.json`). Confirm intentional or open a follow-up PR.

---

## Branches with no PR

| Branch | vs master | Verdict |
|---|---|---|
| `vibe/mistralai-vibe-code-wrapper-6055d2` | +4 / −4 | PR #6's base. **Open a PR for it** so the wrapper reviews separately from TER-9. |
| `mistral/fixes-config-security` | +1 / −4 | Touches `SECURITY.md`, `archwiz/config.py`, `setup.sh`, mistral bridge + a smoke test. Security-adjacent work sitting invisible — **open a PR or delete**. |
| `recreate/refTemplates-skeleton` | +3 / −3 | Metadata-only `refTemplates` restore (README + SOURCE.txt per ref). Cited as policy from `README.md`, but unmergeable-by-policy: `.gitignore` excludes `refTemplates/`, so these files exist only via forced adds. **Decide: skeleton-tracked, or ignored entirely.** Cannot be both. |
| `feature/ci-gate-and-docs` | identical | Dead. Name claims the CI gate that does not exist. Delete. |
| `master-staging` | identical | Either make it the real integration branch (and default) or delete and retarget #5/#6. |
| `termux-monorepo` | identical | Dead. Delete. |
| `critical-proposal` | +8 / −2 | Merged via PR #1 but still ahead. Reconcile. |
| `v0/timerloggedout-5184-43474d34` | — | Stale agent branch. Delete. |

## Recommended merge order

```
1. repo-gate.yml + scripts/ci/ + docs   (this PR — gives everything below a floor)
2. PR #10  curl_cffi fallback           (unblocks running deepcli at all)
3. PR #5   dispatch logging             (retarget to master first)
4. PR #3   session-store untracking     (after credential rotation + hook fix; split)
5. PR #7   termux-mcp                   (add the tunnel auth gate first)
6. PR #8   codex-termux submodule       (resolve threads; settle integrations/ root)
7. PR #9   DeepForge deepcli-first      (needs #10 + #8)
8. vibe base, then PR #6 rebased        (retarget to master; split the 6431 lines)
9. PR #2   Rust CI, rewritten           (workflow_dispatch + paths filter)
```

Cross-cutting, before step 4: **rotate every credential that could appear in the 423
tracked session artifacts.** Everything else here is recoverable; that is not.
