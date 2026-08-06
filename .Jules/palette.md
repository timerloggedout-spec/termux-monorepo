## 2026-08-01 - Flicker-Free Real-Time CLI Dashboards with Rich Live
**Learning:** Terminal dashboards that clear the screen using raw ANSI escape codes (`\033[H\033[J`) or `clear` commands create severe flicker and redraw lag. This harms cognitive accessibility and visual appeal. Using `rich.live.Live` with high-level structural layout (`Table`, `Panel`, `Text`) ensures updates are drawn to the screen differential/flicker-free, and handles terminal exits cleanly.
**Action:** Always prefer `rich.live.Live` (or similar differential-updating curses-like tools) for terminal UI dashboards that require frequent, real-time telemetry updates.

## 2026-08-05 - Color-Blind Accessible Telemetry Status and Liveness Indicators in CLI TUIs
**Learning:** Pairing terminal status values (e.g. SUCCESS, RETRY, CRITICAL) with distinct, universally understood emoji prefixes (✅, 🔄, 🚨, ⏳) provides immediate cognitive and color-blind accessibility, removing reliance on color alone. Additionally, adding a dynamic, timed pulsing character (💓) in the header provides a delightful liveness indicator, giving users immediate feedback that the stream is actively sync'ing.
**Action:** Always design live terminal statuses to be color-blind friendly by pairing text/color states with distinct visual symbols or emojis, and include a simple, clock-synchronized visual pulse for liveness.
