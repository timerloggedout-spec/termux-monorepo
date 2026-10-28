# /tmp tmpfs full — incident record, 2026-10-27

## Symptom

`/tmp` on the fleet VM is a 512M tmpfs. On 2026-10-27 it reached 100%
(512M used, 0 available) and writes began failing ENOSPC fleet-wide —
e.g. a Delphi feed-collector verification write died at 05:33 PT.

## Diagnosis (firsthand)

- Sole consumer: `/tmp/nav-build` — 512M, effectively the entire tmpfs.
  Everything else in /tmp totalled under a few MB.
- Owner: the **Web Design Specialist** lane. Its agent executed at
  2026-10-27T12:21:03Z:
  `git clone --filter=blob:none --depth 1 https://github.com/timerloggedout-spec/termux-monorepo /tmp/nav-build`
  to compose a nav follow-up (the PR #1747 free-tier-value nav links) —
  "nav-build" was that lane's scratch clone. A second lane (3L0 weighting
  backfill) read/exec'd against the same tree 12:25–12:26Z.
- The clone's HEAD was a4ccdc07782c ("chore(ops): record sweep
  accountability receipt"); its `.git` had no index, which made
  `git status` report ~9,037 phantom staged deletions. On-disk comparison
  against HEAD blobs is authoritative: 8,754 of 9,037 files byte-identical,
  217 differing (dominated by `workspace/llm_map` pipeline snapshot data
  generated inside the clone, plus browser GPU/Dawn cache binaries),
  66 absent, and only 2 truly untracked files.
- Verdict: **abandoned scratch**. No process referenced the tree after
  12:26Z; the owner lane's work completed (PR #1747 merged). The clone sat
  at 100% of tmpfs for over an hour because nothing cleaned it up.

## Remediation

- **Archive-first:** the git-unrecoverable subset (217 differing + 2
  untracked files, incl. the llm_map snapshot data — preserved per the
  telemetry/training-data retention rule, never deleted unarchived) was
  tarred to the VM's `~/workspace/diagnostics/tmp-nav-build-2026-10-27/`
  with a README recording the evidence.
- **Relocated, not deleted:** the tree moved intact to
  `~/workspace/relocated/nav-build-2026-10-27/` on the VM, with
  `/tmp/nav-build` left as a symlink to it so any lane still holding the
  old path keeps working.
- Result: `df -h /tmp` — 944K used, 512M available, 1%.

## Guardrail

1. **Convention (fleet AGENTS.md, 2026-10-27):** clones, build trees and
   scratch workspaces go under `~/workspace/scratch/<task>/` (real disk);
   /tmp is for small transient files only. Scratch clones are cleaned up
   in the session that creates them. (The repo-gate lesson of 2026-10-20
   already said clones belong under ~/workspace, not /tmp.)
2. **Tripwire — RETIRED 2026-10-28:** a `tmp-usage-tripwire` hook on the
   VM polled /tmp every 5 minutes to wake a report at ≥80% usage (both
   paths dry-run verified 2026-10-27). It was disabled the next day under
   the owner's VM = sandbox-only order: no standing monitors, daemons or
   cron-audits run on the VM; continuous work lives in GitHub Workflows.
   No workflow equivalent exists for this check — a workflow cannot see
   this VM's /tmp — so the guardrail is the convention above, plus the
   fact that /tmp pressure surfaces immediately as ENOSPC failures in
   whichever lane hits it, as it did here.
