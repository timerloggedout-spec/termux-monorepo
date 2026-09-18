# AR-18 Capability Surface Evidence Schema

**Schema:** `capability-surfaces/v1`  
**Status:** observe-only adapter contract.

This schema normalizes observations from existing connector, plugin, MCP, tool, and repository-local skill inventories so AR-18 can join them to the existing Capability × Specialist matrix. It is an evidence projection, not a new registry.

## Document

```yaml
schema: capability-surfaces/v1
observed_at: <UTC timestamp>
surfaces:
  - kind: connector | plugin | mcp | tool | skill
    id: <stable source identifier>
    provider: <optional provider identity>
    model: <optional model/agent identity>
    capabilities: [<observed/documented capability>]
    availability: available | configured | unavailable | unknown
    authority: observe | read/query | analyze/reproduce | propose | prepare | sandbox-write | repository-write | promote | unknown
    evidence_refs: [<immutable evidence locator>]
    observed_at: <UTC timestamp>
    freshness: current | stale | unknown
```

## Semantics

- `kind` and `id` identify an existing surface; they do not establish authority.
- `capabilities` are surface observations and **never become AR-18 capability declarations by themselves**.
- `provider` and `model` are optional join keys. Provider/model discovery remains owned by provider catalogs and routing SSOTs.
- `availability` is separate from capability, entitlement, execution, and correctness.
- `authority` describes the observed policy/effect boundary; it does not grant that authority.
- `evidence_refs` must point to attributable evidence. Secrets, tokens, raw prompts, issue bodies, and review bodies are excluded.
- `observed_at` and `freshness` prevent stale surface evidence from being presented as current.
- Missing or malformed artifacts fail soft to an empty observation set; the legacy execution route is unaffected.

## Admission boundary

The join is:

`specialist × surface × capability × availability × authority × evidence × freshness`

A surface match enriches a candidate envelope. Admission still requires the existing AR-18 hard gates: declared capability/effect, trusted provenance, policy, live availability, quota/cooldown, current-SHA evidence where required, and explicit branch-write confirmation where required.

This preserves:

`DISCOVERED ≠ DECLARED ≠ VALIDATED ≠ ELIGIBLE`

and:

`VALIDATED ≠ AUTHORIZED`

## Source ownership

This adapter consumes existing source-of-truth inventories including `docs/schemas/provider-capabilities.md`, `.github/connectors/`, repository-local `.agents/skills/`, provider command libraries, and other declared tool/MCP/plugin inventories. It must not duplicate or silently supersede those sources.