# Agent Orchestration and Provider Routing

**Planes:** ephemeral GitHub Actions review/ops; chat completion through llm_api_hub and CLI wrappers; MCP tool execution through hosted/device MCP servers; provider adapters translate external calls into repository event envelopes.

**Flow:** task/role selection → model-router and quota gate → chat or MCP route → scoped adapter → schema/privacy/provenance validation → normalized integration event.

**Findings:** chat and MCP paths are distinct. Hosted MCP, device MCP, Actions and local gateway are separate execution surfaces. Adapter contract is generic; provider promotion state lives in integration registry. Aggregate quota coverage does not prove every provider has a live reader. Provider outputs remain untrusted observations.

**Sources:** [Routing map](../../ops/ROUTING-ORCHESTRATION-MAP.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md) · [Integration catalog](../../integrations/README.md) · [Quota registry](../../ops/QUOTA-REGISTRY.md)
