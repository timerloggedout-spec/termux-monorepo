# Mobile Agent Testers — Integration Runbook

## Purpose

[Mobile Agent Testers](https://github.com/timerloggedout-spec/mobile-agent-testers_fork) adds parallel, persona-driven exploratory QA on hosted Android emulators and iOS simulators. The Termux monorepo already has three complementary surfaces:

| Surface | Role | Authority |
|---|---|---|
| StudySprint android/emulator-smoke.sh | Deterministic Android install, launch, navigation captures, and state-render assertions | Existing regression gate |
| Mobile Agent Testers | Exploratory persona journeys, accessibility/layout observations, bug reproduction | Advisory finding source |
| Termux device registry + pull queue | Persistent physical-device task admission, leases, receipts, and telemetry | Existing physical-device control plane |

The providers stay separate. Findings converge through the existing Integration Intelligence event schema; the adapter does not create another scheduler or control devices.

## Verified provider contract

The inspected agent-testers.yml exposes these inputs:

- source_repo, ref
- app_dir, app_id, framework
- android_personas, ios_personas
- android_build, apk_path
- brief, bug_report, model, record_video

The workflow builds an APK, encrypts it, fans out one emulator per persona, blocks configured analytics hosts, encrypts persona reports, and uploads encrypted artifacts. The fork's scripts/collect.sh downloads and decrypts on the operator's machine using a private key held under ~/.mobile-agent-testers/.

Provider findings are model-generated observations. The provider's duplicate grouping is a hypothesis; retain each persona's finding provenance and reproduce candidates before treating them as confirmed defects.

## StudySprint pilot

StudySprint Android package: org.timerloggedout.studysprint.

The app uses a native Android WebView shell with a bundled web surface. The inspected app tree exposes Today, Plan, Reviews, and Reader. The inspected StudySprint target is Android-only; skip iOS personas for this pilot.

### Build inputs

Run the provider workflow in timerloggedout-spec/mobile-agent-testers_fork. The canonical brief is apps/studysprint/AGENT_BRIEF.md; its fork mirror is proposed in [PR #1](https://github.com/timerloggedout-spec/mobile-agent-testers_fork/pull/1). Until that brief lands on main, select its branch with the workflow dispatch ref shown below.

| Input | Pilot value |
|---|---|
| source_repo | timerloggedout-spec/termux-monorepo |
| ref | Immutable commit SHA under test |
| app_dir | apps/studysprint |
| app_id | org.timerloggedout.studysprint |
| framework | native |
| android_personas | Start with anna,malik; expand after reviewing first run |
| ios_personas | none |
| brief | briefs/studysprint.md |
| android_build | Custom SDK-direct build command below |
| apk_path | android/studysprint.apk |

The custom build runs from app_dir; android/build.sh changes into its own directory and produces android/studysprint.apk. The SDK-direct build requires JDK 17, Android platform 34, build-tools 34.0.0, and Python 3. The hosted runner must expose ANDROID_HOME or ANDROID_SDK_ROOT and cmdline-tools/sdkmanager; install the pinned SDK components before invoking the build. The committed StudySprint development keystore is a development identity only; production signing credentials stay outside this workflow.

Use this custom android_build command:

~~~bash
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses >/dev/null 2>&1 || true
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" "platforms;android-34" "build-tools;34.0.0"
bash android/build.sh
~~~

The external workflow input values are public run metadata. Put credentials and private build arguments in the provider repository's supported Actions secrets. Use synthetic learner content and test-only accounts.

### Recommended staged persona matrix

1. anna + malik: large text/light mode and fast dark-mode navigation.
2. grace + layla: 200% font and Arabic RTL after the app's localization support is confirmed.
3. lucia + kenji: tablet layout and Japanese locale after the first batches are reviewed.

The provider's persona library includes device/OS profiles that may fall back to Pixel 6 when a named AVD profile is unavailable. Treat the actual device profile in the collected report as the evidence, not the requested persona label.

### Suggested test objectives

- First launch and state hydration; verify the footer version and absence of a persistent loading state.
- Navigate Today → Plan → Reviews → Reader and return.
- Create or edit only synthetic study content; test persistence after background/resume and relaunch.
- Check keyboard overlap, large text, contrast, small-screen reachability, empty states, and accessibility labels.
- Verify Reader text flow and review-state feedback.
- Record locale/RTL observations only where the app declares support.

## Invocation

From a machine with gh authenticated to the tester fork:

~~~bash
gh workflow run agent-testers.yml \
  --repo timerloggedout-spec/mobile-agent-testers_fork \
  -f source_repo=timerloggedout-spec/termux-monorepo \
  -f ref=<immutable-termux-commit-sha> \
  -f app_dir=apps/studysprint \
  -f app_id=org.timerloggedout.studysprint \
  -f framework=native \
  -f android_personas=anna,malik \
  -f ios_personas=none \
  -f brief=briefs/studysprint.md \
  -f android_build='export ANDROID_SDK_ROOT="$ANDROID_HOME"; export ANDROID_HOME="$ANDROID_SDK_ROOT"; yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses >/dev/null 2>&1 || true; "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" "platforms;android-34" "build-tools;34.0.0"; bash android/build.sh' \
  -f apk_path=android/studysprint.apk
~~~

A provider run consumes model credits. Record the approved spend ceiling and model before dispatch. Start with two Android personas and increase only when the first run's cost and signal quality are reviewed.

## Trusted evidence collection

1. Fetch the completed provider run ID.
2. On the trusted local workstation, run the fork's bash scripts/collect.sh <run-id>.
3. Keep the private key and decrypted run directory local and access-controlled.
4. Normalize findings with the adapter below; output is metadata-only JSONL.
5. Review each event against source screenshots locally; confirm or reject findings.
6. Reproduce confirmed candidates with apps/studysprint/android/emulator-smoke.sh or a targeted deterministic regression test.
7. Feed confirmed regression evidence into the existing repo PR and dual-gate lifecycle.

Example:

~~~bash
python3 scripts/integrations/mobile_agent_testers_adapter.py \
  --run-dir runs/<run-id> \
  --run-id <run-id> \
  --repository timerloggedout-spec/termux-monorepo \
  --commit <tested-commit-sha> \
  --output mobile-agent-testers.jsonl
~~~

The adapter reads */results/*/findings.json. It emits one event per issue with a stable event ID and idempotency key. It stores a SHA-256 digest reference to each source findings file and excludes raw report text, screenshots, transcript content, email addresses, phone numbers, and token-shaped strings from event output.

## Security and cost

- Keep the provider's RSA private key on the trusted collector only.
- Keep Claude/API credentials in the provider's secret store; keep them out of command-line arguments and run metadata.
- Use the provider's analytics host blocklist and synthetic app data.
- Public GitHub Actions logs/artifacts are public surfaces; rely on the provider's encryption flow and verify every artifact name/status.
- Set a per-run model budget and a small persona batch.
- Do not dispatch paid runs automatically from pull-request events.
- Do not connect this provider to the Termux physical-device queue. Physical-device tasks remain allowlisted and lease/receipt controlled.

## Failure and triage

| Condition | Handling |
|---|---|
| APK build fails | Inspect encrypted build log on trusted collector; preserve deterministic emulator lane |
| AVD profile unavailable | Record fallback profile from result metadata |
| Persona auth/model failure | Mark run incomplete; do not treat missing findings as clean |
| Empty or malformed findings | Adapter skips malformed files and reports diagnostics to stderr |
| AI-only observation | Keep validation_status=pending; human/deterministic reproduction required |
| Confirmed regression | Add deterministic regression test, then rerun emulator and repository gates |

## Lifecycle

DISCOVERED → repo_adapter_implemented → provider_run_pending → collected → observed → reproduced → validated → promoted

Current state: MAT-001 implementation in progress; StudySprint brief PR #1 is open on the tester fork. Provider authentication, budget, first run, and end-to-end validation remain separate evidence-bearing steps. Provider authentication, budget, first run, and end-to-end validation remain separate evidence-bearing steps.
