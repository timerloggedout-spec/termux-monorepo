# Sentry + Linear Integration

Sentry is provisioned under org `o4511844213522432` with **four projects** for this monorepo:

| Platform | Project ID | DSN key (prefix) | Primary use |
|----------|------------|------------------|-------------|
| Python (default) | `4511844223680512` | `a922fa6c…` | ArchWiz, deepcli, CLIs |
| Python aiohttp | `4511844256055296` | `c7fb0bb5…` | aiohttp web services |
| Browser JavaScript | `4511844264640512` | `2fbd3c77…` | web UIs (commingle-swarm/web, dashboards) |
| Rust | `4511844272111616` | `8b6f33db…` | harmonizer, synthegration-cli, maxc |

---

## Python (ArchWiz / deepcli)

### Install

```bash
pip install "sentry-sdk"
```

### Init

```python
from archwiz.sentry_init import init_sentry, capture_exception, capture_message

init_sentry()                    # default python project
# init_sentry(project="aiohttp") # aiohttp project DSN
```

Or full snippet:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://a922fa6cd019e401e779d420d28b155c@o4511844213522432.ingest.us.sentry.io/4511844223680512",
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
)
```

### Verify

```bash
python3 archwiz/sentry_init.py
python3 archwiz/sentry_init.py aiohttp
```

```python
1 / 0  # intentional error
from sentry_sdk import metrics
metrics.count("checkout.failed", 1)
sentry_sdk.logger.info("info log")
```

---

## Python + aiohttp

AIOHTTP integration is **auto-enabled** when `aiohttp` is importable. Init **before** creating the app:

```python
from aiohttp import web
import sentry_sdk

sentry_sdk.init(
    dsn="https://c7fb0bb5cf4210fae90119131c12b320@o4511844213522432.ingest.us.sentry.io/4511844256055296",
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
)

async def hello(request):
    1 / 0  # test error
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes([web.get("/", hello)])
web.run_app(app)
```

Or via helper: `init_sentry(project="aiohttp")`.

Python 3.6 only: also `pip install aiocontextvars`.

---

## Browser JavaScript

### npm / yarn / pnpm

```bash
npm install --save @sentry/browser
```

```javascript
import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: "https://2fbd3c77388239145b6dd872f1e054aa@o4511844213522432.ingest.us.sentry.io/4511844264640512",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", /^https:\/\/yourserver\.io\/api/],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

// verify
Sentry.metrics.count("test_counter", 1);
// myUndefinedFunction();
```

Starter module: `docs/sentry/browser-init.js`

### Loader Script (no bundler)

```html
<script
  src="https://js.sentry-cdn.com/2fbd3c77388239145b6dd872f1e054aa.min.js"
  crossorigin="anonymous"
></script>
<script>
  Sentry.onLoad(function () {
    Sentry.init({
      tracesSampleRate: 1.0,
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
    });
  });
</script>
```

Useful for static pages such as `termux-ecosystem-architecture.html`.

---

## Rust

### Cargo.toml

```toml
[dependencies]
sentry = "0.49.0"
```

### Init + verify

```rust
fn main() {
    let _guard = sentry::init((
        "https://8b6f33db85568dc94e5db28dfe5eee72@o4511844213522432.ingest.us.sentry.io/4511844272111616",
        sentry::ClientOptions {
            release: sentry::release_name!(),
            send_default_pii: true,
            ..Default::default()
        },
    ));

    // Sentry will capture this
    panic!("Everything is on fire!");
}
```

Apply in crates under `harmonizer-prod_cli/`, `synthegration-cli/`, `workspace/maxc/`, `appliedSxi/maxc/` as needed. Example: `docs/sentry/rust_main_example.rs`.

---

## Linear Sync Bridge

`archwiz/linear_sync.py` reads local `master_tasks.json` + `taDone.md` and updates matching Linear issues (e.g. TER-5).

### Setup

```bash
export LINEAR_API_KEY="lin_api_..."
export LINEAR_TEAM="Termux-monorepo_linear"   # optional
python3 archwiz/linear_sync.py --dry-run
python3 archwiz/linear_sync.py
```

Dashboard menu **[8] Linear Sync** (Manus PR #13) invokes the same script.

| Local | Linear state |
|-------|--------------|
| task id in taDone.md | Done / completed |
| otherwise | Todo / unstarted / Backlog |

Agents can also use Linear MCP tools (`linear___save_issue`, etc.) without the Python bridge.

---

## Env overrides

| Variable | Effect |
|----------|--------|
| `SENTRY_DSN` | Force a specific DSN (wins over project) |
| `SENTRY_PROJECT` | `python` \| `aiohttp` |
| `SENTRY_RELEASE` | Release name tag |
| `ARCHWIZ_ENV` | Sentry environment tag |
| `LINEAR_API_KEY` | Enable live Linear updates |

---

## PR / branch

- Branch: `feature/sentry-linear-integration`
- PR: #16 → `master-staging`
- Linear: TER-14
