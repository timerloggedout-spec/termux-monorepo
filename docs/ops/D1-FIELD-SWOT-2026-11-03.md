# D1 SWOT of record — StudySprint vs the "Strands SDK: Workshop to Ship" field

Recon: 2026-11-03. Sources: owner's 4 ground-truth screenshots (read firsthand) ·
D1 roster census (55 projects, scroll-to-exhaustion, list order, cards) ·
Swarm receipted deep-reads (SyllabusSync full Body + repo; rows file = import record).
Field shape: 55 projects · likes/comments ≈ 0 field-wide (max 1 like on 10) ·
two crowded clusters (climate/health, mostly Tamil-first single-surface apps) ·
education ≈ 15 entries, exactly ONE direct competitor.

## The direct competitor — SyllabusSync AI (differentiation map)

Verified from its repo + Body (team of 1, published Nov 2, repo public):
FastAPI backend (4 agents: syllabus/planner/video/codegen) · React/TS frontend ·
Supabase Postgres+Auth · tests claimed (49 backend, vitest, Playwright, CI) ·
model = Bedrock Nova Lite named (no model id printed) ·
**"live" deployment = syllabussync-ai.vercel.app (Vercel + Supabase) — not AWS-hosted.**

| Axis | StudySprint (ours) | SyllabusSync AI |
| --- | --- | --- |
| Ingest | syllabus → **verified evidence set; agent ABSTAINS when evidence fails** | PDF syllabi → roadmaps; no evidence gate found |
| Planning | bounded week-by-week plans · re-plan on missed sessions · no-guilt mechanics | calendar study plans · tasks · progress % |
| Memory engine | **FSRS-6 + SM-2 selectable · .apkg + Obsidian export** | **none** (repo-wide search: FSRS/spaced/SM-2/Leitner = 0) |
| Surfaces | **CLI · TUI · web · Android — released per-surface, APK device-verified** | one web app |
| Evidence discipline | stamped receipts (sha) on every run · public "verify it yourself" links | none found |
| Hosting truth | public repo + Pages; claims stamped, incl. honest false stamps | "live" = Vercel+Supabase; Bedrock is a model call |
| Verification | 130-test suite · emulator gate · device smokes · public releases v0.1→v0.5 | README-claimed tests + CI |

Peer flag: **Ladder** (#55) is the field's only other evidence-discipline entry
(deterministic verbatim-quote gate; the only other project naming an SR algorithm —
SM-2 retrieval dates; AgentCore entrypoint). It validates the category; it is not
a planning competitor.

## SWOT (dual-valence: every strength carries its exposure, stated)

### Strengths (internal)
- **Evidence-gated planning** — ABSTAIN/ALLOW/ESCALATE with hash-stamped receipts;
  in-field, only Ladder shares the discipline class. *Flip:* invisible at card
  level — it must be made lexical in the v1.0.0 Update block, not left in the repo.
- **A real spaced-repetition engine** (FSRS-6 + SM-2, exports) where the direct
  competitor has none and the field has one SM-2 mention.
- **Four shipped, released, device-verified surfaces** vs a single-surface field.
- **Verifiable depth**: public releases, emulator gate, device-smoke recordings,
  the merged AWS production-span schema set. *Flip:* depth rewards Gate-2
  reading; Gate-1 is a screen — see Weaknesses.

### Weaknesses (internal, honest stamps)
- **Receipts stamp `strands_agent_available: false` · `deployment: false`** in the
  shipped build, while rival cards NAME live Bedrock models (Nova Lite, Claude 3.5
  Sonnet). On the Strands/AWS axis this is the Gate-1 exposure the Oracle scored —
  even though the nearest rival's "live" is a Vercel app making a Bedrock call.
- **Live proof one leg short**: model access settled (fleet key + gemini-3.8-flash
  accepted; run 1 = withdrawn model id, run 2 = provider 503), tool-chain receipt
  pending run 3. The AWS span is fully specced, not deployed (account = req-1 gate).
- Card presentation is plainer than SyllabusSync's polished dashboard cover;
  solo-author perception vs team entries.

### Opportunities (external)
- **55-entry field, top-50 gate**: ~40 entries are single-surface demos in two
  crowded clusters (heat alone is 5-deep: HeatSafe Shift · HeatShield Madurai ·
  Madurai HeatShield · HeatShield Sentinel · Nafas). A complete, verified,
  multi-surface education entry is structurally scarce.
- **The freeze-day Update block is a free second impression** no rival is
  positioned to match with a receipted live tool-chain (on proof) + v1.0.0.
- **Field-wide, "live" is soft**: of the full 55-row record (PR #4581), only ~13
  name a public endpoint, and several prominent ones are localhost, mocked, or
  admitted plans (CareNest "Bedrock judge pending/blocked" · Sukoon's body states
  the running code is Gemini and Bedrock is the plan · HeatShield Sentinel
  is_demo=True, live inference unverified). Verified-and-receipted beats named
  every time a judge clicks — our verify links are the field's exception.
  (Template duplication also recurs: Mugil/MazhaiMitra share near-identical
  bodies and claims.)
- Production-span recon already ranked (HF Spaces first — free, persistent,
  keep-warm on our own automation): the deployment gap is closable inside the
  judging window (Nov 9–23), not only before the freeze.

### Threats (external)
- **Gate-1 screening weights named-model/live signals**: honest false stamps can
  read as "agent not running" against Nova-Lite-named cards. This is the threat
  the production-tier decision answers.
- **Name/concept proximity**: StudySprint vs SyllabusSync (+ a second
  "StudySprint"-titled project by another team appears in the field's data —
  contested row, quarantined in the recon record; our canonical project URL +
  article are the disambiguators). Differentiation must be lexical everywhere.
- **Operational**: Actions queue congestion is live today; the freeze sequence
  (v1.0.0 cut → snapshot 22:30 PT → frozen-state verify) rides it.

## Bottom line for the two consumers
- **Production-tier decision:** the SWOT prices the gap exactly — the only axis
  where the field's card-level story beats ours is "named live model." The proof
  (in flight) + a ranked off-AWS span close it without touching any honest stamp.
- **v1.0.0 Update block:** lead with the differentiators a screener can verify in
  one click — evidence receipts · FSRS-6/SM-2 · four surfaces · device-verified
  APK — and, on the proof landing, the live tool-chain receipt line.
