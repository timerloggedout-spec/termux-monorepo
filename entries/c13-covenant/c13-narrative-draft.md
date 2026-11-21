# C13 — Narrative draft

- **RFP:** Digital Promise — K-12 AI Infrastructure Program, "Integrating Digital Public Goods to Advance AI-Enabled Formative Assessment" (Skipso, dp.skipso.com)
- **Submission filename convention (per RFP record):** `[PILASTNAME]_K12AI_RFPIntegratingDigitalPublicGoods_Narrative.PDF` — [OWNER: PI last name required to finalize filename]
- **Limit:** ≤6,000 words · **This draft:** see footer word count
- **Applicant:** [OWNER TO CONFIRM: legal applicant name and entity form — project of record: termux-monorepo / timerloggedout-spec, U.S.-based]
- **Grant:** up to $600,000 · 18 months · 2027-02-01 → 2028-07-31 · 3 phases
- **Status:** FIRST DRAFT 2026-11-19 · NOT SUBMITTED · Bracketed `[…]` items are owner decisions — full list in `c13-gaps-list.md`

---

## Outline

| § | Section | Target words |
|---|---------|--------------|
| 1 | The problem the RFP names | 450 |
| 2 | The harness: infrastructure, not another app | 700 |
| 3 | Harness tasks (≥4 required — five specified) | 900 |
| 4 | Demonstration application: StudySprint as proof | 400 |
| 5 | Serving multiple developers (majority of effort) | 550 |
| 6 | Work plan: three phases, 18 months | 700 |
| 7 | Teacher transparency and control, by design | 450 |
| 8 | Learner variability and formative-assessment grounding | 400 |
| 9 | Evaluation plan | 400 |
| 10 | Open licensing and digital public goods | 250 |
| 11 | Privacy, safety, accessibility | 350 |
| 12 | Team qualifications | 400 |
| 13 | Capacity and commitment | 200 |
| 14 | Budget summary | 150 |
| 15 | Risks and mitigations | 300 |
| 16 | Sustainability | 200 |
| | **Total target** | **ceiling 6,000; this draft ≈3,700 — headroom reserved for learning-sciences citations (§8) and pilot detail (§6) once placeholders fill** |

---

## 1. The problem the RFP names

Formative assessment works when a teacher can see what a learner is thinking, while there is still time to act on it. AI tools now promise to help at exactly that moment — drafting questions, reading student responses, suggesting feedback — but the current generation of tools hands teachers finished outputs with no visible workings. The RFP names the resulting failure points directly: limited teacher transparency and control over AI outputs, incoherent instruction, and poor adaptation to learner variability. Each failure has the same root. The AI layer is built as a product surface, not as infrastructure: its reasoning is private to the vendor, its behavior cannot be inspected or corrected by the teacher, and every new classroom tool rebuilds the same opaque machinery from scratch.

A teacher who cannot see why a question was generated, what evidence a score rests on, or which model produced a feedback draft cannot exercise professional judgment over any of it. A developer who wants to build a better tool inherits the same opacity, because there is no open, education-tuned harness underneath — no shared layer that handles model access, task structure, evidence capture, and human approval as common goods. This proposal builds that layer, once, in the open, and proves it in a real teacher-facing application.

The beneficiaries are, first, teachers in U.S. K-12 classrooms, who gain AI assistance they can inspect and overrule; second, learners, whose formative feedback arrives faster and better targeted while remaining under a teacher's authority; and third, the developer and district ecosystem, which gains shared infrastructure instead of another silo. The need is current, not speculative: districts are adopting AI tools now, under exactly the transparency and control deficits the RFP names, and the absence of open infrastructure means each adoption re-creates the same risks behind a different logo.

## 2. The harness: infrastructure, not another app

We propose an openly licensed agent harness for AI-enabled formative assessment: a reusable runtime that sits between AI models and classroom applications, and that any developer can adopt, extend, and audit. The harness has five components.

**Task runtime.** Formative-assessment work is expressed as structured tasks — generate, interpret, draft, adapt, audit (Section 3) — each with declared inputs, declared outputs, and a schema a developer can implement against. Tasks are model-agnostic: the runtime routes each task to an available model under quota-aware, pre-flight-checked dispatch, so a classroom tool never hard-codes a single vendor and never fails silently when a provider refuses or runs dry.

**Receipts layer.** Every task execution produces a receipt: the model and version used, the prompt and source materials, the student evidence spans relied on, a confidence statement, and a verification state. A claim the system cannot support with evidence is marked unverified rather than smoothed over. This discipline is not aspirational for us — it is how our own fleet operates daily, where every reported result must carry its evidence inline or be flagged as unestablished. The receipts layer turns that operational rule into a product guarantee for teachers.

**Teacher control surface.** Receipts are useless if they are buried in logs. The harness exposes them at the point of decision: a teacher reviewing an AI-drafted question sees its objective, its sources, and its difficulty rationale; a teacher reviewing a feedback draft sees the evidence it cites and can edit, reject, or replace it before any student sees it. Approval gates are harness-level primitives, not per-app afterthoughts, so every application built on the harness inherits them.

**Adaptation engine.** The harness maintains a per-learner formative state — objectives attempted, misconceptions hypothesized, evidence accumulated — and uses it to adapt difficulty and sequencing. Adaptation decisions are themselves receipted: a teacher can see why the next item got harder, easier, or different in kind.

**Provenance ledger and audit export.** All receipts accumulate in an append-only ledger. A teacher, school, or district can export the complete record of what the AI did, when, on what evidence, and under whose approval — the artifact a district needs before it can responsibly adopt any AI assessment tool at scale.

**Deployment shape.** The harness is a library and service layer, not a hosted destination: a developer embeds it in their own application, and a district can run it within its own environment and data policies. Model calls leave through the runtime's dispatch only, which means a district's data-flow review has exactly one well-specified boundary to examine. Every component is replaceable — storage, model providers, and the control-surface front end — because infrastructure that cannot be partially adopted will not be adopted at all. A conformance suite (Section 5) defines what "implements the harness" means, so claims by any product, including ours, are testable rather than rhetorical.

## 3. Harness tasks

The RFP requires the narrative to specify the tasks the harness performs. We specify five; the first four are the required core, the fifth is the accountability task that makes the other four adoptable.

**Task 1 — Generate.** From a teacher-supplied learning objective, curriculum reference, and constraints (reading level, item count, formats), the harness generates formative assessment items. Each item ships with its receipt: the objective it targets, the source material it draws on, its anticipated misconceptions, and its difficulty rationale. A teacher can regenerate with changed constraints, edit any item, or discard the set — generation proposes, the teacher disposes.

**Task 2 — Interpret.** Given student responses, the harness produces misconception hypotheses: structured claims about what a learner appears to misunderstand, each citing the specific response evidence that supports it and each carrying a confidence and verification state. Interpretation never outputs a bare score. Where evidence is thin, the harness says so and proposes the smallest next probe that would discriminate between competing hypotheses.

**Task 3 — Draft feedback under approval.** The harness drafts student-facing feedback and teacher-facing next-step suggestions from the interpretation state. Drafts are gated: nothing reaches a student without explicit teacher approval, and the approval itself is recorded in the ledger. Teachers can edit drafts in place; edits feed the adaptation state, so the system learns a teacher's standards from their corrections rather than from silent acceptance.

**Task 4 — Adapt.** Using the per-learner formative state, the harness selects or generates the next item, adjusts difficulty, and re-sequences objectives. Adaptation is conservative by construction: it acts on receipted evidence, it explains itself in the control surface, and a teacher can pin, override, or disable adaptation per learner or per class.

**Task 5 — Audit and export.** The harness compiles the provenance ledger into reviewable exports: per-learner, per-class, or per-period reports of AI activity, approvals, overrides, and outcomes. This task serves the adults accountable for the system — department heads, instructional coaches, district reviewers — and converts transparency from a feature claim into a document a district can file.

**A worked pass through the tasks.** A teacher enters Friday's objective — adding fractions with unlike denominators — and constraints: five items, fourth-grade reading level (Generate). She reviews the items with their receipts, edits one, discards one whose anticipated misconception duplicates another's. Students respond in class. The harness returns class-level interpretation: a third of responses support the hypothesis that learners are adding denominators directly, each hypothesis citing the responses behind it (Interpret). It drafts feedback for each group and a ten-minute re-teach suggestion for the teacher (Draft — she approves two drafts, rewrites one). Monday's set adapts: more items isolating the denominator error for one group, extension items for students whose evidence shows mastery (Adapt). At month's end, her department head exports the ledger: every item, hypothesis, approval, and override, intact (Audit).

## 4. Demonstration application: StudySprint as proof

A harness that nobody has used is a claim, not infrastructure. StudySprint — our formative-study application, built on a receipts discipline in which study guidance is generated from a learner's own materials and every output is traceable to its source — will be rebuilt on the harness as the reference implementation and demonstration application. StudySprint proves the harness in a teacher's hands: objectives in, receipted items out; student work in, evidence-cited interpretations out; feedback drafted, approved, delivered, and logged.

StudySprint is deliberately not the center of this proposal. Its role is evidentiary: it is the running proof that the harness's tasks, receipts, and approval gates work end-to-end, and the codebase external developers read first when they adopt the harness. The majority of funded effort serves the harness and the developers who build on it, per the RFP's majority-of-effort rule (Section 5).

## 5. Serving multiple developers

The RFP funds infrastructure, and infrastructure is measured by who else can build on it. Three commitments structure our developer service.

**Majority of effort.** More than half of funded work — measured in budget and in milestones — goes to the shared harness, its documentation, its conformance tests, and developer support, rather than to our own demonstration application. The budget (Section 14) is built to this rule, and phase milestones report against it.

**A real toolkit.** Developers receive: the harness runtime under an open license; a task-schema specification with a conformance test suite, so a developer can verify their integration behaves as specified; reference integrations, with StudySprint as the worked example; and documentation written for a developer who has never seen the codebase, tested by having external developers actually use it in Phase 3.

**Phase 3 developer cohort.** In the final phase, at least three independent developers or teams — recruited openly, supported with stipends from the grant (Section 14), and chosen for diversity of classroom context — will build their own formative-assessment products on the harness. Their integrations, friction reports, and conformance results are deliverables of this grant, published openly, because the friction an external developer hits is the most honest documentation of what infrastructure still owes its users. [PLACEHOLDER: developer letters of support strengthen this section — none are on record yet; recruiting targets and any letters received go here before submission.]

## 6. Work plan: three phases, 18 months

**Phase 1 — Harness core (months 1–6, Feb–Jul 2027).** Build the task runtime, receipts layer, and provenance ledger; implement Tasks 1–3; rebuild StudySprint on the harness as the reference implementation; publish the first public release under open licenses with the task-schema specification. Milestones: harness v0.1 with Tasks 1–3 conformance-tested; StudySprint reference integration running; receipts and ledger export demonstrated end-to-end. A small teacher advisory group [PLACEHOLDER: recruitment route — partner classrooms or advisory panel; owner/partner decision] reviews the control surface from Phase 1, so teacher judgment shapes the gates before they harden.

**Phase 2 — Adaptation, pilots, toolkit (months 7–12, Aug 2027–Jan 2028).** Implement Task 4 (adapt) and Task 5 (audit/export) to full conformance; harden the teacher control surface from advisory-group feedback; run structured classroom pilots [PLACEHOLDER: pilot sites/districts — to be named or described by recruitment status at submission]; publish the developer toolkit: documentation, conformance suite, integration guides; open the Phase 3 developer call. Milestones: harness v1.0; pilot report with pre-registered measures (Section 9); toolkit public; ≥3 developers selected for Phase 3.

**Phase 3 — External developers and public-good hardening (months 13–18, Feb–Jul 2028).** Support at least three independent developers building on the harness; run their integrations through conformance; publish their friction reports and our responses; complete the independent evaluation; deliver the final openly licensed release, the full provenance-ledger specification, and a sustainability handover (Section 16). Milestones: ≥3 external products integrated and conformance-verified; evaluation report public; final release and documentation complete.

**Deliverables, by phase.** Phase 1: harness v0.1 (Tasks 1–3), receipts and ledger specification v1, StudySprint reference integration, public repository with open licenses. Phase 2: harness v1.0 (Tasks 1–5), teacher control surface v1, developer toolkit and conformance suite, pilot report against pre-registered measures. Phase 3: at least three external integrations with conformance results, developer friction reports with responses, independent evaluation report, final release with governance and sustainability documentation. Every deliverable is public on release; there is no private final report that the field cannot read.

## 7. Teacher transparency and control, by design

Transparency in this harness is not a dashboard added at the end; it is the data model. Because every task emits a receipt, the teacher's view is complete by construction: for any AI output, the teacher can answer what produced it, from what materials, on what evidence, with what confidence, and what happened to it next — including their own edits and rejections, which the ledger preserves rather than overwriting. Control is equally structural. Approval gates sit in the task runtime, so a developer building on the harness cannot accidentally ship unreviewed AI feedback to students; the gate can be configured (per class, per task type) but not silently removed, and any configuration change is itself ledgered. Overrides are first-class data: when a teacher corrects the system, the correction is recorded with the same care as the original output, and it changes future behavior through the adaptation state. We regard the override rate — how often teachers intervene, and on what — as one of the most informative signals the pilots will produce, and it is a pre-registered evaluation measure, not a vanity metric to be minimized.

## 8. Learner variability and formative-assessment grounding

The harness's interpretation and adaptation tasks rest on established formative-assessment practice: elicit evidence of learning, interpret it against a model of how understanding develops, and act while action can still change the outcome. The misconception-hypothesis structure of Task 2 reflects that practice — the unit of interpretation is not a score but a claim about a learner's thinking, tied to evidence and open to revision by the next response. Adaptation (Task 4) is deliberately conservative: small steps, explained in the control surface, reversible by the teacher, because variability between learners is real and a system that adapts opaquely to a wrong hypothesis does active harm. [LEARNING-SCIENCES PLACEHOLDER: this section is drafted from the technical side. Before submission it requires review and co-signature by the named learning-sciences lead (see Section 12 and `c13-gaps-list.md`), whose research grounding — learning progressions, misconception literature, formative-assessment evidence base — must be cited here in their own scholarly framing. Do not submit with this placeholder unfilled.]

## 9. Evaluation plan

We evaluate the way we build: criteria declared in advance, evidence attached, negative results published. Before pilots begin, we will pre-register the evaluation measures: (a) receipt completeness — the share of AI outputs carrying full provenance, target 100% by construction and audited by sampling; (b) teacher override and edit rates by task type, interpreted qualitatively with pilot teachers; (c) interpretation quality — misconception hypotheses rated against teacher judgment on shared response sets; (d) developer measures — time-to-first-integration for Phase 3 developers, conformance pass rates, friction-report themes; (e) majority-of-effort accounting — the share of funded effort serving external developers, reported per phase. An independent evaluator [PLACEHOLDER: evaluator identity/organization — budgeted at $60,000; procurement route is an owner decision] conducts the Phase 3 evaluation and co-authors the public report. Where measures miss their targets, the report says so and says why; a harness the field can trust must publish its failures with the same receipts as its successes.

Pilots are sized for evidence, not theater: a small number of classrooms, used deeply, with teachers as paid collaborators whose override behavior and judgment are primary data. We would rather report interpretation quality on a few hundred real student responses, rated against teacher judgment, than usage counts from thousands of accounts nobody interviewed. The developer evaluation follows the same rule: three external teams, observed closely from first clone to conformance pass, tell the field more about infrastructure quality than any download statistic.

## 10. Open licensing and digital public goods

All funded outputs are digital public goods. Code is released under MIT or Apache-2.0; data, content, and documentation under CC-BY-4.0, per the RFP's licensing terms. Releases are public from Phase 1 — not a single end-of-grant dump — in public repositories with versioned releases, so any district, developer, or researcher can adopt, audit, or fork the harness at any point. No funded component depends on a proprietary service in a way that would strand adopters: model access is routed through the harness's provider-agnostic dispatch, and the receipts, schemas, and ledger formats are specified openly so an independent implementation is possible.

## 11. Privacy, safety, accessibility

The harness is designed for K-12 data realities. Student work processed by the harness is educational data: the design default is minimization — process what a task needs, retain what the ledger requires for accountability, and make retention configurable by the adopting school or district, whose policies govern. The architecture supports deployment patterns that keep student data within district-controlled environments, and the provenance ledger records AI behavior without requiring the ledger itself to become a second copy of every student's work [PLACEHOLDER: final privacy posture — data-retention defaults, FERPA/COPPA alignment statement, and any subprocessors — requires owner confirmation with the security/privacy review budgeted in Section 14]. Safety follows from the control model: students never receive unapproved AI feedback; generated items pass the teacher before use; and every output's receipt makes post-hoc review possible when something goes wrong. Accessibility is a release criterion, not a patch: the teacher control surface and the StudySprint demonstration are built to WCAG 2.2 AA targets, with accessibility checks in the conformance suite so downstream developers inherit the standard.

## 12. Team qualifications

**Project Lead / Principal Investigator — [OWNER: legal name, title, CV for Supplemental PDF].** Leads the applicant project of record, termux-monorepo: a multi-surface AI operations fleet run under an evidence discipline in which every reported result carries its receipt or is marked unverified — the direct ancestor of this proposal's receipts layer. Record includes designing and operating queue, dispatch, and scoring machinery across dozens of AI providers; shipping openly licensed infrastructure under deadline across a slate of competitive entries; and the StudySprint demonstration application line. [OWNER: select 3–5 citable outputs/public artifacts for the Supplemental CV.]

**Lead Harness Engineer — [OWNER: name or "same as PI" if a one-person technical lead; CV for Supplemental PDF].** Responsible for the task runtime, receipts layer, and provenance ledger. Fleet record: provider-agnostic dispatch across a registered field of 9,588 model endpoints with pre-flight quota verification; failure-class ledgers distinguishing credential, account, and configuration failures — the same taxonomy the harness's audit export gives districts; conformance and validator tooling for multi-developer integration.

**Evaluation Lead — [OWNER: name; may be the independent evaluator of Section 9 if structured at arm's length].** Responsible for pre-registered measures and the Design-of-Experiments discipline the fleet uses for its own selection and scoring: criteria and falsifiers declared before runs, cohorts scored against rubrics, negative results preserved in the record.

**Learning-Sciences Lead — [OPEN PLACEHOLDER — NO PERSON ON RECORD. The RFP requires named key personnel on the educational/learning-sciences side with outputs/publications, CV in the Supplemental PDF, and a commitment letter. Contemplated route per fleet record: engage a learning-sciences consultant or partner academic for the grant term, with a signed commitment letter before submission. This slot must be filled with a real, named person who has agreed to serve; it cannot be drafted around. See `c13-gaps-list.md`, item G2.]**

## 13. Capacity and commitment

[OWNER DECISION — BRACKETED, DO NOT SUBMIT AS-IS. The grant obligates the applicant to an 18-month program of work, 2027-02-01 → 2028-07-31, across three phases with public deliverables. The owner authorized drafting on 2026-11-19; the capacity commitment itself is a separate, explicit owner decision. On owner's confirmation, replace this bracket with: "The applicant commits the personnel and schedule described in Sections 6 and 12 for the full 18-month grant period, with the Project Lead accountable for phase deliverables and reporting." Until that confirmation lands, this proposal is a draft, and no submission may be made on the strength of this section.]

## 14. Budget summary

Total request: $600,000 over 18 months (Phase 1 $176,000 · Phase 2 $175,000 · Phase 3 $249,000 — Phase 3 carries the developer subawards and the independent evaluation). The full category-by-phase skeleton is in the accompanying budget workbook (`c13-budget-skeleton.xlsx`), built for transfer onto the RFP's budget template [OWNER: the RFP requires its own XLS/XLSX template — figures must be re-keyed onto that template at submission]. Personnel (technical) is the largest line at $252,000; Phase 3 developer subawards ($75,000 across at least three developers), teacher pilot honoraria ($36,000), independent evaluation ($60,000), and privacy/security and accessibility review ($33,000) are protected lines — they buy the external evidence this proposal's claims rest on.

## 15. Risks and mitigations

**Model-provider volatility.** Providers change pricing, quotas, and terms mid-stream; we know this from operating across dozens of them. Mitigation is architectural: provider-agnostic dispatch, pre-flight verification before any metered call, and task schemas that let a developer substitute models without rewriting their application.

**Teacher time.** Pilots fail when they tax the people they claim to serve. The control surface is designed for review-speed — receipts summarize before they detail — and pilot honoraria recognize teacher time as a cost, not a donation.

**Learning-sciences capacity.** The team's open gap (Section 12) is named rather than hidden: the grant budgets the role, the work plan puts learning-sciences review of interpretation and adaptation in Phase 1 before those tasks harden, and submission is blocked until the role is filled by a named, committed person.

**Adoption risk.** Infrastructure nobody adopts is a report, not a public good. Phase 3 puts at least three external developers on the harness with money, support, and a conformance suite, and publishes their friction honestly — the strongest adoption evidence a grant of this size can produce.

## 16. Sustainability

The harness is openly licensed and provider-agnostic, so its survival does not depend on this applicant's survival: any district, developer, or successor team can maintain or fork it. Within the grant, sustainability work is concrete: documentation tested by external developers, a conformance suite that lets the community verify implementations without us, and governance notes for post-grant maintenance. After the grant, the applicant's own fleet continues to run on the same receipts discipline the harness embodies, and StudySprint continues as a maintained reference implementation [OWNER: confirm post-grant maintenance commitment wording — a light commitment is fine, but it must be one the owner will actually keep].

---

**Word count (narrative body, §§1–16):** 3,684 words (final count 2026-11-19, after the §14 budget-figure alignment) — within the ≤6,000 limit, with headroom reserved for the learning-sciences citations and pilot detail that enter when the Section 12 placeholders fill.
**Bracketed placeholders:** applicant legal name · PI last name (filename) · learning-sciences lead · capacity commitment · pilot sites · developer letters · independent evaluator · privacy posture · post-grant maintenance wording.
