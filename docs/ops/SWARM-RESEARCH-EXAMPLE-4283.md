# SWARM RESEARCH — worked example: issue #4283, headless Android emulator smoke gate (2026-11-03)

`[MUSEai]@{role:{optimizations-assurance}}` · Tasking: main (owner order 2026-11-03) — pilot run of `docs/ops/SWARM-RESEARCH-TEMPLATE.md` · Run window: 2026-11-03 ~06:52–07:00 PT

## Preflight — leg states

| Leg | State | Evidence |
|---|---|---|
| SOFA read | **LIVE** (re-run 2026-11-03 ~07:07 PT) | `sofa.py status` verifies firsthand: agent **Muse Spark** (`a1bac8d7-d467-4c00-a04b-1501fa60beaf`, contributor, publish_directly), server-granted scopes = full 10 (read · identity · draft.read/write · write.direct/request · vote · verify · delete.own · offline_access), refresh rotates. First run (06:52 PT) found the leg DOWN (`invalid_grant`); the reconnect landed between runs — both states are on this record. |
| SOFA write | SCOPE-LIVE | write scopes granted; template discipline unchanged — ASK posts only on a genuine total miss (not triggered — see §6). |
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

## 3. SOFA search (re-run, leg LIVE)

Four atom searches (`sofa_search`) + a playbook-type search + a tag
probe (`android-virtual-device`):

| Atom query | Result |
|---|---|
| `Unknown AVD name emulator` | 1 hit — question `9d27a149` (below) |
| `ANDROID_AVD_HOME avdmanager` | same 1 hit |
| `headless android emulator CI` | ∅ on-topic (Playwright/Tauri/keyring TILs — noise) |
| `android emulator github actions avd` | same hit + 1 off-topic TIL |
| playbooks: `android emulator` | ∅ — recorded MISS |
| tag probe `avd` | ∅ — recorded MISS |

**Top candidate, read in full** (`sofa_get_post`): question
`9d27a149-0c9f-497c-85f7-1697049be9fb` — "Android Virtual Device
Creation - API 37.2 system image not showing" (by midhun-hermes;
answer trust: **not enough evidence**; its 1 reply's claims all marked
`untested`). Substance: API 37.2 is a preview SDK; Device Manager hides
preview-channel system images. **Verdict: adjacent, NOT applicable** —
our image is stable API 34, installed and visible; our failure is AVD
*discovery* (producer/consumer home divergence), a different atom. It
neither corroborates nor contradicts the fleet root cause; ranked below
fleet evidence per the template rule and set aside, not silently
dropped.

## 4. Cross-check vs our own record (the carrying leg this run)

| Candidate claim | Fleet evidence | Verdict |
|---|---|---|
| Boot failure = slow TCG/KVM starvation | emulator.log (artifacts 13238922225 + 13238697048, byte-identical tails): emulator exits at startup with `Unknown AVD name [ss-smoke]` — it never booted at all | contradicted |
| AVD creation silently failed in the install step | Job steps for run 41653198644: step 6 Install Android SDK pieces = success (avdmanager ran); the AVD exists *somewhere* — the emulator's searched homes ($ANDROID_AVD_HOME · $ANDROID_SDK_HOME/avd · $HOME/.android/avd per its own error text) do not include where avdmanager wrote it, because neither step pins ANDROID_AVD_HOME | holds — root cause |
| Bounded-wait hardening (#4344) is implicated | verdict arrived as `FAIL: no boot` inside the bound — the harness reported correctly; the failure is upstream (AVD discovery), not the waits | contradicted |
| SOFA `9d27a149`: AVD failure = preview system image not visible to the device manager | Our image is stable API 34; sdkmanager installed it and the install step succeeded; the emulator's own error names AVD *discovery*, not image visibility | does not hold here (adjacent problem) |

## 5. Synthesis — the fix candidate

| Field | Content |
|---|---|
| Fix | Pin `ANDROID_AVD_HOME=$HOME/.android/avd` in the workflow's SDK-install step before `avdmanager create avd`; persist via GITHUB_ENV so the smoke step resolves the same home; assert `ss-smoke.ini` exists + `emulator -list-avds` shows `ss-smoke` before leaving the step; harness logs `-list-avds` at the head of emulator.log |
| Provenance | Fleet: emulator.log artifacts above · workflow at master (blob read 2026-11-03) · issue #4283 comment 6606654188 (inconclusive stamp). SOFA: searched live (4 atoms + playbook + tag probes) — one adjacent hit (`9d27a149`, untested claims) read in full and set aside as not applicable; the candidate stands on fleet evidence |
| Landed as | **PR #4365 — MERGED `44a74dc0bcde`**; acceptance pair attempt 2 dispatched (stamped on #4283, comment 6606937138) |
| Verification | Attempt-2 pair: repro run 41657458297 must FAIL with the #4276 signature (`Loading your course` present / version footer missing) and green run 41657475081 must PASS with per-view captures |
| Kill signal | Either run's emulator.log shows `Unknown AVD name` again, or repro's verdict is `FAIL: no boot` — the fix is dead and the AVD-home claim reopens |

## 6. ASK draft

Not triggered — the fleet leg produced the candidate. (Had both legs
missed, the draft title stood ready: `emulator 37.2.13 — "Unknown AVD
name" for an avdmanager-created AVD in GitHub Actions — AVD home
resolution` + intake/atoms/already-tried as the body; posting gated on
write scopes.)

## Outcome stamp (attempt 2, 2026-11-03)

- **Candidate's harness half: PROVEN.** Attempt-2 emulator.log head
  shows `ss-smoke` in `-list-avds`; the emulator booted, installed, and
  captured all four views in both runs. ∅ `Unknown AVD name` — the kill
  signal did NOT fire.
- **Repro leg: exact.** Run 41657458297 → `FAIL: state never loaded
  (#4276 signature present)`, artifact 13239799783.
- **Green leg: FAILED one layer deeper.** Run 41657475081 → master
  renders the named load-failure state ("Couldn't load your course
  data"); state.json is verified inside the APK (build.sh guard) and
  the #4276 interceptor is on master — the remaining failure sits at
  the WebView fetch layer in the AOSP image's older WebView (full
  record: #4283 comment 6607425169 · #4276 comment 6607426082).
- **Cycle 2 opens** on the new atom set {file:// fetch · intercepted
  XHR · WebViewAssetLoader} — a fresh run of this template when the
  Desk/D1 route the follow-up fix; the pending owner device smoke on
  0.1.1 (modern WebView) is the deciding evidence for emulator-only vs
  device-real.
