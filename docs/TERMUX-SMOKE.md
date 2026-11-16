# Termux Smoke Gate — Agentic runtime surface

> **Branch:** `termux-smoke`
> **Script:** `scripts/ci/termux_smoke.py`
> **Workflow:** `.github/workflows/termux-smoke.yml`

## Position in the spine

```
repo-gate → termux-smoke → language gates → provider tests → master
```

## How to run

```bash
python3 scripts/ci/termux_smoke.py
python3 scripts/ci/termux_smoke.py --with-optional
python3 scripts/ci/termux_smoke.py --json --with-optional
```

## What it checks

| Check | Required |
|-------|----------|
| python-version ≥ 3.9 | yes |
| repo-layout (gate scripts + docs) | yes |
| repo-gate compiles | yes |
| smoke self-compiles | yes |
| git on PATH | yes |
| bash on PATH | yes on Termux, soft elsewhere |
| writable TMPDIR | yes |
| deepcli / multi-ai / archwiz compile | optional |

Full detail: see `master-staging` copy if this summary is abbreviated.
