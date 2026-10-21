# Hark bridge: queue work for Hark from GitHub Actions

Hark has **no inbound webhook, public API, or API token**, so nothing can call
Hark directly. Instead, a GitHub issue is the job: any workflow opens an issue
labeled `hark:queue`, and Hark's scheduled poller reads the queue, does the
work, and reports back on the issue.

```
workflow ──uses──▶ hark-enqueue.yml ──▶ issue [hark:queue] ──(poll every 2h)──▶ Hark
                                                         ◀── comment + hark:done / hark:blocked:<class>
```

## Job contract

| Field | Where | Meaning |
|---|---|---|
| title | issue title | The task, in plain words ("Re-run Vercel prod deploy for help-wanted-dash") |
| key | `<!-- hark-key: … -->` marker + YAML | Dedup key. Same key while the issue is open = append, not a new issue |
| project | YAML | Which Hark project owns the job (slugs below) |
| priority | YAML | `P0` urgent, `P1` normal, `P2` whenever |
| inputs | YAML mapping | Anything the job needs (PR numbers, run ids, URLs). **Never secret values** |
| done_when | YAML | What Hark must verify before it marks the job done |
| source | YAML | Run URL that enqueued it (filled in automatically) |

Example issue body (what `hark-enqueue.yml` writes):

````
<!-- hark-key: vercel-redeploy:help-wanted-dash -->
```yaml
key: vercel-redeploy:help-wanted-dash
project: deploy-quota
priority: P1
inputs:
  workflow: tribute-vercel-prod.yml
  ref: master
done_when: |
  help-wanted-dash.vercel.app/data/build.json serves the latest master SHA
source: https://github.com/OWNER/REPO/actions/runs/123
enqueued_at: 2026-10-19T09:30:00Z
```
````

### Labels

| Label | Set by | Meaning |
|---|---|---|
| `hark:queue` | caller | Open job waiting for Hark |
| `hark:deferred` | Hark | Waiting for the post-reset heavy batch (quota) |
| `hark:done` | Hark | Finished; issue closed with an evidence comment |
| `hark:blocked:<class>` | Hark | Stuck. `<class>` is one of `needs_login`, `needs_connector`, `permission_missing`, `endpoint_missing`, `rate_limit`, `transient`, `needs_user` |

A human can also queue a job by hand: open an issue with the YAML body above and add `hark:queue`.

### Project slugs

`hark-bridge` (default, small jobs) · `monorepo-ops` (Actions health / fix PRs) · `deploy-quota` (Vercel, Render) · `bot-triage` (bot PRs and issues) · `device` (BLU View 5 / Termux provisioning) · `access-resilience` (credentials and access paths) · `platform201-queue` (Platform201 planning) · `delphi` (Delphi Oracle RFP gate; docs/ops/DELPHI-LANE-CONTRACT.md) · `tribute-system1-routing` (Tribute System 1 HITL escalations from tribute-system1.yml; key `tribute-s1/<owner>/<repo>/<number>`, P1 for question_to_us, else P2; shadow until repo variable `TRIBUTE_S1_ENQUEUE` is `true`) · `main`.

## Calling it from a workflow

The caller must grant `issues: write` (a reusable workflow can't exceed its caller's permissions).

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: ./build.sh

  ask-hark:
    needs: build
    if: failure()
    permissions:
      issues: write
      contents: read
    uses: ./.github/workflows/hark-enqueue.yml
    with:
      title: "Root-cause build failure on ${{ github.ref_name }}"
      key: build-failure:${{ github.workflow }}:${{ github.ref_name }}
      project: monorepo-ops
      priority: P1
      inputs: |
        run_url: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        sha: ${{ github.sha }}
      done_when: "An additive fix PR is open and its checks pass, or the cause is explained on the issue"
```

Outputs: `issue_number` and `action` (`created` or `appended`).

Manual / from another tool:

```bash
gh workflow run hark-enqueue.yml -R timerloggedout-spec/termux-monorepo \
  -f title="Check Render deploy" -f key=render:check -f project=deploy-quota -f priority=P2
```

## How Hark processes the queue

- **Poller, every 2 hours.** Reads open `hark:queue` issues, highest priority first (then oldest).
  Small jobs it does itself; project-scoped jobs it hands to that project's agent. It comments
  with evidence (run URL + conclusion, PR number, served SHA, API readback), then relabels and
  closes. When the queue is empty it says nothing.
- **Quota-aware.** Each run checks Hark's usage first.
  - Daily usage above 80%: only `P0` runs; `P1`/`P2` get `hark:deferred`.
  - Monthly pool above 85%: all non-`P0` work pauses until the pool resets; the user is told once.
- **Post-reset heavy batch, daily 02:15 Pacific.** Right after Hark's daily usage resets, runs
  the deferred `P1`/`P2` jobs.

Latency is therefore up to ~2 hours for normal jobs (Hark's schedule floor is ~1 hour), and up to
a day for deferred heavy jobs. Use `P0` sparingly.

## Rules

- Never put secret values in an issue. Secret **names** are fine.
- Jobs follow the repo's additive-only rule: nothing moves or deletes existing files.
- A job is only `hark:done` with evidence.

## Not yet wired

- Mirroring queue rows into the Neon `ops_queue` table (Platform201 Planning Queue). The issue stays
  the source of truth; a mirror step will be added once that table's schema lands.
