# Codespace / Bifrost Operational Health

## Repository-side verification

- `.devcontainer/devcontainer.json` exists and defines Python 3.12 Bullseye, Node 20, Rust, GitHub CLI, setup.sh, and 4 CPU / 8 GB / 32 GB requirements.
- `docs/ops/CODESPACE-AGENT-LANE.md` defines Codespaces as the interactive/support plane.
- `docs/ops/CODESPACE-CREDENTIALS-SSOT.md` defines the credential precedence without exposing token values.
- `.github/workflows/codespace-health.yml` can inspect an existing Codespace and optionally start it when it is Shutdown.
- BIFROST-006 identifies Codespaces as the preferred mocker/Bifrost/Go benchmark host.

## Live-state caveat

Repository configuration is verified. Current Codespace state requires an authenticated Codespaces API call.

Existing BIFROST-006 evidence records `agent-bifrost-006-5g7qvg7pqjggh4jqv` reaching Provisioning → Available on 2026-09-23, while `glorious-capybara-wrq7vrqj7xqjh995p` was Shutdown after idle timeout. That historical evidence does not prove either is Available now.

## Recovery

If the Bifrost Codespace is Shutdown:
1. Run Codespace start (dispatch) with the exact name.
2. Re-check until Available.
3. If deleted/expired, run Codespace create on master.
4. Re-run BIFROST-006 mocker-backed smoke.
5. Record machine, Codespace, Bifrost SHA, benchmarking SHA, host, load, success rate, p50/p99, throughput.

Do not classify Shutdown as a provider failure or automatically infer that reprovisioning is required.

The current connector does not expose a direct authenticated Codespaces start/list operation, so this lane does not claim a current live state without workflow/API evidence.
