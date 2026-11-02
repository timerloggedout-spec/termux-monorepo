# NSE-023 — pinned dependency register

Owner ruling (2026-11-02): the Lean Implementation scope = Batteries ∧
Mathlib ∧ further Lean libraries, each as a **pinned dependency** with
{pin revision · toolchain · license · provenance} recorded here, dual-gate
review intact, fail-closed oracle contract unchanged. An unrecorded
library is not an oracle input. Each dependency compiles under its OWN
pinned toolchain (toolchains differ across pins — that is expected and
recorded, not smoothed).

| Library | Pin revision | Toolchain (pin's own) | License | Provenance | Status |
|---|---|---|---|---|---|
| Batteries (fork) | `36cc05ca2d0e469bfbeea9437f460e19238e885e` | `leanprover/lean4:v4.34.0-rc1` | Apache-2.0 | `timerloggedout-spec/batteries_fork` (fork of leanprover-community/batteries); submodule `refTemplates/smods/batteries_fork` | ACTIVE — P-001 PASS against this pin |
| Mathlib | `cc8b65263ab8ef05dd813bccd999400f0303fdcc` | `leanprover/lean4:v4.36.0-rc2` | Apache-2.0 | upstream `leanprover-community/mathlib4`, master HEAD as retrieved 2026-11-02 (commit dated 2026-11-02T13:31:39Z); pin is the immutable SHA, not the moving branch | REGISTERED — compile proof = packet P-002 (oracle Mathlib leg) |
| (further libraries) | — | — | — | register open; admission = pin + this row + dual-gate | ∅ yet |

Notes:
- Pin discipline: pins are immutable SHAs. A pin bump is a new row version
  via PR with the reason recorded; never a silent re-point.
- License texts live in the upstream repositories at the pin; the register
  records the license identity, not a copy.
