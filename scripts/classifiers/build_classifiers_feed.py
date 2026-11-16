#!/usr/bin/env python3
"""classifiers-feed/v1 generator — single writer: tier1-classifiers
steward lane. Emits ops/classifiers/classifiers-feed.json: the full
classifier estate census (unit · group · state · converged + basis ·
outputs · %-breakdown/winner availability) + the observatory
quartet as-coded detail + census headlines.

Counting rule: unit = one recon row / one named system (baseline
docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28 + steward-verified
deltas). CellCog counted once (listed in F and L of the recon).
States: live / dormant (exists, not producing: code-only, never-run,
fail-last, parked) / dead. Converged = steward frame AND reconciled
definitions AND versioning with a comparison line (all three).

Honesty rules: class shares are labelled SHARES, not confidences;
winner-% names MoneyBall winprob only, with its parked state shown.

Recount note: the explicit unit list below sums to 71 unique units
(live 43) — the 2026-11-02 census headline (72 / live 44) carried
+1 arithmetic errors (one phantom row, one live overcount in F);
dormant 26 / dead 2 / converged 3 / multi-output 18 were unaffected.
This feed's headlines are recomputed from these rows, never copied.
"""
import json
import sys

# id, name, group, state, converged, converged_note, outputs,
# pct_kind (None | class-shares | vote-shares | winprob), winner_parked
U = [
 ("observatory-quartet", "Mev/Jev/Kev/Laya + trial.py", "A", "live", False,
  "unconverged: no version line; laya weights unreconciled (agreed gap)",
  ["trial records", "leaderboard"], None, False),
 ("observatory-dispatch", "dispatch.py + adapters (gemini/openrouter/systemone)", "A", "live", False,
  "unconverged: no version line",
  ["trial dispatch results (free-only route enforcement)"], None, False),
 ("system-one-catalog", "System One catalog (88 entries)", "A", "live", False,
  "unconverged: definitions reconciled; no versioning",
  ["catalog JSON (config/system_one_catalog.json)", "catalog doc (SYSTEM-ONE-CATALOG.md)"], None, False),
 ("classify-pr", "classify_pr (vocab v2, production runner ml-pr-lane-classify)", "B", "live", True,
  "converged: steward-operated production; vocab v2 versioned; live-2 DoE tuning comparison open",
  ["pr-lane-feed.json (per-PR verdict rows)", "pr-lane-series.jsonl (per-run class counts)"],
  "class-shares", False),
 ("ml-stages", "stages pipeline (features/evaluate/bind/ingest/recon/train/monitor/export)", "B", "dormant", False,
  "unconverged: no steward frame",
  ["lane lifecycle stage artifacts (by design)"], None, False),
 ("moneyball-scorer", "moneyball scorer", "B", "dormant", False,
  "unconverged: no version line; PARKED by owner 2026-10-28 until statistically significant data exists",
  ["PR priority scores (winprob)", "explain output"], "winprob", True),
 ("ml-peers", "peers (registry/collision/overlap/grok/jules)", "B", "dormant", False,
  "unconverged: code-only, no steward frame",
  ["collaborator collision/overlap registry (by design)"], None, False),
 ("eval-lanes", "eval_lanes (registry/contract/native/app_probe/gamut)", "B", "dormant", False,
  "unconverged: code-only, no steward frame",
  ["evaluator-lane capability registry (by design)"], None, False),
 ("ates-spine", "ates spine/observer", "B", "dormant", False,
  "unconverged: no steward frame",
  ["benchmark receipts"], None, False),
 ("command-center", "command_center board", "B", "dormant", False,
  "unconverged: code-only, no steward frame",
  ["session/board ranking (by design)"], None, False),
 ("model-selection-market", "model_selection_market", "C", "live", False,
  "unconverged: no version line",
  ["provider/model selection decisions", "selection + quota ledger"], None, False),
 ("model-router", "model_router + bootstrap", "C", "dormant", False,
  "unconverged: code-only",
  ["task to model route decisions (by design)"], None, False),
 ("model-performance-index", "model_performance_index", "C", "dormant", False,
  "unconverged: code-only",
  ["model performance tiers (by design)"], None, False),
 ("decision-engines", "decision_engines", "C", "dormant", False,
  "unconverged: code-only",
  ["decision rule verdicts (by design)"], None, False),
 ("provider-model-catalog", "provider_model_catalog", "C", "live", False,
  "unconverged: no version line",
  ["provider catalog", "secret-name map"], None, False),
 ("delphi-gate", "delphi gate.py", "D", "live", False,
  "unconverged: no steward-frame versioning",
  ["delphi:* label-state assignments (parked/shadow/promoted)"], None, False),
 ("delphi-proposals", "cross_vote / method_cycle / generate_proposal", "D", "live", False,
  "unconverged: no steward-frame versioning",
  ["generated proposals", "panel votes", "calibration / weights updates"], "vote-shares", False),
 ("delphi-participant-cycle", "participant_cycle", "D", "dormant", False,
  "unconverged: never ran",
  ["participant arm states (by design; never ran)"], None, False),
 ("delphi-rfp-flood", "rfp_flood_feed + segments + research_axes", "D", "live", False,
  "unconverged: no version line",
  ["RFP feed", "segments", "research_axes"], None, False),
 ("delphi-ledger-feed", "ledger_feed / ledger_fetch", "D", "live", False,
  "unconverged: no version line",
  ["ledger feed", "Neon mirror currents"], None, False),
 ("delphi-oracle-panel", "oracle_panel_feed", "D", "dormant", False,
  "unconverged: fail-last 2026-10-28",
  ["public panel feed"], None, False),
 ("delphi-tribute-ingest", "tribute_ingest", "D", "dormant", False,
  "unconverged: fail-last 2026-10-28",
  ["tribute outcome ledgers"], None, False),
 ("delphi-signal", "delphi-signal (workflow_call)", "D", "dormant", False,
  "unconverged: never-run by design",
  ["signal fan-in"], None, False),
 ("delphi-registries", "delphi registries (panel/ledgers/surfaces)", "D", "live", False,
  "unconverged: data registries, no version line",
  ["panel.json", "ledgers.json", "surfaces.json"], None, False),
 ("repo-gate", "repo_gate", "E", "live", False,
  "unconverged: no steward-frame versioning",
  ["PR hygiene/portability verdict (check run)"], None, False),
 ("tribute-system1", "tribute_system1 (+ participation, tribute audit)", "E", "live", False,
  "unconverged: no version line",
  ["CPPH-ranked tribute targets", "participation records", "tribute audit"], None, False),
 ("reviewer-metrics", "reviewer_metrics collect", "E", "live", False,
  "unconverged: no version line",
  ["reviewer delivery-rate metrics"], None, False),
 ("phantom-secrets-audit", "secrets_audit (phantom)", "E", "live", False,
  "unconverged (nearest miss): steward-operated, definitions maintained, no version line",
  ["phantom-secret remediation doc (per-name classification: provisioned/compiled/dead-branch/provisioning)"],
  None, False),
 ("secrets-scan", "secrets-scan", "E", "dormant", False,
  "unconverged: dormant since 2026-10-05",
  ["secret-pattern findings"], None, False),
 ("comment-quality-sweep", "comment_quality_sweep", "E", "dormant", False,
  "unconverged: never ran",
  ["comment quality report (productive/noise classes) (by design; never ran)"], None, False),
 ("help-wanted-preflight", "help_wanted preflight_candidate", "E", "live", False,
  "unconverged: no version line",
  ["claim-candidate block verdicts"], None, False),
 ("v1-pr-rollup", "_v1_pr_rollup / _v1_mergeable (legacy)", "E", "dormant", False,
  "unconverged: legacy generation, superseded in practice",
  ["PR rollup classes", "mergeable classes"], None, False),
 ("session-categories", "session_categories (x3 copies)", "E", "dormant", False,
  "unconverged: code-only; 3 identical copies (drift risk)",
  ["session category assignments (by design)"], None, False),
]
U += [
 ("peer-review-orchestrator", "peer-review-orchestrator.yml", "F", "live", False,
  "unconverged: no version line", ["review routing assignments"], None, False),
 ("gemini-dispatch", "gemini-dispatch.yml", "F", "live", False,
  "unconverged: no version line", ["dispatched Gemini review output"], None, False),
 ("gemini-after-peers", "gemini-after-peers.yml", "F", "live", False,
  "unconverged: no version line", ["second-pass review verdicts"], None, False),
 ("gemini-review", "gemini-review.yml", "F", "dead", False,
  "unconverged: dead since 2026-08-20, superseded by dispatch/after-peers",
  ["review verdicts (ceased)"], None, False),
 ("gemini-triage", "gemini-triage.yml", "F", "dormant", False,
  "unconverged: never ran", ["triage verdicts (by design; never ran)"], None, False),
 ("gemini-invoke", "gemini-invoke.yml", "F", "dormant", False,
  "unconverged: never ran", ["invoke results (by design; never ran)"], None, False),
 ("gemini-interactions-smoke", "gemini-interactions-smoke.yml", "F", "dormant", False,
  "unconverged: never ran", ["smoke verdicts (by design; never ran)"], None, False),
 ("cellcog-review", "cellcog-review.yml", "F", "live", False,
  "unconverged: no version line", ["CellCog review verdicts"], None, False),
 ("agent-review-auto-jules", "agent-review-auto-jules.yml", "F", "live", False,
  "unconverged: no version line", ["Jules review dispatches"], None, False),
 ("issue-lifecycle-triage", "issue-lifecycle-triage.yml", "F", "live", False,
  "unconverged: no version line", ["issue lifecycle label/state transitions"], None, False),
 ("issue-comment-router", "issue-comment-router.yml", "F", "live", False,
  "unconverged: no version line", ["comment routing assignments"], None, False),
 ("remote-gamut", "remote-gamut-evaluation.yml", "F", "dead", False,
  "unconverged: dead surface — never ran and judge key phantom (GAMUT_JUDGE_API_KEY)",
  ["gamut evaluation verdicts (never produced)"], None, False),
 ("agent-mvt", "agent-mvt-experiment.yml", "F", "dormant", False,
  "unconverged: never ran", ["MVT assignments (by design; never ran)"], None, False),
 ("team-mvt", "team-mvt.yml", "F", "dormant", False,
  "unconverged: fail-last 2026-10-28", ["team MVT assignments"], None, False),
 ("research-intake", "research_intake.py", "G", "live", False,
  "unconverged: no version line", ["research seed records"], None, False),
 ("observatory-intake", "observatory_intake.py", "G", "live", False,
  "unconverged: no version line", ["observatory provenance records"], None, False),
 ("apk-xref-intake", "apk_xref_intake.py", "G", "live", False,
  "unconverged: no version line", ["apk-xref/v1 records"], None, False),
 ("re-taxonomy-intake", "re_taxonomy_intake.py", "G", "live", False,
  "unconverged: no version line", ["validated taxonomy nodes"], None, False),
 ("target-intake", "target-intake (validate_brief)", "G", "live", False,
  "unconverged: no version line", ["intake plans"], None, False),
 ("proposal-delphi-trigger", "proposal-delphi-trigger.yml", "G", "live", False,
  "unconverged: no version line", ["Delphi trigger events"], None, False),
 ("repository-observatory", "repository-observatory (collector)", "H", "live", False,
  "unconverged: no version line",
  ["repo provenance index (owned/starred/watching classes)"], None, False),
 ("delphic-bayesian-lab", "delphic-bayesian-observatory-lab.yml", "H", "dormant", False,
  "unconverged: dormant since 2026-10-05", ["bayesian observatory output"], None, False),
 ("surface-feeds", "surface_feeds (collect_3l0/moneyball/doe/mvt)", "I", "live", False,
  "unconverged: no version line",
  ["3L0 feed", "moneyball feed", "doe feed", "mvt feed"], None, False),
 ("dispatch-tree-feed", "dispatch_tree_feed", "I", "live", False,
  "unconverged: no version line", ["dispatch cadence tree"], None, False),
 ("effectiveness-ledgers", "effectiveness ledgers (action / pr-production / pr-change)", "I", "live", False,
  "unconverged: no version line",
  ["action-effectiveness ledger", "pr-production ledger", "pr-change-effectiveness ledger"],
  None, False),
 ("hex-moneyball-evidence", "hex-moneyball-evidence", "I", "dormant", False,
  "unconverged: PARKED with MoneyBall 2026-10-28", ["moneyball evidence artifacts"], None, False),
 ("provider-batch-claims", "provider-batch reconcile (claims)", "J", "live", False,
  "unconverged: no version line", ["per-family provider claims"], None, False),
 ("quota-dispatch", "quota registry + quota-dispatch-tree (router-regression dormant in-row)", "J", "live", False,
  "unconverged: no version line", ["quota registry", "dispatch tree"], None, False),
 ("openrouter-free-catalog-sync", "openrouter-free-catalog-sync", "J", "live", False,
  "unconverged: no version line", ["free-route allowlist state"], None, False),
 ("provider-recon-compound", "provider-recon-compound", "J", "dormant", False,
  "unconverged: fail-last 2026-10-28", ["provider recon fan-in"], None, False),
 ("coderabbit", "CodeRabbit (external)", "L", "live", False,
  "unconverged: external surface, no steward frame", ["PR review comments"], None, False),
 ("devin", "Devin (external)", "L", "live", False,
  "unconverged: external surface, no steward frame",
  ["PR reviews", "wiki index"], None, False),
 ("qodo", "Qodo (external)", "L", "live", False,
  "unconverged: external surface, no steward frame", ["PR review output"], None, False),
 ("ecc-tools", "ECC Tools (external)", "L", "live", False,
  "unconverged: external surface, no steward frame",
  ["comment findings", "check-run finding mirrors"], None, False),
 ("gemini-second-pass", "Gemini 2nd pass (external)", "L", "live", False,
  "unconverged: external surface, no steward frame", ["second-pass review verdicts"], None, False),
 ("jules-bolt", "Jules/Bolt (external)", "L", "live", False,
  "unconverged: external surface, no steward frame", ["authored PRs"], None, False),
 ("notation-scorer", "notation compliance scorer (nc-1 instrument)", "M", "live", True,
  "converged: DoE nc-1 design + amendments; Linguist-reconciled definitions; v1/v2 versions with scored comparisons",
  ["layer-output units.jsonl (per-unit score + density)", "evaluator flags JSONL"],
  "class-shares", False),
 ("chat-intent", "chat-intent (owner-message intent classifier)", "M", "dormant", True,
  "converged: DoE method register v1/v2 with backfill; registered 2026-11-01/02; dormant = no production consumer yet",
  ["intent verdict JSON (intent + rule + evidence)"], None, False),
]

GROUPS = {"A": "deepcli observatory", "B": "ml/pipelines", "C": "model selection / routing",
          "D": "Delphi system", "E": "repo gates & audits", "F": "workflow triage / review",
          "G": "intake classifiers", "H": "repository observatory",
          "I": "dashboard / feed classifiers", "J": "provider substrate",
          "L": "external surfaces", "M": "post-recon steward builds (2026-10-28+)"}

QUARTET = {
    "home": "deepcli/deepcli/observatory/",
    "pipeline": "mev (produce) -> jev (judge) -> kev (verify) -> laya (synthesize) via trial.py",
    "mev": "producer: generates candidate responses/artifacts for classification",
    "jev": "judge: rubric scoring of artifacts; judge != producer enforced in code (a producer cannot judge its own output)",
    "kev": "verifier: grounds artifacts against source via token-F1 and exact-match checks",
    "laya": "weighted merger / synthesizer: score = 0.7 * Jev + 0.3 * Kev",
    "trial": "trial.py runs the quartet per artifact set and emits trial records",
    "leaderboard": "leaderboard.py ranks trials; tournament.py runs bracket comparisons",
    "dispatch": "dispatch.py + llm/adapters: free-only gate FREE_PROVIDERS={gemini, openrouter}; paid routes refused unless explicitly enabled; SystemOne adapter via observatory/decide.py",
    "hindsight": "trial records are retained toward HindSight; live retain currently fails at the HindSight deployment surface (payloads persist in-repo) — GAP, see gaps[]",
    "coded_quirk": "trial.run_trial filters failed jev/kev entries before zipping with artifacts in laya.synthesize — mid-list failures can mispair verdicts (as-coded, unfixed)",
    "variance_requirement": {
        "owner_requirement": "2026-11-02: the weighted merger requires variances for optimizations — the 0.7 Jev / 0.3 Kev weights are constants today; optimizing them requires per-source variance data.",
        "required_fields_per_trial_population": ["jev_score_variance", "kev_score_variance", "jev_kev_covariance", "jev_kev_disagreement_rate"],
        "carriers": ["trial records", "leaderboard output"],
        "purpose": "the variance series must exist BEFORE any weight tuning is attempted",
        "variance_state": "NOT_ESTABLISHED — trial/leaderboard outputs carry no dispersion fields today; completed-trial n is single-digit (first completed trial 2026-10-27), so no tuning-grade series exists",
    },
    "first_completed_trial": "run 40509162104 SUCCESS 2026-10-27 (OpenRouter free route)",
}

GAPS = [
    "States for non-delta units are as of the 2026-10-28 recon pull; only steward-verified deltas were refreshed (classify_pr production, MoneyBall park, group M additions).",
    "Outputs of code-only / never-run units are by-design (code paths), not observed artifacts.",
    "%-breakdown availability is scored conservatively: emitted share/score tables only (4 units). Scores without share tables do not count.",
    "HindSight live retain fails at the deployment surface (scaffold POST /retain contract rejected); trial/observatory payloads persist in-repo instead.",
    "Tier-1 boundary is still the owner's to draw (flagged 2026-10-28, unconfirmed); this feed covers the full census estate, not a Tier-1 subset.",
    "chat-intent has no production consumer yet; its comparison line opens when labeled chat outcomes exist (ESTABLISHED gate unmet).",
    "Gamut is dead end-to-end (remote-gamut dead, eval_lanes gamut code-only, GAMUT_JUDGE_API_KEY phantom).",
]


def main() -> int:
    units = []
    for uid, name, grp, state, conv, note, outputs, pct, winner_parked in U:
        units.append({
            "id": uid, "name": name, "group": grp, "group_name": GROUPS[grp],
            "state": state, "converged": conv, "converged_basis": note,
            "outputs": outputs,
            "pct_breakdown": {"available": pct is not None, "kind": pct,
                               "label": "SHARES not confidences" if pct in ("class-shares", "vote-shares") else None},
            "winner": {"available": uid == "moneyball-scorer", "kind": "winprob" if uid == "moneyball-scorer" else None,
                       "state": "parked" if winner_parked else None},
        })
    headlines = {
        "estate_units": len(units),
        "live": sum(1 for u in units if u["state"] == "live"),
        "dormant": sum(1 for u in units if u["state"] == "dormant"),
        "dead": sum(1 for u in units if u["state"] == "dead"),
        "converged": sum(1 for u in units if u["converged"]),
        "multi_output": sum(1 for u in units if len(u["outputs"]) >= 2),
    }
    feed = {
        "schema": "classifiers-feed/v1",
        "generated_at": "2026-11-02",
        "generator": "scripts/classifiers/build_classifiers_feed.py (single writer: tier1-classifiers steward)",
        "baseline": "docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28.md + steward-verified deltas",
        "headlines": headlines,
        "correction_note": ("Recount from the explicit unit list: estate 71 / live 43. The earlier "
                            "census headline (72 / live 44) carried +1 arithmetic errors; dormant 26, "
                            "dead 2, converged 3, multi-output 18 verified unaffected."),
        "honesty": {"shares": "class shares are SHARES, not confidences",
                    "winner_pct": "winner % names MoneyBall winprob only; MoneyBall is PARKED (owner, 2026-10-28)"},
        "groups": GROUPS,
        "units": units,
        "observatory_quartet": QUARTET,
        "gaps": GAPS,
    }
    out = sys.argv[1] if len(sys.argv) > 1 else "classifiers-feed.json"
    with open(out, "w") as fh:
        json.dump(feed, fh, indent=1)
    print("units", headlines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
