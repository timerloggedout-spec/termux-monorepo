# Sentry + Linear Integration

## Sentry

### Install

```bash
pip install "sentry-sdk"
```

### Init (early in any long-running process)

```python
from archwiz.sentry_init import init_sentry, capture_exception, capture_message, start_profiler, stop_profiler

init_sentry()  # uses GitHub-provisioned DSN; override with SENTRY_DSN
```

Or copy the official snippet:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://a922fa6cd019e401e779d420d28b155c@o4511844213522432.ingest.us.sentry.io/4511844223680512",
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
)
```

### Verify

```python
# intentional error
1 / 0

# or
from archwiz.sentry_init import capture_message
capture_message("hello from termux-monorepo")
```

### Metrics / logs

```python
from sentry_sdk import metrics
metrics.count("checkout.failed", 1)
metrics.gauge("queue.depth", 42)
metrics.distribution("cart.amount_usd", 187.5)

import sentry_sdk
sentry_sdk.logger.info("info log")
sentry_sdk.logger.error("error log")
```

### Profiling

```python
from archwiz.sentry_init import start_profiler, stop_profiler
start_profiler()
# ... hot path ...
stop_profiler()
```

## Linear Sync Bridge

`archwiz/linear_sync.py` reads local `master_tasks.json` + `taDone.md` and updates matching Linear issues (e.g. TER-5).

### Setup

1. Create a Linear personal API key (Settings → API).
2. Export it:

```bash
export LINEAR_API_KEY="lin_api_..."
# optional
export LINEAR_TEAM="Termux-monorepo_linear"
```

3. Run:

```bash
python3 archwiz/linear_sync.py          # live update when key present
python3 archwiz/linear_sync.py --dry-run  # report only
```

Dashboard menu item **[8] Linear Sync** (on `manus/novel-work` / PR #13) invokes the same script.

### Status mapping

| Local | Linear state |
|-------|--------------|
| task id appears in taDone.md | Done / completed |
| otherwise | Todo / unstarted / Backlog |

### Agent / MCP note

Grok and other agents can also drive Linear via the connected Linear MCP tools (`linear___save_issue`, `linear___list_issues`, etc.) without the Python bridge. The bridge exists for on-device Termux automation and CI.

## PR / branch

- Branch: `feature/sentry-linear-integration`
- Builds on path-normalization work from Manus PR #13 (`manus/novel-work`)
- Target: `master-staging`
