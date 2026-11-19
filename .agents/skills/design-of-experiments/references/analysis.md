# Analysis and confirmation
Prespecify response transformation, model terms, hierarchy, contrasts, alpha/multiplicity, missingness handling, exclusions, and variance structure. For ordinary fixed-effect DOE use a suitable linear model only when its error assumptions are defensible; use GLMs for suitable non-Gaussian responses and mixed models for appropriate hierarchical randomization.

Plot responses against actual time/order, factors, and groups. Inspect residual-versus-fit, residual-versus-order, scale, influential points, and distributional diagnostics. Avoid treating a normality test alone as a model validity verdict. Count and investigate failures rather than silently deleting them.

Maintain model hierarchy when interactions or squares are included unless a justified scientific parameterization says otherwise. Do not claim causal interpretation for measured, nonrandomized covariates. Distinguish exploratory term selection from confirmatory tests; data-driven model search can make naive intervals and p-values optimistic.

Report effect estimates in interpretable units, uncertainty, fit and prediction limitations, alias structure, deviations, and practical significance. Confirmation needs independent experimental units under the proposed setting and comparators, with prediction uncertainty and acceptance criteria set in advance. No outcome-fitting CLI is included in this release.
