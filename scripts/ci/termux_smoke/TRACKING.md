# termux_smoke — suite tracking

Registry of smoke suites under `scripts/ci/termux_smoke/<suite>/`.
Invoked from `scripts/ci/termux_smoke.py` (core) and `--with-optional`.

| Suite | Path | Required in core? | Network? | Source | Status |
|-------|------|-------------------|----------|--------|--------|
| **connectors** | `scripts/ci/termux_smoke/connectors/` | presence + compile (core soft-required) | no | #70 project-management / connectors | active |
| deepcli | (inline in termux_smoke.py) | no | no | legacy | active |
| archwiz | (inline in termux_smoke.py) | no | no | legacy | active |
| termux-api | (inline) | no | no | legacy | active |

## Rules

1. Each suite lives in `scripts/ci/termux_smoke/<name>/`.
2. Entry point: `smoke_<name>.py` or documented in suite README.
3. Core path: stdlib only, no pip, no network required to PASS.
4. Optional path may soft-skip missing deps (NOTE, not FAIL).
5. Update this table when adding/removing suites.

## Connectors suite (#70)

Tracks offline health of `.github/connectors/`:

- `connector_manager.py` present + compiles
- `health_check.sh` present + `bash -n`
- YAML configs present: `llm_providers.yaml`, `github.yaml`, `webhooks.yaml`, `exchanges.yaml`
- Optional: `list_connectors` if PyYAML installed (no live API calls)

Follow-up extraction of exchanges scope remains **#74**.
