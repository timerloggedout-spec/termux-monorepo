# SWARM RESEARCH — worked example: issue #4283, headless Android emulator smoke gate (2026-11-03)

`[MUSEai]@{role:{optimizations-assurance}}` · Tasking: main (owner order 2026-11-03) — pilot run of `docs/ops/SWARM-RESEARCH-TEMPLATE.md` · Run window: 2026-11-03 ~06:52–07:00 PT

## Preflight — leg states

| Leg | State | Evidence |
|---|---|---|
| SOFA read | **DOWN — NOT_ESTABLISHED** | `sofa.py status` → token refresh `{'error': 'invalid_grant'}` (2026-11-03, this run). Re-consent with write scopes in flight at Connectors Inventory. ∅ SOFA results claimed anywhere below. |
| SOFA write | GATED | scopes not widened; ASK = text only (not triggered — see §6). |
| Fleet record | LIVE | PAT API + run artifacts, refs inline. |

## 1. Intake

| Field | Content |
|---|---|
| Issue | termux-monorepo #4283 — headless emulator smoke gate for the StudySprint APK (assert the #4276 state-loaded signals pre-device) |
| Statement | CI acceptance pair: the 0.1.0 build must FAIL with the #4276 signature; master must PASS. Attempt 1 pair both ended `FAIL: no boot`. |
| Environment | GitHub ubuntu-latest (KVM via udev rule) · emulator 37.2.13 · system image android-34 default x86_64 · AVD `ss-smoke` created by avdmanager in the SDK-install step · local VM lane: ∅ /dev/kvm (TCG boots never completed — execution home = Actions, ruled) |
| Already tried | local TCG boots, 2 images, ~20–40 min, ∅ boot_completed · CI wedged pair 41649866732/41650341849 (unbounded adb waits → cancelled → hardening PR #4344 merged `667c4001884d`) · CI pair attempt 1: 41653154949 (repro) + 41653198644 (green), both `FAIL: no boot` |

## 2. Atoms

- `"Unknown AVD name [ss-smoke]"` (verbatim from emulator.log, both artifacts)
- `avdmanager create avd` × `emulator -avd` — producer/consumer surface pair
- `ANDROID_AVD_HOME` / AVD search-path divergence (constraint class: AVD provisioning in CI)
- `sys.boot_completed` headless boot (ruled out as the failure — the emulator never started)

## 3. SOFA search

NOT_ESTABLISHED — read leg down at preflight (invalid_grant). No hits
claimed, no rankings inferred. This section populates on the re-run after
the Connectors Inventory re-consent lands; the pilot target stays this
issue class per the tasking.

## 4. Cross-check vs our own record (the carrying leg this run)

| Candidate claim | Fleet evidence | Verdict |
|---|---|---|
| Boot failure = slow TCG/KVM starvation | emulator.log (artifacts 13238922225 + 13238697048, byte-identical tails): emulator exits at startup with `Unknown AVD name [ss-smoke]` — it never booted at all | contradicted |
| AVD creation silently failed in the install step | Job steps for run 41653198644: step 6 Install Android SDK pieces = success (avdmanager ran); the AVD exists *somewhere* — the emulator's searched homes ($ANDROID_AVD_HOME · $ANDROID_SDK_HOME/avd · $HOME/.android/avd per its own error text) do not include where avdmanager wrote it, because neither step pins ANDROID_AVD_HOME | holds — root cause |
| Bounded-wait hardening (#4344) is implicated | verdict arrived as `FAIL: no boot` inside the bound — the harness reported correctly; the failure is upstream (AVD discovery), not the waits | contradicted |

## 5. Synthesis — the fix candidate

| Field | Content |
|---|---|
| Fix | Pin `ANDROID_AVD_HOME=$HOME/.android/avd` in the workflow's SDK-install step before `avdmanager create avd`; persist via GITHUB_ENV so the smoke step resolves the same home; assert `ss-smoke.ini` exists + `emulator -list-avds` shows `ss-smoke` before leaving the step; harness logs `-list-avds` at the head of emulator.log |
| Provenance | Fleet: emulator.log artifacts above · workflow at master (blob read 2026-11-03) · issue #4283 comment 6606654188 (inconclusive stamp). SOFA: NOT_ESTABLISHED (leg down) |
| Landed as | **PR #4365 — MERGED `44a74dc0bcde`**; acceptance pair attempt 2 dispatched (stamped on #4283, comment 6606937138) |
| Verification | Attempt-2 pair: repro run 41657458297 must FAIL with the #4276 signature (`Loading your course` present / version footer missing) and green run 41657475081 must PASS with per-view captures |
| Kill signal | Either run's emulator.log shows `Unknown AVD name` again, or repro's verdict is `FAIL: no boot` — the fix is dead and the AVD-home claim reopens |

## 6. ASK draft

Not triggered — the fleet leg produced the candidate. (Had both legs
missed, the draft title stood ready: `emulator 37.2.13 — "Unknown AVD
name" for an avdmanager-created AVD in GitHub Actions — AVD home
resolution` + intake/atoms/already-tried as the body; posting gated on
write scopes.)

## Outcome stamp

PENDING — attempt-2 verdicts stamp on #4283 at completion; this record
updates with the result + whether the kill signal fired.
