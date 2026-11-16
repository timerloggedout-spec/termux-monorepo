# Demo script — under 3 minutes

Run `demo.py` on screen; it executes live against this public repo.
Narration timings assume the script's three scenarios.

**0:00 — The problem (30s).**
"Agents act on evidence they're handed — and handed evidence is usually
a claim. This is the Delphi Oracle: it judges a proposed action and
fails closed. No material evidence, it abstains. Consequential actions,
it escalates. Its one limit: it could only judge what it was handed.
So we gave it a tool."

**0:30 — Scenario 1: asserted evidence (30s).**
"Is PR 1620 ready? The requester asserts the checks are green. The
oracle abstains — an assertion is not evidence, and nothing was
fetched."

**1:00 — Scenario 2: fetch_evidence (60s).**
"Same question, artifact named. The tool retrieves the PR's real state
and its check runs — read-only — and assembles an evidence set where
every item carries provenance, a freshness stamp, and a content hash.
Now the oracle grades *fetched* evidence: ALLOW_RECOMMENDATION, with a
versioned receipt of exactly what it judged."

**2:00 — Scenario 3: the class rule (40s).**
"A credential-mutation request. The tool fetches real, material
evidence — and the answer is still ESCALATE. Evidence never outranks
the action class; consequential means a human decides."

**2:40 — Close (20s).**
"One tool turned a judge of claims into a judge of evidence. The
handler ships as a Lambda unit behind a Strands Decider agent; this
recording runs the identical code locally — no AWS account, no claims
beyond the receipts on screen."
