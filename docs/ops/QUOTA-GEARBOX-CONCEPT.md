# Quota Gearbox — concept design (shifting gears + RPM)

Owner order 2026-10-29 19:27 PT, via the cadence lane. Concept design for the
smooth-flow quota system already graphed by quota-usage/v1 (PR #2360). This is
a DESIGN document: nothing here is live behavior. It hands to Web Design as
usual (PM merges); the admin surface it describes is INTERNAL-designation,
like the challenge admin-metrics precedent — never a public render.

Data in: `ops/quota/quota-usage.json` (quota-usage/v1) + planner `slices[]`
(quota-specialist PR #2381) + `ops/quota/allocations.json`
(quota-allocations/v1, issue #1884) + `docs/ops/RATE-LIMIT-2026-10-29.md`.

## 1. Metaphor mapping — every term is an exact data field

| Metaphor | Exact meaning | Source field |
|---|---|---|
| RPM | Current burn rate, calls/min, per bucket | Derived from successive readings of a bucket (`series1_api_core.points[].remaining` deltas over time) — measured only where a meter exists (see §5) |
| Redline | Replenishment flow rate = limit ÷ window, phase-aligned to the reset epoch | `series1_api_core.model` (`limit`, `window_ms`, `anchor_reset`); the flow line on the burn-down |
| Over-rev | Burn ahead of the flow line → early death before reset | Point below `idealRemaining(t)` (fault `below_line`) |
| Lugging | Burn behind the flow line late in the window → quota wasted at replenishment | Point above `idealRemaining(t)` near the reset epoch (fault `above_line`) |
| Gear | Priority class in the allocation ladder | `ops/quota/allocations.json` focus, ordered: 1 `winning` (standing), 2 `repo-development` (leftover-only), 3 `research` (leftover-only), 4 `boinc-donations` (leftover-only, GitHub-provider pools only). The shipped UI reads the ladder from planner `slices[]`, not from this table |
| Shift | A dynamic re-allocation / re-prioritization event | A #1884 re-split record (PR citing #1884), rendered as a `shift` annotation (§4) |
| Tachometer | Per-slice gauge (lane \| project \| profile \| surface) | Slice flow = pool flow × share (planner `slices[]`); needle = target flow where no meter exists (§5) |
| Timing slack | Reserve that releases into lower gears as reset nears | Pool reserve (allocations remainder) reinterpreted as a release curve — PROPOSED behavior, §3b |

## 2. Surfaces

- **Dashboard (read-mostly):** tachometers per slice, current gear per slice,
  burn vs the replenishment diagonal, shift log (annotations of type `shift`).
- **Admin (settings, INTERNAL):** the interactive core in §3. Never public
  render; same designation discipline as `metrics_internal`.

## 3. Admin priority settings — schema draft

```json
{
  "slice_setting": {
    "pool_id": "github",
    "focus": "winning",
    "gear": 1,
    "pct": 100,
    "mode": "standing | leftover-only | none",
    "runtime_mode": "manual | automatic",
    "target_flow_per_min": "derived, read-only: pool_flow x pct, ladder-ordered"
  },
  "guardrails": [
    "per pool: sum(pct) <= 100 — enforced at edit time, preview shows the sum live",
    "reserve_pct = 100 - sum(pct), rendered as timing slack (release curve), never a static idle block",
    "leftover-only slices draw in ladder order, only quota the higher gear cannot consume before expiry (allocations constraint, unchanged)",
    "card rule unchanged: no setting authorizes a card-gated account or paid tier"
  ],
  "audit_event": {
    "event": "shift", "at": "ISO-8601", "actor": "admin identity / lane role",
    "pool_id": "...", "focus": "...", "field": "pct | gear | mode",
    "old": "any", "new": "any", "cites": "#1884", "pr": "the re-split PR that lands it",
    "subset_filter": "work-type tags checked for this change, or null",
    "input_source": "slider | preset | checkbox-bulk"
  }
}
```

### Admin controls (owner refinement, 2026-10-29 19:30 PT)

- **% sliders, one per slice**, with **preset buttons** that snap sliders to
  named postures. The preset vocabulary is the existing allocation postures —
  no new words invented: `Winning 100` (standing 100 to the top gear),
  `leftover-only` (draw only what higher gears cannot consume),
  `excluded / reserve-100` (0 everywhere, reserve 100 — the Codespaces
  posture), plus `equal-split` (pool shared evenly across the checked
  subset). A slider move fires the live re-derivation preview (slice flow =
  pool flow × share) before any commit.
- **Checkbox lane-subset selection:** the admin checks a SUBSET of lanes by
  work-type tag — the fleet's work classes: `issue`, `rfp`, `challenge`,
  `research`, `repo-dev`, `collectors` (tag set open, these are the owner's
  examples plus the standing classes) — and applies a priority/share change
  to the checked subset in bulk. Unchecked lanes are untouched, and the
  subset filter scopes which sliders are shown/active at all.
- **Guardrail behavior — block, not auto-balance (flagged):** both were
  mocked; the allocations discipline supports BLOCKING. Auto-balancing would
  silently rewrite other slices' shares, which breaks two standing rules —
  every change is an explicit audited old→new per slice, and the reserve is
  an explicit computed remainder, "never silently absorbed". So: when a
  slider or bulk apply would push a pool over 100%, the control blocks and
  shows the overage; the admin resolves it explicitly. Auto-balance stays in
  the mock as the rejected alternative, labeled as such.
```

Live re-derivation preview: editing a share re-derives every slice's flow in
the pool (pool flow × share, ladder-ordered) before anything is saved; a shift
takes effect only as the auditable #1884 record (a PR), exactly like cadence
re-splits today.

## 4. Shift-log annotation type (for the existing graph)

Extends quota-usage/v1 `annotations[]` with `type: "shift"` entries shaped
like the audit event above (`at`, `actor`, `slice`, `field`, `old`, `new`,
`cites: "#1884"`, `pr`). Rendered as markers on the burn timeline at `at`.
State today: the type is DEFINED and the log is EMPTY — no re-split tick has
been exercised yet (allocations `set_at` 2026-10-27).

## 5. Gearbox interactions to mock

1. **Manual shift** — admin re-prioritizes now: drag the ladder / step a
   share; preview re-derives flows; confirm writes the audit event (→ PR).
2. **Automatic mode** — cadence derives gears from flow correction (planner
   multiplier / `target_flow_per_min`); admin sees proposed shifts, not
   silent ones.
3. **Downshift-to-protect** — one action throttles collector classes when
   remaining < derived reserve (QAC-007 formula: planned + limit/10,
   `docs/ops/RATE-LIMIT-2026-10-29.md`).
4. **End-of-window release** — as reset nears, timing slack opens to gears
   3–4 (research, BOINC) so quota the top gears cannot consume is not wasted:
   the anti-lugging move, symmetric to downshift-to-protect.

Mock state for all four lives in the pack's `gearbox.mock` block, flagged
MOCK — example settings + one example shift event for design review only.

## 6. What the data cannot honestly render (NOT ESTABLISHED over invented)

- **Per-slice RPM is NOT ESTABLISHED.** No per-consumer attribution exists
  for the shared PAT bucket (GitHub exposes none to a PAT — established
  repeatedly in the rate-limit record). Slice tachometers render the
  planner's `target_flow_per_min` (a TARGET needle) or stay blank — never a
  measured rate dressed up as one. Bucket-level RPM is real only for the
  metered buckets (PAT core from readings, installation, GraphQL).
- **Gear state is CONFIGURED state** (allocations.json), not observed
  behavior; the UI must label it as the standing configuration.
- **Timing-slack release is PROPOSED.** Today's reserve is a static explicit
  per-pool remainder; the release curve is this design's proposal, pending
  cadence gate math (cadence lane supplies on request).
- **Planner `slices[]` detail** (208 slices / 52 pools, 124 numeric, per
  cadence via quota-specialist PR #2381) was not viz-verified at design
  time; the shipped UI must read `slices[]` itself, never this doc's copy.
