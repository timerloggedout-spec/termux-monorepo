# Factorials and regular fractions
For a two-level quantitative factor, code x=(natural-midpoint)/half_range. The coefficient of x is half the high-minus-low effect in a balanced orthogonal first-order parameterization; it is not the full effect.

A regular fraction defines generated factors as signed products of independent basic factors. Example D=A*B*C gives I=ABCD (resolution IV): main effects are aliased with three-factor interactions; two-factor interactions are aliased with other two-factor interactions, including AB=CD, AC=BD, AD=BC. An intercept plus all four main effects and six pairwise interactions cannot be uniquely fit from its eight corner runs.

Resolution is the shortest nonidentity defining word length. Resolution III confounds some main effects with two-factor interactions; IV separates main effects from two-factor interactions but not all pairs from each other; V separates main effects and two-factor interactions from each other under the usual higher-order-interaction interpretation. Higher-order terms can still alias important effects.

The CLI takes generator products as names of basic factors only, e.g. {"D":"A*B*C"}; an optional leading minus sign selects the complementary fraction. It computes the full defining subgroup for these generators. It does not search for a minimum-aberration fraction or select scientifically negligible interactions.

A center is not a replicate of a factorial corner. Center repetitions can contribute pure error and a global curvature check; they do not identify separate square coefficients. Replicate whole treatments on independent units when independent error is required.
