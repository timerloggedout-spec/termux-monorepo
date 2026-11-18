"""DO build ∧ name DoE cells: fractional-factorial generation 0 ∧ neighbor/new-level proposals."""
from __future__ import annotations

import hashlib
import itertools
import json
import random


def mid(values):
    return values[len(values) // 2]


def default_level(spec: dict) -> dict:
    return {k: mid(v["values"]) for k, v in (spec or {}).items()}


def signature(c: dict) -> str:
    return json.dumps([c["model"], c.get("model_level", {}), c["features"], c.get("features_level", {}), c["layer"]],
                      sort_keys=True)


def cell_id(gen: int, c: dict) -> str:
    h = hashlib.sha1(signature(c).encode()).hexdigest()[:6]
    return f"g{gen}-{c['model']}-{c['features']}-{c['layer']}-{h}"


def make_cell(gen, f, model, feat, layer, mlevel=None, flevel=None):
    c = {"model": model, "model_level": mlevel if mlevel is not None else default_level(f["model"]["params"].get(model)),
         "features": feat, "features_level": flevel if flevel is not None else default_level(f["features"]["params"].get(feat)),
         "layer": layer}
    c["id"] = cell_id(gen, c)
    return c


def generation0(factors: dict, design: str = "fractional-factorial") -> list[dict]:
    M, F, L = factors["model"]["levels"], factors["features"]["levels"], factors["layer"]["levels"]
    cells = []
    for (mi, m), (fi, ft), (li, ly) in itertools.product(enumerate(M), enumerate(F), enumerate(L)):
        # 1/3 fraction: each model meets every feature ∧ every layer once (Latin square per model)
        if design == "full-factorial" or (fi + li) % len(L) == mi % len(L):
            cells.append(make_cell(0, factors, m, ft, ly))
    return cells


def _extend(spec: dict, values: list, idx: int, step: int):
    """Return the neighbor value; at an edge, mint a new level geometrically within [min, max]."""
    j = idx + step
    if 0 <= j < len(values):
        return values[j], None
    if len(values) < 2:
        return None, None
    a, b = (values[0], values[1]) if j < 0 else (values[-1], values[-2])
    new = a * a / b if isinstance(a, (int, float)) and b else None
    if new is None:
        return None, None
    if spec.get("int"):
        new = int(round(new))
        if new == a:
            new = a - 1 if j < 0 else a + 1
    else:
        new = float(f"{new:.4g}")
    if ("min" in spec and new < spec["min"]) or ("max" in spec and new > spec["max"]):
        return None, None
    return new, ("prepend" if j < 0 else "append")


def neighbors(cell: dict, factors: dict, minted: list) -> list[dict]:
    out = []
    for part, kind_key in (("model_level", "model"), ("features_level", "features")):
        pspec = factors[kind_key]["params"].get(cell[kind_key], {})
        for name, spec in pspec.items():
            vals = spec["values"]
            cur = cell[part].get(name, mid(vals))
            if cur not in vals:
                continue
            for step in (-1, 1):
                v, how = _extend(spec, vals, vals.index(cur), step)
                if v is None:
                    continue
                if how:
                    spec["values"] = ([v] + vals) if how == "prepend" else (vals + [v])
                    minted.append({"factor": f"{kind_key}.{cell[kind_key]}.{name}", "new_level": v})
                    vals = spec["values"]
                n = json.loads(json.dumps(cell))
                n[part][name] = v
                out.append(n)
    for ly in factors["layer"]["levels"]:
        if ly != cell["layer"]:
            n = json.loads(json.dumps(cell)); n["layer"] = ly; out.append(n)
    for ft in factors["features"]["levels"]:
        if ft != cell["features"]:
            n = json.loads(json.dumps(cell)); n["features"] = ft
            n["features_level"] = default_level(factors["features"]["params"].get(ft)); out.append(n)
    return out


def explore(factors: dict, tried: set, rnd: random.Random, k: int) -> list[dict]:
    combos = list(itertools.product(factors["model"]["levels"], factors["features"]["levels"], factors["layer"]["levels"]))
    rnd.shuffle(combos)
    out = []
    for m, ft, ly in combos:
        c = make_cell(0, factors, m, ft, ly)
        if signature(c) not in tried:
            out.append(c)
        if len(out) >= k:
            break
    return out
