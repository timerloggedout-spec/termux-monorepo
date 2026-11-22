"""Local observatory trial baseline.

Mev, Jev, and Kev are independent role implementations whose evidence is
reduced by Laya. The current runner evaluates candidate artifacts against
the configured critic and verifier; candidate IDs preserve evidence identity
when individual stages fail. This baseline is one tournament arm, not the
required topology for the wider classifier capability graph.
"""
from __future__ import annotations
import asyncio, hashlib, json, os, time, urllib.request, urllib.error
from pathlib import Path
from .mev import produce
from .jev import critique
from .kev import verify
from .laya import synthesize
from .leaderboard import Leaderboard

HOME = Path.home()
HS_URL = os.environ.get("HS_REMOTE_URL") or os.environ.get("HS_LOCAL_URL") or "http://localhost:18888"
HS_KEY = os.environ.get("HINDSIGHT_API_KEY", "")
BANK = os.environ.get("HINDSIGHT_BANK_ID", "termux-monorepo::primary")


def _retain(content: str, meta: dict) -> int:
    item = {"content": content, "metadata": {k: str(v) for k, v in meta.items()}}
    body = json.dumps({"items": [item]}).encode()
    hdrs = {"Content-Type": "application/json"}
    if HS_KEY:
        hdrs["Authorization"] = f"Bearer {HS_KEY}"
    req = urllib.request.Request(
        f"{HS_URL}/v1/default/banks/{BANK}/memories",
        data=body, method="POST", headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0



def _composition_hash(bank_cfg: dict) -> str:
    """Deterministic hash of bank configuration (mission, disposition, boosts)."""
    return hashlib.sha256(
        json.dumps(bank_cfg, sort_keys=True).encode()
    ).hexdigest()[:12]


def _bank_export(base: str, key: str, bank: str) -> dict:
    """GET /v1/default/banks/{bank}/export -> template manifest."""
    hdrs = {"Accept": "application/json"}
    if key:
        hdrs["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        f"{base}/v1/default/banks/{bank}/export", headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        return {}


def _bank_config(base: str, key: str, bank: str) -> dict:
    """GET /v1/default/banks/{bank} -> live config (mission, disposition)."""
    hdrs = {"Accept": "application/json"}
    if key:
        hdrs["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        f"{base}/v1/default/banks/{bank}", headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        return {}


async def run_trial(prompt: str,
                    providers: list[tuple[str, str]],
                    rubric: dict,
                    judge: tuple[str, str],
                    reference: dict | None = None,
                    task: str = "default",
                    client_factory=None) -> dict:
    """Return full trial record: artifacts, jevs, kevs, laya, score."""
    t0 = time.time()
    artifacts = []
    for index, (prov, model) in enumerate(providers):
        candidate_id = f"candidate-{index:04d}"
        try:
            a = await produce(prompt, prov, model, client_factory=client_factory)
            a.update({"candidate_id": candidate_id, "ok": True})
            artifacts.append(a)
        except Exception as e:
            artifacts.append({"candidate_id": candidate_id, "provider": prov,
                              "model": model, "text": "", "ok": False,
                              "error": str(e)[:200]})

    jevs = []
    for a in artifacts:
        candidate_id = a["candidate_id"]
        if not a.get("ok"):
            jevs.append({"candidate_id": candidate_id, "scores": {},
                         "rationale": "upstream_artifact_failed", "ok": False})
            continue
        try:
            j = await critique(a, rubric, judge[0], judge[1],
                               client_factory=client_factory)
            j.update({"candidate_id": candidate_id, "ok": True})
            jevs.append(j)
        except Exception as e:
            jevs.append({"candidate_id": candidate_id, "scores": {},
                         "rationale": str(e)[:200], "ok": False})

    kevs = []
    for a in artifacts:
        candidate_id = a["candidate_id"]
        if not a.get("ok"):
            kevs.append({"candidate_id": candidate_id, "match_score": None,
                         "deltas": [], "ok": False})
            continue
        try:
            k = verify(a, reference or {"text": ""}, method="token_f1")
            k.update({"candidate_id": candidate_id, "ok": True})
            kevs.append(k)
        except Exception as e:
            kevs.append({"candidate_id": candidate_id, "match_score": None,
                         "deltas": [], "ok": False, "error": str(e)[:200]})

    # Preserve one stage result per candidate. Laya joins and excludes by ID;
    # compacting successful stage arrays would shift verdicts across candidates.
    laya = synthesize(artifacts, jevs, kevs)

    lb = Leaderboard()
    _bank_cfg = _bank_config(HS_URL, HS_KEY, BANK)
    _comp_hash = _composition_hash(_bank_cfg)

    for entry in laya["ranked"]:
        lb.record(
            role="laya", task=task,
            provider=entry["provider"], model=entry["model"],
            score=entry["composite"], ok=True,
            composition_hash=_comp_hash,
        )

    winner = laya.get("winner") or {}
    if winner:
        _retain(
            f"[trial:{task}] winner={winner['provider']}/{winner['model']} "
            f"composite={winner['composite']} prompt={prompt[:200]}",
            {"kind": "trial", "task": task, "role": "laya",
             "provider": winner.get("provider",""),
             "model": winner.get("model",""),
             "composite": winner.get("composite",0.0)},
        )

    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "composition_hash": _comp_hash,
        "bank_config": _bank_cfg,
        "task": task,
        "prompt": prompt,
        "providers": providers,
        "judge": judge,
        "artifacts": artifacts,
        "jevs": jevs,
        "kevs": kevs,
        "laya": laya,
        "winner": winner,
        "elapsed_ms": int((time.time() - t0) * 1000),
    }
