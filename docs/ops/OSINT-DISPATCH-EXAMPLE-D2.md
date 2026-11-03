# OSINT dispatch — worked example: D2 identity gap + podium harvest

`[MUSEai]@{role:{optimizations-assurance}}` · Template:
`docs/ops/OSINT-DISPATCH-TEMPLATE.md` · Tasking: owner order
2026-11-03 09:23 PT via main (first live exercise of the template:
re-run today's D2 identity-gap + podium harvests through it) ·
Harvest of record: podium-crawl run **41685778614** (2026-11-03
17:35Z dispatch, SUCCESS) → dataset version **2026-11-03.run1**
(artifact 13257485708) · Baseline: pinned v1 (`2026-11-03.v1`,
sha256 537981b8…).

## Preflight

- Charter: lablab public surfaces — chartered in PODIUM-DATASET.md
  (public-only · no session). ✓
- Scope class: **participant/judge observation** — rails §6 apply
  in full. ✓
- Competency binding: crawl+receipt (podium pipeline) · ingest
  discipline (append-only, conflicts kept) · identity discipline
  (podium research record) · statistical honesty (test plan). ✓

## 1. Intake

| Field | Content |
|---|---|
| Question | Who judges D2 (Vultr Agent Rush), and what is the edition's podium/field state? |
| Subject | edition `vultr-hackathon` (lablab.ai) |
| Consumer | MoneyBall test plan (test ③ feasibility) · D2 exercise record |
| Already known | v1: vultr judges 0 · podium_n 0 · field_n null; all 6 v1 judges belong to the Alpaca edition |

## 2–3. Atoms, legs, receipts

| Atom | Source class → tool | Receipt |
|---|---|---|
| Edition record | event platform → podium_crawl | `lablab.ai/ai-hackathons/vultr-hackathon` · http 200 · 347,940 B · sha256 in snapshot sources |
| Judge pool | event platform (edition-page cards) | same fetch — cards absent for this edition |
| Podium | event platform (recent-winners + edition) | 10 sources crawled, all http 200 |
| Field | event platform (`/live` surface) | `…/vultr-hackathon/live` · http 200 · 229,849 B |

## 5. Dual-valence readings

- **Zero judge cards for Agent Rush** → venue opacity for this
  edition ∧ nothing whatsoever about the judges themselves; the
  stamp lands on the venue (template §5, third example — this
  exact case).
- **Field moved between crawls** (1 project removed, 1 changed,
  1 conflict vs v1) → the field is live and churning toward the
  Nov 8 close ∧ any field statistic computed today is a
  mid-window snapshot, not a denominator.

## 8. Verdicts

| Atom | Verdict | Basis |
|---|---|---|
| Edition | **RESOLVED** | title/URL receipted in both versions |
| Judge pool (D2) | **NOT_ESTABLISHED** — never-published (event-platform surfaces) | two independent crawls (v1 + run1) of the edition page carry zero judge cards while a sibling edition's page carries 6; the ceiling is the venue's disclosure (podium research record, atom (a)). The sponsor-recap class (template §2③ — where judge names lived for other events) is a separate leg, owned by the Recruitment lane's identity-gap record; this verdict binds the platform surfaces only |
| Judge↔track linkage | **NOT_ESTABLISHED** — by construction | no pool exists to attribute; test ③ remains a descriptive census |
| Podium (D2) | **NOT_ESTABLISHED — temporal** | podium_n 0 with the event in window; re-stamps on the next crawl after winners publish |
| Field (D2) | **PARTIAL** | field_n 3 via `/live` vs 2,302 approved registrants — the gallery denominator leg (test-plan C1) remains the tests' precondition |

Dataset delta v1 → run1: 55 → 88 entities (projects 30 → 63
across editions) · changes {added 0 · removed 1 · changed 1} ·
conflicts 1 (kept, per ingest discipline). Consumers pin
`2026-11-03.run1` for this record; v1 stays pinned where cited.

*Template note:* the exercise needed nothing the template does
not carry. One sharpening adopted into practice: NOT_ESTABLISHED
stamps name their species (never-published vs temporal vs
no-surface) — the three have different re-check triggers.
