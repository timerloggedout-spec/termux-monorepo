# Device-offline hold and non-device work continuation

**Status:** HOLD — device-dependent ChronoMancer execution is paused by operator direction  
**As of:** 2026-11-11  
**Scope:** Termux environment on the physical device, ADB transport, screen/display and device-network reliability.

## Operator-provided condition

The Termux environment on the device contains the components required to use and test ChronoMancer. The device is currently unavailable because of a broken screen and unreliable ADB/network connectivity. The operator explicitly directed: **HOLD**.

This is an availability constraint, not evidence that ChronoMancer or its Termux components are defective.

## Hold boundary

Until the operator explicitly resumes device work:

- Do not initiate ADB sessions, reconnect loops, remote shell commands, device-side installs, device-side tests, or device state mutations.
- Do not ask automation to keep retrying a failing device transport.
- Do not substitute a remote Linux runner or GitHub Actions job and describe it as a Termux-on-device test.
- Do not classify the lack of device evidence as a test failure or a pass.
- Preserve the current device state; do not attempt repair, flashing, reset, or recovery actions.

The hold applies to physical-device-dependent ChronoMancer execution and validation. It does **not** block independent documentation, schema design, GitHub-hosted research, non-device control-plane work, review, or repository CI that does not claim device equivalence.

## Evidence classification

| Evidence source | Permitted while held | What it proves |
|---|---|---|
| GitHub source inspection | Yes | What the checked-in source declares/implements at the inspected SHA |
| Documentation and schema review | Yes | Contract consistency and documentation completeness |
| GitHub Actions on hosted runners | Yes | Results for the exact workflow, runner, environment and SHA shown |
| Static/unit tests on a non-Termux host | Only if independently runnable and explicitly labelled | Host-specific behavior, not Android/Termux compatibility |
| Termux on the physical device | No | No new device evidence until resumed |
| ADB transport and screen/network diagnostics | No | No current device-health conclusion |

Record unavailable device validation as `NOT_RUN_DEVICE_HOLD`, not `FAIL`, `PASS`, or generic `UNKNOWN`. Preserve the reason and the date of the hold.

## Work that continues

1. Complete the architecture and ownership contracts for Foresight, HyperForge, Workflow Controls, Admin Web, Admin Graph, Collaborator Management, FireSight and release management.
2. Define machine-readable contracts and validation fixtures that do not require the device.
3. Review GitHub Actions and repository evidence on their actual candidate SHAs.
4. Keep device-specific acceptance criteria visible and unfulfilled until physical-device testing resumes.
5. Continue documentation, review, and independent component design without changing the held ChronoMancer execution boundary.

## Resume criteria

Device work may resume only after the operator explicitly lifts the hold and confirms a viable access path. At that point, first perform a non-mutating connectivity/availability check, record device/OS/Termux/runtime identity, and agree on the exact test scope before any state-changing operation.

A device test receipt must identify device/runtime, command, source SHA, start/end time, exit status, captured output, and any transport interruptions. A disconnected test is `INTERRUPTED`, not a product failure.

## Relationship to current ChronoMancer work

- The session-scoped fork-selection change is tracked separately in PR #5169.
- The integrated architecture plan is tracked in PR #5168.
- This document does not authorize merging, device execution, campaign dispatch, or promotion.
- The preregistered `cb-1-chronomancer-emission` campaign remains subject to its own explicit `doe-expert` approval and two-file allowed-path contract.

## Operator rule

**HOLD is a scoped execution boundary, not a repository-wide stop signal.** Continue all independent work that can be done safely and evidenced without the unavailable device.
