# PolyGlot localization — work items

Proposal: polyglot-localization
Scope: shared localization infrastructure and Urdu-first Teammate Portal.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| POLY-001 | Establish locale registry, Urdu/English catalogs, mapping, translation manifest, provider registry, DOE design, and optional feedback schema. | JSON validation; stable message IDs; source revision provenance; explicit Urdu RTL metadata. | Implementing |
| POLY-002 | Render Teammate Portal in English and Urdu with accessible language navigation and RTL. | Renderer tests; generated HTML assertions for lang/dir, translated labels, keyboard-accessible links. | Implementing |
| POLY-003 | Run blinded provider comparison using fixed Urdu task cohort and record multi-response outcomes. | Pre-registered design, schema-valid run records, repeated treatments, human review receipts. | Pending |
| POLY-004 | Integrate opt-in teammate feedback into the evaluation loop. | Consent-bearing, anonymous-by-default feedback records linked to exact translation revisions. | Pending |
| POLY-005 | Run repository gates and independent review; reconcile promotion state. | repo-gate, Termux smoke, proposal validator, CI and review evidence on exact SHA. | Pending |
