# `batteries_fork` integration note

- Source: `leanprover-community/batteries`
- Local fork: `timerloggedout-spec/batteries_fork`
- Submodule path: `refTemplates/smods/batteries_fork`
- Pinned revision: `36cc05ca2d0e469bfbeea9437f460e19238e885e`
- Role: Lean 4 extended-library foundation and research dependency.
- Status: governed submodule; development experiments should begin under `research/` before promotion into applied runtime paths.

## Why it is here

Batteries supplies reusable Lean data structures, tactics, lemmas, and supporting infrastructure. It can strengthen proof-oriented tooling, validation utilities, and future Lean-native components without forcing the whole monorepo to become a Lean project.

## Upstream drift

At review time, `leanprover-community/batteries` was two commits ahead of the fork, with the latest upstream commit bumping the toolchain from `v4.34.0-rc1` to `v4.34.0-rc2`. Treat the fork pin as deliberate; update it only after compatibility/build checks.

## AppliedSxi / research placement

`appliedSxi` is present in the monorepo whitelist but was not independently identifiable as a repository from the GitHub connector search. Therefore this integration does not assume it is the correct development home. Use a clearly governed `research/` location first, then promote proven artifacts to `appliedSxi` or another applied namespace once their dependency and ownership boundaries are explicit.

## Relationship to existing forks

This follows the monorepo's existing pattern of user-owned fork submodules and the governed fork inventory. It should not be duplicated as another unrestricted copy of Batteries.
