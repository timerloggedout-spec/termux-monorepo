# ML Pipelines (slim keep-alive extract)

Implements: `MLP-KEEP-001`

Extract-only vs #682 (130 files) and wholesale #432/#549/#601.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Promote path remains dual-gate only.
