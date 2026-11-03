# StudySprint — performance & size budgets

Budgets are ceilings chosen to bite before users hurt, not
descriptions of current numbers. Every measured run is a
**lab run** (method stated with it); field data would
supersede it. Overruns are named here, never silently
re-baselined — a budget moves only by a deliberate edit to
this file in a reviewed PR.

## Budgets

| Surface | Metric | Budget | Why |
|---|---|---|---|
| webApp | LCP | ≤ 2.5 s | web.dev "good" threshold |
| webApp | CLS | ≤ 0.1 | web.dev "good" threshold |
| webApp | INP | ≤ 200 ms | web.dev "good" threshold |
| webApp | shell transfer (first load) | ≤ 100 KB | the whole app should cost less than one photo |
| webApp | bundled demo state.json | ≤ 32 KiB | demo data stays demo-sized |
| APK | installed asset size | ≤ 64 KiB | the sideload pitch is "smaller than a ringtone" |
| TUI | cold path (import + state build) | ≤ 1.5 s | terminal tools must feel instant |

## Measured run — 2026-11-03 (app-package D, #4439)

Method: headless Chromium (Playwright) on the build VM,
the shipped 0.2.0 (+ #4438 tree) bundle served over
loopback HTTP, no throttling, 420×900 viewport; LCP/CLS
from PerformanceObserver; INP proxied by the maximum
`event` entry duration across a real interaction script
(tab → SR flip → grade), since a lab has no field INP.
Sizes from the tree and the reproducible APK build.

| Metric | Measured | Budget | Verdict |
|---|---|---|---|
| LCP | 592 ms | 2.5 s | PASS (4× headroom) |
| CLS | 0.040 | 0.1 | PASS — watch: 40% of budget, from the loading→content swap |
| Interaction (INP proxy) | max event 168 ms / 43 events | 200 ms | PASS — watch: 84% of budget; the grade→recompute+render path is the long event |
| Shell transfer | 54,810 B | 100 KB | PASS |
| state.json (bundled) | 23,560 B | 32 KiB | PASS |
| APK | 50,321 B | 64 KiB | PASS |
| TUI cold path | 703 ms (import 699 · state 4) | 1.5 s | PASS |

Overruns: **none.** Watch items (named, not hidden): CLS
and the interaction path above. If either crosses its
budget in a later run, the run's PR names it here before
any budget conversation starts.
