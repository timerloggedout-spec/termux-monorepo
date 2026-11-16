# connectors smoke suite

Offline verification of `.github/connectors/` from the #70 project-management refresh.

```bash
# via umbrella smoke
python3 scripts/ci/termux_smoke.py --with-optional

# direct
python3 scripts/ci/termux_smoke/connectors/smoke_connectors.py
python3 scripts/ci/termux_smoke/connectors/smoke_connectors.py --json
```

No network. No credentials required for PASS.
Live API probes stay in `.github/connectors/health_check.sh` (run manually with secrets).
