# Architecture

Browser UI → HTTPS/Caddy → Python API on Vultr VM → deterministic matching + impact engine → SQLite case state and append-only audit chain.

The optional narration adapter calls an OpenAI-compatible endpoint (Vultr Serverless Inference or a private AMD-compatible endpoint). It receives minimized structured evidence and cannot affect matching, exposure arithmetic, or approvals.

## Authority boundaries

- Matching arithmetic: deterministic engine only.
- Exception classification: deterministic rules with source evidence.
- Resolution proposal: deterministic rule output; optional model may narrate.
- Approve/hold/reject: authenticated human controller with a note and expected-version check.
- Payment release and ledger posting: explicitly not implemented.
- Audit history: append-only SQLite table with UPDATE/DELETE triggers and a SHA-256 predecessor chain.

## Data path

1. A structured case contains invoice, purchase order (including revision), and goods receipt lines.
2. The matcher joins by SKU and compares invoice quantity, PO authorization, receipt quantity, and unit price.
3. The impact calculator identifies affected invoice, PO, receipt, vendor, and payment batch; computes a bounded exposure basis; and lists downstream actions held.
4. A controller decision is committed with an audit event in the same transaction.
5. An evidence endpoint exports the case, computed analysis, and audit events.

## Deployment boundary

The service binds to 127.0.0.1:8080 behind Caddy TLS. SQLite lives on persistent VM storage. Do not horizontally share a SQLite file; replace it with a transactional shared database before scaling multiple app instances.

## Non-goals

No PDF OCR, autonomous payment, vendor outreach, production ERP writeback, multi-currency FX, or arbitrary agent tool execution in v0.1.
