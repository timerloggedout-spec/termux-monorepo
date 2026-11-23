# Validation — issue #1497

Base: freshly fetched `master-staging` at `1a5af217f3ef9815ce31068d547ad28b69dd8ac7`. Execution environment: isolated issue worktree on Linux x86_64, Python 3.12.3; not Android/Termux hardware.

| Check | Observed result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_antigravity_readiness.py' -v` | PASS, 7 tests |
| `python3 scripts/proposals/validate_registry.py` | PASS, 15 proposals consistent |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS; existing debt counters unchanged |
| `python3 scripts/ci/termux_smoke.py` | PASS; `termux=False`, including connectors-suite |
| `python3 scripts/antigravity/readiness.py --workspace "$PWD"` | Exit 2: expected missing prerequisite, `agy_on_path=false`; repository marker and project skills present |
| Seed SHA-256 | Matches supplied attachment: `94db6d0900cc31727466add4bee9ec8e748bcee3ab549b4e0b77ef0cad34e4bb` |
| Whitespace audit | Original seed has a trailing blank-line warning; preserved intentionally for byte-identical provenance. Excluding the immutable seed, the patch is clean. |

The offline tool correctly reports `runtime_verified=false`, `settings_modified=false`, and `model_prompts_launched=0`. The CLI is not installed on this execution host. Nothing was installed to hide that fact. These results establish repository-deliverable validation, not an operational Antigravity connection, native Termux compatibility, sandbox containment, or on-device provisioning.

No merge or auto-merge is authorized. Linear remains unresolved because its connector requires login; issue #1497 contains the documented fallback tracking entry. No unrelated shared-checkout changes are included.

Independent review identified missing legacy `.agent/skills` detection. Fixed it and added a dedicated regression test; all 7 tests and both gates passed again. No other correctness issue was reported.

## Operational follow-up — AGY-1497-04/05/06

Follow-up stays on the existing issue branch, preserving the shared dirty checkout. Device provisioning is blocked, not completed.

| Check | Observed result |
|---|---|
| Original readiness suite | PASS, 7 tests |
| Initial thin-worktree suite | PASS, 4 tests before independent-review hardening; final result recorded below |
| Project skill format validator | PASS for `.agents/skills/agy-bounded-collaboration` |
| `python3 scripts/proposals/validate_registry.py` | PASS, 15 proposals consistent |
| Repository gate after staging new files | PASS, 14 PR paths; 4 Python and 1 JSON hard-checked; final rerun recorded below |
| `python3 scripts/ci/termux_smoke.py` | PASS on Linux x86_64, not native Termux evidence |
| Offline readiness inventory | Expected exit 2: `agy_on_path=false`, `runtime_verified=false`, `settings_modified=false`, `model_prompts_launched=0` |
| Device 2 transport | Known secondary tailnet peer online; one relay ping succeeded; one strict pinned SSH attempt closed before server host-key exchange/authentication |
| Device 2 identity and CLI | UNKNOWN: no device-local command executed; version, settings, discovery, authentication and native-agent dispatch not reverified |
| Changes to either handset, Origin or its backup | None |

Independent review reproduced a shared Git configuration change: sparse-checkout setup enables `extensions.worktreeConfig`. The original helper described it incorrectly as runtime-only. This prompted an explicit opt-in and rejection of ambiguous pre-existing configurations before rollout. Sparse settings themselves were observed per-worktree; plain Git status correctly handled omitted paths. See final checks below for the hardened implementation.

Reviewed earlier PR head `d7b8022e92c161e8326dbce23611c536d115ffa3`: OPEN/APPROVED/UNSTABLE; one CodeRabbit approval, zero inline comments, four failed Vercel deployment contexts, successful repo-gate/Termux-smoke. Approval belongs to that head, not automatically to follow-up commits. Vercel failure causes were not investigated or attributed to this patch.

The full [operational plan](OPERATIONAL-PLAN.md) records the changed conditional Device 2 authorization, identity gate, collaboration surfaces, thin-worktree adaptation, remaining build verification/pilot, acceptance and rollback. Project skill and template are repository artifacts; no native custom agents, hooks, plugins, remote daemon, scheduler, Google auth or live agy settings were changed. No model-token readiness test was performed.

Final hardened validation: `python3 -m unittest discover -s tests -p 'test_antigravity*.py' -v` PASS **14 tests** (7 readiness + 7 thin-worktree). Skill validator PASS; proposal registry PASS; staged-file repo-gate PASS; Termux-smoke PASS on Linux; whitespace audit PASS. Regression tests cover explicit extension opt-in, ordinary plain-Git sparse status, source dirty preservation, config preservation except the approved extension, and ambiguous dormant/shared configuration rejection. No helper apply was run on the real repository or any phone; apply tests use disposable fixtures. AGY-1497-05 is repository-complete; AGY-1497-04 and AGY-1497-06 remain blocked.
