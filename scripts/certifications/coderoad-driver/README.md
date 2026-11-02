# CodeRoad completion driver (certifications leg)

Executes freeCodeCamp project/workshop completions with the **real
CodeRoad VS Code extension**, headless, inside the course's own
rdb-alpha environment — driven by `.github/workflows/cert-coderoad.yml`.

Mechanism (pinned from `coderoad/coderoad-vscode` source):

- The image is freeCodeCamp's `rdb-alpha` Dockerfile (Ubuntu 20.04,
  PostgreSQL 12, Node 18) plus VS Code, Xvfb, the `coderoad.coderoad`
  extension, and the fleet driver extension (`driver/`).
- VS Code launches on the course checkout with
  `CODEROAD_TUTORIAL_URL` set: the extension fetches `tutorial.json`,
  loads it into its state machine, runs the course setup hooks, and
  configures its test runner — no UI interaction involved (the webview
  is only a renderer).
- The orchestrator (`orchestrate.sh`) waits for setup (PostgreSQL up,
  `.freeCodeCamp` deps installed), stages the verified solution
  (`STAGE_CMD`), runs the suite once directly for a diagnostic TAP
  artifact, then raises the GO flag.
- The driver extension fires the registered `coderoad.run_test`
  command; CodeRoad runs the step tests itself, marks the position
  complete, and on the final step posts `tutorial_complete` to the
  tutorial's webhook (`https://api.freecodecamp.org/coderoad-challenge-completed`)
  with the `CodeRoad-User-Token` header taken from the
  `CODEROAD_WEBHOOK_TOKEN` environment variable (repo secret, sealed
  by Provisioning; never printed, filed, or committed).
- Evidence: CodeRoad session state (`CODEROAD_SESSION_STORAGE_PATH`),
  driver `RESULT.json`, direct TAP output, container logs — uploaded
  as run artifacts. Verdict posts on issue #506. The authoritative
  completion check is the on-account Step-1 record (Platforms lane).

Token lifecycle: run-time ENV only; revoked on completion/abandonment
(Provisioning lane holds the vault capture and the revoke action).
