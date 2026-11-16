# Executor probe amendment (QUE #5176 fold c.6842923762)

Owner method directive (main stamp #5230 c.6842907164): indefinite
HOLD on `quota_unknown` is a defect — unknown resolves by usage.
Cadence countersign on the probe semantics: #5152 c.6842945679.
The #5230 build landed the record surface; this amendment adds the
firing leg in the dispatch executor and the consumption leg in its
decide cycle.

## The loop

1. **Probe leg (decide).** When a filing's rotation ends in HOLD
   and an arm's cause is `quota_unknown`, the decision carries ONE
   bounded probe for the first unknown-blocked arm (run budget: 1;
   metering-class — the filing still HOLDs this cycle, and the
   value/escalation fire gates are unchanged).
2. **Vehicle.** The executor workflow dispatches the build-arm
   census for that arm only (bounded smoke, ≤3 completions), waits
   for the run, and downloads its census feed artifact.
3. **Record.** `dispatch_executor.py probe-result` maps the census
   row to a probe outcome — the probe measures QUOTA, so the invoke
   leg decides (invoke OK = `success` even if the census's separate
   agent-loop leg failed; terminal 429 = `quota_terminal`;
   missing secret = `auth_error`; invoke failure = `route_error`).
   The proven draw of a successful probe is the invoke leg's 1
   request, never the smoke's bound. `bucket_headroom.py
   record-probe` appends the hash-chained `quota_probe` event to
   `ops/quota/quota-probe-ledger.jsonl` and converts the bucket's
   typed headroom in the bucket-headroom feed; the workflow commits
   both files (the executor's contents:write scope exists for this
   commit only).
4. **Consumption (next cycles).** decide() reads the headroom feed
   (`--measured`): a still-valid measurement for the arm's bucket
   converts the gate — `exact`/`lower_bound` supply headroom,
   `zero_until_reset` reads as terminal-for-the-window; stale or
   unbounded-old records measure nothing and the arm earns a fresh
   probe instead. A converted fire's pre-flight stamp carries
   source `quota-probe-measured` — probe results are the attempt-2
   gate's coverage evidence, never a bypass of it.

## Feed mechanics

Provider-arm buckets (`gemini-api-free`, `<arm>-free-tier`) are not
in the headroom watcher's GitHub-API read universe: they enter the
feed through their first probe (record-probe creates the row,
kind `provider-arm`) and the watcher carries them verbatim across
its cycles — a watcher run never erases probe-measured state.

Verified end-to-end locally: census success → record-probe
`converted (lower_bound 1)` → next decide FIRES the arm with the
probe-measured pre-flight.
