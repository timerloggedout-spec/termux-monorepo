# Mesh request schema · v1 (2026-11-18)

DO route work to mesh nodes through an append-only `REQUESTS.jsonl`; executors append outcomes to `DONE.jsonl`.

## REQUESTS line
`{"id": uuid4, "ts_utc": "YYYY-MM-DDTHH:MM:SSZ", "from": "dispatch|issue#N|<node>", "target": T, "kind": K, "ref": "<git ref ∨ issue ∨ path>", "args": {object ≤2000 chars}, "priority": "T1".."T4"}`

- target ∈ {hark-vm, actions, codespaces, cloudshell, muse-vm, any}
- kind ∈ {eval, export, hygiene, probe} · allowlist only · ¬ arbitrary shell
- priority default T4

## DONE line
`{"id": <request id>, "ts_utc", "by": "<executor>", "status": "done|rejected|queued", "result": {object}, "run": "<run url>"}`

## Stores ∧ drains
| target | store | drain |
|---|---|---|
| hark-vm, any | `timerloggedout-spec/hark-vm-workspace-backup:repo-exports/REQUESTS.jsonl` | Hark cron 0f4c2bd2 · every 6h :15 PT ⇒ DONE.jsonl |
| actions | same store ∧ inline | `.github/workflows/mesh-request.yml` runs allowlisted kinds {probe, hygiene} ⇒ DONE line; eval ∨ export ⇒ status queued |
| codespaces, cloudshell | same store | executor ⇒ #5232 creds; inline executor ∄ ⇒ status queued |
| muse-vm | mirror ⇒ `timerloggedout-spec/muse-vm-workspace-backup:repo-exports/REQUESTS.jsonl` iff OPERATOR write ✓ | Muse VM cadence-priority drain (#5549); Hark ¬ touches muse.ai |

## Intake
- `workflow_dispatch` on `mesh-request.yml` {target, kind, ref, args, priority}
- issue labeled `mesh:request`, body lines `target: …`, `kind: …`, `ref: …`, `args: {…}`, `priority: T#`
- Writes: contents API fast-forward append (`scripts/mesh/append_jsonl.py`), ¬ force; store default branch ruleset `append-only` {deletion, non_fast_forward}.
