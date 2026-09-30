# ArchWiz Hyper-Forge — Gemini Source Plan

**Status:** posted for collaborative review  
**Source:** Gemini-derived Hyper-Forge proposal material supplied to the project conversation  
**Implementation baseline:** PR #937, merged to `master` on 2026-09-30  
**Scope:** preserve the proposal's intent and terminology without treating unimplemented concepts as completed.

## 1. Source intent

The Gemini material describes a Termux-first **ArchWiz / Hyper-Forge** concept framed as a “PhD in Your Pocket”: a unified operator surface for research, agent dispatch, forensics, workflow construction, timeline/state exploration, documentation, promotion, and validation.

The proposal is not a single replacement application. It composes existing repository capabilities behind a coherent cockpit and identifies a future native Android presentation with four primary tabs:

1. **Swarm Dispatch**
2. **Forensics & RECON**
3. **Pipeline & CI**
4. **Metrics & Live**

The source material also names Foresight and ChronoMancer as important conceptual subsystems.

## 2. Source cockpit matrix

The Gemini material enumerates a 20-operation cockpit. The current implementation is a repository-grounded recomposition of that idea; the exact legacy numbering is not treated as canonical.

| Source operation | Intent |
|---|---|
| 1 | Autonomous dispatch |
| 2 | Archaeology / deep RECON |
| 3 / 3.5 | Agent shell |
| 4 | Live metrics |
| 5 | Backup |
| 6 | Ecosystem refresh |
| 7 | Profile manager |
| 8 | Task/workflow builder |
| 9 | Timeline editor |
| 10 | Workflow builder / health-oriented workflow surface |
| 11 | Restore |
| 12 | Health |
| 13 | Session pipeline |
| 14 | Activity feed |
| 15 | Lexicon harvest |
| 16 | Live view |
| 17 | Forensic toolchain |
| 18 | Docs pipeline |
| 19 | Promote sandbox |
| 20 | Dual-gate CI |

### Important normalization

The source material contains some numbering variation between versions of the Gemini discussion. Therefore this document preserves the **capabilities**, not a false claim that every historical list used identical numbering.

## 3. Source architectural concepts

### Foresight

The proposal identifies `foresight_collect.py` and `foresight_state.json` as the Foresight collection/state surface.

Intent:

```text
RECON / INDEX
     ↓
FORESIGHT
impact / context
     ↓
time-aware planning + bounded dispatch
```

### ChronoMancer

The proposal identifies `timeline_editor.py` and the session store / ChronoMancer logic as the time-aware editing and fork surface.

Intent:

- inspect historical/session state
- edit or branch timeline-oriented state
- feed bounded work into dispatch
- preserve evidence through validation

### Governance and gates

The proposal references repository governance such as:

- `CLAUDE.md`
- `docs/proposals/registry.yaml`
- `docs/ARCHW1Z-GATE.md`
- `docs/icm/CLAUDE.md`

and the dual validation commands:

```bash
python3 scripts/ci/repo_gate.py --base origin/master
python3 scripts/ci/termux_smoke.py
```

The gates remain correctness evidence; they are not replaced by cockpit presentation.

## 4. Source Android direction

The proposal calls for four native Android tabs:

```text
┌───────────────────────────────────────────┐
│ SWARM │ FORENSICS │ PIPELINE │ METRICS   │
└───────────────────────────────────────────┘
```

This is a **future native presentation target**. The merged Termux cockpit is not represented as a native Android application.

## 5. Source operating model

The source material repeatedly converges on a loop in which observation precedes promotion:

```text
RECON
 → PLAN / MEASURE
 → ACT
 → COMMIT
 → WAIT
 → WATCH
 → VALIDATE
 → RE-FETCH
 → COMPARE
 → CLASSIFY
 → RECORD
 → REPEAT
```

This is compatible with the repository's evidence-first operating model.

## 6. Source boundaries

The Gemini proposal is a design source, not an execution receipt. This plan therefore distinguishes:

- **source requirement** — what the Gemini material proposed
- **implementation** — what is actually present in the repository
- **derived engineering decomposition** — how this project organizes remaining work
- **evidence** — repository/GitHub state that proves an implementation exists

No unimplemented Gemini concept is silently promoted to “done.”
