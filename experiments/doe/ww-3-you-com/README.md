# ww-3-you-com — webWrapper build campaign (DoE)

Owner route (2026-10-31, via main): the 13 [target] webWrapper issues
execute via quota system + swarm dispatch under DoE separation;
execution lead = optimizations-assurance. Availability gates order,
not standing: cloud-only targets dispatch first (wave: ww-1 DDG,
ww-2 Brave, ww-3 You.com — this campaign completes the wave).

Target: you-com (brief #1798) — api-extraction webWrapper to the
deepCLI spec over the public You.com search surface (no account, no
session, read-only), completing the DDG/You.com zero-token-search set.
Probe budget 24 (brief cap).

Selection provenance: basis = Scout-roster rationale (discovery layer,
no routing authority); Provider Index build-arm coverage landed
(PR #2939) so the evaluator is unheld from the start for this
campaign; the jules label = trigger mechanics only. Builder = Jules
(issues route); evaluator = Gemini (evidence-only, on builder PR).
No production route before verdict.
Design: DESIGN.json.

## Design seed (inference-batch work product)

Drafted 2026-11-01 as production work by the class-corrected inference
batch (provider-invoke; evidence issue #3141) — two independent
provider drafts, folded here as design input. The brief governs
where they differ.

### Capability inventory (merged)

- `search` — query with optional parameters (page, per-page count,
  filters, sorting); returns structured results (title, description,
  URL, metadata) in the sibling wrappers' JSON format.
- `get_suggestions` — query-prefix suggestions list.
- `get_result` — fetch one result by ID.
- Error surfaces: network/API unavailability, authentication/session
  errors (public surface: expected minimal), rate limiting (backoff),
  invalid parameters (400-class), response-parse errors.

### Acceptance criteria (merged, testable)

1. `search` returns a JSON response with at least one result for a
   valid query, in the same format as the DuckDuckGo/Brave wrappers.
2. `get_suggestions` returns at least three suggestions for a prefix
   with known completions.
3. Rate-limit responses are handled by retry-after-delay, not a crash.
4. Invalid parameters (e.g. negative page) return a 400-class error.
5. Results support pagination (subsequent pages retrievable).
6. Endpoint error scenarios return appropriate, structured messages.

Provenance of the drafts: Cohere `c4ai-aya-expanse-32b` and SeaLion
`aisingapore/Llama-SEA-LION-v3-70B-IT` invoke completions on #3141
(the only two ✓ invokes of the 24-provider batch).
