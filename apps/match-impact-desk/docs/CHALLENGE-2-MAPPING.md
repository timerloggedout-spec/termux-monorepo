# Vultr Agent Rush — Challenge 2 mapping

Official event: https://lablab.build/ai-hackathons/vultr-hackathon

| Published Challenge 2 expectation | Match Impact Desk implementation |
|---|---|
| Enterprise-focused solution | Procurement/accounts-payable exception control |
| Multi-step agentic or rule-based workflow | Ingest → match → classify → calculate impact → propose resolution → controller decision → evidence |
| Real product-style web experience | Responsive queue, workbench, impact graph, audit timeline |
| Vultr VM backend | Python API service and SQLite on a Vultr Cloud Compute VM (deployment recipe supplied; live deployment still pending) |
| Public web application | Caddy/TLS deployment recipe supplied; public URL not claimed until provisioned and smoke-tested |
| Finance/accounting/procurement focus | Three-way invoice / PO / receipt matching, price and quantity exceptions |
| Serverless Inference optional for C2 | Optional OpenAI-compatible brief adapter; core app does not depend on it |
| GitHub repository and setup docs | This directory, tests, architecture, deployment and AMD notes |
| Recorded demo | Not yet recorded; recommended script is in the root README's signature scenario |

## Judging-oriented differentiation

- Business value: clean matches pass; controller time focuses on real exceptions.
- Technology: deterministic arithmetic, optimistic concurrency, append-only hash-linked audit.
- Originality: impact-radius preview enumerates downstream objects and blocks payment/ledger actions until a human decision.
- Presentation: the amended-PO $50 variance is a short, reproducible signature moment.

The official event page says Challenge 2 requires a Vultr VM backend and a web app deployed on Vultr; Serverless Inference is optional and Vultr GPUs are unavailable for this event. AMD acceleration is therefore an optional private inference integration, not a hardware dependency or an unverified benchmark claim.
