# Manus computer-replay harvester (observe-mode)

Implements: MLP-05 (Issue #503, continues #265)

Capture is **self-session only**. Out of scope: auth bypass, other users,
TLS-pinning defeat. Raw captures stay untracked; only schema, normalizer,
and a synthetic fixture are committed.

```text
raw JSON  ->  normalize.event()  ->  JSONL (dedup session_id+stream_seq)
```

Run:

```bash
python3 probes/manus/harvester/cli.py --fixture probes/manus/fixtures/sample-session.jsonl
python3 -m unittest tests/ml_pipelines/test_manus_harvester.py
```

Gates remain `repo_gate.py` + `termux_smoke.py`. This scaffold is
non-blocking until a real own-session sample is operator-approved.
