# Advanced designs and handoffs
Mixtures: component proportions sum to a fixed total, so use a mixture parameterization (e.g. Scheffe forms) with constraints and a suitable region. Do not feed component proportions into an ordinary unrestricted-factor quadratic model with intercept and call it identifiable.

Constrained/optimal designs: specify candidate set or continuous feasible region, model, weights, criterion (D/A/I or another), runs, replication restrictions, start points, seed, and search convergence. Compare against alternate starts and scientifically relevant prediction locations. D-optimality is relative to the specified model and region, not universal superiority.

Robustness/Taguchi: distinguish control from noise factors and define the loss or robustness criterion. Signal-to-noise summaries are not a substitute for checking interactions and error structure. Consider crossed control/noise experiments and direct mean/variance modeling.

Sequential experimentation: predefine information gates, resource limits, augmentation rules, and independent confirmation. Adaptive stopping changes inferential properties; distinguish engineering optimization from confirmatory hypothesis testing.

Clinical, animal, hazardous, regulated, and consequential public-policy studies require qualified domain/statistical and governance review. This package does not generate regulatory protocols or approve unsafe settings.
