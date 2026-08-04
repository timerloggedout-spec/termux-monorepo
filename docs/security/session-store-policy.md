# Session-store policy

Session stores are private local state, not repository assets. GitHub cannot
make a directory into a private secret store: GitHub Actions secrets hold
individual values and are injected only during a workflow run.

The following locations must remain untracked:

- `.deepcli/session_store/`
- `.pi/agent/sessions/`
- `cli-synthegration/conv_repo/sessions/`

Use GitHub Actions secrets only for a narrowly scoped runtime credential, pass
it through an environment variable, and never serialize it into a session,
artifact, log, cache, or commit. Persistent session archives belong in a
separate encrypted store with access controls and credential rotation.

The recovered `cli-synthegration/codex/blobs/` collection is derived from the
historical blob revision by `tools/sanitize_codex_blobs.py`. Its manifest gives
the source revision, output hashes, and redaction counts without retaining a
removed value.
