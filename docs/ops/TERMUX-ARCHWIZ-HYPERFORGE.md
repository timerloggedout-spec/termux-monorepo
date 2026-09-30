# ArchWiz Termux Hyper-Forge

**Status:** implemented as a Termux-first operator surface.

## Purpose

This lane turns the existing ArchWiz primitives into one dependency-free ANSI/TUI cockpit without creating a second orchestration protocol.

The Hyper-Forge surface is an adapter over existing repository-owned tools:

- archwiz/archwiz.py — established cockpit
- workspace/llm_map/foresight_collect.py — Foresight aggregation
- harmony_hub/workspace/agent/chronomancer.py — time-loop/fork logic
- scripts/ci/repo_gate.py — repository gate
- scripts/ci/termux_smoke.py — Termux smoke gate

Canonical state remains in source files, protocol objects, GitHub, and validation evidence. The visual layer is never authoritative.

## Launch

From the repository root on Termux:

    python3 archwiz/termux_cockpit.py

Optional Tron-inspired display mode:

    ARCHWIZ_THEME=tron python3 archwiz/termux_cockpit.py

No third-party Python package is required.

## Cockpit matrix

The 20 slots are an operator navigation matrix, not a claim that every historical menu item is present under exactly that number in every legacy ArchWiz build.

| Surface | Existing implementation |
|---|---|
| Dispatch | archwiz/autonomous_runner.py |
| RECON | archwiz/archaeo_sweep.py |
| Foresight | workspace/llm_map/foresight_collect.py |
| ChronoMancer | archwiz/timeline_editor.py + harmony_hub/workspace/agent/chronomancer.py |
| Forensics | existing ArchWiz forensic helpers when present |
| Promotion | workspace/llm_map/promote_workspace.py |
| Governance | scripts/ci/repo_gate.py + scripts/ci/termux_smoke.py |

Unavailable optional helpers are treated as not installed, not silently fabricated.

## Tron visual contract

The theme is intentionally terminal-native:

- ANSI only; no GUI toolkit dependency.
- High-contrast cyan/green/amber status vocabulary.
- Fixed-width panels that degrade cleanly on small Termux displays.
- ARCHWIZ_THEME controls the display mode.
- No network access is introduced by the theme.
- No credentials, prompts, or model output are embedded in the UI source.

The aesthetic is a presentation layer. It does not alter execution authority, routing semantics, evidence schemas, or promotion policy.

## Foresight + ChronoMancer

The two concepts are deliberately composed rather than duplicated:

    RECON / INDEX
         |
         v
      FORESIGHT
      impact/context
         |
         +--------------------+
         |                    |
         v                    v
     CHRONOMANCER          DISPATCH
     time-aware fork       bounded task
         |                    |
         +---------+----------+
                   v
              VALIDATION
           repo-gate + smoke
                   |
                   v
                RECORD

Foresight is an impact/context surface. ChronoMancer is a time-aware session/fork surface. Neither is a substitute for correctness validation.

## README imagery

Visual header assets are treated as seed art, not runtime evidence. A generated or uploaded image must not be described as showing live branch counts, CI state, or repository telemetry unless the artifact is actually generated from a verified snapshot.

This keeps the cinematic/Tron direction compatible with the repository's evidence-first operating rules.
