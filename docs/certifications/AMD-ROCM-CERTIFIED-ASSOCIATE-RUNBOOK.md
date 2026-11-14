# AMD ROCm Certified Associate — preparation and evidence runbook

**Lane:** standalone AMD certification / Value lane  
**Relationship to AMD-ACADEMY-5:** separate certification; not a substitute for any of the five gate courses  
**Source checked:** 2026-11-14  
**Status:** preparation runbook only; authenticated account eligibility and enrollment are not yet verified

## 1. Official program facts

AMD's current ROCm Certified page describes the Associate credential as available and free to join through the AMD AI Developer Program. The Associate path contains five modules, module assessments, and a certification exam. Passing the exam yields a Credly digital badge and 500 AMD AI Developer Program points.

Official sources:

- https://developer.amd.com/rocm-certified/
- https://developer.amd.com/legal/rocm-certified-developer-program-agreement/

Public program availability does not establish this learner account's enrollment, eligibility, access window, module completion, exam readiness, or point credit. Verify each from the authenticated AMD account before acting.

## 2. Associate curriculum

| Module | Official title | Preparation focus |
|---|---|---|
| 1 | ROCm Orientation, Setup, and GPU Architecture Fundamentals | ROCm ecosystem, environment requirements, GPU computing foundations |
| 2 | AMD Instinct Architecture | Accelerator architecture, compute and memory concepts |
| 3 | ROCm Libraries and AI Frameworks | ROCm libraries, supported frameworks, training and inference |
| 4 | HIP Programming and CUDA Porting | HIP application development, CUDA-to-HIP migration |
| 5 | Performance Optimization and Profiling | Profiling tools, bottleneck diagnosis, kernel/memory/workload optimization |

Use the module syllabus and authorized labs as the source of truth. Keep notes and practice artifacts separate from protected assessment material.

## 3. Assessment integrity boundary — mandatory

The AMD ROCm Certified Developer Program Agreement v1.1 (effective July 2026) treats Evaluation content as confidential and prohibits unauthorized assistance, unauthorized collaboration, unauthorized materials/devices, and generative-AI tools or services during Evaluations unless AMD expressly permits them.

Therefore:

- Do not use ChatGPT, QUE, an agent, or another generative-AI service to answer, solve, submit, or replay module assessments or the certification exam unless AMD explicitly authorizes that use.
- Do not capture, store, summarize, transcribe, share, or reverse-engineer evaluation questions, tasks, item banks, scoring rubrics, or keys.
- Stop automation before a quiz, exam, scored assessment, proctored step, identity check, or other Evaluation unless the applicable AMD rule explicitly authorizes the proposed action.
- Preparation, concept explanations, public documentation research, and non-evaluative practice may proceed outside protected evaluation steps.
- If policy applicability is unclear, stop and obtain written clarification from AMD before proceeding.

This boundary takes precedence over throughput or automation goals.

## 4. Safe preparation sequence

1. Confirm AMD AI Developer Program membership and authenticated access.
2. Record account-visible access activation/expiry, timezone, and any eligibility conditions; do not infer these from public pages.
3. Confirm that ROCm Certified Associate enrollment is available in the account.
4. Review the official module syllabus and AMD's public ROCm documentation.
5. Prepare a local study environment only where the official module instructions authorize it; record OS, hardware, ROCm version, container/runtime, and reproducible setup notes.
6. Complete permitted learning and hands-on preparation independently of protected assessment steps.
7. Stop at each assessment boundary and let the candidate proceed under AMD's rules.
8. After the candidate completes a module or credential step, read the account's progress state back before recording completion.
9. After passing the final exam, verify the Credly badge and AMD account points independently.

## 5. Evidence and status model

Track the following states separately:

- `ACCESS_VERIFIED`
- `ENROLLMENT_VERIFIED`
- `MODULE_COMPLETED`
- `ASSESSMENT_COMPLETED` (status only; never retain assessment content)
- `EXAM_PASSED`
- `CREDENTIAL_ISSUED`
- `BADGE_VERIFIED`
- `POINTS_CREDITED`
- `EVIDENCE_CAPTURED`

For each module/credential, retain only permitted, non-sensitive evidence references:

- course/module identifier and official title
- authenticated account state and observation timestamp
- completion timestamp and LMS read-back reference
- certificate or badge URL and SHA-256 where issued
- redacted account points-balance screenshot reference and SHA-256
- adapter/runtime version and compliant execution receipt, if automation was used outside an Evaluation
- explicit blocker or `NOT_ESTABLISHED` where evidence is missing

Never place passwords, cookies, OTPs, session tokens, raw browser profiles, or evaluation content in GitHub, logs, or artifacts. Store screenshots and certificates in the approved evidence location; commit only non-sensitive metadata and references.

## 6. Completion criteria

The ROCm Certified Associate lane is complete only when:

1. all five modules are recorded complete in the authenticated account;
2. the certification exam is passed under AMD's rules;
3. the official Credly badge is independently verifiable;
4. the AMD account reflects the associated 500-point award; and
5. the evidence ledger contains the permitted certificate/badge and points evidence.

Course completion alone is not certification. A public landing page is not proof of account eligibility. A transcript or text summary is not a substitute for the actual account evidence.

## 7. Current blockers

- Authenticated AMD account activation and expiry timestamps: `NOT_ESTABLISHED`
- Current ROCm Associate enrollment and eligibility in the learner account: `NOT_ESTABLISHED`
- Module completion state: `NOT_ESTABLISHED`
- Exam scheduling/eligibility and any permitted AI-assistance exception: `NOT_ESTABLISHED`
- Credly badge and 500-point credit for this learner: `NOT_ESTABLISHED`

Do not mark the lane complete or schedule an exam until the account-specific checks are performed.
