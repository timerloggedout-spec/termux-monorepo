# Match Impact Desk

Vultr Agent Rush · Challenge 2 — Powering the Future of Work.

A procurement exception-control workspace built around deterministic three-way matching, impact analysis, human approval, and audit-ready evidence.

The existing Quarantine Browser Clerk is the separate Challenge 1 / Blast Radius Zero entry. Match Impact Desk is the second-track application; it does not duplicate the browser-sandbox runtime.

## Workflow

1. Match purchase order + invoice + goods receipt line by line.
2. Detect duplicate invoices, price variance, missing reference lines, and quantity-over-receipt.
3. Calculate exposure and enumerate affected invoice, PO, receipt, vendor, and payment batch.
4. Propose a scoped resolution (credit memo, hold, or duplicate block).
5. Require a controller decision with a note and optimistic version check.
6. Append a SHA-256 linked audit event and export an evidence packet.

No payment is released, no ledger is posted, and no vendor is contacted. Approval records a resolution decision only.

## Signature scenario

Case MID-2402: PO revision 2 sets the motor unit price at $115.00; invoice INV-NORTH-8821 requests $120.00 for 10 motors; the goods receipt confirms all 10. The engine calculates a $50.00 variance, proposes a credit-memo request, and keeps payment release blocked.

Other fictional fixtures cover a clean match, duplicate invoice, and receipt shortage.

## Run locally

Python 3.11+; standard library only.

    python -m unittest discover -s tests -v
    python app.py

Open http://127.0.0.1:8080.

## Controls

- Production mutations require MATCHDESK_ADMIN_TOKEN and X-Operator-Token.
- Development writes without a token are accepted only from loopback.
- Audit table rejects UPDATE and DELETE.
- Stale decisions return HTTP 409.
- Exception approval requires a substantive resolution note.
- Inference is optional and advisory only; deterministic matching remains authoritative.
- No raw secrets or request bodies are logged.

## Optional AMD / Vultr inference

Vultr Serverless Inference can draft a controller brief through its OpenAI-compatible endpoint. AMD Lemonade/ROCm-compatible endpoints can be configured for local/private narration; the endpoint must be reachable over a private authenticated network. See docs/AMD-OPTIONAL-INFERENCE.md.

## Vultr deployment

Challenge 2 requires a Vultr VM backend and public web app; Serverless Inference is optional. Deployment files are in deploy/. A real VM, public URL, DNS/TLS, and remote smoke test are not claimed until evidenced.

## API

GET /health, /api/overview, /api/cases, /api/audit, /api/audit/verify, /api/cases/{id}/evidence. POST /api/cases ingests a validated structured invoice/PO/receipt case.

POST /api/cases/{id}/decision and /api/cases/{id}/brief.

## Limitations

Synthetic USD fixtures only. No PDF OCR, production ERP connector, payment rail, ledger write, or multi-currency FX is enabled. The impact graph covers modeled objects, not every enterprise dependency. This is a deployable demo foundation, not a certified accounting control.

MIT License.
