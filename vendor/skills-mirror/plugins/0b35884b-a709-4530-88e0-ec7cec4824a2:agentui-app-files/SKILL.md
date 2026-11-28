---
name: agentui-app-files
description: Upload, list, download, share and delete files in an AgentUI workspace's file storage with `agentui files`. Use when the user wants to put a file into AgentUI — an image, PDF, CSV, logo or dataset the app or a colleague needs to reach; wants a public or temporary link to a file already in the workspace; or asks where their AgentUI app should store uploads and attachments. Not for ordinary local file work, and not for uploads to any other service.
---

# Workspace file storage

```bash
agentui files upload ./report.pdf                 # private by default → returns a file id
agentui files upload ./logo.png --public          # permanent URL anyone with the link can read
agentui files upload ./data.csv --name q3.csv --type text/csv
agentui files list --search invoice --mine
agentui files list --category image --since 2026-09-01 --sort size --order desc
agentui files download <fileId> --out ./here/
agentui files url <fileId>                        # temporary share link (prints expiry + scope)
agentui files publish <fileId> --yes              # make an existing private file public
agentui files delete <fileId> [fileId...] --yes  # permanent; many ids at once
```

## Rules that matter

- **Private is the default and should stay the default.** `--public` and `files publish`
  make the object readable by anyone holding the link, permanently. Confirm with the
  user before either — "make it public?" is a one-line question, and un-publishing does
  not un-share what was already copied.
- A **private** upload returns a file id and `url: null` — its link is minted per request
  and is a bearer credential for that one object, so it never leaves the process. A
  `--public` upload returns a real, permanent `url` you can hand over. `files url` is the
  one explicit share verb for everything else, and it states the expiry and the scope.
- Uploading is not the same as putting the file in the app. To let the app's users
  upload files at runtime, that belongs in app code — check
  `agentui skills info "Database Operations"` and `AGENTS.md`, and see ``agentui-ship-app``.
- The app's icon is its own command, not a file upload: `agentui project icon logo.png --yes`.
- `files list` pages at 100. `--all` walks the pages for you but **stops at 2,000 files**
  and flags the result as truncated — continue from the offset it reports rather than
  assuming you saw the whole workspace.

- `files list` filters: `--category` (image, video, audio, pdf, spreadsheet,
  document, archive, other), `--since` / `--before` (dates), `--min-size` /
  `--max-size` (bytes), `--visibility public|private`, `--sort createdAt|name|size`,
  `--order asc|desc`. The platform checks each one: a bad value is refused with the
  allowed values listed.
- `files delete` removes the file from storage and the database, and it cannot be
  undone. Confirm with the user, list exactly which files, and only then pass `--yes`.
  It accepts many ids and sends them in batches of 100. If any id is not found or
  storage refuses it, the command exits 1 with `deleted`, `notFound` and `failed` in
  the payload. Report those counts; do not say "deleted" when only some were.
  `failed` files are still stored, and the error message includes the retry command.

Use `--json` and read back the `id` — that is what every other files command takes.
