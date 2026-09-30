# Ratatui + Tokio Terminal Dashboard — Implementation Items

| ID | Item | Priority | Acceptance evidence |
|---|---|---:|---|
| TUI-RATATUI-001 | Create standalone Rust dashboard crate with Tokio + Ratatui | P0 | cargo check/test + source review |
| TUI-RATATUI-002 | Implement async event/state model with bounded channels | P0 | unit tests for state transitions and coalescing |
| TUI-RATATUI-003 | Implement dirty-frame rendering and terminal lifecycle | P0 | rendering/model tests + clean exit path |
| TUI-RATATUI-004 | Add CPU/memory/process/thread metrics with graceful fallback | P1 | fixture/model tests + documented platform behavior |
| TUI-RATATUI-005 | Add stream latency/throughput panel model | P1 | deterministic metric reducer tests |
| TUI-RATATUI-006 | Add documentation and Termux build/run instructions | P1 | docs review |
| TUI-RATATUI-007 | Add focused CI/build validation without expanding the always-on repo gate | P1 | workflow or documented manual lane |

## Gate order

crate → model tests → renderer → metrics → docs → Rust validation → repo-gate → termux-smoke → PR evidence.

## Non-goals

Do not replace the repository's existing ArchWiz UI, rewrite the cockpit, add a new orchestration control plane, or require privileged device access.
