# scripts/tribute — recon-first, resource-efficient worktree toolkit

Tuned for BLU B160V.  Metadata check runs before any byte is cloned.

## Subcommands

    tribute_lane.sh recon <owner/repo>              # metadata only, no clone
    tribute_lane.sh run   <owner/repo> <cmd...>     # recon + prepare + exec + sweep
    tribute_lane.sh prep  <owner/repo> [paths]      # shallow + partial + sparse
    tribute_lane.sh size  <owner/repo>
    tribute_lane.sh list
    tribute_lane.sh sweep --ttl-hours 6
    tribute_lane.sh hygiene [--apply]               # termux-monorepo .git analysis

## Method

| Layer | Setting | Effect |
|---|---|---|
| Recon | `gh api repos/{o}/{r}` | size, default branch, activity — zero clone |
| Cap | 200 MB default | ABORT before network if exceeded |
| Depth | `--depth=1` | single commit |
| Filter | `--filter=blob:none` | trees only; blobs on demand |
| Sparse | `--sparse --cone <paths>` | only named directories materialized |
| Cache | `~/.cache/tribute/<owner>__<repo>` | reused across runs |
| Sweep | idle 6 h | auto removed on next invocation |
| Meter | `~/.deepcli/logs/tribute/tribute.jsonl` | seconds, disk MB, sparse set |

## Tribute lane usage

    # Help-wanted scout — read one file from a foreign repo
    scripts/tribute/tribute_lane.sh run some-org/some-repo cat README.md

    # Help-given audit — grep specific paths
    scripts/tribute/tribute_lane.sh run some-org/some-repo rg -n "TODO" docs/

    # Pre-flight without cloning
    scripts/tribute/tribute_lane.sh recon some-org/some-repo

## termux-monorepo hygiene

    scripts/tribute/tribute_lane.sh hygiene
    scripts/tribute/tribute_lane.sh hygiene --apply

Reports .git size, refs, pack stats, top bloat directories, dirty count.
`--apply` runs aggressive gc + repack + prune-packed.
