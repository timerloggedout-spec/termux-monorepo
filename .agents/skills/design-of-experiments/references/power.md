# Precision and power planning
Do not report power without specifying effect contrast, effect units, error model, variance source, alpha, sidedness, multiplicity, allocation, sample size, and dependence assumptions. Distinguish coefficient, high-minus-low effect, and standardized effect.

For homoskedastic independent errors in a full-rank linear model with fixed X, Var(beta_hat)=sigma^2 (X'X)^(-1). For a prespecified contrast c, variance is sigma^2 c'(X'X)^(-1)c. Use the correct noncentral t/F distribution and actual error degrees of freedom, or a validated simulation matching the assignment and analysis.

Use a pilot, historical evidence, or sensitivity range for sigma; do not infer it from a design matrix. Report a precision or power curve over plausible variance/effect values when uncertainty is material. A rank audit is not a power analysis. Saturated models need external error information or additional replication, with assumptions clearly disclosed.

Simulation protocol: fix scenario and seed; simulate independent units and assignment; generate outcomes under explicit model and effect; fit the prespecified analysis; count rejections and failures; report Monte Carlo standard error sqrt(p*(1-p)/B). Missingness, cluster variation, and planned multiplicity should be represented. No general power calculator is bundled.
