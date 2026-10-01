# BIFROST-006 evidence — 2026-09-23

## Codespaces observed

| Name | State | Machine | Notes |
|------|-------|---------|-------|
| `agent-bifrost-006-5g7qvg7pqjggh4jqv` | Provisioning→Available | standardLinux32gb | Created via workflow_dispatch + ARCHWIZ/OPERATOR secrets (run 35837921144) |
| `glorious-capybara-wrq7vrqj7xqjh995p` | **Shutdown** | standardLinux32gb | Created ~2026-09-15; idle timeout stopped compute — **not** limit-rotation |

## Why Shutdown is not “rotating due to a limit”

GitHub stops a codespace after **idle timeout** (default **30 minutes** without interaction). That yields state **Shutdown**: VM off, disk kept. Concurrent/spending limits would **block create** with an API error, not flip an existing codespace to Shutdown.

Retention: stopped codespaces can be auto-deleted after retention days (default up to 30).

## Credential path (broadcast)

See `docs/ops/CODESPACE-CREDENTIALS-SSOT.md`.

```text
ARCHWIZ_GITHUB_TOKEN || OPERATOR_GITHUB_TOKEN || OPERATOR_TOKEN
```

#184 = names/scopes inventory only.

## Smoke evidence

GHA workflow `bifrost-006-smoke.yml` produces `results-mocker-smoke.json` artifact (mocker path; no paid OpenRouter).

Agent-Identity: Grok (Administrator)
