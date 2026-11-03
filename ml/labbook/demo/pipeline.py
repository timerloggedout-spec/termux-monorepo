"""The canonical labbook demo workload.

The shape the whole validation program ran on every platform: a branch
(two competing model families) x a 5-fold foreach, a join that refuses
to merge conflicting values, and a gate stated as data. Deterministic
(synthetic data, fixed split: row i belongs to fold i % 5).

Arithmetic note: `_mse` accumulates squared errors in row order and
divides once — byte-for-byte the same order `labbook.verify` uses to
re-derive the headline from stored parts, so agreement is exact.
"""

import random

from labbook.compiler import Node, Pipeline

N_FOLDS = 5
TRUE_MODEL = "y = 1.0 + 2.0*x + 0.3*x^2 + noise(0, 0.5)"


def _feat(name, x):
    if name == "1":
        return 1.0
    if name == "x":
        return x
    if name == "x^2":
        return x * x
    raise ValueError(f"unknown feature {name!r}")


def _solve(a, b):
    """Gaussian elimination for the normal equations (small, exact order)."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / m[i][i]
    return x


def _fit(rows, features, ridge):
    k = len(features)
    a = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    for row in rows:
        xs = [_feat(f, row["x"]) for f in features]
        for i in range(k):
            b[i] += xs[i] * row["y"]
            for j in range(k):
                a[i][j] += xs[i] * xs[j]
    for i in range(k):
        a[i][i] += ridge
    return _solve(a, b)


def _mse(rows, features, coef):
    se = 0.0
    for row in rows:
        pred = 0.0
        for c, f in zip(coef, features):
            pred += c * _feat(f, row["x"])
        se += (row["y"] - pred) ** 2
    return se / len(rows)


# ------------------------------------------------------------------ nodes


def load_data(ctx, inputs, params):
    rng = random.Random(params["seed"])
    rows = []
    for _ in range(200):
        x = rng.uniform(-3.0, 3.0)
        y = 1.0 + 2.0 * x + 0.3 * x * x + rng.gauss(0.0, 0.5)
        rows.append({"x": x, "y": y})
    ctx.log_metric("n_rows", len(rows))
    return {"dataset": rows}


def _train(features, metric_name, model_asset, metrics_asset):
    def node(ctx, inputs, params):
        rows = inputs["dataset"]
        fold = params["fold"]
        test = [r for i, r in enumerate(rows) if i % N_FOLDS == fold]
        train = [r for i, r in enumerate(rows) if i % N_FOLDS != fold]
        coef = _fit(train, features, params["ridge"])
        mse = _mse(test, features, coef)
        ctx.log_metric(metric_name, mse)
        return {
            model_asset: {"fold": fold, "features": features, "coef": coef},
            metrics_asset: {"fold": fold, "mse": mse},
        }

    return node


train_linear = _train(["1", "x"], "fold_mse_linear",
                      "fold_models_linear", "fold_metrics_linear")
train_quadratic = _train(["1", "x", "x^2"], "fold_mse_quad",
                         "fold_models_quad", "fold_metrics_quad")


def join(ctx, inputs, params):
    """Merge the arms. Refuses to guess (Metaflow row 6): a fold reported
    twice with different values is a hard failure naming the conflict,
    never a silent pick."""
    means = {}
    for arm, metrics_asset in (("linear", "fold_metrics_linear"),
                               ("quad", "fold_metrics_quad")):
        by_fold = {}
        for entry in inputs[metrics_asset]:
            fold, mse = entry["fold"], entry["mse"]
            if fold in by_fold and by_fold[fold] != mse:
                raise ValueError(
                    f"conflicting values for fold {fold} of {metrics_asset}: "
                    f"{by_fold[fold]!r} vs {mse!r} — refusing to merge")
            by_fold[fold] = mse
        missing = [f for f in range(N_FOLDS) if f not in by_fold]
        if missing:
            raise ValueError(f"{metrics_asset} is missing folds {missing}")
        means[arm] = sum(by_fold[f] for f in range(N_FOLDS)) / N_FOLDS
    winner = "linear" if means["linear"] <= means["quad"] else "quadratic"
    winner_mse = means["linear"] if winner == "linear" else means["quad"]
    ctx.log_metric("cv_mean_linear", means["linear"])
    ctx.log_metric("cv_mean_quad", means["quad"])
    ctx.log_metric("winner_mse", winner_mse)
    return {"cv_metrics": {"cv_mean_linear": means["linear"],
                           "cv_mean_quad": means["quad"],
                           "winner": winner}}


def report(ctx, inputs, params):
    cv = inputs["cv_metrics"]
    text = (
        "labbook demo report\n"
        f"true model: {TRUE_MODEL}\n"
        f"cv_mean_linear: {cv['cv_mean_linear']!r}\n"
        f"cv_mean_quad:   {cv['cv_mean_quad']!r}\n"
        f"winner: {cv['winner']}\n"
    )
    return {"report": text}


def legacy_export(ctx, inputs, params):
    """A pickle-class artifact, on purpose: the flagged-exception path
    (row 2) exercised by the canonical workload so the format test has
    something real to check."""
    return {"legacy_blob": {"cv_metrics": inputs["cv_metrics"],
                            "note": "legacy consumer payload"}}


PIPELINE = Pipeline(
    name="demo",
    params={
        "seed": {"type": "int", "default": 42},
        "ridge": {"type": "float", "default": 0.1},
    },
    cache_policy="per-artifact-store",
    stack_name="local",
    nodes=[
        Node("load", "pipeline:load_data",
             outputs=["dataset"], params=["seed"]),
        Node("train_linear", "pipeline:train_linear",
             inputs={"dataset": "one"},
             outputs=["fold_models_linear", "fold_metrics_linear"],
             params=["ridge"], foreach={"param": "fold", "values": [0, 1, 2, 3, 4]}),
        Node("train_quadratic", "pipeline:train_quadratic",
             inputs={"dataset": "one"},
             outputs=["fold_models_quad", "fold_metrics_quad"],
             params=["ridge"], foreach={"param": "fold", "values": [0, 1, 2, 3, 4]}),
        Node("join", "pipeline:join",
             inputs={"fold_metrics_linear": "all",
                     "fold_metrics_quad": "all",
                     "fold_models_linear": "all",
                     "fold_models_quad": "all"},
             outputs=["cv_metrics"]),
        Node("report", "pipeline:report",
             inputs={"cv_metrics": "one"}, outputs=["report"],
             gate="cv_mean_quad < 1.0"),
        Node("legacy_export", "pipeline:legacy_export",
             inputs={"cv_metrics": "one"}, outputs=["legacy_blob"]),
    ],
    aggregates={
        "cv_mean_linear": {"op": "mean", "metric": "fold_mse_linear",
                           "node": "train_linear"},
        "cv_mean_quad": {"op": "mean", "metric": "fold_mse_quad",
                         "node": "train_quadratic"},
    },
    verify={"headline": "cv_mean_quad", "strategy": "fold_mse_mean",
            "dataset": "dataset", "models": "fold_models_quad",
            "metric": "fold_mse_quad"},
)
