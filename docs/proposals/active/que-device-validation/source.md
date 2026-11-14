# Source and RECON Record — QUE Device Validation

**Observed:** 2026-11-14  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Working branch:** `feat/que-device-capability-registry-20261114`

## Primary repository evidence

| Source | Verified finding | Confidence |
|---|---|---|
| `CLAUDE.md` | `master` is the integration target; proposal registry/items authorize work; dual gates are repo-gate + termux-smoke; agents execute to completion when evidence gates pass. | Verified |
| `docs/proposals/PROCESS.md` | Proposal lifecycle is ingest → register → itemize → review → execute → close; P0 requires second mind or Operator. | Verified |
| `docs/proposals/AGENTIC-PERMISSIONS.md` | Workflow YAML writes may require Operator PAT/custom GitHub App with Workflows write; first-time permissions remain human edge. | Verified |
| `ops/que/README.md` | QUE feeds are a producer/served-state projection; queue state and transition events are recorded; this feed collector is not evidence of an emulator fleet. | Verified |
| `docs/ops/DOE-FAMILY.md` | DoE is a family; one dispatched/executed run = one experiment observation; campaign and component evaluations remain separate. | Verified |
| `docs/ops/corpus/EXPERIMENT.schema.json` | Existing experiment record schema is shared across DoE family. | Verified |
| `docs/ops/EVIDENCE-ENVELOPE.schema.json` | Canonical SHA-bound evidence envelope exists and must be reused. | Verified |
| `docs/architecture/INFRASTRUCTURE-REGISTRY-DESIGN.md` | IDRR indexes/reconciles existing authorities and must not become a second database, scheduler, poller or telemetry ledger. | Verified |
| `docs/integrations/README.md` + `registry.json` | Integration Intelligence already separates discovery, session availability, repository adapter implementation, end-to-end validation and promotion. | Verified |
| `apps/studysprint/android/emulator-smoke.sh` | A headless Android AVD smoke gate exists for the StudySprint APK. | Verified |
| `.github/workflows/studysprint-apk-smoke.yml` | A workflow provisions Android API 34 x86_64 AVD and runs the APK smoke harness. | Verified |
| `scripts/ci/termux_smoke.py` + `docs/TERMUX-SMOKE.md` | A stdlib Termux/runtime-surface smoke gate exists; it is not full Android device parity. | Verified |
| `docs/recon/team-formation/GAME_PLAYER_FLEET.md` | Machine profiles are described as managed capabilities with version, hardware class, limits, reset procedure and evidence policy. | Verified |
| `docs/icm/objects/platform/termux-agentic-hub.md` | Historical Termux Agentic Hub architecture is marked stale/ghost; live device/MCP/worker availability must not be inferred. | Verified |

## External and prior issue context

- Issue #55, “Testing Environment Termux Sandbox Setup & Scripts”, is the existing Termux sandbox research/intake anchor. It identifies Termux Docker, Waydroid, Android Studio AVD and QEMU as different candidate environments; their present availability is not established by that issue.
- Android AVD, QEMU, Waydroid and Termux Docker are distinct backend classes. Android Emulator is not synonymous with a general QEMU system-emulation deployment.
- Existing StudySprint AVD validation is a concrete precedent, not proof that all Android APIs or hardware surfaces are emulated.

## Important unknowns

- No current live Android/Termux device session was available to this RECON.
- No fleet-wide emulator capacity, installed QEMU/Waydroid/Termux-Docker inventory, device inventory, or live runner health is established here.
- The complete set of device-dependent modules has not yet been exhaustively enumerated.
- Existing QUE feed artifacts establish observed workflow queue/transition data, not device-lab machine inventory or a generic device task-dispatch API.

## Method

Classify claims as:
- **verified** — directly supported by current repository source or a concrete workflow/script;
- **candidate** — named in a proposal, issue, external catalog or research source, but not runtime-verified;
- **unknown** — no adequate evidence;
- **contradicted/stale** — current canonical source explicitly supersedes or rejects the assumption.

Future RECON must re-fetch the source and record source SHA, retrieval time, exact evidence location, environment fingerprint and confidence. A stale snapshot is never copied forward as a current availability claim.
