# Apache Camel — integration runtime reference

**Class:** external integration framework / MCP interoperability reference  
**Status:** metadata-first candidate; not yet a live `smods` gitlink  
**Proposed live pin:** `refTemplates/smods/camel_fork-apache`

## Why it is relevant

Apache Camel provides a broad integration framework with Java/YAML/XML route DSLs, connector components, Enterprise Integration Patterns, and two distinct MCP surfaces:

- Camel CLI MCP helps agents author, validate, inspect, and diagnose Camel integrations.
- Camel MCP Server exposes explicitly selected application routes as MCP tools/resources.

The initial research target is governed interoperability with `hub_mcp`, Actions, and the existing evidence/telemetry plane—not a replacement for those systems.

## Adoption boundary

- Keep this directory metadata-only while provenance, security, and Termux compatibility are being evaluated.
- Do not clone the full source tree in routine CI.
- Do not expose unrestricted Camel tools or arbitrary routes to agents.
- A live shallow gitlink requires an immutable reviewed SHA, a demonstrated runtime need, compatibility evidence, and passing dual gates.

See `docs/proposals/active/apache-camel-smods-integration/RFP.md` for the opportunity assessment and execution gates.

## Source

See `SOURCE.txt`.
