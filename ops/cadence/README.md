# Cadence Dispatch — CI-hosted hook stack

## Purpose

Move heavy secret scanning off the device and onto GitHub Actions. Local
hooks stay sub-ms. CI handles diff gates, scheduled deep scans, and quota
management.

## Layers

| Layer | Where | Cadence | Scope |
|---|---|---|---|
| commit-msg | device | every commit | Conventional Commits + DO Framework |
| pre-commit | device | every commit (thin) | no-op unless RUN_HEAVY_HOOKS=1 |
| secrets-scan | Actions | push / PR | gitleaks diff + entropy |
| cadence-fast | Actions | every 6h | full-tree gitleaks |
| cadence-deep | Actions | Sunday 03:00 UTC | full history + trufflehog |
| hooks-cache | Actions | Monday 02:00 UTC | warm pip + binary caches |

## Quota

Budget: 1200 min/mo reserved (GitHub free tier = 2000). Circuit breaker at
300 remaining minutes demotes scheduled-fast to weekly.

## Tools

- gitleaks 8.30.1 — diff + history scanning
- trufflehog 3.63.7 — verified-only deep scan
- entropy_scan.py — Shannon entropy gate
- detect-secrets — baseline suppression

## Operation

Device:

    hooks-mode thin        # default; fast
    hooks-mode off         # bypass pre-commit entirely
    RUN_HEAVY_HOOKS=1 git commit ...   # opt-in offline scan

CI:

    gh workflow run secrets-scan -f scope=diff -f tool=all
    gh workflow run cadence-dispatch -f cadence=deep
    gh run list --workflow=cadence-dispatch

## Files

- .github/workflows/secrets-scan.yml
- .github/workflows/cadence-dispatch.yml
- .github/workflows/hooks-cache.yml
- ops/cadence/secrets-scan-policy.yml
- scripts/entropy_scan.py
- scripts/commit-msg.sh
- .gitleaks.toml
