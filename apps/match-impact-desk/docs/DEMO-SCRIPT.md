# 90-second demo script

## Opening (0:00–0:10)
"Match Impact Desk automates the clean majority of accounts-payable matching and gives controllers a bounded, evidence-backed queue for the exceptions. It never autonomously releases money."

Show the four dashboard cards and exception workbench.

## Signature exception (0:10–0:40)
Open MID-2402 / Northstar Components.

- Show PO revision 2 at $115.00 per motor.
- Show invoice INV-NORTH-8821 at $120.00 for 10 motors.
- Show the receipt confirming 10 units.
- Point to the deterministic $50.00 price variance and credit-memo recommendation.

Narration: "This is the amended-PO trap: the receipt quantity is valid, but the invoice still uses the superseded unit price."

## Impact radius (0:40–0:55)
Show the invoice → PO → receipt → vendor → payment-batch impact chain and the blocked payment-release / ledger-posting actions.

Narration: "The system tells the controller what is affected before a decision is made. It does not silently push an approval downstream."

## Human decision + evidence (0:55–1:15)
Enter a substantive controller note and record the resolution. Open the audit timeline and verify the hash chain. Export the evidence packet.

Narration: "A decision is version-checked, attributable, append-only, and exportable. Payment release remains false."

## Other controls (1:15–1:25)
Show MID-2403 duplicate block and MID-2404 receipt shortage hold.

## Close (1:25–1:30)
"Match Impact Desk turns AP reconciliation into a governed workflow: deterministic matching, explicit blast radius, human authority, and verifiable evidence."

## Recording rules

- Use only the synthetic seed records.
- Show the live Vultr-hosted URL only after DNS/TLS and external smoke checks pass.
- If the optional model endpoint is not configured, show the deterministic fallback honestly.
- Do not imply ERP, payment, or ledger integrations that are not implemented.
