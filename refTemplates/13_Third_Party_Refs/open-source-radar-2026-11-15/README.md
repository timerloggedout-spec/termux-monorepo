# Open Source Radar — 2026-11-15

**Discovery source:** SiliconNoon, Open Source Radar — November 15: Alibaba's Open Code Review
**Reviewed:** 2026-11-16
**Lifecycle:** DISCOVERED → RESEARCH_ONLY
**Disposition contract:** smods-disposition.json

The radar is discovery provenance; upstream repositories and official docs are implementation authorities. Recheck versions, stars, availability, and license scope before implementation or pinning.

## Alibaba Open Code Review
Upstream: https://github.com/alibaba/open-code-review
License: Apache-2.0
Hybrid code-review CLI: deterministic file selection, bundling, and rule matching around LLM review judgments; upstream describes coding-agent, MCP, CI/CD, session viewer, and OpenTelemetry surfaces.
Potential fit: independent advisory review lane. Evaluate on a frozen PR cohort using precision, recall, F1, coverage, line accuracy, latency, token cost, duplicate findings, and reviewer intervention. Precision-first does not prove complete coverage. Do not grant independent corrective-write authority.

## Chrome DevTools MCP
Upstream: https://github.com/ChromeDevTools/chrome-devtools-mcp
Official guide: https://developer.chrome.com/docs/devtools/agents
License: Apache-2.0
MCP server and CLI for Chrome inspection, network/console diagnostics, screenshots, performance traces, and browser automation.
Potential fit: browser-side preview validation and measured performance evidence through the existing Web Adapter Foundry.
Security: authenticated browser state can expose private content and authorize actions. Use isolated least-privilege profiles, read-only by default. Never commit cookies, local storage, browser profiles, CDP endpoints/tokens, downloads, or raw page content. Keep browser sessions isolated from repository secrets and untrusted PR code. Do not claim Termux support without device smoke evidence.

## AG-UI
Upstream: https://github.com/ag-ui-protocol/ag-ui
Docs: https://docs.ag-ui.com/
License: MIT
Open event-based protocol for the agent-to-user-application boundary, with lifecycle, message, tool-call, state, activity, and related events over transports such as SSE, WebSockets, and webhooks.
Potential fit: compare event semantics and UI streaming/state synchronization against canonical JSONL/OpenTelemetry contracts. AG-UI complements MCP (agent-to-tool) and A2A (agent-to-agent); it does not replace them. Require replay/resume, ordering, idempotency, authorization, and transport-failure analysis before adoption.

## Univer Office SDK
Upstream: https://github.com/dream-num/univer
Docs: https://docs.univer.ai/overview
License boundary: repository open-source packages are Apache-2.0; commercial SDK modules/extensions are separately licensed. Verify each selected package and feature.
Office SDK for spreadsheet/document editing, calculation, and file processing; the Web SDK includes content models and headless processing.
Potential fit: structured SHE/Moneyball report artifacts and headless workbook/document verification. Evaluate package scope, fidelity, import/export, accessibility, bundle size, and runtime compatibility against existing CSV/JSONL/Markdown/PDF generation before adding a large dependency.

## Decision
The four references form a verification-and-interaction cluster: review changes (Open Code Review), inspect runtime behavior (Chrome DevTools), standardize agent/user interaction (AG-UI), and create/verify Office artifacts (Univer). They are independent candidates, not an adopted bundle. No source code is copied, installed, forked, or pinned by this record.
