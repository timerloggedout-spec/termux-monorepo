## 2026-08-01 - Flicker-Free Real-Time CLI Dashboards with Rich Live
**Learning:** Terminal dashboards that clear the screen using raw ANSI escape codes (`\033[H\033[J`) or `clear` commands create severe flicker and redraw lag. This harms cognitive accessibility and visual appeal. Using `rich.live.Live` with high-level structural layout (`Table`, `Panel`, `Text`) ensures updates are drawn to the screen differential/flicker-free, and handles terminal exits cleanly.
**Action:** Always prefer `rich.live.Live` (or similar differential-updating curses-like tools) for terminal UI dashboards that require frequent, real-time telemetry updates.

## 2026-10-24 - Reactivity and Closure States in Lit-HTML PWAs
**Learning:** In lightweight custom reactive PWAs built with lit-html, asynchronous initialization tasks (like fetching remote state) inside nested components can trigger infinite render loops or execute before the DOM mounts. Structuring components as factory closures that accept a root `reRender` callback, and using `setTimeout(..., 0)` to defer initialization, safely updates UI state only after the complete DOM hierarchy has mounted.
**Action:** In custom lit-html SPAs, always wrap state-holding components in closures accepting `reRender` callbacks and defer mount-time fetches with `setTimeout`.
