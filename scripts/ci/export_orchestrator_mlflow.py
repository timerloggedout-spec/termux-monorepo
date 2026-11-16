#!/usr/bin/env python3
"""Export canonical orchestrator benchmark JSONL for optional MLflow evaluation."""
import argparse, json
from pathlib import Path

def load_rows(path: Path):
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value=json.loads(line)
            if not isinstance(value,dict): raise ValueError("each JSONL row must be an object")
            rows.append(value)
    return rows

def to_mlflow_rows(rows):
    return [{k:row.get(k) for k in ("benchmark_case_id","outcome","deterministic_score","judge_score","judge_weight","wrong_commit_penalty","net_score","evidence_fingerprint")} for row in rows]

def log_run(rows, experiment):
    try: import mlflow
    except ImportError as exc: raise RuntimeError("mlflow is required only for --log-run") from exc
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name="ates-orchestrator-benchmark"):
        for i,row in enumerate(rows):
            for key in ("deterministic_score","judge_score","net_score","wrong_commit_penalty"):
                value=row.get(key)
                if isinstance(value,(int,float)): mlflow.log_metric(f"case_{i}_{key}",float(value))
            mlflow.set_tag(f"case_{i}_outcome",str(row.get("outcome")))
            mlflow.set_tag(f"case_{i}_id",str(row.get("benchmark_case_id")))
        mlflow.log_text(json.dumps(to_mlflow_rows(rows),sort_keys=True,indent=2),"orchestrator-benchmark-eval.json")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True,type=Path); p.add_argument("--output",required=True,type=Path); p.add_argument("--log-run",action="store_true"); p.add_argument("--experiment",default="ates-orchestrator")
    a=p.parse_args(); rows=load_rows(a.input); exported=to_mlflow_rows(rows); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(exported,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    if a.log_run: log_run(rows,a.experiment)
    return 0

if __name__ == "__main__": raise SystemExit(main())