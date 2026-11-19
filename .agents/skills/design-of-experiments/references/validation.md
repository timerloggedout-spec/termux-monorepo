# Design release audit
Check config schema, unique factor names, finite increasing ranges, intended model, valid generators, physical feasibility, run count, point coverage, allocation, randomization and operational restrictions. Then inspect model matrix rank, singular values/conditioning, and degrees of freedom.

Bundled counts: residual_df = n-rank(X); pure_error_df = n-number_of_unique_coded_settings; lack_of_fit_df = number_of_unique_coded_settings-rank(X). These are algebraic counts under the proposed fixed-effect treatment model. Pure-error interpretation requires independent equivalent-condition repetitions and a suitable error structure. No lack-of-fit F test can be performed without observed responses and a valid error estimate.

The audit normalizes each nonzero model column to unit Euclidean norm before computing a condition number. It flags exact proportional columns and absolute normalized dot products above 0.95. These pairwise diagnostics cannot detect all multicolumn dependencies; matrix rank supplies the broader check. Thresholds are numerical heuristics, not guarantees of adequate prediction precision.

Validation also checks coded/natural consistency, bounds, sequential unique run IDs, required metadata columns, expected treatment-setting multiplicities, and finite numeric data. It does not determine whether actual physical execution matched the schedule. Audit logs and independent review remain necessary.
