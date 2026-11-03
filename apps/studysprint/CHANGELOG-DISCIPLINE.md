# StudySprint — CHANGELOG discipline (all surfaces)

One changelog of record: `apps/studysprint/CHANGELOG.md`.
Every surface and the foundation write into it; there are no
per-surface changelog files, so a reader (or a judge) gets the
whole project's history in one scroll. This doc is the
convention; the file conforms as of app-package D (#4439).

## Structure

- `## [Unreleased]` at the top, always present. Everything
  not yet cut accumulates here.
- Inside Unreleased, one `###` section per work batch, newest
  first. A batch PR **carries its own section**; when batch
  PRs merge sequentially, the merger keeps all sections
  (never squash two batches into one heading).
- At a release cut, the cut's sections move under a versioned
  heading (`## [X.Y.Z] — date`) and a fresh empty Unreleased
  stays on top.

## Section naming — the version lines stay separate

- `### Surfaces X.Y.Z (…)` — a surfaces batch. Surfaces
  version independently of the foundation (owner ruling,
  2026-11-03): webApp/APK/TUI share one surfaces line, bumped
  together, MINOR per parity iteration, PATCH per fix batch.
- `### Foundation vX.Y.Z (…)` — a core batch (the study
  engine: pipeline, SR, calendar/geo, hardening). The
  foundation line carries the road to v1.0.0 at the D1
  submission; post-1.0.0 it is PATCH-only.
- `### App-package <letter> — <name> (#issue)` — the
  app-package checklist batches (A packaging · B PWA ·
  C release trust · D docs/budgets · E first-run). These fold
  into the next surfaces version; they never bump a version
  by themselves.

## Entry style

- One bullet per landed change, written for a user/reader:
  what changed and why it matters, with the mechanism named
  in one clause. Defects fixed say what the defect WAS.
- Honest edges are entries too: a capability stated absent,
  a budget watch item, a known artifact — if it ships, it is
  written. Nothing is silently dropped from a section when
  sections combine.
- Evidence and parity claims in a PR body must match what
  the section says; the section is the durable copy.

## Conformance (checked at #4439)

The in-tree CHANGELOG follows this discipline: single file ·
Unreleased on top · Surfaces 0.1.1 → 0.2.0 and App-package
A–D sections present in merge order · foundation releases
versioned below. Deviations found at the check: none
structural; the Surfaces 0.1.3 section predates the naming
convention's parenthetical and is left as history (history
is not rewritten to match a later convention).
