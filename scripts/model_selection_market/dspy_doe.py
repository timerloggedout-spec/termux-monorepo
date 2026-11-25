#!/usr/bin/env python3
"""MSM-004 — DSPy DoE-MVT consideration lane.

Arms are evaluated against the deterministic ATES orchestrator benchmark.
DSPy remains optional and is never the production router or an automatic
weight mutator. No paid routes are introduced by this lane.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from math import comb
from urllib.parse import urlparse

@dataclass
class DoeArm:
    arm_id: str
    signature: str
    metric_names: list[str] = field(default_factory=lambda: ["exact_match", "latency_ms"])
    factors: dict[str, str] = field(default_factory=dict)
    free_only: bool = True

class DspyDoeStub:
    """Offline-capable bridge from DoE arms to deterministic benchmark results."""
    def __init__(self) -> None:
        self.runs: list[dict[str, Any]] = []

    def run_arm(self, arm: DoeArm, *, model_id: str="stealth/ox-alpha", role: str="triage", observed_metrics: Mapping[str, Any] | None=None) -> dict[str, Any]:
        if not arm.free_only: raise ValueError("MSM-004 free_only required")
        metrics = dict(observed_metrics) if observed_metrics is not None else {name:(1.0 if name=="exact_match" else 12.0) for name in arm.metric_names}
        rec={"lane":"dspy_doe_consideration","not_default_router":True,"arm_id":arm.arm_id,"signature":arm.signature,"model_id":model_id,"role":role,"factors":dict(arm.factors),"metrics":metrics,"observed_at":datetime.now(timezone.utc).isoformat(),"affinity":["approxination_ABCD","performance_ledger","ates_orchestrator_benchmark"]}
        self.runs.append(rec); return rec

    def record_benchmark_result(self, arm: DoeArm, result: Mapping[str, Any], *, model_id: str="stealth/ox-alpha", role: str="triage") -> dict[str, Any]:
        outcome=result.get("outcome")
        if outcome not in {"PASS","FAIL_DETERMINISTIC","INCONCLUSIVE","BLOCKED"}: raise ValueError("invalid benchmark outcome")
        metrics={k:result.get(k) for k in ("deterministic_score","judge_score","judge_weight","net_score","wrong_commit_penalty")}
        metrics["outcome"]=outcome
        return self.run_arm(arm,model_id=model_id,role=role,observed_metrics=metrics)

    def cohort_summary(self) -> dict[str, Any]:
        return {"policy":"consideration_only","run_count":len(self.runs),"arms":[r["arm_id"] for r in self.runs],"note":"Promote optimizer artifacts only via dual-gate PR; never auto weight mutate"}

class LiveTaskDoe(DspyDoeStub):
    """Append-only paired real-task evidence sharing the legacy runs collection."""
    CONTEXTS = {"termux-development", "tribute"}
    OUTCOMES = {"PASS", "FAIL", "PARTIAL", "UNKNOWN", "ERROR", "BLOCKED"}

    def __init__(self, *, contexts: list[str], hypotheses: Mapping[str, str], metric: str,
                 meaningful_effect: float, planned_looks: list[int], sample_cap: int,
                 alpha: float, power_target: float, treatment_order_seed: int,
                 control: DoeArm, candidate: DoeArm, screening: bool = False,
                 runs: list[dict[str, Any]] | None = None) -> None:
        super().__init__()
        if not contexts or len(set(contexts)) != len(contexts) or set(contexts) - self.CONTEXTS:
            raise ValueError("contexts must be unique supported contexts")
        if set(hypotheses) != set(contexts) or any(not isinstance(h, str) or not h for h in hypotheses.values()):
            raise ValueError("declare a hypothesis for each context")
        ints = (planned_looks, sample_cap, treatment_order_seed)
        if (not isinstance(metric, str) or not metric or not isinstance(meaningful_effect, (int, float)) or isinstance(meaningful_effect, bool) or meaningful_effect <= 0 or
                not isinstance(planned_looks, list) or any(type(n) is not int for n in planned_looks) or not planned_looks or
                planned_looks != sorted(set(planned_looks)) or planned_looks[0] < 1 or type(sample_cap) is not int or sample_cap < planned_looks[-1]):
            raise ValueError("invalid metric, effect, looks, or sample cap")
        if not 0 < alpha < 1 or not 0 < power_target < 1 or type(treatment_order_seed) is not int:
            raise ValueError("invalid alpha, power target, or order seed")
        if control.arm_id == candidate.arm_id or not control.free_only or not candidate.free_only:
            raise ValueError("distinct free control and candidate arms required")
        plan = {"contexts": list(contexts), "hypotheses": dict(hypotheses), "metric": metric,
                "meaningful_effect": meaningful_effect, "planned_looks": list(planned_looks),
                "sample_cap": sample_cap, "alpha": alpha, "power_target": power_target,
                "treatment_order_seed": treatment_order_seed, "control_arm": control.arm_id,
                "candidate_arm": candidate.arm_id, "screening": screening}
        self._plan_json = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self._plan_hash = hashlib.sha256(self._plan_json.encode()).hexdigest()
        self.runs = runs if runs is not None else []

    @property
    def plan(self) -> dict[str, Any]:
        return json.loads(self._plan_json)

    def _check_plan(self) -> dict[str, Any]:
        plan = self.plan
        if hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest() != self._plan_hash:
            raise ValueError("frozen plan integrity check failed")
        return plan

    def record_task(self, *, task_url: str, source_snapshot_hash: str, task_contract_hash: str,
                    context: str, task_unit_id: str, repetition: int, attempt: int,
                    source_sha: str, arm_id: str, outcome: str) -> dict[str, Any]:
        plan = self._check_plan()
        parsed = urlparse(task_url) if isinstance(task_url, str) else None
        if context not in plan["contexts"] or arm_id not in {plan["control_arm"], plan["candidate_arm"]}:
            raise ValueError("context or arm outside frozen plan")
        if not parsed or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
            raise ValueError("task URL must be a public HTTPS URL")
        if (not re.fullmatch(r"[0-9a-fA-F]{64}", source_snapshot_hash or "") or
            not re.fullmatch(r"[0-9a-fA-F]{64}", task_contract_hash or "") or
            not re.fullmatch(r"[0-9a-fA-F]{40}", source_sha or "") or not isinstance(task_unit_id, str) or not task_unit_id):
            raise ValueError("SHA-256 snapshot/contract, SHA-1 source commit, and task unit identity required")
        if type(repetition) is not int or type(attempt) is not int or repetition < 1 or attempt < 1:
            raise ValueError("positive integer repetition and attempt required")
        if outcome not in self.OUTCOMES: raise ValueError("invalid outcome")
        identity = (context, task_unit_id, repetition, attempt, arm_id)
        for old in self.runs:
            if old.get("lane") != "dspy_doe_live_task":
                continue
            if old.get("task_url") == task_url and (old.get("context"), old.get("task_unit_id")) != (context, task_unit_id):
                raise ValueError("one source task cannot become multiple independent units")
            if old.get("context") == context and old.get("task_unit_id") == task_unit_id:
                if any(old.get(key) != value for key, value in (("task_url", task_url), ("source_snapshot_hash", source_snapshot_hash), ("task_contract_hash", task_contract_hash), ("source_sha", source_sha))):
                    raise ValueError("paired task source and contract must stay frozen")
            if old.get("lane") == "dspy_doe_live_task" and tuple(old.get(k) for k in ("context", "task_unit_id", "repetition", "attempt", "arm_id")) == identity:
                raise ValueError("duplicate task-arm-repetition-attempt")
        rec = {"lane": "dspy_doe_live_task", "plan": copy.deepcopy(plan), "plan_sha256": self._plan_hash, "task_url": task_url,
               "source_snapshot_hash": source_snapshot_hash, "task_contract_hash": task_contract_hash,
               "context": context, "task_unit_id": task_unit_id, "repetition": repetition,
               "attempt": attempt, "source_sha": source_sha, "arm_id": arm_id,
               "outcome": outcome, "observed_at": datetime.now(timezone.utc).isoformat()}
        self.runs.append(rec)
        return rec

    def analyze(self, *, look: int) -> dict[str, Any]:
        plan = self._check_plan()
        if type(look) is not int or look not in plan["planned_looks"]:
            raise ValueError("look was not prespecified")
        corrected = plan["alpha"] / (len(plan["contexts"]) * len(plan["planned_looks"]))
        result = {"policy": "consideration_only", "look": look, "screening": plan["screening"], "contexts": {}}
        for context in plan["contexts"]:
            rows = [r for r in self.runs if r.get("lane") == "dspy_doe_live_task" and r.get("context") == context and r.get("plan_sha256") == self._plan_hash]
            units: dict[str, dict[str, list[dict[str, Any]]]] = {}
            for row in rows: units.setdefault(row["task_unit_id"], {}).setdefault(row["arm_id"], []).append(row)
            if len(units) > look:
                raise ValueError("observations exceed the exact declared look; freeze cohort before analysis")
            wins = losses = completed = censored = incomplete = 0
            for arms in units.values():
                if set(arms) != {plan["control_arm"], plan["candidate_arm"]}:
                    incomplete += 1; continue
                vals = {}
                invalid = False
                for arm, attempts in arms.items():
                    outcomes = [r["outcome"] for r in attempts if type(r.get("repetition")) is int]
                    # Multiple attempts/repetitions or conflicting observations cannot silently become a clean pair.
                    if len(outcomes) != 1:
                        invalid = True; break
                    vals[arm] = outcomes[0]
                if invalid or any(v not in {"PASS", "FAIL"} for v in vals.values()):
                    censored += 1; continue
                completed += 1
                c, t = vals[plan["control_arm"]], vals[plan["candidate_arm"]]
                if c != t:
                    if t == "PASS": wins += 1
                    else: losses += 1
            p = 1.0 if not (wins + losses) else min(1.0, 2 * sum(comb(wins + losses, k) for k in range(min(wins, losses) + 1)) / 2**(wins + losses))
            effect = (wins - losses) / completed if completed else 0.0
            claim = (not plan["screening"] and completed == look and not censored and not incomplete and completed > 0 and p <= corrected and effect >= plan["meaningful_effect"])
            result["contexts"][context] = {"eligible_pairs": completed, "completed_pairs": completed, "discordant_wins": wins,
                "discordant_losses": losses, "tie_pairs": completed - wins - losses, "censored_pairs": censored,
                "incomplete_pairs": incomplete, "exact_two_sided_p": p, "corrected_alpha": corrected,
                "net_effect": effect, "task_level_effect": effect, "winner": plan["candidate_arm"] if claim else None,
                "status": "winner" if claim else "inconclusive", "interval": None,
                "interval_note": "No confidence interval reported; no automatic score promotion."}
        return result

def main() -> int:
    import argparse
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--demo",action="store_true"); args=p.parse_args()
    stub=DspyDoeStub()
    if args.demo:
        for aid,sig in [("A","triage_v1"),("B","triage_v2"),("C","triage_cot"),("D","triage_short")]: stub.run_arm(DoeArm(arm_id=aid,signature=sig))
    print(json.dumps({"runs":stub.runs,"summary":stub.cohort_summary()},indent=2,sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
