# Demo script — under 3 minutes

Run `demo.py` on screen; it executes offline against the sample
syllabus in `examples/`.

**0:00 — The problem (30s).** "First-gen students get a syllabus PDF
and no map. StudySprint turns a verified syllabus into a week-by-week
plan. It inherits the Delphi Oracle evidence gate from our D0 entry:
it never plans from a claim — only from a fetched syllabus."

**0:30 — Scenario 1: asserted only (30s).** "The student asserts the
topics. No file named, nothing fetched. The gate abstains: an
assertion is not a syllabus."

**1:00 — Scenario 2: fetched syllabus (70s).** "The syllabus file is
named. fetch_study_evidence stamps every week with provenance, a
freshness window, and a hash. The gate allows — and StudySprint builds
the plan (learn + retrieve per topic), a week-1 recall quiz, and a
re-plan that carries missed week 1 into week 2."

**2:10 — Scenario 3: the class rule (30s).** "A credential-mutation
request, evidence fetched and material — still ESCALATE. Evidence
never outranks the action class."

**2:40 — Close (20s).** "One evidence gate, one new study-evidence
tool, a plan a student can trust. Built with the Strands Agents SDK;
this recording runs the identical gate locally — receipts on screen,
no deployment claimed beyond them."
