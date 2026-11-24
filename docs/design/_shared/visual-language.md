# Shared Visual Language

**Scope:** cross-system visual conventions. System-owned implementations remain authoritative for actual tokens and components.

## Current evidence

- Tribute Dashboard has a shared stylesheet at [`apps/tribute-dashboard/dashboard.css`](../../../apps/tribute-dashboard/dashboard.css) and implementation guidance in its [README](../../../apps/tribute-dashboard/README.md).
- Repository palette guidance lives in [PALETTE.md](../../ops/PALETTE.md) and [PALETTE-UX-ACCESSIBILITY.md](../../ops/PALETTE-UX-ACCESSIBILITY.md).
- Dashboard-specific visual conventions belong to their owning dashboard and chart standards.

## Reuse rules

1. Reference existing tokens before proposing new values.
2. Keep semantic color meaning consistent where systems share a visual language.
3. Document system-specific overrides in that system's `design.md`.
4. Treat screenshots and rendered exports as review artifacts; keep editable source in Git.
5. Record confirmed values from source files. Mark unverified visual conventions as candidates.

## Open gaps

- A single cross-product token package and ownership contract are not established by the cited sources.
- Component reuse across web and terminal surfaces requires explicit platform-specific evidence.
