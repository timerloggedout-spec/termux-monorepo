"""Dashboard surface feeds — 3L0, MoneyBall, MVT, DoE, ATES.

Reads only repository records (plus the checked-in workflow observations
snapshot, itself an API read with its own read_at stamp) and emits one feed
JSON per surface into apps/help-wanted-dashboard/data/. The pages consume
their feed and nothing else. Facts the records do not hold are emitted as
named gaps, never synthesized. Refresh = re-run this collector and land the
result by PR, exactly like the Oracle Panel feed.

Contract: docs/ops/DASHBOARD-SURFACE-FEEDS.md
MVT/DoE/ATES separation: docs/ops/MVT-DOE-ATES-SEPARATION.md
"""
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"
SCHEMA = "dashboard-surface-feed/v1"

HONESTY = [
    "Show only what the record holds; a value the record does not hold renders as absent, never synthesized.",
    "Defined-but-not-run experiments render as exactly that.",
    "Weights and scores are read from the code and records at collection time, never transcribed from prose claims.",
    "Workflow run counts are API observations stamped with their read time, not live claims.",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(rel: str):
    return json.loads((ROOT / rel).read_text())


def _observations() -> dict:
    p = ROOT / "scripts" / "dashboards" / "workflow_observations.json"
    if p.exists():
        return json.loads(p.read_text())
    return {"schema": "dashboard-workflow-observations/v1", "read_at": None, "workflows": {}}


def _feed(surface: str, sources: list, payload: dict, gaps: list) -> dict:
    return {
        "schema": SCHEMA,
        "surface": surface,
        "generated_at": _now(),
        "sources": sources,
        "honesty_rules": HONESTY,
        "data": payload,
        "gaps": gaps,
    }


# ---------------------------------------------------------------- MoneyBall

def collect_moneyball() -> dict:
    weights_mod = ast.parse((ROOT / "ml/pipelines/moneyball/weights.py").read_text())
    weights, stale_cap = {}, None
    for node in ast.walk(weights_mod):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "WEIGHTS":
            weights = ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "STALE_CAP":
            stale_cap = ast.literal_eval(node.value)
    norm = ast.parse((ROOT / "ml/pipelines/moneyball/normalize.py").read_text())
    clamp = {}
    for node in ast.walk(norm):
        if isinstance(node, ast.FunctionDef) and node.name == "clamp":
            args = node.args.args
            defaults = node.args.defaults
            clamp = {a.arg: ast.literal_eval(d) for a, d in zip(args[len(args) - len(defaults):], defaults)}
    explain = ast.parse((ROOT / "ml/pipelines/moneyball/explain.py").read_text())
    explain_keys = []
    for node in ast.walk(explain):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "score" in keys:
                explain_keys = keys
    obs = _observations()["workflows"].get("hex-moneyball-evidence.yml", {})
    payload = {
        "what_it_scores": "Pull requests. score(pr) in ml/pipelines/moneyball/scorer.py sums transparent signal weights and clamps the total.",
        "weights": weights,
        "stale_cap": stale_cap,
        "stale_rule": "staleness adds age_days * stale_day, floored at stale_cap",
        "clamp": clamp,
        "signals": [
            {"signal": "dual_gate_green", "condition": "gates repo-gate == success AND termux-smoke == success"},
            {"signal": "on_master_base", "condition": "base ref is master"},
            {"signal": "files_under_100", "condition": "changed_files <= 100"},
            {"signal": "has_tests", "condition": "pr.has_tests is true"},
            {"signal": "fresh", "condition": "age_days < 2"},
            {"signal": "draft", "condition": "pr is a draft (penalty)"},
            {"signal": "dirty", "condition": "mergeable_state == dirty (penalty)"},
            {"signal": "wrong_base", "condition": "base ref set and not master (penalty)"},
            {"signal": "minesweeper", "condition": "minesweeper_extract(pr) matches (penalty)"},
            {"signal": "wholesale", "condition": "pr.wholesale is true (penalty)"},
            {"signal": "stale_day", "condition": "per full day of age (penalty, floored at stale_cap)"},
        ],
        "explain_output_keys": explain_keys,
        "explain_note": "explain(pr) returns the score, the lane classification (ml.pipelines.lanes.classify), the full weights table, and the PR's recorded why.",
        "consumers": [
            "ml/pipelines/command_center/board.py — scores shaped PRs onto the command-center board",
            "ml/pipelines/cli.py — CLI surface",
            "ml/pipelines/stages/features.py — feature stage",
            "ml/pipelines/viz/cctv.py — visualization",
        ],
        "quota_multiplier": "ml/pipelines/moneyball/quota_weights.py: quota_multiplier(provider) scales a candidate's 3L0/ELO x role score by remaining-budget fraction over remaining-time fraction, capped at 2.0; 0 when a quota is exhausted; 1.0 (neutral) when there is no evidence or no readings file.",
        "hex_contract": {
            "version": "3l0.moneyball.v1",
            "role": "Hex is the analytics/evidence layer (docs/ops/HEX-MONEYBALL-INTEGRATION.md); GitHub Actions remains the execution plane and the durable ledger stays outside Hex.",
            "datasets": ["experiment_run", "agent_task_attempt", "provider_call", "outcome_score", "manager_decision"],
            "identity": "records key on the Actions run attempt (run_id + run_attempt), not the run alone",
        },
        "evidence_workflow": {
            "file": ".github/workflows/hex-moneyball-evidence.yml",
            "does": "runs scripts/hex_moneyball_export.py — sanitizes an NDJSON agent telemetry stream into CSV records with a provenance manifest (scripts/hex_moneyball_artifact_provenance.py)",
            "observed_runs": obs,
        },
        "test_evidence": "ml/pipelines/test_scorer.py: a clean candidate PR outscores a wholesale PR under the shipped weights; weights and clamp are unit-tested (test_weights.py, test_explain.py).",
    }
    gaps = [
        "No committed per-PR MoneyBall score outputs exist in the repo: scores are computed live by the board/CLI at runtime and the evidence workflow's exports land as Actions artifacts, not committed files. This page therefore shows the scoring system exactly as coded, not a fabricated scoreboard.",
    ]
    sources = [
        "ml/pipelines/moneyball/{scorer,weights,normalize,explain,quota_weights}.py",
        "docs/ops/HEX-MONEYBALL-INTEGRATION.md",
        "scripts/hex_moneyball_export.py + .github/workflows/hex-moneyball-evidence.yml",
        "scripts/dashboards/workflow_observations.json (Actions API read)",
    ]
    return _feed("moneyball", sources, payload, gaps)


# --------------------------------------------------------------------- 3L0

def collect_3l0() -> dict:
    rm = _read_json("docs/ops/generated/reviewer-metrics.json")
    providers = []
    for name, p in sorted(rm.get("providers", {}).items()):
        by_class = {}
        tot_c = tot_d = 0
        for cls, v in sorted(p.get("by_author_class", {}).items()):
            by_class[cls] = {
                "cycles": v.get("cycles"), "delivered": v.get("delivered"),
                "delivery_rate": v.get("delivery_rate"),
                "median_latency_sec": v.get("median_latency_sec"),
                "cooldown_cycles": v.get("cooldown_cycles"),
            }
            tot_c += v.get("cycles") or 0
            tot_d += v.get("delivered") or 0
        providers.append({
            "provider": name, "cycles": tot_c, "delivered": tot_d,
            "delivery_rate": round(tot_d / tot_c, 4) if tot_c else None,
            "contexts": len(p.get("by_context", {})),
            "by_author_class": by_class,
        })
    providers.sort(key=lambda x: (x["delivery_rate"] is None, -(x["delivery_rate"] or 0), -x["cycles"]))
    history = {}
    for cyc in rm.get("cycles", []):
        for name, pv in (cyc.get("providers") or {}).items():
            history.setdefault(name, []).append({
                "cycle_id": cyc.get("cycle_id"), "pr": cyc.get("pr"),
                "started_at": cyc.get("cycle_started_at"),
                "delivered": pv.get("delivered"), "latency_sec": pv.get("latency_sec"),
                "cooldown": pv.get("cooldown"),
            })
    for name in history:
        history[name] = history[name][-24:]
    import yaml
    peers_doc = yaml.safe_load((ROOT / ".github/connectors/llm-peers.yaml").read_text())
    peers = []
    for pname, p in sorted((peers_doc.get("peers") or {}).items()):
        models = [{"id": m.get("id"), "roles": m.get("roles"), "soft_limits": m.get("soft_limits")}
                  for m in (p.get("models") or [])]
        peers.append({"provider": pname, "models": models})
    panel = _read_json("ops/delphi/panel.json")
    payload = {
        "definition": "The custom 3L0 score is an inference matrix, not a claim of objective model intelligence (docs/ops/AGENT-TEAM-ORCHESTRATION.md). MoneyBall/3L0 scores providers, agents and models AFTER repeated success, for admission and routing weight — it does not pick the next HTTP model for a single request.",
        "components": [
            "task outcome / acceptance", "useful feedback cycles", "time to integrated result",
            "latency and requests used", "retry / failure rate", "conflict and duplicate-work rate",
            "human intervention", "context efficiency", "attribution confidence",
            "provider availability and quota",
        ],
        "pipeline": "provider catalog -> normalized evidence -> Scout roster -> MVT -> telemetry -> MoneyBall/3L0 -> admission (docs/ops/SCOUT-ROSTER.md). Admission requires successful task probes, attributable telemetry, correctness/outcome evidence, regression checks, and the applicable manager/3L0 policy; 'candidate' means eligible to probe, not proven capable.",
        "router": {
            "mechanic": "scripts/model_router.py scores each model entry as elo x role_suitability (x MoneyBall quota_multiplier where applied); entries without a recorded elo use the router default of 1000.",
            "default_elo": 1000,
            "peers_source": ".github/connectors/llm-peers.yaml — provider peers, model ids, roles and soft budgets (real free-tier request-per-day limits)",
            "peers": peers,
        },
        "response_history": {
            "record": "docs/ops/generated/reviewer-metrics.json (schema reviewer-metrics/v1) — the fleet's measured per-response record: every peer-review cycle, whether the provider delivered, and its latency. This is response history as recorded; it is a reviewer surface, and it is not dressed up as a model-intelligence ranking.",
            "generated_at": rm.get("generated_at"),
            "window": rm.get("window"),
            "providers_ranked": providers,
            "history_tail": history,
        },
        "delphi_weights": {
            "panel_defaults": panel.get("roles"),
            "formula": panel.get("formula"),
            "seed_note": panel.get("seed_note"),
            "live_source": "The live weights live on the Delphi weighting ledger, issue #1489 (EWMA/elo lineage); panel.json carries the defaults/seeds, not the live values.",
        },
    }
    gaps = [
        "No committed machine-readable 3L0 rankings table exists in the repo: rankings are computed at routing time (elo x role suitability x quota multiplier), and no per-model elo values are committed — the router default of 1000 applies where no elo is recorded.",
        "Per-response scoring history exists for the reviewer surface (reviewer-metrics, shown above), not as a standalone 3L0 history file.",
    ]
    sources = [
        "docs/ops/AGENT-TEAM-ORCHESTRATION.md + docs/ops/SCOUT-ROSTER.md + docs/ops/ROUTING-LOGIC-CHAIN.md",
        "scripts/model_router.py + .github/connectors/llm-peers.yaml",
        "docs/ops/generated/reviewer-metrics.json",
        "ops/delphi/panel.json (defaults) + weighting ledger issue #1489 (live values)",
    ]
    return _feed("3l0", sources, payload, gaps)


# --------------------------------------------------------------------- MVT

def collect_mvt() -> dict:
    schema = _read_json("docs/ops/corpus/EXPERIMENT.schema.json")
    import yaml
    wf = yaml.safe_load((ROOT / ".github/workflows/agent-mvt-experiment.yml").read_text())
    inputs = list(((wf.get(True) or wf.get("on") or {}).get("workflow_dispatch") or {}).get("inputs", {}).keys()) \
        if isinstance(wf, dict) else []
    obs = _observations()["workflows"]
    loop_obs = obs.get("agent-mvt-experiment.yml", {})
    payload = {
        "method": "Multivariate testing as practiced: simultaneous provider lanes over a live target (Team MVT), and schema-conforming loop experiments comparing a candidate ref against a baseline ref (the experiment loop). Arm designs come from the DoE library and arms execute under the ATES invariants — both cited below, owned by their surfaces.",
        "experiment_record_schema": {
            "file": "docs/ops/corpus/EXPERIMENT.schema.json",
            "required": schema.get("required"),
            "status_enum": (((schema.get("properties") or {}).get("status") or {}).get("enum")),
            "identity": "canonical row identity is cohort x task x arm x repetition; each row retains task fingerprint, environment fingerprint, benchmark version, arm-factor hash, trace id, deterministic verdict, ATES metrics, and optional judge score",
        },
        "experiment_loop": {
            "file": ".github/workflows/agent-mvt-experiment.yml",
            "mode": "workflow_dispatch only; candidate and baseline refs are checked out independently, measured and recorded; it NEVER mutates refs",
            "inputs": inputs,
            "observed_runs": loop_obs,
            "state": "defined_not_run" if loop_obs.get("total_runs", 0) == 0 else "observed_runs",
        },
        "team_mvt": {
            "file": ".github/workflows/team-mvt.yml",
            "mode": "simultaneous provider lanes over an issue/PR target; dispatched, issue-edited and master-push triggered; cadence owned by quota-dispatch-tree.yml (issue #1573)",
            "observed_runs": obs.get("team-mvt.yml", {}),
        },
        "citations": [
            {
                "surface": "ates",
                "record": "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md + apps/help-wanted-dashboard/data/ates-feed.json",
                "label": "ATES harness — the seven hard invariants",
                "note": "The invariants gate every arm MVT runs; they are ATES property, cited here, not copied.",
            },
            {
                "surface": "doe",
                "record": "deepcli/deepcli/observatory/doe.py + apps/help-wanted-dashboard/data/doe-feed.json",
                "label": "DoE design library",
                "note": "full_factorial / taguchi_l9 / mvt_shuffle generate the arm designs MVT campaigns consume (doe.py: 'DoE helpers for MVT campaigns').",
            },
        ],
    }
    gaps = [
        "No committed experiment records conforming to EXPERIMENT.schema.json exist in the repo: the experiment loop has never been dispatched (0 runs observed), so there are no recorded MVT experiment results to rank or chart. Defined-but-not-run renders as exactly that.",
    ]
    sources = [
        "docs/ops/corpus/EXPERIMENT.schema.json",
        ".github/workflows/agent-mvt-experiment.yml + .github/workflows/team-mvt.yml",
        "scripts/dashboards/workflow_observations.json (Actions API read)",
    ]
    return _feed("mvt", sources, payload, gaps)


# -------------------------------------------------------------------- ATES

def collect_ates() -> dict:
    obs = _observations()["workflows"]
    fixtures = _read_json("tests/fixtures/ates/orchestrator_mvt.json")
    case_ids = [c.get("case", {}).get("case_id") for c in fixtures]
    loop_obs = obs.get("agent-mvt-experiment.yml", {})
    payload = {
        "doc": "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md",
        "invariants": [
            "abstention availability", "wrong-commit penalty", "required-fragment preservation",
            "distractor isolation", "deterministic execution failure", "isolated SPAWN behavior",
            "actor/critic private-context isolation",
        ],
        "invariant_note": "The minimum viable test cohort covers seven hard invariants. Failed experiments remain evidence and are not automatically rerun merely to improve dashboards.",
        "workflows": [
            {
                "file": ".github/workflows/ates-orchestrator-benchmark.yml",
                "name": "ATES Orchestrator Benchmark",
                "role": "Deterministic benchmark: on changes to the evaluator, the fixtures or the ATES docs, runs the orchestrator suites and evaluates scripts/ci/evaluate_orchestrator_benchmark.py over the fixtures, asserting the deterministic verdicts (pass case PASS; leak case FAIL_DETERMINISTIC with net_score 0.0).",
                "observed_runs": obs.get("ates-orchestrator-benchmark.yml", {}),
            },
            {
                "file": ".github/workflows/ates-phase-b-run-receipt.yml",
                "name": "ATES Phase B Run Receipt",
                "role": "Run receipts: on completion of 'Continuous agent ops', emits a metadata-only receipt (scripts/ci/emit_ates_run_receipt.py — event + run id/attempt; no head_commit, no html_url) and publishes it as a 30-day Actions artifact.",
                "observed_runs": obs.get("ates-phase-b-run-receipt.yml", {}),
            },
            {
                "file": ".github/workflows/agent-mvt-experiment.yml",
                "name": "Agent MVT experiment loop",
                "role": "Execution vehicle for the MVT surface's schema-conforming experiments: checks out candidate and baseline refs independently, measures, records.",
                "discipline": "permissions are contents:read only; the workflow header states it NEVER mutates refs — branch switching never becomes history rewriting.",
                "observed_runs": loop_obs,
                "state": "defined_not_run" if loop_obs.get("total_runs", 0) == 0 else "observed_runs",
            },
        ],
        "fixtures": {
            "file": "tests/fixtures/ates/orchestrator_mvt.json",
            "label": "Synthetic boundary cases for the benchmark suite — fixtures, not recorded experiment results.",
            "cases": case_ids,
        },
        "trace_schema": "docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json — validated by the benchmark workflow on every run.",
        "citations": [
            {
                "surface": "mvt",
                "record": "docs/ops/corpus/EXPERIMENT.schema.json + apps/help-wanted-dashboard/data/mvt-feed.json",
                "label": "MVT — experiment records and practice",
                "note": "Experiments the harness executes are recorded in the EXPERIMENT schema and owned by the MVT surface.",
            },
            {
                "surface": "doe",
                "record": "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md (§DoE) + apps/help-wanted-dashboard/data/doe-feed.json",
                "label": "DoE — first factorial slice",
                "note": "The factorial design for ATES-cohort arms is defined in §DoE of the harness doc and owned by the DoE surface.",
            },
        ],
    }
    gaps = [
        "No committed ATES results ledger exists: benchmark verdicts are asserted inside the workflow run and run receipts publish as 30-day Actions artifacts; this feed observes run counts and latest receipts from the API snapshot only.",
        "The experiment loop has never been dispatched (0 runs observed): the harness's execution vehicle is defined, not yet exercised.",
    ]
    sources = [
        "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md",
        ".github/workflows/ates-orchestrator-benchmark.yml + .github/workflows/ates-phase-b-run-receipt.yml + .github/workflows/agent-mvt-experiment.yml",
        "tests/fixtures/ates/orchestrator_mvt.json",
        "scripts/dashboards/workflow_observations.json (Actions API read)",
    ]
    return _feed("ates", sources, payload, gaps)


# --------------------------------------------------------------------- DoE

def collect_doe() -> dict:
    doe_mod = ast.parse((ROOT / "deepcli/deepcli/observatory/doe.py").read_text())
    functions = []
    for node in doe_mod.body:
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "signature": f"{node.name}({', '.join(a.arg for a in node.args.args)})",
                "doc": (ast.get_docstring(node) or "").strip(),
            })
    payload = {
        "methods_library": {
            "file": "deepcli/deepcli/observatory/doe.py — DoE helpers for MVT campaigns",
            "functions": functions,
        },
        "skill": {
            "file": ".agents/skills/multivariate-doe/SKILL.md",
            "factor_space": "provider x model x prompt x manager x cohort x sequencing (default agent-team factor space; extendable with task family, scope/ref, tool policy, context budget, concurrency, validation and recovery policy)",
            "design_rules": [
                "State the hypothesis before running treatments.",
                "Define factor levels explicitly and preserve their provenance.",
                "Separate the same-task treatment from adversarial/reviewer prompt variants.",
                "Randomize or rotate treatment order where ordering can confound results.",
                "Preserve a stable cohort/ref so code changes do not masquerade as model effects.",
                "Record manager/policy version independently from provider/model identity.",
                "Do not use latency as a correctness proxy.",
                "Record resource/quota state as a capacity variable, not a quality score.",
                "Repeat successful-looking treatments before promotion.",
                "Preserve negative, skipped, unavailable, and censored observations.",
                "Avoid p-hacking: do not select a design or metric after seeing the result.",
                "If the design changes midstream, create a new cohort/version and retain the prior ledger.",
            ],
        },
        "first_factorial_slice": {
            "source": "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md — an experiment arm varies declared factors while task contract hash, environment fingerprint, benchmark version and deterministic scorer remain fixed",
            "executor": "ATES harness — this slice is the §DoE design inside the ATES doc; arms designed here execute under the ATES invariants and are recorded on the MVT surface.",
            "factors": {"routing": ["single", "delegated"], "actor_critic": ["off", "on"],
                        "abstention": ["required"], "spawn": ["isolated"], "judge": ["off", "inconclusive-only"]},
            "primary_outcomes": ["deterministic pass rate", "boundary leakage rate", "required-fragment omission rate", "deterministic execution success rate"],
            "secondary_outcomes": ["net benchmark score", "wrong-commit count", "retry/error rate", "ATES/WTCV", "parallel yield", "time-to-integration", "human intervention", "attribution confidence"],
        },
        "dspy_lane": {
            "file": "docs/proposals/active/model-selection-market/DSPY-DOE-LANE.md + scripts/model_selection_market/dspy_doe.py",
            "state": "design_only",
            "note": "Consideration/optimization lane (MSM-004 design): DSPy arms feed the APPROX-006 A/B/C/D cohort entry; optimizer artifacts never silently mutate production routing weights and stay on the dual-gate promotion path. The design doc records the runtime extract as a later PR — the lane is defined, not run.",
        },
        "citations": [
            {
                "surface": "delphi",
                "record": "docs/proposals/passes/strands-rfp-response/cycle/IMPLEMENTATION.json",
                "label": "Delphi Oracle Method cycle — implementation round",
                "note": "The repo's one executed per-candidate comparison record, owned by the Delphi surface and rendered on the Oracle Panel. Cited so the comparison is findable from here; it is not a DoE campaign and contributes no DoE results to this feed.",
            },
        ],
    }
    gaps = [
        "No standalone committed DoE campaign records exist in the repo: the methods library, skill and factorial slice are defined; the DSPy optimizer lane is design-only. Campaigns defined-but-not-run render as exactly that.",
        "DoE results: none. The only executed per-candidate comparison in the repo is a Delphi record (see citations) — this surface claims no results from it.",
    ]
    sources = [
        "deepcli/deepcli/observatory/doe.py",
        ".agents/skills/multivariate-doe/SKILL.md",
        "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md (§DoE)",
        "docs/proposals/active/model-selection-market/DSPY-DOE-LANE.md",
        "docs/proposals/passes/strands-rfp-response/cycle/IMPLEMENTATION.json (citation only — Delphi-owned record)",
    ]
    return _feed("doe", sources, payload, gaps)


COLLECTORS = {"moneyball": collect_moneyball, "3l0": collect_3l0, "mvt": collect_mvt, "doe": collect_doe, "ates": collect_ates}
FILENAMES = {"moneyball": "moneyball-feed.json", "3l0": "3l0-feed.json", "mvt": "mvt-feed.json", "doe": "doe-feed.json", "ates": "ates-feed.json"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", choices=sorted(COLLECTORS) + ["all"], default="all")
    ap.add_argument("--out-dir", default=str(DATA))
    a = ap.parse_args()
    names = sorted(COLLECTORS) if a.surface == "all" else [a.surface]
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in names:
        feed = COLLECTORS[name]()
        (out / FILENAMES[name]).write_text(json.dumps(feed, indent=1) + "\n")
        print(f"wrote {FILENAMES[name]} ({feed['generated_at']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
