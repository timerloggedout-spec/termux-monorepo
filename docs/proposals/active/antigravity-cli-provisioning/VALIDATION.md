# Validation — issue #1497

Base: freshly fetched `master-staging` at `1a5af217f3ef9815ce31068d547ad28b69dd8ac7`. Execution environment: isolated issue worktree on Linux x86_64, Python 3.12.3; not Android/Termux hardware.

| Check | Observed result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_antigravity_readiness.py' -v` | PASS, 6 tests |
| `python3 scripts/proposals/validate_registry.py` | PASS, 15 proposals consistent |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS; existing debt counters unchanged |
| `python3 scripts/ci/termux_smoke.py` | PASS; `termux=False`, including connectors-suite |
| `python3 scripts/antigravity/readiness.py --workspace "$PWD"` | Exit 2: expected missing prerequisite, `agy_on_path=false`; repository marker and project skills present |
| Seed SHA-256 | Matches supplied attachment: `94db6d0900cc31727466add4bee9ec8e748bcee3ab549b4e0b77ef0cad34e4bb` |
| Whitespace audit | Original seed has a trailing blank-line warning; preserved intentionally for byte-identical provenance. Excluding the immutable seed, the patch is clean. |

The offline tool correctly reports `runtime_verified=false`, `settings_modified=false`, and `model_prompts_launched=0`. The CLI is not installed on this execution host. Nothing was installed to hide that fact. These results establish repository-deliverable validation, not an operational Antigravity connection, native Termux compatibility, sandbox containment, or on-device provisioning.

No merge or auto-merge is authorized. Linear remains unresolved because its connector requires login; issue #1497 contains the documented fallback tracking entry. No unrelated shared-checkout changes are included.
