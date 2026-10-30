# Repo Replay — import{methods} (consumer record)

[MUSEai]@{role:{repo-replay}}

The **repo-replay system is owned by its own repo**:
<https://github.com/timerloggedout-spec/repo-replay> (spec `replay-store/v1`,
engine **RevWright**). This monorepo does NOT contain the system. It
**imports its methods by reference** and serves as a consumer + test subject.
Clear distinction, by owner order (2026-10-29): owner-original concept and
code, zero external integrations.

## Imported methods (from repo-replay `METHODS.md`)

`extract` · `build_index` · `compose` · `replay` · `verify` · `fill_gap` ·
`jit_resolve` · `edit` — machine-readable import: `config/repo-replay-import.json`.

## Model (summary; canonical text lives in repo-replay)

- Source of truth = the owner's session-chat code exports. Session Provenance
  Code Extractions alone can build the entire repo.
- A file = a **recipe**: ordered pointers `(session,msg,blk,hash)` + ops
  (`customize` ref, `before|after|{around && in}`, up to full refactor).
  Pointer-only authorship is valid; aggregates may mix pointers from
  responses that edited the same or different files (original path =
  metadata, not constraint).
- Index = one structure, two directions: forward provenance->object,
  reverse `hash->[pointer...]` (1:N).
- History = repo-replay's own DAG (recipe hash + parents + op log); blame
  is intrinsic. Not git history.
- Signal channel (`signal/v1`): `cmd` outputs embedded in session exports
  (`tree`, `ls -laR`, search results, exclusion lists, `bin`/`alias`/`PATH`)
  act as the expected-tree oracle and env clues — evidence, never content.

## This repo's roles in validation

- **V1**: this GitHub repo (current; carries collaborator deletions made
  against the rules — each is a gap-fill test case).
- Test repos are provisioned **with** `.git` as oracle (V0); V2 = GitLab
  earlier copy `a-group2180532/termux-monorepo`; V3 = Termux local, both
  devices; V4 = device Origin (first commit corrupted — graduation test:
  rebuild everything prior from Session Provenance mapping only).
- Early reference implementation draft: `archwiz/forensic_toolchain.py`
  (Forensic curated pipeline) — also the likely surface UX for RevWright
  module dispatches. Kin: Archaeo (`archwiz/archaeo_sweep.py`, `forge.py`),
  Oracle (`archwiz/oracle_v2.py`, `impact_oracle.py`) — adjacent, not core.

All decisions in this project are temporary by design: up for
revision|review for goal progress.
