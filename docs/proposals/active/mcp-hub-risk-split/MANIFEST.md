# Proposal: mcp-hub / hub_mcp risk split

## Status
Active — implements the "keep both, split by risk" decision on the
mcp-hub vs. hub_mcp architecture question.

## Context
`mcp-hub` (PR #442, merged) consolidated `termux-mcp` and `android-mcp`
behind one public Vercel deployment, bearer-token gated. Separately,
`docs/architecture/transport-and-identity-decision.md` and
`docs/architecture/termux-agentic-hub.md` document an already-accepted,
already-tested architecture (`hub_mcp/`) built specifically to keep the
phone off public transport: job-envelope over GitHub, no direct HTTP path
to the device.

Both now exist. Operator decision: don't pick one exclusively — split by
risk per tool.

## Decision
- **mcp-hub (public HTTP, bearer-token gated):** read-only / stateless
  tools only. Public exposure is an acceptable trade for low-latency
  status checks.
- **hub_mcp (job-envelope, no public transport):** anything that runs a
  command, changes device/package state, or touches `adb`.

See ITEMS.md for the per-tool disposition.
