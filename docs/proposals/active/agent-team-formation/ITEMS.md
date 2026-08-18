# ITEMS — agent-team-formation

| ID | Item | Priority | Status | Owner | Evidence of completion | Dependencies |
|---|---|---|---|---|---|---|
| ATF-01 | Confirm the canonical team names, role map, and protected-role list in `TEAM_CHARTER.md`. | P1 | draft | Operator + Orchestration | Recorded Operator review and independent reviewer response in `MANIFEST.md`. | None |
| ATF-02 | Define a versioned role-score event schema with raw evidence links, confidence, verdict, and invalidation support. | P1 | proposed | Orchestration + Research | Schema document, sample events for research/dev/CI, and reviewer validation. | ATF-01 |
| ATF-03 | Reconcile MoneyBall implementation state: lane SSOT says PR #131 is merged while live PR metadata reports it open and dirty. | P0 | proposed | Delivery Reliability + Orchestration | Written disposition naming the authoritative implementation revision and corrective update to the stale record. | ATF-01 |
| ATF-04 | Refactor routing so role-specific scores plus shared safety floor drive eligibility; retain aggregate ELO/3L0 only as a traceable display signal. | P1 | blocked | Development + Orchestration | Tests show cross-role scores do not grant eligibility and low-confidence candidates are not auto-preferred. | ATF-02, ATF-03, accepted proposal |
| ATF-05 | Add protected-role, dry-run, minimum-sample, and reversible-deactivation controls before any score-driven cull or clone automation. | P0 | blocked | Development + Security Assurance | Tests covering every control; independent security review; Operator approval for policy thresholds. | ATF-02, ATF-03, accepted proposal |
| ATF-06 | Establish the Authorized Mobile Analysis intake record and artifact-provenance template for issue #236 and future Android work. | P1 | proposed | Authorized Mobile Analysis + Security Assurance | Template accepted; one sandbox-only, explicitly authorized dry-run intake completed or documented as blocked. | ATF-01 |
| ATF-07 | Create game QA intake and test-report templates limited to owned, open-source, or expressly authorized builds. | P2 | proposed | Game QA & Accessibility | Template includes build identity, authorization, environment, reproducible steps, and accessibility observations. | ATF-01 |
| ATF-08 | Create an evidence-only weekly roster calibration report; do not schedule automated roster mutations. | P2 | blocked | Orchestration + Delivery Reliability | Report generator validates inputs, omits secrets, and has a dry-run test. | ATF-02, ATF-03, ATF-05 |
| ATF-09 | Restore or explicitly replace the required `master-staging` integration branch path before implementation work opens. | P0 | blocked | Operator + Delivery Reliability | Branch policy or documented replacement approved by Operator and reflected in repository instructions. | None |
| ATF-10 | Reconcile the documented Termux smoke gate with the current repository contents; the referenced `scripts/ci/termux_smoke.py` is absent from the inspected branch. | P0 | blocked | Delivery Reliability + Operator | Restored or replaced gate with documented invocation and a successful verification run. | ATF-09 |

## Implementation constraints

ATF-04, ATF-05, and ATF-08 are implementation items. They require this proposal to be accepted, a clean integration base, a separate worktree, focused tests, and both repository gates. ATF-03, ATF-09, and ATF-10 are blocking disposition work; they must be resolved before presenting a roster change as merge-ready.

The reverse-engineering and red-team labels in issue #236 are routed only to the charter's **Authorized Mobile Analysis & Forensics** and **Security Assurance / Authorized Red Team** teams. The following work is excluded from every item in this proposal: cracking, warez, DRM or anti-cheat bypass, account compromise, credential extraction, malware, persistence, phishing, exploitation of third parties, or real-money betting.
