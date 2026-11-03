# SWARM RESEARCH TEMPLATE — issue → SOFA search → solution FIX

`[MUSEai]@{role:{lane-moniker}}` · Tasking: {owner/manager order, source chat or issue #, date} · Deliverable pattern: this file · Exemplar: `docs/ops/SWARM-RESEARCH-EXAMPLE-4283.md`

**Job:** given an ISSUE (defect · tooling failure · blocked build), find the
SOLUTION and return a FIX — one fix candidate, with provenance and a
verification step that proves or kills it. Not a survey, not a menu.

**Knowledge source of record:** Stack Overflow for Agents
(agents.stackoverflow.com) via the `custom.stackoverflow-agents` helper
`~/workspace/custom-connectors/custom.stackoverflow-agents/bin/sofa.py`
(connector doc: `~/workspace/custom-connectors/custom.stackoverflow-agents/CONNECTOR.md`).

**Leg gates (hard):**
- READ legs run now under the granted scopes (`sofa.read` +
  `sofa.identity.read`): `sofa_search` · `sofa_get_post` ·
  `sofa_list_related_playbooks` · `sofa_pull_playbook` · `sofa_tags` ·
  `sofa_search_external_links` · `sofa_my_verifications` ·
  `sofa_connection_status`.
- WRITE leg is GATED: ask/reply/vote/verify need widened scopes
  (`sofa.write.*` / `sofa.vote` / `sofa.draft.*`). Re-consent is in flight
  at Connectors Inventory. Until `sofa.py status` shows the write scopes
  LIVE, step 6 produces ASK **text only** — nothing posts.
- If the READ leg itself is down (preflight fails — e.g. refresh
  `invalid_grant`), stamp the leg `NOT_ESTABLISHED` with the verbatim
  error, run the fleet-record leg (step 4) alone, and say so in the
  output. **∅ fabricated SOFA results, ever.**

**Rules of engagement:** firsthand evidence only · a SOFA answer that
contradicts firsthand fleet evidence LOSES (step 4) · secret values never
(names only) · one fix candidate — a candidate without a kill-test is
not a candidate · negative results are recorded, not rounded away.

---

## Preflight

```bash
python3 ~/workspace/custom-connectors/custom.stackoverflow-agents/bin/sofa.py status
```

Record: connection state · agent · scopes · leg state {read: live|down,
write: gated|live}. Down ⇒ proceed with step 4 as the only evidence leg
and mark every SOFA-dependent field `NOT_ESTABLISHED`.

## 1. Intake

| Field | Content |
|---|---|
| Issue | {repo issue # / incident ref + title} |
| Statement | {the failure, verbatim where possible} |
| Environment | {tool + version · OS/runner · device/VM class · hard constraints (no-KVM, egress, scope, quota)} |
| Already tried | {each attempt + its ref (run #, PR #, commit) + its outcome — never re-derive a dead end} |

## 2. Atoms — decompose into searchable problems

One atom = one search. Extract:

- **Error strings** — verbatim, quoted (`"Unknown AVD name [ss-smoke]"`).
- **Tool+version pairs** — `emulator 37.2.13` · `avdmanager (cmdline-tools 11076708)`.
- **Constraint class** — {no-KVM · AVD provisioning in CI · token bucket ·
  egress proxy · auth scope · …}.
- **Surface pair** — {the tool that produced state} × {the tool that
  failed to find/consume it} — divergence bugs hide here.

## 3. SOFA search (per atom)

```bash
SOFA=~/workspace/custom-connectors/custom.stackoverflow-agents/bin/sofa.py
python3 $SOFA sofa_search --query "<atom>"
python3 $SOFA sofa_list_related_playbooks --query "<atom>"   # if supported args differ: sofa.py describe <tool>
python3 $SOFA sofa_tags --query "<tool>"                     # tag grounding for the ASK draft
```

Per atom record: hits {post id · title · verification state} · playbooks
{slug · pulled y/n} · ∅ hit = a recorded MISS (negative evidence, feeds
step 6). **Rank:** verified posts > pulled playbooks > unverified posts >
external-link assessments. Read the top candidate in full
(`sofa_get_post --id <n>` / `sofa_pull_playbook`) before ranking it —
titles do not rank.

## 4. Cross-check vs our own record

Sources: repo issues/PRs (PAT helper API) · `docs/ops/` · lane memory ·
prior runs' artifacts/logs.

| Candidate claim | Fleet evidence | Verdict |
|---|---|---|
| {from SOFA} | {run # / PR # / log line / ∅} | holds · contradicted · untested-here |

**Contradicted ⇒ the candidate loses**, however verified it is on SOFA —
their environment is not ours. Agreement raises rank; `untested-here`
candidates must carry that label into step 5.

## 5. Synthesis — ONE fix candidate

| Field | Content |
|---|---|
| Fix | {the change, concretely — file/step/flag level} |
| Provenance | {SOFA post ids / playbook slugs} + {fleet refs from step 4} |
| Verification | {the exact run/test/dispatch + the signal that PROVES it} |
| Kill signal | {the observation that KILLS it — stated in advance} |
| Blast radius | {what else the change touches · rollback shape} |

## 6. Total miss → ASK draft (write leg, gated)

Both legs empty ⇒ draft the question SOFA should answer:

- **Title:** {tool+version} — {error string} — {constraint class}
- **Body:** intake (step 1) + atoms (step 2) + already-tried with refs —
  everything a responder needs, nothing they must guess.
- **Tags:** from the step-3 tag grounding.

The draft ships as text in the run record. Posting fires ONLY when the
preflight shows write scopes live; the run record then gains the post id.

---

## Run record (output shape)

One file per researched issue: `docs/ops/SWARM-RESEARCH-<issue>.md`,
sections = preflight leg states · intake · atoms · per-atom SOFA results
(or NOT_ESTABLISHED) · cross-check table · the fix candidate (or the ASK
draft) · outcome stamp when the verification step lands.
