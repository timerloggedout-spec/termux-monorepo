## 2026-08-01 - Flicker-Free Real-Time CLI Dashboards with Rich Live
**Learning:** Terminal dashboards that clear the screen using raw ANSI escape codes (`\033[H\033[J`) or `clear` commands create severe flicker and redraw lag. This harms cognitive accessibility and visual appeal. Using `rich.live.Live` with high-level structural layout (`Table`, `Panel`, `Text`) ensures updates are drawn to the screen differential/flicker-free, and handles terminal exits cleanly.
**Action:** Always prefer `rich.live.Live` (or similar differential-updating curses-like tools) for terminal UI dashboards that require frequent, real-time telemetry updates.

## 2026-08-07 - Reactive lit-html Rendering Loop callbacks for UI Responsiveness
**Learning:** In simple lit-html single page applications, local variable state does not automatically survive or trigger re-renders. When designing interactive elements (e.g. loading animations, async buttons, and disabled states), passing a root rendering callback function (e.g., `reRender`) into components allows children to trigger DOM updates on-demand. This maintains accessible ARIA updates and reactive visual states.
**Action:** Design stateless/state-holding components to accept a rendering callback to ensure asynchronous triggers seamlessly update the interactive DOM.
