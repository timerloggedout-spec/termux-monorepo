# Contributing to StudySprint

## Developing — run from source (the developer route)

End users install the TUI with the pipx one-liner in
[TUI.md](TUI.md). To hack on it, run from a clone:

```
git clone https://github.com/timerloggedout-spec/studysprint.git && cd studysprint && pip install textual fsrs genanki && python3 tui.py
```

(Verified verbatim from a clean environment 2026-11-03: fresh clone
→ deps → the TUI boots to the Today screen. Already cloned? Just
`pip install textual fsrs genanki && python3 tui.py` from the repo
root.)

The test suite: `python3 -m pytest tests/`. The installable
distribution (`pyproject.toml`) covers the TUI surface and the
core modules it imports; the core CLI (`agent.py` / `demo.py`)
runs from the clone only — it resolves a vendored oracle from the
repo tree by design.

## Building the APK — signing (read this first)

Every APK build signs with the project's committed DEV keystore:

- **Key:** `android/keystore/studysprint-dev.keystore` — it is in this
  tree; build with the key that is here, never a substitute.
- **Alias:** `studysprint` · **Password:** `android`
- **Build + sign:** `bash android/build.sh` (JDK 17 + Android SDK
  platform android-34 / build-tools 34.0.0 + python3). The script
  builds and signs in one pass and fails loudly if the keystore is
  missing — treat that as a stop.

**The one rule: all builds sign with this key.** Android refuses an
update signed by a different key over an existing install, so a build
signed any other way silently breaks updates for every installed copy.

**Scope:** this is a DEV key for sideload distribution only — never a
store or production key.

Full details (certificate fingerprint, rotation procedure):
[APK.md](APK.md), "Signing — the project key", and the note beside the
key at `android/keystore/README.md`.
