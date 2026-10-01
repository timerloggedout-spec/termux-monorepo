"""Trial orchestrator — runs Mev → Jev → Kev → Laya end-to-end.

1. produce(prompt) via N providers → artifacts
2. critique(artifact, rubric) via judge (differ from producer)
3. verify(artifact, reference) — token_f1 if reference supplied
4. synthesize(artifacts, jevs, kevs) → ranked winner
5. persist to Leaderboard + Hindsight (fanout)
"""
from __future__ import annotations
import asyncio, json, os, time, urllib.request, urllib.error
from pathlib import Path
from .mev import produce
from .jev import critique
from .kev import verify
from .laya import synthesize
from .leaderboard import Leaderboard

HOME = Path.home()
HS_URL = os.environ.get("HS_REMOTE_URL") or os.environ.get("HS_LOCAL_URL") or "http://localhost:18888"
HS_KEY = os.environ.get("HINDSIGHT_API_KEY", "")
BANK = os.environ.get("HINDSIGHT_BANK_ID", "deepagent::termux-monorepo")


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
    for prov, model in providers:
        try:
            a = await produce(prompt, prov, model, client_factory=client_factory)
            a["ok"] = True
            artifacts.append(a)
        except Exception as e:
            artifacts.append({"provider": prov, "model": model, "text": "",
                              "ok": False, "error": str(e)[:200]})

    jevs = []
    for a in artifacts:
        try:
            j = await critique(a, rubric, judge[0], judge[1],
                               client_factory=client_factory)
            j["ok"] = True
            jevs.append(j)
        except Exception as e:
            jevs.append({"scores": {}, "rationale": str(e)[:200], "ok": False})

    kevs = []
    for a in artifacts:
        try:
            k = verify(a, reference or {"text": ""}, method="token_f1")
            k["ok"] = True
            kevs.append(k)
        except Exception as e:
            kevs.append({"match_score": 0.0, "deltas": [], "ok": False})

    laya = synthesize([a for a in artifacts if a["ok"]],
                      [j for j in jevs if j.get("ok")],
                      [k for k in kevs if k.get("ok")])

    lb = Leaderboard()
    for entry in laya["ranked"]:
        lb.record(
            role="laya", task=task,
            provider=entry["provider"], model=entry["model"],
            score=entry["composite"], ok=True,
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
