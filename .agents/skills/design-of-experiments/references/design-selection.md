# Design selection
| Objective/constraint | Candidate | Main caution |
|---|---|---|
| Few factors, interactions of interest | Full factorial | Runs grow exponentially |
| Many factors, screening budget | Regular fractional factorial | Explicit aliases and resolution |
| Strong screening budget pressure | Plackett-Burman | Main effects can be contaminated by interactions |
| Local curvature | CCD or Box-Behnken | Check region, squared-term estimability, confirmation |
| Drift/batches | Randomized blocks | Protect treatment information from block confounding |
| Hard-to-change settings | Split plot | Multiple error strata |
| Fractions sum to one | Mixture design | Ordinary independent-factor interpretation fails |
| Forbidden combinations | Constrained optimal design | Candidate space, model, and algorithm dependence |
| Noisy controllable/noise factors | Robustness design | Define robustness criterion and noise distribution |

Specify the model, feasible region, experimental unit, and randomization before selecting the matrix. A high-resolution fraction can still be too small for the proposed model. Check rank directly.

Adapt sequentially: screen, augment to resolve ambiguity/curvature, then confirm. Preserve the chronological stage variable; pooling stages without considering time and protocol changes can bias interpretation.
