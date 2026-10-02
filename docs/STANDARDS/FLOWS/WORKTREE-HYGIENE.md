# Worktree Hygiene - 2026-10-02

Rule: push-to-origin BEFORE remove. One at a time. Verify SHA between.

## Status - all four removed

| # | Branch | wip ref on origin | SHA | Reclaimed |
|---|--------|-------------------|-----|-----------|
| 1 | hindsight-wire | wip/hindsight-wire-2026-10-02 | ca046ceb | 223M |
| 2 | fix/session-store-prune-expired | wip/fix-session-store-prune-expired-2026-10-02 | 0b135032 | 254M |
| 3 | feat/manus-termux-mcp-connector | wip/feat-manus-termux-mcp-connector-2026-10-02 | 8a5b911e | 222M |
| 4 | docs/termux-mcp-lean-template | wip/docs-termux-mcp-lean-template-2026-10-02 | 23b17161 | 222M |

Total reclaimed: ~921M

## Recurring shape

WT=<path>; BR=<branch>; WIP=wip/${BR//\//-}-<date>
1. git -C "$WT" status --porcelain   # must be empty
2. git -C "$WT" submodule deinit --all --force
3. SHA=$(git -C "$WT" rev-parse HEAD)
4. git -C "$WT" push origin "HEAD:refs/heads/$WIP"
5. REM=$(git -C ~ ls-remote --heads origin "$WIP" | awk "{print \$1}")
6. [ "$SHA" = "$REM" ] || exit 1
7. git -C ~ worktree remove --force --force "$WT"

Note: --force --force required for submodule worktrees.
Single force fails with "working trees containing submodules cannot be moved or removed".

## Storage gates (sentinel)

termux-resource-snapshot.sh. PRESSURE on ANY: mem<150M, swap<128M, avail<1G, used>=95%.
Must clear BOTH avail>1GiB AND used<95 to return OK.

## Anti-patterns burned this session

1. hs-pack 124-part chunk, no gate. Gate now at hs-pack line 128.
2. Ignored the on-disk sentinel before the write.
3. rm at prompt without rm-safe --confirm.
4. Confused ~/.cache/whisper (py) with ~/forensic-indexer/whisper.cpp (src).
5. Heredocs in interactive zsh. Use printf with single-quoted args.
6. mapfile / readarray (bash-only). Use for x in */ globs.
7. /tmp writes on Termux. Use ~/.cache/hs-research/.
8. Pipe-to-tail masks exit codes. Re-read state.
9. Trusted array-empty string comparison. [ "" -eq 0 ] in zsh is TRUE.

## Reserved for explicit owner approval

- ~/forensic-indexer/whisper.cpp (recovering on demand via download-ggml-model.sh)
- ~/CTranslate2
- ~/.deepcli/session_store
- Anything under /storage/emulated/0/Android/{data,obb,media}
- Any am/pm/intent fire
- Any ADB-mediated operation
